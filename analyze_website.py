#!/usr/bin/env python3
"""分析中考网站点结构"""

import requests
from bs4 import BeautifulSoup

def analyze_zhongkao_structure():
    # 检查中考网主站的实际结构
    url = 'https://www.zhongkao.com'
    print(f'分析中考网主站结构: {url}')

    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            title = soup.title.text if soup.title else '无标题'
            print(f'页面标题: {title}')

            # 查找导航菜单或学科分类
            nav_elements = soup.find_all(['nav', 'menu', 'ul'])
            print(f'发现 {len(nav_elements)} 个导航元素')

            # 查找学科相关的链接
            subject_links = []
            all_links = soup.find_all('a', href=True)

            subject_keywords = ['数学', '语文', '英语', '物理', '化学', 'math', 'chinese', 'english']

            for link in all_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)

                if any(keyword in text for keyword in subject_keywords):
                    full_url = href if href.startswith('http') else f'{url.rstrip("/")}{href}'
                    subject_links.append((text, full_url))

            print(f'发现 {len(subject_links)} 个学科相关链接:')
            for text, link_url in subject_links[:10]:
                print(f'  {text} -> {link_url}')

            # 检查页面中是否有学科栏目
            content_divs = soup.find_all('div', class_=True)
            print(f'页面中有 {len(content_divs)} 个带class的div')

            # 显示一些可能的栏目容器
            for div in content_divs[:5]:
                class_name = div.get('class', ['unknown'])
                text = div.get_text(strip=True)[:100]
                print(f'  类名: {class_name}, 内容: {text}...')

        else:
            print(f'请求失败: {response.status_code}')

    except Exception as e:
        print(f'分析失败: {e}')

if __name__ == "__main__":
    analyze_zhongkao_structure()

