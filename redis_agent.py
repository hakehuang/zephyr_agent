import redis
import json

class RedisAgent:
    def __init__(self, host='localhost', port=6379, db=0):
        self.client = redis.Redis(host=host, port=port, db=db)
        self._check_connection()

    def _check_connection(self):
        try:
            if self.client.ping():
                print("Successfully connected to Redis")
        except redis.ConnectionError as e:
            raise Exception(f"Redis connection failed: {str(e)}")

    def store_data(self, key, value):
        try:
            serialized = json.dumps(value)
            return self.client.set(key, serialized)
        except (TypeError, redis.RedisError) as e:
            print(f"Data storage error: {e}")
            return False

    def retrieve_data(self, key):
        try:
            data = self.client.get(key)
            return json.loads(data) if data else None
        except (json.JSONDecodeError, redis.RedisError) as e:
            print(f"Data retrieval error: {e}")
            return None

    def process_request(self, input_data):
        from langchain.chains import LLMChain
        from langchain.prompts import PromptTemplate
        import os
        
        prompt = PromptTemplate.from_template(
            """基于以下用户输入生成响应：
            {query}
            """
        )
        
        llm = OpenAI(
            temperature=0.7,
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            model_name=os.getenv('MODEL_NAME')
        )
        chain = LLMChain(llm=llm, prompt=prompt)
        return {
            "status": "processed",
            "input": input_data,
            "result": chain.run(input_data['query'])
        }