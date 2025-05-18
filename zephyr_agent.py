import subprocess
import os
from typing import Optional

class ZephyrAgent:
    COMMAND_MAP = {
        'init': ['init'],
        'clone': ['clone'],
        'pr': ['pr'],
        'compile': ['compile'],
        'test': ['test']
    }

    def __init__(self, project_path: str = '.'):
        self.project_path = os.path.abspath(project_path)

    def handle_command(self, params):
        command_type = params[0] if params else 'help'
        args = params[1:] if len(params) > 1 else []
        
        if command_type in self.COMMAND_MAP:
            method_name = f'execute_{command_type}'
            return getattr(self, method_name)(args)
        return _('cli.error.unknown_command')

    def execute_init(self, args):
        path = next((a.split('=')[1] for a in args if '--path' in a), '.')
        self.__init__(path)
        return self.setup_environment()

    def execute_clone(self, args):
        if not args:
            raise ValueError(_('cli.error.missing_url'))
        self.clone_repo(args[0])
        return _('cli.repo_cloned').format(path=self.project_path)

    def check_environment(self) -> bool:
        required_tools = ['cmake', 'ninja', 'dtc', 'west', 'gcc', 'python3-dev', 'twister']
        required_python = ['pytest']
        missing = [tool for tool in required_tools 
                  if not self._check_tool_installed(tool)]
        missing += [pkg for pkg in required_python 
                  if not self._check_python_package(pkg)]
        if missing:
            print(_('cli.error.missing_tools').format(missing=', '.join(missing)))
            return False
        return True

    # 新增Python包检测逻辑和测试方法
    def _check_python_package(self, package: str) -> bool:
        try:
            subprocess.run(['python', '-m', 'pip', 'show', package],
                          stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL,
                          check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def run_twister_tests(self, args: str = ''):
        try:
            cmd = ['west', 'twister']
            if args:
                cmd.extend(args.split())
            subprocess.run(cmd,
                         cwd=self.project_path,
                         check=True,
                         capture_output=True)
        except subprocess.CalledProcessError as e:
            error_msg = _('cli.error.test_failure').format(error=e.stderr.decode())
            if 'No tests found' in error_msg:
                raise RuntimeError(_('cli.error.no_tests_found'))
            elif 'build error' in error_msg.lower():
                raise RuntimeError(_('cli.error.compile_failed'))
            raise RuntimeError(error_msg)

    def clone_repo(self, repo_url: str):
        try:
            subprocess.run(['git', 'clone', '--recursive', repo_url, self.project_path],
                          check=True,
                          capture_output=True)
        except subprocess.CalledProcessError as e:
            error_output = e.stderr.decode()
            if 'fatal: not a git repository' in error_output:
                raise RuntimeError(_('cli.error.init_first'))
            elif 'Could not resolve host' in error_output:
                raise RuntimeError(_('cli.error.network_issue'))
            raise RuntimeError(_('cli.error.repo_clone_failed').format(error=error_output))

    def switch_pr(self, pr_number: int):
        try:
            subprocess.run(['git', 'fetch', 'origin', f'pull/{pr_number}/head:pr-{pr_number}'],
                          cwd=self.project_path,
                          check=True,
                          capture_output=True)
            subprocess.run(['git', 'checkout', f'pr-{pr_number}'],
                          cwd=self.project_path,
                          check=True)
        except subprocess.CalledProcessError as e:
            error_output = e.stderr.decode()
            if 'invalid refspec' in error_output:
                raise RuntimeError(_('cli.error.invalid_pr').format(number=pr_number))
            elif 'pathspec' in error_output:
                raise RuntimeError(_('cli.error.uncommitted_changes'))
            raise RuntimeError(_('cli.error.pr_switch_failed').format(error=error_output))

    def _check_tool_installed(self, tool: str) -> bool:
        try:
            subprocess.run([tool, '--version'],
                          capture_output=True,
                          check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def setup_environment(self):
        if not self.check_environment():
            # 安装必要依赖
            subprocess.run(['pip', 'install', 'west'], check=True)
            subprocess.run(['west', 'update'], check=True)

    def clone_repo(self, repo_url: str):
        subprocess.run(['git', 'clone', repo_url, self.project_path], 
                      check=True)

    def switch_pr(self, pr_number: int):
        subprocess.run(['git', 'fetch', 'origin', f'pull/{pr_number}/head:pr-{pr_number}'],
                      cwd=self.project_path,
                      check=True)
        subprocess.run(['git', 'checkout', f'pr-{pr_number}'],
                      cwd=self.project_path,
                      check=True)
        subprocess.run(['west', 'update'], check=True)

    def compile_project(self, board: str = 'native_posix'):
        build_dir = os.path.join(self.project_path, 'build')
        subprocess.run(['west', 'build', '-b', board, '.'],
                      cwd=self.project_path,
                      check=True)