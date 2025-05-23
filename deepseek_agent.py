"""
Copyright 2025 NXP

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import requests
from typing import Optional

class DeepSeekAgent:
    API_BASE = 'https://api.deepseek.com/v1'
    
    def __init__(self):
        if not self.check_dependencies():
            self._install_dependencies()
        
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        if not self.api_key:
            raise ValueError('DEEPSEEK_API_KEY未在环境变量中设置')
            
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        })

    def handle_command(self, params):
        command = params[0] if params else 'help'
        if command == 'chat':
            return self._handle_chat(params[1:])
        return '未知命令，可用命令: chat'

    def _handle_chat(self, args):
        try:
            response = self.session.post(
                f'{self.API_BASE}/chat/completions',
                json={
                    'model': 'deepseek-chat',
                    'messages': [{'role': 'user', 'content': ' '.join(args)}]
                }
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except requests.exceptions.RequestException as e:
            return f'API请求失败: {str(e)}'

    def check_dependencies(self):
        try:
            import requests
            return True
        except ImportError:
            return False

    def _install_dependencies(self):
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'requests'])