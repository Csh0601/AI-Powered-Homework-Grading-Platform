#!/usr/bin/env python3
"""分析中考网语文页面结构"""

import requests
from bs4 import BeautifulSoup

def analyze_chinese_page():
    url = 'https://www.zhongkao.com/czyw/'
    print(f'分析中考网语文页面: {url}')

    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            title = soup.title.text if soup.title else '无标题'
            print(f'页面标题: {title}')

            # 分析页面结构
            print(f'页面主要元素:')

            # 查找所有div
            divs = soup.find_all('div')
            print(f'  div元素数量: {len(divs)}')

            # 查找有class的div
            class_divs = soup.find_all('div', class_=True)
            print(f'  有class的div: {len(class_divs)}')

            # 显示前几个class名称
            if class_divs:
                print('  常见class名称:')
                classes = set()
                for div in class_divs[:20]:
                    if div.get('class'):
                        classes.update(div.get('class'))
                for cls in list(classes)[:10]:
                    print(f'    - {cls}')

            # 查找链接
            links = soup.find_all('a', href=True)
            print(f'链接数量: {len(links)}')

            # 查找教育相关链接
            edu_links = []
            for link in links[:30]:
                text = link.get_text(strip=True)
                href = link.get('href', '')

                # 查找教育相关内容
                if any(keyword in text for keyword in ['语文', '阅读', '作文', '古诗', '文言文', '试题', '练习']):
                    full_url = href if href.startswith('http') else f'https://www.zhongkao.com{href}'
                    edu_links.append((text, full_url))

            print(f'教育相关链接 ({len(edu_links)} 个):')
            for text, link_url in edu_links[:10]:
                print(f'  {text} -> {link_url}')

            # 查找可能的内容容器
            content_containers = soup.find_all(['div', 'section', 'article', 'main'])
            print(f'内容容器数量: {len(content_containers)}')

            if content_containers:
                # 查找第一个大的内容容器
                for container in content_containers:
                    if len(container.get_text(strip=True)) > 100:  # 内容较多的容器
                        content = container.get_text(strip=True)[:200]
                        print(f'主要内容预览: {content}...')
                        break

        else:
            print(f'请求失败: {response.status_code}')

    except Exception as e:
        print(f'分析失败: {e}')

if __name__ == "__main__":
    analyze_chinese_page()

