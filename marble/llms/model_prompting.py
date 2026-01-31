import litellm
from beartype import beartype
from beartype.typing import Any, Dict, List, Optional
from litellm.types.utils import Message

from marble.llms.error_handler import api_calling_error_exponential_backoff
from marble.utils import get_logger

logger = get_logger("LLM_CALL")

@beartype
@api_calling_error_exponential_backoff(retries=5, base_wait_time=1)
def model_prompting(
    llm_model: str,
    messages: List[Dict[str, str]],
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
    mode: Optional[str] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
    tool_choice: Optional[str] = None,
) -> List[Message]:
    """
    Select model via router in LiteLLM with support for function calling.
    """
    # litellm.set_verbose=True
    api_key = None
    if "together_ai/TA" in llm_model:
        base_url = "https://api.ohmygpt.com/v1"
    elif "deepseek" in llm_model:
        base_url = "https://api.deepseek.com/v1"
    elif "gpt" in llm_model:
        base_url = "https://api.deerapi.com/v1"
        # TODO 配置第三方APIKEY
        api_key = ""
    else:
        base_url = None
    try:
        max_length = 350000
        max_token_num = 4096
        # logger.info(f"大模型输入: {messages}")
        for msg in messages:
            if len(msg["content"]) > max_length:
                logger.info(f"The input of the large model is too large and is being compressed: {msg['content']}")
                msg["content"] = msg["content"][:max_length] + '...'
        completion = litellm.completion(
            model=llm_model,
            messages=messages,
            max_tokens=max_token_num,
            n=return_num,
            top_p=top_p,
            temperature=temperature,
            stream=stream,
            tools=tools,
            tool_choice=tool_choice,
            base_url=base_url,
            api_key=api_key,
        )
        # logger.info(f"大模型输出: {completion}")
        message_0: Message = completion.choices[0].message
        assert message_0 is not None
        assert isinstance(message_0, Message)
        return [message_0]
    except Exception as e:
        logger.info(f"Error: Request a large model - {str(e)}")
        raise e
