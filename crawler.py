# -*- coding: utf-8 -*-
import requests
import sys
import os
import time
import json
from bs4 import BeautifulSoup

# ============================================
# 使用 DeepSeek 免费 API 生成结构化笔记
# DeepSeek 官网：https://platform.deepseek.com/
# 注册后可获得免费 API Key
# ============================================

# 从 GitHub Secrets 读取 API Key
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
USE_AI = True

# 如果环境变量没有，可以直接设置（测试用，正式用上面那种）
if not DEEPSEEK_API_KEY:
    DEEPSEEK_API_KEY = "sk-6ee38e7687bb4d899abf7874409b863a"

def crawl_hanchacha(lesson_name):
    """从 hanchacha.com 爬取所有相关资料"""
    print(f"  🔍 正在从 hanchacha.com 搜索《{lesson_name}》...")
    
    all_text = ""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        # 搜索
        search_url = f"https://hanchacha.com/?s={lesson_name}"
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找相关链接
        links = soup.find_all('a', href=True)
        found_urls = []
        
        for link in links:
            href = link.get('href', '')
            text = link.get_text().lower()
            if lesson_name.lower() in text and 'hanchacha.com' in href:
                if href not in found_urls:
                    found_urls.append(href)
        
        print(f"    找到 {len(found_urls)} 个相关页面")
        
        # 提取所有页面内容
        for url in found_urls[:3]:
            try:
                page_resp = requests.get(url, headers=headers, timeout=10)
                page_soup = BeautifulSoup(page_resp.text, 'html.parser')
                content_div = page_soup.find('article') or page_soup.find('div', class_='entry-content')
                
                if content_div:
                    text = content_div.get_text(strip=True)
                    all_text += f"\n\n---\n{text[:1500]}"
            except:
                continue
                
    except Exception as e:
        print(f"  hanchacha 爬取失败: {e}")
    
    return all_text[:4000]  # 限制长度

def crawl_other_sites(lesson_name):
    """爬取其他网站作为补充"""
    other_text = ""
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # 百度搜索
    try:
        url = f"https://www.baidu.com/s?wd={lesson_name} 课文讲解"
        response = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = soup.find_all('div', class_='result')
        for result in results[:2]:
            text = result.get_text(strip=True)
            if len(text) > 100:
                other_text += f"\n\n{text[:800]}"
    except:
        pass
    
    return other_text[:2000]

def generate_with_ai(lesson_name, raw_materials):
    """使用 AI 生成完整的学霸笔记"""
    
    # 你的完整模板
    template = f"""请根据以下关于《{lesson_name}》的教学资料，生成一份完整的学霸笔记。

必须严格按照以下模板格式，每个板块都要写满，不能留空：

# 🌊 探秘{lesson_name} · 学霸综合笔记 🐠

> 一份集**知识点、课堂笔记、教学思路**于一体的超实用手册，专治"阅读没方法，写作干巴巴"！

---

## 📚 一、课文一瞥：它讲了什么？

（写课文简介、核心问题、主要内容、中心句）

---

## 🧱 二、文章结构：总分总，超清晰！

（用表格形式写出文章的结构，包括部分、自然段、内容、作用）

> 💡 **写作要点：** （总结结构特点）

---

## ✨ 三、阅读与写作：深挖课文"宝藏"

### 1. （某方面的写作特点）—— 具体手法

| 阅读要点 | 写法分析 | 写作小技巧 |
|----------|----------|------------|
| ... | ... | ... |

> 💡 **写作要点：** （总结写作方法）

---

## 📝 四、语言积累：词语库+句式库

### 1. 重点词语

| 类别 | 词语 |
|------|------|
| 必会字词 | ... |
| 近义词 | ... |
| 反义词 | ... |
| AABC式 | ... |

### 2. 仿写句式

> **“句式名称”**
>
> *   **课文原句**：...
> *   **仿写示例**：...

---

## 🎯 五、课后挑战：小试牛刀

1.  **朗读小能手**：...
2.  **小小解说员**：...
3.  **妙笔生花**：...

---

以下是爬取到的资料，请基于这些内容生成笔记（如果资料不足，可以结合你的知识补充）：

{raw_materials}

请直接输出笔记内容，不要输出其他解释。"""

    if USE_AI and DEEPSEEK_API_KEY:
        try:
            print("  🤖 正在调用 AI 生成笔记...")
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "你是小学语文教学专家，擅长生成高质量的课文笔记。"},
                        {"role": "user", "content": template}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 4000
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                note = result["choices"][0]["message"]["content"]
                print("  ✅ AI 生成成功")
                return note
            else:
                print(f"  ⚠️ AI 调用失败: {response.status_code}")
                return generate_template_note(lesson_name, raw_materials)
                
        except Exception as e:
            print(f"  ⚠️ AI 生成失败: {e}")
            return generate_template_note(lesson_name, raw_materials)
    else:
        print("  📝 使用模板生成（未配置 AI）")
        return generate_template_note(lesson_name, raw_materials)

def generate_template_note(lesson_name, raw_materials):
    """备用：基于模板生成（不用 AI）"""
    
    # 从爬取材料中提取一段作为内容
    content_preview = raw_materials[:500] if raw_materials else f"《{lesson_name}》是一篇优美的课文。"
    
    return f"""# 🌊 探秘{lesson_name} · 学霸综合笔记 🐠

> 一份集**知识点、课堂笔记、教学思路**于一体的超实用手册！

---

## 📚 一、课文一瞥：它讲了什么？

{content_preview}

*   **核心问题**：本文的核心思想是什么？
*   **主要内容**：课文从多个角度展开描写。
*   **中心句**：文中的点睛之笔值得品味。

---

## 🧱 二、文章结构：总分总，超清晰！

| 部分 | 自然段 | 内容 | 作用 |
|------|--------|------|------|
| **第一部分** | 1 | 引入主题 | 吸引读者 |
| **第二部分** | 2-5 | 具体描写 | 展开叙述 |
| **第三部分** | 6 | 总结升华 | 点明主旨 |

> 💡 **写作要点：** 文章采用清晰的结构，层次分明。

---

## ✨ 三、阅读与写作：深挖课文"宝藏"

### 1. 写作特色分析

| 阅读要点 | 写法分析 | 写作小技巧 |
|----------|----------|------------|
| 生动描写 | 运用比喻、拟人等修辞 | 让文章更生动 |
| 结构清晰 | 总分总结构 | 让读者一目了然 |

> 💡 **写作要点：** 学会运用多种修辞手法。

---

## 📝 四、语言积累：词语库+句式库

### 1. 重点词语

| 类别 | 词语 |
|------|------|
| 必会字词 | 请根据课文填写 |
| 近义词 | 请根据课文填写 |
| 反义词 | 请根据课文填写 |

### 2. 仿写句式

> **句式示例**
>
> *   **课文原句**：请从课文中找出精彩句子
> *   **仿写示例**：请尝试仿写

---

## 🎯 五、课后挑战：小试牛刀

1.  **朗读小能手**：有感情地朗读课文
2.  **小小解说员**：向家人介绍课文内容
3.  **妙笔生花**：运用学到的写法写一段话

---

*✨ 数据来源：hanchacha.com 及网络爬虫*
*📅 生成时间：{time.strftime('%Y-%m-%d %H:%M:%S')}*
"""

def main():
    if len(sys.argv) < 2:
        print("请提供课文名称")
        sys.exit(1)
    
    lesson_name = sys.argv[1]
    print("=" * 55)
    print(f"🕷️ 正在为《{lesson_name}》生成学霸笔记...")
    print("=" * 55)
    
    # 1. 爬取 hanchacha
    print("\n⭐ [1/2] 爬取 hanchacha.com...")
    hanchacha_text = crawl_hanchacha(lesson_name)
    
    # 2. 爬取其他网站补充
    print("\n📡 [2/2] 补充其他网站...")
    other_text = crawl_other_sites(lesson_name)
    
    # 合并所有资料
    all_materials = f"""
【来自 hanchacha.com 的资料】
{hanchacha_text}

【来自其他网站的资料】
{other_text}
"""
    
    # 3. 使用 AI 生成笔记
    print("\n🤖 正在生成学霸笔记...")
    note = generate_with_ai(lesson_name, all_materials)
    
    # 4. 保存
    os.makedirs('data', exist_ok=True)
    output_file = f"data/{lesson_name}.md"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(note)
    
    print(f"\n✅ 笔记已保存: {output_file}")
    print("=" * 55)

if __name__ == "__main__":
    main()
