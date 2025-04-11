from groq import Groq
from dotenv import load_dotenv
import os
import groq
from telegram.ext import ContextTypes

load_dotenv()

# Create a ChatBot
chatbot = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)
SYSTEM_PROMPT = {
    "role": "system",
    "content": "你是一位專業且親切的 AI 助理，請用繁體中文回覆，並使用 Markdown 格式。"
}


def generate_response(message: str, context: ContextTypes.DEFAULT_TYPE):
    """產生 AI 回應"""

    messages = context.user_data.get("messages", [])

    # 如果對話歷史中還沒有 system prompt，就先加入
    if not messages or messages[0].get("role") != "system":
        messages.insert(0, SYSTEM_PROMPT)

    # 加入使用者訊息
    messages.append({
        "role": "user",
        "content": message,
    })

    # 更新 context 中的 messages
    context.user_data["messages"] = messages

    response_queue = ""
    try:
        for resp in chatbot.chat.completions.create(
            messages=context.user_data.get("messages"),
            model=context.user_data.get("model", "llama3-8b-8192"),
            stream=True,
        ):
            if resp.choices[0].delta.content:
                response_queue += resp.choices[0].delta.content
            if len(response_queue) > 100:
                yield response_queue
                response_queue = ""
    except groq.GroqError as e:
        yield f"Error: {e}\nStart a new conversation, click /new"
    yield response_queue
