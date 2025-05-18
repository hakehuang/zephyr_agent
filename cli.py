import argparse
import subprocess
import sys
from dotenv import load_dotenv
import os
from zephyr_agent import ZephyrAgent
from deepseek_agent import DeepSeekAgent

def execute_cody_command(args):
    try:
        result = subprocess.run(
            ['npx', 'cody'] + args,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(_('cli.error.command_failed').format(error=e.stderr))
        sys.exit(1)

class CodyCLI:
    AGENT_MATRIX = {
        'zephyr': {
            'patterns': [
                r'(?i)({}|{})'.format(_('cli.pattern.env_init'), _('cli.pattern.set_path')),
                r'(?i)({}|{})'.format(_('cli.pattern.clone_repo'), _('cli.pattern.download_code')),
                r'(?i)({}|{})'.format(_('cli.pattern.switch_pr'), _('cli.pattern.merge_request')),
                r'(?i)({}|{})'.format(_('cli.pattern.compile'), _('cli.pattern.build_fw')),
                r'(?i)({}|{})'.format(_('cli.pattern.run_test'), _('cli.pattern.execute_case'))
            ],
            'agent': ZephyrAgent
        },
        'deepseek': {
            'patterns': [
                r'(?i)(智能问答|知识查询|API调用)',
                r'(?i)使用DeepSeek',
                r'(?i)调用.*模型'
            ],
            'agent': DeepSeekAgent
        }
    }

    def __init__(self):
        self.active_agents = {}

    def _classify_intent(self, query):
        for agent_name, config in self.AGENT_MATRIX.items():
            for pattern in config['patterns']:
                if re.search(pattern, query, re.IGNORECASE):
                    return {
                        'agent': agent_name,
                        'params': self._extract_parameters(agent_name, query)
                    }
        return {'agent': 'cody', 'params': []}

    def process_query(self, query):
        intent = self._classify_intent(query)
        if intent['agent'] == 'cody':
            # 检测Cody CLI可用性
            try:
                subprocess.run(['npx', 'cody', '--version'], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                # 自动切换到DeepSeek备用模式
                intent['agent'] = 'deepseek'
                intent['params'] = self._extract_parameters('deepseek', query)
            else:
                return execute_cody_command(['--query', query])
        
        agent_class = self.AGENT_MATRIX[intent['agent']]['agent']
        if intent['agent'] not in self.active_agents:
            self.active_agents[intent['agent']] = agent_class()
        
        try:
            response = self.active_agents[intent['agent']].handle_command(intent['params'])
            return {'agent': intent['agent'], 'response': response}
        except Exception as e:
            return {'agent': intent['agent'], 'error': str(e)}

    def _extract_parameters(self, agent_name, query):
        param_extractors = {
            'zephyr': {
                'init': lambda q: ['init', '--path', re.search(r'{}[：:]\s*(\S+)'.format(_('cli.pattern.path')), q).group(1)] if _('cli.pattern.path') in q else ['init'],
                'clone': lambda q: ['clone', re.search(r'(http[s]?://\S+)', q).group(1)],
                'pr': lambda q: ['pr', re.search(r'{}|{}'.format(_('cli.pattern.pr_number'), _('cli.pattern.pr_id')), q).group(1)],
                'compile': lambda q: ['compile', '-b', re.search(r'{}[：:]\s*(\w+)'.format(_('cli.pattern.board')), q).group(1)]
            },
        'deepseek': {
            'chat': lambda q: ['chat', re.sub(r'^{}\s*'.format(_('cli.pattern.qa_prefix')), '', q)]
        }
        }

        command_types = {
            r'(?i){}'.format(_('cli.pattern.init')): 'init',
            r'(?i){}'.format(_('cli.pattern.clone')): 'clone',
            r'(?i){}'.format(_('cli.pattern.pr')): 'pr',
            r'(?i){}'.format(_('cli.pattern.compile')): 'compile'
        }
        for pattern, cmd_type in command_types.items():
            if re.search(pattern, query):
                return param_extractors[agent_name][cmd_type](query)
        return []

    def _execute_zephyr_command(self, base_cmd, query):
        cmd_args = base_cmd.copy()
        # 参数提取逻辑
        if 'init' in base_cmd:
            if '路径' in query:
                cmd_args.extend(['--path', re.search(r'路径[：:]\s*(\S+)', query).group(1)])
        elif 'clone' in base_cmd:
            url_match = re.search(r'(http[s]?://\S+)', query)
            if url_match:
                cmd_args.append(url_match.group(1))
        elif 'pr' in base_cmd:
            pr_num = re.search(r'PR\s*(\d+|#\d+)|编号\s*(\d+)', query)
            if pr_num:
                cmd_args.append(pr_num.group(1) or pr_num.group(2))
        elif 'compile' in base_cmd:
            board_match = re.search(r'板型[：:]\s*(\w+)', query)
            if board_match:
                cmd_args.extend(['-b', board_match.group(1)])
        return execute_cody_command(cmd_args)

if __name__ == "__main__":
    load_dotenv()
    import re
    parser = argparse.ArgumentParser(prog='cody', description=_('cli.description'))
    parser.add_argument('--zephyr-cmd', help=_('cli.internal.zephyr_command'), nargs='*', default=[])
    subparsers = parser.add_subparsers(dest='command')

    # 查询子命令
    query_parser = subparsers.add_parser('query', help=_('cli.help.query'))
    query_parser.add_argument('input', nargs='?', help='查询内容')

    # 交互式子命令
    interactive_parser = subparsers.add_parser('interactive', help=_('cli.help.interactive'))

    # Zephyr子命令
    zephyr_parser = subparsers.add_parser('zephyr', help=_('cli.help.zephyr'))
    zephyr_subparsers = zephyr_parser.add_subparsers(dest='zephyr_command', required=True)

    init_parser = zephyr_subparsers.add_parser('init', help=_('cli.help.init_env'))
    init_parser.add_argument('--path', type=str, default='.', help=_('cli.help.init_path'))

    clone_parser = zephyr_subparsers.add_parser('clone', help=_('cli.help.clone_repo'))
    clone_parser.add_argument('repo_url', type=str, help=_('cli.help.repo_url'))

    pr_parser = zephyr_subparsers.add_parser('pr', help=_('cli.help.switch_pr'))
    pr_parser.add_argument('pr_number', type=int, help=_('cli.help.pr_number'))

    compile_parser = zephyr_subparsers.add_parser('compile', help=_('cli.help.compile'))
    compile_parser.add_argument('-b', '--board', type=str, required=True, help=_('cli.help.board'))

    test_parser = zephyr_subparsers.add_parser('test', help=_('cli.help.run_tests'))
    test_parser.add_argument('-a', '--args', help=_('cli.help.additional_args'))

    try:
        cli = CodyCLI()
        
        # 处理自然语言解析后的内部命令
        if args.zephyr_cmd:
            args.command = 'zephyr'
            args.zephyr_command = args.zephyr_cmd[0]
        
        if args.command == 'query':
            query = args.input or input(_('cli.prompt.query'))
            response = cli.process_query(query)
            print(response)
        elif args.command == 'interactive':
            while True:
                query = input(_('cli.prompt.interactive'))
                if query.lower() in ('exit', 'quit'): break
                if query:
                    response = cli.process_query(query)
                    if isinstance(response, dict):
                        if 'error' in response:
                            print(f"[!] {response['agent']} Agent Error: {response['error']}")
                        else:
                            print(f"[{response['agent'].upper()}] {response.get('response', '')}")
                    else:
                        print(f"[CODY] {response}")
        elif args.command == 'zephyr':
            agent = ZephyrAgent(args.path) if hasattr(args, 'path') else ZephyrAgent()
            try:
                if args.zephyr_command == 'init':
                    if not agent.check_environment():
                        print(_('cli.installing_dependencies'))
                        agent.setup_environment()
                    else:
                        print(_('cli.env_ready'))
                elif args.zephyr_command == 'clone':
                    agent.clone_repo(args.repo_url)
                    print(_('cli.repo_cloned').format(path=agent.project_path))
                elif args.zephyr_command == 'pr':
                    agent.switch_pr(args.pr_number)
                    print(_('cli.pr_switched').format(number=args.pr_number))
                elif args.zephyr_command == 'compile':
                    agent.compile_project(args.board)
                    print(_('cli.build_complete'))
                elif args.zephyr_command == 'test':
                    agent.run_twister_tests(args.args)
            except subprocess.CalledProcessError as e:
                print(_('cli.error.command').format(error=e.stderr))
            except Exception as e:
                print(_('cli.error.general').format(error=str(e)))
    except Exception as e:
        print(_('cli.error.prefix') + str(e))