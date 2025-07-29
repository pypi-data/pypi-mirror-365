#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import uuid
import time
from datetime import datetime
from collections import namedtuple, OrderedDict
from importlib.resources import read_text

import requests
from loguru import logger
from rich.rule import Rule
from rich.panel import Panel
from rich.align import Align
from rich.table import Table
from rich.syntax import Syntax
from rich.console import Console, Group
from rich.markdown import Markdown

from .. import T, __respkg__
from ..exec import BlockExecutor
from .runtime import CliPythonRuntime
from .plugin import event_bus
from .utils import get_safe_filename
from .blocks import CodeBlocks, CodeBlock
from .interface import Stoppable
from .multimodal import MMContent, LLMContext

CONSOLE_WHITE_HTML = read_text(__respkg__, "console_white.html")
CONSOLE_CODE_HTML = read_text(__respkg__, "console_code.html")

class Task(Stoppable):
    MAX_ROUNDS = 16

    def __init__(self, context):
        super().__init__()
        self.task_id = uuid.uuid4().hex
        self.log = logger.bind(src='task', id=self.task_id)
        
        self.context = context
        self.settings = context.settings
        self.prompts = context.prompts

        self.start_time = None
        self.done_time = None
        self.instruction = None
        self.saved = None
        self.gui = context.gui
        
        self.cwd = context.cwd / self.task_id
        self.console = Console(file=context.console.file, record=True)
        self.max_rounds = self.settings.get('max_rounds', self.MAX_ROUNDS)
        
        self.mcp = context.mcp
        self.client = context.client_manager.Client()
        self.role = context.role_manager.current_role
        self.code_blocks = CodeBlocks(self.console)
        self.runtime = CliPythonRuntime(self)
        self.runner = BlockExecutor()
        self.runner.set_python_runtime(self.runtime)

    def to_record(self):
        TaskRecord = namedtuple('TaskRecord', ['task_id', 'start_time', 'done_time', 'instruction'])
        start_time = datetime.fromtimestamp(self.start_time).strftime('%H:%M:%S') if self.start_time else '-'
        done_time = datetime.fromtimestamp(self.done_time).strftime('%H:%M:%S') if self.done_time else '-'
        return TaskRecord(
            task_id=self.task_id,
            start_time=start_time,
            done_time=done_time,
            instruction=self.instruction[:32] if self.instruction else '-'
        )
    
    def use(self, name):
        ret = self.client.use(name)
        return ret

    def save(self, path):
       if self.console.record:
           self.console.save_html(path, clear=False, code_format=CONSOLE_WHITE_HTML)

    def save_html(self, path, task):
        if 'chats' in task and isinstance(task['chats'], list) and len(task['chats']) > 0:
            if task['chats'][0]['role'] == 'system':
                task['chats'].pop(0)

        task_json = json.dumps(task, ensure_ascii=False, default=str)
        html_content = CONSOLE_CODE_HTML.replace('{{code}}', task_json)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html_content)
        except Exception as e:
            self.console.print_exception()
        
    def _auto_save(self):
        instruction = self.instruction
        task = OrderedDict()
        task['instruction'] = instruction
        task['start_time'] = self.start_time
        task['done_time'] = self.done_time
        task['chats'] = self.client.history.json()
        task['runner'] = self.runner.history
        task['blocks'] = self.code_blocks.to_list()

        filename = self.cwd / "task.json"
        try:
            json.dump(task, open(filename, 'w', encoding='utf-8'), ensure_ascii=False, indent=4, default=str)
        except Exception as e:
            self.log.exception('Error saving task')

        filename = self.cwd / "console.html"
        #self.save_html(filename, task)
        self.save(filename)
        self.saved = True
        self.log.info('Task auto saved')

    def done(self):
        if not self.instruction or not self.start_time:
            self.log.warning('Task not started, skipping save')
            return
        
        self.done_time = time.time()
        if not self.saved:
            self.log.warning('Task not saved, trying to save')
            self._auto_save()

        os.chdir(self.context.cwd)  # Change back to the original working directory
        curname = self.task_id
        newname = get_safe_filename(self.instruction, extension=None)
        if newname and os.path.exists(curname):
            try:
                os.rename(curname, newname)
            except Exception as e:
                self.log.exception('Error renaming task directory', curname=curname, newname=newname)

        self.log.info('Task done', path=newname)
        self.console.print(f"[green]{T('Result file saved')}: \"{newname}\"")
        self.context.diagnose.report_code_error(self.runner.history)
        if self.settings.get('share_result'):
            self.sync_to_cloud()
        
    def process_reply(self, markdown):
        parse_mcp = self.mcp is not None
        ret = self.code_blocks.parse(markdown, parse_mcp=parse_mcp)
        if not ret:
            return None
        
        json_str = json.dumps(ret, ensure_ascii=False, indent=2, default=str)
        self.box(f"✅ {T('Message parse result')}", json_str, lang="json")

        if 'call_tool' in ret:
            return self.process_mcp_reply(ret['call_tool'])

        errors = ret.get('errors')
        if errors:
            event_bus('result', errors)
            self.console.print(f"{T('Start sending feedback')}...", style='dim white')
            feed_back = f"# 消息解析错误\n{json_str}"
            ret = self.chat(feed_back)
        elif 'exec_blocks' in ret:
            ret = self.process_code_reply(ret['exec_blocks'])
        else:
            ret = None
        return ret

    def print_code_result(self, block, result, title=None):
        line_numbers = True if 'traceback' in result else False
        syntax_code = Syntax(block.code, block.lang, line_numbers=line_numbers, word_wrap=True)
        json_result = json.dumps(result, ensure_ascii=False, indent=2, default=str)
        syntax_result = Syntax(json_result, 'json', line_numbers=False, word_wrap=True)
        group = Group(syntax_code, Rule(), syntax_result)
        panel = Panel(group, title=title or block.name)
        self.console.print(panel)

    def process_code_reply(self, exec_blocks):
        results = OrderedDict()
        for block in exec_blocks:
            event_bus('exec', block)
            self.console.print(f"⚡ {T('Start executing code block')}: {block.name}", style='dim white')
            result = self.runner(block)
            self.print_code_result(block, result)
            results[block.name] = result
            event_bus('result', result)

        msg = self.prompts.get_results_prompt(results)
        self.console.print(f"{T('Start sending feedback')}...", style='dim white')
        return self.chat(msg)

    def process_mcp_reply(self, json_content):
        """处理 MCP 工具调用的回复"""
        block = {'content': json_content, 'language': 'json'}
        event_bus('tool_call', block)
        self.console.print(f"⚡ {T('Start calling MCP tool')} ...", style='dim white')

        call_tool = json.loads(json_content)
        result = self.mcp.call_tool(call_tool['name'], call_tool.get('arguments', {}))
        event_bus('result', result)
        code_block = CodeBlock(
            code=json_content,
            lang='json',
            name=call_tool.get('name', 'MCP Tool Call'),
            version=1,
        )
        self.print_code_result(code_block, result, title=T("MCP tool call result"))
        self.console.print(f"{T('Start sending feedback')}...", style='dim white')
        msg = self.prompts.get_mcp_result_prompt(result)
        return self.chat(msg)

    def box(self, title, content, align=None, lang=None):
        if lang:
            content = Syntax(content, lang, line_numbers=True, word_wrap=True)
        else:
            content = Markdown(content)

        if align:
            content = Align(content, align=align)
        
        self.console.print(Panel(content, title=title))

    def print_summary(self, detail=False):
        history = self.client.history
        if detail:
            table = Table(title=T("Task Summary"), show_lines=True)

            table.add_column(T("Round"), justify="center", style="bold cyan", no_wrap=True)
            table.add_column(T("Time(s)"), justify="right")
            table.add_column(T("In Tokens"), justify="right")
            table.add_column(T("Out Tokens"), justify="right")
            table.add_column(T("Total Tokens"), justify="right", style="bold magenta")

            round = 1
            for row in history.get_usage():
                table.add_row(
                    str(round),
                    str(row["time"]),
                    str(row["input_tokens"]),
                    str(row["output_tokens"]),
                    str(row["total_tokens"]),
                )
                round += 1
            self.console.print("\n")
            self.console.print(table)

        summary = history.get_summary()
        summary['elapsed_time'] = time.time() - self.start_time
        summarys = "| {rounds} | {time:.3f}s/{elapsed_time:.3f}s | Tokens: {input_tokens}/{output_tokens}/{total_tokens}".format(**summary)
        event_bus.broadcast('summary', summarys)
        self.console.print(f"\n⏹ [cyan]{T('End processing instruction')} {summarys}")

    def chat(self, context: LLMContext, *, system_prompt=None):
        quiet = self.context.settings.gui and not self.context.settings.debug
        msg = self.client(context, system_prompt=system_prompt, quiet=quiet)
        if msg.role == 'error':
            self.console.print(f"[red]{msg.content}[/red]")
            return None
        if msg.reason:
            content = f"{msg.reason}\n\n-----\n\n{msg.content}"
        else:
            content = msg.content
        self.box(f"[yellow]{T('Reply')} ({self.client.name})", content)
        return msg.content

    def _get_system_prompt(self):
        params = {}
        if self.mcp:
            params['mcp_tools'] = self.mcp.get_tools_prompt()
        params['util_functions'] = self.runtime.get_function_list()
        params['tool_functions'] = {}
        params['role'] = self.role
        return self.prompts.get_default_prompt(**params)
    
    def run(self, instruction: str):
        """
        执行自动处理循环，直到 LLM 不再返回代码消息
        instruction: 用户输入的字符串（可包含@file等多模态标记）
        """
        self.box(f"[yellow]{T('Start processing instruction')}", instruction, align="center")
        mmc = MMContent(instruction, base_path=self.context.cwd)
        try:
            content = mmc.content
        except Exception as e:
            self.console.print(f"[red]{e}[/red]")
            return

        if not self.client.has_capability(content):
            self.console.print(f"[red]{T('Current model does not support this content')}[/red]")
            return

        if not self.start_time:
            self.start_time = time.time()
            self.instruction = instruction
            event_bus('task_start', content)
            if isinstance(content, str):
                user_prompt = self.prompts.get_task_prompt(content, gui=self.gui)
            system_prompt = self._get_system_prompt()
        else:
            system_prompt = None
            if isinstance(content, str):
                user_prompt = self.prompts.get_chat_prompt(content, self.instruction)

        self.cwd.mkdir(exist_ok=True)
        os.chdir(self.cwd)

        rounds = 1
        max_rounds = self.max_rounds
        self.saved = False
        response = self.chat(user_prompt, system_prompt=system_prompt)
        while response and rounds <= max_rounds:
            response = self.process_reply(response)
            rounds += 1
            if self.is_stopped():
                self.log.info('Task stopped')
                break
        
        self.print_summary()
        self._auto_save()
        self.console.bell()
        self.log.info('Loop done', rounds=rounds)

    def sync_to_cloud(self, verbose=True):
        """ Sync result
        """
        url = T("https://store.aipy.app/api/work")

        trustoken_apikey = self.context.settings.get('llm', {}).get('Trustoken', {}).get('api_key')
        if not trustoken_apikey:
            trustoken_apikey = self.context.settings.get('llm', {}).get('trustoken', {}).get('api_key')
        if not trustoken_apikey:
            return False
        self.console.print(f"[yellow]{T('Uploading result, please wait...')}")
        try:
            # Serialize twice to remove the non-compliant JSON type.
            # First, use the json.dumps() `default` to convert the non-compliant JSON type to str.
            # However, NaN/Infinity will remain.
            # Second, use the json.loads() 'parse_constant' to convert NaN/Infinity to str.
            data = json.loads(
                json.dumps({
                    'apikey': trustoken_apikey,
                    'author': os.getlogin(),
                    'instruction': self.instruction,
                    'llm': self.client.history.json(),
                    'runner': self.runner.history,
                }, ensure_ascii=False, default=str),
                parse_constant=str)
            response = requests.post(url, json=data, verify=True,  timeout=30)
        except Exception as e:
            print(e)
            return False

        status_code = response.status_code
        if status_code in (200, 201):
            if verbose:
                data = response.json()
                url = data.get('url', '')
                if url:
                    self.console.print(f"[green]{T('Article uploaded successfully, {}', url)}[/green]")
            return True

        if verbose:
            self.console.print(f"[red]{T('Upload failed (status code: {})', status_code)}:", response.text)
        return False
