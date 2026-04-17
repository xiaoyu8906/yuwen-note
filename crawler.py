import os
import sys
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

# 适配OpenRouter的配置
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url="https://openrouter.ai/api/v1",  # OpenRouter的接口
)

def search_lesson_url(lesson_name):
    # 搜索hanchacha的课文
    search_url = f"https://hanchacha.com/search?keyword={lesson_name}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    # 找到第一个课文链接
    link = soup.find("a", href=True)
    if link:
        return "https://hanchacha.com" + link['href']
    return None

def get_lesson_content(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    # 提取课文内容
    content = soup.find("div", class_="content")
    if content:
        return content.get_text(strip=True)
    return None

def generate_note(lesson_name, content):
    prompt = f"""
你是一个小学语文老师，请根据下面的课文《{lesson_name}》，生成一份完整的小学语文笔记，包含以下部分：
1. 生字组词：列出课文里的生字，每个生字组3-5个词语
2. 重点词语：列出课文里的重点词语，解释意思
3. 课文解析：分析课文的主要内容、中心思想
4. 句子赏析：找出课文里的重点句子，进行赏析
5. 课后练习：出3-5道课后练习题

课文内容：
{content}

请按照这个格式生成，用markdown格式，清晰明了，适合小学生使用。
"""
    response = client.chat.completions.create(
        model="deepseek-chat",  # OpenRouter的模型
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def save_note(lesson_name, note):
    # 保存笔记到data目录
    if not os.path.exists("data"):
        os.makedirs("data")
    with open(f"data/{lesson_name}.md", "w", encoding="utf-8") as f:
        f.write(note)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python crawler.py <lesson_name> [lesson_url]")
        sys.exit(1)
    
    lesson_name = sys.argv[1]
    lesson_url = sys.argv[2] if len(sys.argv) > 2 else None
    
    print("开始爬取课文...")
    if not lesson_url:
        lesson_url = search_lesson_url(lesson_name)
        if not lesson_url:
            print("搜索失败，请手动输入课文链接")
            sys.exit(1)
    
    content = get_lesson_content(lesson_url)
    if not content:
        print("获取课文内容失败")
        sys.exit(1)
    
    print("开始AI生成笔记...")
    note = generate_note(lesson_name, content)
    
    print("保存笔记...")
    save_note(lesson_name, note)
    
    print("生成完成！")
