# -*- coding: utf-8 -*-
import requests
import sys
import os
import time
import re
from bs4 import BeautifulSoup

# ============================================
# 优先爬取 hanchacha.com 的课文资料
# 智能填充模板的所有板块
# ============================================

def crawl_hanchacha(lesson_name):
    """从 hanchacha.com 爬取所有相关资料"""
    print(f"  🔍 正在从 hanchacha.com 搜索《{lesson_name}》...")
    
    result = {
        "content": "",       # 课文内容
        "knowledge": "",     # 知识点
        "notes": "",         # 课堂笔记
        "structure": "",     # 文章结构
        "writing": "",       # 写作手法
        "words": "",         # 词语积累
        "sentences": "",     # 重点句子
        "exercises": "",     # 课后练习
        "summary": ""        # 中心思想
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        # 方法1：直接搜索
        search_url = f"https://hanchacha.com/?s={lesson_name}"
        print(f"    搜索: {search_url}")
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找所有相关链接
        links = soup.find_all('a', href=True)
        found_urls = []
        
        for link in links:
            href = link.get('href', '')
            text = link.get_text().lower()
            if lesson_name.lower() in text and 'hanchacha.com' in href:
                if href not in found_urls:
                    found_urls.append(href)
        
        print(f"    找到 {len(found_urls)} 个相关页面")
        
        # 访问每个页面提取内容
        for url in found_urls[:5]:
            try:
                print(f"    正在提取: {url}")
                page_resp = requests.get(url, headers=headers, timeout=10)
                page_soup = BeautifulSoup(page_resp.text, 'html.parser')
                
                # 提取主要内容
                content_div = page_soup.find('article') or page_soup.find('div', class_='entry-content') or page_soup.find('div', class_='post-content')
                
                if content_div:
                    full_text = content_div.get_text(strip=True)
                    title = page_soup.find('title')
                    title_text = title.get_text() if title else ""
                    
                    # 根据页面标题分类存储
                    if '知识点' in title_text or '知识梳理' in title_text:
                        result["knowledge"] = extract_smart_content(full_text, 2000)
                    elif '课堂笔记' in title_text or '笔记' in title_text:
                        result["notes"] = extract_smart_content(full_text, 2000)
                    elif '结构' in title_text or '层次' in title_text:
                        result["structure"] = extract_smart_content(full_text, 1500)
                    elif '写作' in title_text or '手法' in title_text:
                        result["writing"] = extract_smart_content(full_text, 1500)
                    elif '词语' in title_text or '字词' in title_text:
                        result["words"] = extract_smart_content(full_text, 1500)
                    elif '句子' in title_text or '赏析' in title_text:
                        result["sentences"] = extract_smart_content(full_text, 1500)
                    elif '练习' in title_text or '习题' in title_text:
                        result["exercises"] = extract_smart_content(full_text, 1500)
                    elif '中心' in title_text or '主旨' in title_text:
                        result["summary"] = extract_smart_content(full_text, 1000)
                    else:
                        # 默认存到内容区
                        if not result["content"]:
                            result["content"] = extract_smart_content(full_text, 2000)
                            
            except Exception as e:
                print(f"    提取失败: {e}")
                
    except Exception as e:
        print(f"  hanchacha 爬取失败: {e}")
    
    return result

def extract_smart_content(text, max_len):
    """智能提取内容，去除多余空白"""
    if not text:
        return ""
    # 清理文本
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    if len(text) > max_len:
        text = text[:max_len] + "..."
    return text

def generate_smart_note(lesson_name, data):
    """智能生成完整的笔记，填充所有板块"""
    
    # 如果某个板块为空，根据已有内容智能生成
    if not data["knowledge"] and data["notes"]:
        data["knowledge"] = "本文是一篇优秀的课文，" + data["notes"][:200]
    
    if not data["structure"]:
        data["structure"] = """| 部分 | 自然段 | 主要内容 |
|------|--------|----------|
| 开头 | 第1段 | 引出主题 |
| 中间 | 第2-5段 | 具体描写 |
| 结尾 | 最后一段 | 总结升华 |"""
    
    if not data["writing"]:
        data["writing"] = """本文运用了以下写作手法：
1. **比喻**：生动形象地描写事物
2. **拟人**：赋予事物人的情感
3. **排比**：增强语势，突出情感
4. **对比**：突出事物特点"""
    
    if not data["words"]:
        data["words"] = """| 类别 | 词语 |
|------|------|
| 重点词语 | 请根据课文填写 |
| 近义词 | 请根据课文填写 |
| 反义词 | 请根据课文填写 |
| 四字词语 | 请根据课文填写 |"""
    
    if not data["sentences"]:
        data["sentences"] = """> 请从课文中找出最精彩的句子抄写下来：
> ________________________________
> 
> **我的赏析**：这句话运用了____的修辞手法，生动地写出了____。"""
    
    if not data["exercises"]:
        data["exercises"] = """1. **朗读**：有感情地朗读课文3遍
2. **背诵**：背诵你最喜欢的段落
3. **仿写**：模仿课文写法，写一段话
4. **思考**：读完课文，你有什么感受？"""
    
    if not data["summary"]:
        data["summary"] = f"《{lesson_name}》通过生动的描写，表达了作者的思想感情。"
    
    # 生成完整笔记
    note = f"""# 📖 {lesson_name} · 学霸综合笔记

> 一份集**知识点、课堂笔记、教学思路**于一体的超实用手册
> **数据来源**：hanchacha.com 语文同步
> **生成时间**：{time.strftime('%Y-%m-%d %H:%M:%S')}

---

## 📚 一、课文一瞥：它讲了什么？

{data["content"] if data["content"] else f'《{lesson_name}》是一篇优美的课文，通过生动的描写展现了丰富的内涵。建议查阅教材原文仔细阅读。'}

*   **主要内容**：{data["knowledge"][:100] if data["knowledge"] else '课文从多个角度展开描写。'}
*   **中心思想**：{data["summary"][:100]}

---

## 🧱 二、文章结构：总分总，超清晰！

{data["structure"]}

> 💡 **写作要点：** 文章采用清晰的结构，条理分明，层次清楚。

---

## ✨ 三、阅读与写作：深挖课文"宝藏"

### 📖 知识点梳理
{data["knowledge"] if data["knowledge"] else '请参考课堂笔记和教材。'}

### ✍️ 写作手法分析
{data["writing"]}

---

## 📝 四、语言积累：词语库+句式库

### 重点词语

{data["words"]}

### 重点句子赏析

{data["sentences"]}

---

## 🎯 五、课后挑战：小试牛刀

{data["exercises"]}

---

## 📒 六、课堂笔记

{data["notes"] if data["notes"] else '请记录课堂上的重点内容：\n\n1. \n2. \n3. '}

---

## 💡 七、我的思考

通过学习这篇课文，我学到了：________________________________

我还想了解：________________________________

---

*✨ 每天进步一点点！继续加油！* 
*🔍 数据来源：hanchacha.com 语文同步资源*
"""
    return note

def main():
    if len(sys.argv) < 2:
        print("请提供课文名称")
        sys.exit(1)
    
    lesson_name = sys.argv[1]
    print("=" * 55)
    print(f"🕷️ 正在从 hanchacha.com 爬取《{lesson_name}》完整资料...")
    print("=" * 55)
    
    # 爬取 hanchacha
    print("\n⭐ [主要来源] hanchacha.com")
    data = crawl_hanchacha(lesson_name)
    
    # 统计结果
    filled = sum(1 for v in data.values() if v)
    print(f"\n📊 爬取统计：共 {filled}/7 个板块有内容")
    
    # 生成完整笔记
    print("\n📝 正在生成完整笔记...")
    note = generate_smart_note(lesson_name, data)
    
    # 保存
    os.makedirs('data', exist_ok=True)
    output_file = f"data/{lesson_name}.md"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(note)
    
    print(f"\n✅ 笔记已保存: {output_file}")
    print("=" * 55)

if __name__ == "__main__":
    main()
