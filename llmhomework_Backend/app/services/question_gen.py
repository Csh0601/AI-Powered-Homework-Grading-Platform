import random
import openai

PROMPT_TEMPLATES = [
    "请写出关于{knowledge}的选择题：\nA. 选项1\nB. 选项2\nC. 选项3\nD. 选项4\n答案: A",
    "请简述{knowledge}的定义。",
    "{knowledge}的常见考点有哪些？"
]

# 需在环境变量或openai.api_key中配置API Key
openai.api_key = 'YOUR_OPENAI_API_KEY'

def call_gpt_api(knowledge):
    prompt = f"请根据以下知识点生成一道相关的选择题：{knowledge}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']

def generate_question(knowledge, use_gpt=False):
    if use_gpt:
        return call_gpt_api(knowledge)
    else:
        return random.choice(PROMPT_TEMPLATES).format(knowledge=knowledge)
