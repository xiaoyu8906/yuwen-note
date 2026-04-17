import os
import sys
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

# 获取参数
lesson_name = sys.argv[1]
lesson_url = sys.argv[2] if len(sys.argv) > 2 else None

# 爬取课文内容
if lesson_url:
    # 手动输入的链接
    url = lesson_url
else:
    # 自动搜索
    search_url = f"https://hanchacha.com/search?q={lesson_name}"
    search_response = requests.get(search_url)
    soup = BeautifulSoup(search_response.text, 'html.parser')
    # 找到第一个搜索结果
    first_result = soup.find('a', href=True)
    if not first_result:
        raise Exception("没找到对应的课文")
    url = "https://hanchacha.com" + first_result['href']

# 爬取课文内容
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
content = soup.find('div', class_='content')
if not content:
    raise Exception("没找到课文内容")
text = content.get_text(strip=True, separator='\n')

# AI生成笔记
api_key = os.environ.get("OPENAI_API_KEY")
# 这里改成你自己的base_url，比如OpenRouter的话是https://openrouter.ai/api/v1
base_url = "https://api.openai.com/v1"

client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

prompt = f"""
你是一个小学语文老师，根据下面的课文内容，生成一份完整的小学语文笔记，包含：
1. 课文解析
2. 生字词（拼音、组词）
3. 重点句子解析
4. 中心思想
5. 课后练习

课文内容：
{text}

请用markdown格式输出，不要有多余的内容。
"""

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": prompt}
    ]
)

note = response.choices[0].message.content

# 保存笔记
os.makedirs('data', exist_ok=True)
with open(f'data/{lesson_name}.md', 'w', encoding='utf-8') as f:
    f.write(note)

print(f"笔记生成成功：data/{lesson_name}.md")
