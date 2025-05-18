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

from cli import CodyCLI
from redis_agent import RedisAgent

if __name__ == "__main__":
    # 初始化Redis智能体
    agent = RedisAgent()
    
    # 示例交互
    sample_data = {
        "user_id": 1001,
        "query": "天气查询",
        "timestamp": "2024-03-15 10:00:00"
    }
    
    # 存储数据
    storage_key = "user:1001:session"
    agent.store_data(storage_key, sample_data)
    
    # 检索数据
    retrieved = agent.retrieve_data(storage_key)
    print("检索到的数据:", retrieved)
    
    # 处理请求
    response = agent.process_request(sample_data)
    print("\n处理结果:", response)