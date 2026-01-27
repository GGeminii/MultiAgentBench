import os

from exceptiongroup import catch
from litellm import completion
from litellm.types.utils import Message

XIAOMI_MODEL = "openrouter/xiaomi/mimo-v2-flash:free"  # 自定义模型标识
OLLAMA_MODE = "openrouter/qwen/qwen3-next-80b-a3b-instruct:free"
if __name__ == "__main__":
    try:
        os.environ["OPENROUTER_API_KEY"] = ""
        # 核心调用：通过litellm的completion函数，传入自定义base_url和api_key
        # 1. 定义工具（以天气查询为例）
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "根据城市名称查询当前天气情况",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "城市名称，例如：北京、上海"
                            }
                        },
                        "required": ["city"]
                    }
                }
            }
        ]
        response = completion(
            stream=False,
            tools=tools,
            tool_choice="auto",
            model=OLLAMA_MODE,  # 自定义模型名
            messages=[
                {"role": "user", "content": "你好，今天北京天气如何"}  # 对话消息
            ]
        )

        # 提取并打印回复内容
        print("自定义API回复：")
        print( response)
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"【错误】请求大模型 - {str(e)}")
        raise e