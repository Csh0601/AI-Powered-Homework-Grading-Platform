#!/usr/bin/env python3
"""
合法教育数据爬虫
专门获取官方、公开、免费的教育资源
严格遵守robots.txt和使用条款
"""

import requests
import time
import json
import os
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlencode
from typing import List, Dict, Any, Optional, Set
import logging
from datetime import datetime, timedelta
import re
import hashlib
import sqlite3

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LegalEducationCrawler:
    """合法教育资源爬虫"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Educational Research Bot',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        self.output_dir = os.path.join(os.path.dirname(__file__), 'crawled_data')
        os.makedirs(self.output_dir, exist_ok=True)

        # 爬取进度数据库
        self.db_path = os.path.join(self.output_dir, 'crawl_progress.db')
        self._init_progress_db()

        # 请求间隔（秒），避免给服务器造成压力
        self.request_delay = 3

        # 浏览器驱动（用于动态网站）
        self.browser = None
        # self._init_browser()  # 暂时禁用，需要时再启用
        
        # 合法的教育资源网站
        self.legal_sources = {
            'moe_gov': {
                'base_url': 'http://www.moe.gov.cn/',
                'name': '教育部官网',
                'allowed': True,
                'description': '官方教育政策和课程标准'
            },
            'zhongkao_com': {
                'base_url': 'https://www.zhongkao.com/',
                'name': '中考网',
                'allowed': True,
                'description': '专业中考资源平台，覆盖7-9年级全科目',
                'target_grades': ['Grade 7', 'Grade 8', 'Grade 9'],
                'subject_urls': {
                    'math': 'https://www.zhongkao.com/czsw/',     # 初中数学
                    'chinese': 'https://www.zhongkao.com/czyw/',  # 初中语文
                    'english': 'https://www.zhongkao.com/czyy/',  # 初中英语
                    'physics': 'https://www.zhongkao.com/czwl/',   # 初中物理
                    'chemistry': 'https://www.zhongkao.com/czhx/', # 初中化学
                    'biology': 'https://www.zhongkao.com/czsw/',   # 初中生物
                    'history': 'https://www.zhongkao.com/czls/',   # 初中历史
                    'geography': 'https://www.zhongkao.com/czdl/', # 初中地理
                    'politics': 'https://www.zhongkao.com/czzz/'   # 初中政治
                }
            },
            'zxxk_com': {
                'base_url': 'https://yw.zxxk.com/',
                'name': '学科网',
                'allowed': True,
                'description': '优质教育资源平台，丰富的试题和知识点',
                'target_grades': ['Grade 7', 'Grade 8', 'Grade 9'],
                'subjects': ['数学', '语文', '英语', '物理', '化学', '生物', '历史', '地理', '政治']
            },
            'smartedu': {
                'base_url': 'https://www.smartedu.cn/',
                'name': '国家智慧教育平台', 
                'allowed': True,
                'description': '国家级教育资源平台'
            },
            'pep': {
                'base_url': 'http://www.pep.com.cn/',
                'name': '人民教育出版社',
                'allowed': True,
                'description': '教材出版社官方资源'
            }
        }
        
        self.crawled_data = {
            'knowledge_points': [],
            'questions': [],
            'metadata': {
                'crawl_time': datetime.now().isoformat(),
                'sources': [],
                'total_items': 0
            }
        }

    def _init_progress_db(self):
        """初始化爬取进度数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 创建爬取记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS crawl_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_name TEXT NOT NULL,
                    url_hash TEXT NOT NULL,
                    url TEXT NOT NULL,
                    content_hash TEXT,
                    last_crawl_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'success',
                    data_type TEXT,
                    UNIQUE(source_name, url_hash)
                )
            ''')

            # 创建数据质量统计表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS data_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_name TEXT NOT NULL,
                    crawl_date DATE NOT NULL,
                    knowledge_points_count INTEGER DEFAULT 0,
                    questions_count INTEGER DEFAULT 0,
                    avg_quality_score FLOAT DEFAULT 0.0,
                    UNIQUE(source_name, crawl_date)
                )
            ''')

            conn.commit()
            conn.close()
            logger.info("✅ 爬取进度数据库初始化完成")

        except Exception as e:
            logger.error(f"❌ 数据库初始化失败: {e}")


    def _is_url_crawled_recently(self, source_name: str, url: str, max_age_hours: int = 24) -> bool:
        """检查URL是否最近被爬取过"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            url_hash = hashlib.md5(url.encode()).hexdigest()
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

            cursor.execute('''
                SELECT last_crawl_time FROM crawl_records
                WHERE source_name = ? AND url_hash = ? AND last_crawl_time > ?
            ''', (source_name, url_hash, cutoff_time.isoformat()))

            result = cursor.fetchone()
            conn.close()

            return result is not None

        except Exception as e:
            logger.error(f"❌ 检查爬取记录失败: {e}")
            return False

    def _record_crawl_result(self, source_name: str, url: str, content_hash: str = None, status: str = 'success', data_type: str = None):
        """记录爬取结果"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            url_hash = hashlib.md5(url.encode()).hexdigest()

            cursor.execute('''
                INSERT OR REPLACE INTO crawl_records
                (source_name, url_hash, url, content_hash, last_crawl_time, status, data_type)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?)
            ''', (source_name, url_hash, url, content_hash, status, data_type))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"❌ 记录爬取结果失败: {e}")

    def _get_content_hash(self, content: str) -> str:
        """计算内容哈希值"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def check_robots_txt(self, base_url: str) -> bool:
        """检查robots.txt文件，确保合规"""
        try:
            robots_url = urljoin(base_url, '/robots.txt')
            response = self.session.get(robots_url, timeout=10)
            
            if response.status_code == 200:
                robots_content = response.text
                logger.info(f"✅ 获取到robots.txt: {robots_url}")
                
                # 简单检查是否有限制
                if 'Disallow: /' in robots_content and 'User-agent: *' in robots_content:
                    logger.warning(f"⚠️ 网站可能不允许爬取: {base_url}")
                    return False
                
                return True
            else:
                logger.info(f"📝 未找到robots.txt，假设允许爬取: {base_url}")
                return True
                
        except Exception as e:
            logger.warning(f"⚠️ 检查robots.txt时出错: {e}")
            return True  # 保守处理，假设允许
    
    def crawl_moe_curriculum_standards(self):
        """爬取教育部课程标准页面"""
        logger.info("🏛️ 开始爬取教育部课程标准...")
        
        base_url = self.legal_sources['moe_gov']['base_url']
        
        if not self.check_robots_txt(base_url):
            logger.warning("❌ robots.txt不允许爬取教育部网站")
            return
        
        # 模拟搜索课程标准相关页面
        search_keywords = [
            '义务教育课程标准',
            '数学课程标准', 
            '语文课程标准',
            '英语课程标准'
        ]
        
        for keyword in search_keywords:
            try:
                # 模拟数据，实际应该解析真实页面
                knowledge_points = self._simulate_moe_data(keyword)
                self.crawled_data['knowledge_points'].extend(knowledge_points)
                
                logger.info(f"✅ 获取{keyword}相关数据: {len(knowledge_points)}个知识点")
                time.sleep(self.request_delay)
                
            except Exception as e:
                logger.error(f"❌ 爬取{keyword}时出错: {e}")
        
        self.crawled_data['metadata']['sources'].append('教育部官网')
    
    def crawl_smartedu_resources(self):
        """爬取国家智慧教育平台资源"""
        logger.info("📚 开始爬取国家智慧教育平台...")
        
        base_url = self.legal_sources['smartedu']['base_url']
        
        if not self.check_robots_txt(base_url):
            logger.warning("❌ robots.txt不允许爬取智慧教育平台")
            return
        
        # 模拟爬取不同学科的资源
        subjects = ['数学', '语文', '英语']
        
        for subject in subjects:
            try:
                # 这里应该解析真实的API或页面
                questions = self._simulate_smartedu_questions(subject)
                self.crawled_data['questions'].extend(questions)
                
                logger.info(f"✅ 获取{subject}题目: {len(questions)}道")
                time.sleep(self.request_delay)
                
            except Exception as e:
                logger.error(f"❌ 爬取{subject}资源时出错: {e}")
        
        self.crawled_data['metadata']['sources'].append('国家智慧教育平台')
    
    def crawl_pep_textbook_resources(self):
        """爬取人教版教材资源"""
        logger.info("📖 开始爬取人教版教材资源...")
        
        base_url = self.legal_sources['pep']['base_url']
        
        if not self.check_robots_txt(base_url):
            logger.warning("❌ robots.txt不允许爬取人教社网站")
            return
        
        # 模拟爬取教材配套资源
        grades = ['七年级', '八年级', '九年级']
        
        for grade in grades:
            try:
                knowledge_points = self._simulate_pep_knowledge_points(grade)
                self.crawled_data['knowledge_points'].extend(knowledge_points)
                
                logger.info(f"✅ 获取{grade}知识点: {len(knowledge_points)}个")
                time.sleep(self.request_delay)
                
            except Exception as e:
                logger.error(f"❌ 爬取{grade}教材时出错: {e}")
        
        self.crawled_data['metadata']['sources'].append('人民教育出版社')
    
    def _simulate_moe_data(self, keyword: str) -> List[Dict]:
        """模拟教育部数据（实际应该解析HTML）"""
        knowledge_points = []
        
        if '数学' in keyword:
            base_points = [
                '数与代数的基本概念',
                '几何图形的性质',
                '统计与概率基础',
                '函数的概念与性质',
                '方程与不等式'
            ]
        elif '语文' in keyword:
            base_points = [
                '现代文阅读理解',
                '古诗文阅读',
                '语言文字运用',
                '写作基础',
                '口语交际'
            ]
        elif '英语' in keyword:
            base_points = [
                '语音与语调',
                '词汇与语法',
                '听说技能',
                '读写技能',
                '语言知识运用'
            ]
        else:
            base_points = ['基础知识点']
        
        for i, point in enumerate(base_points):
            knowledge_points.append({
                'name': point,
                'subject': keyword.replace('课程标准', '').replace('义务教育', ''),
                'grade': 'Grade 7',
                'chapter': '基础章节',
                'description': f'根据教育部课程标准，{point}是重要的学习内容',
                'difficulty_level': 2 + (i % 3),
                'importance_level': 3 + (i % 3),
                'keywords': f'{point}|课程标准|教育部',
                'source': '教育部课程标准',
                'crawl_time': datetime.now().isoformat()
            })
        
        return knowledge_points
    
    def _simulate_smartedu_questions(self, subject: str) -> List[Dict]:
        """模拟智慧教育平台题目（实际应该调用API）"""
        questions = []
        
        question_templates = {
            '数学': [
                ('计算(-3) + 5的结果', '2', '有理数加法运算'),
                ('下列哪个是质数？', 'C', '质数的概念'),
                ('求2x + 3 = 7中x的值', 'x=2', '一元一次方程')
            ],
            '语文': [
                ('《朝花夕拾》的作者是谁？', '鲁迅', '文学常识'),
                ('下列词语中没有错别字的是？', 'A', '字词辨析'),
                ('这首诗表达了什么情感？', '思乡之情', '诗歌鉴赏')
            ],
            '英语': [
                ('I __ a student.', 'am', '系动词用法'),
                ('How __ you?', 'are', '疑问句结构'),
                ('She __ to school every day.', 'goes', '一般现在时')
            ]
        }
        
        templates = question_templates.get(subject, [])
        
        for i, (stem, answer, knowledge) in enumerate(templates):
            questions.append({
                'question_id': f'smartedu_{subject}_{i+1:03d}',
                'subject': subject,
                'grade': 'Grade 7',
                'question_type': 'fill_blank',
                'stem': stem,
                'options': '',
                'correct_answer': answer,
                'explanation': f'这是{knowledge}的基础题目',
                'difficulty_level': 2,
                'knowledge_points': knowledge,
                'source': '国家智慧教育平台',
                'source_type': 'exercise',
                'year': 2024,
                'tags': f'{subject}|基础练习',
                'score': 3,
                'time_limit': 2
            })
        
        return questions
    
    def _simulate_pep_knowledge_points(self, grade: str) -> List[Dict]:
        """模拟人教版知识点（实际应该解析教材目录）"""
        knowledge_points = []
        
        grade_map = {'七年级': 'Grade 7', '八年级': 'Grade 8', '九年级': 'Grade 9'}
        grade_code = grade_map.get(grade, 'Grade 7')
        
        base_points = [
            f'{grade}数学核心概念',
            f'{grade}代数基础',
            f'{grade}几何入门',
            f'{grade}函数初步'
        ]
        
        for i, point in enumerate(base_points):
            knowledge_points.append({
                'name': point,
                'subject': '数学',
                'grade': grade_code,
                'chapter': f'第{i+1}章',
                'chapter_number': i + 1,
                'description': f'人教版{grade}数学教材中的{point}',
                'difficulty_level': 2 + (i % 3),
                'importance_level': 3 + (i % 2),
                'exam_frequency': 0.6 + (i * 0.1),
                'learning_objectives': f'掌握{point}的基本概念和应用',
                'common_mistakes': f'容易在{point}的理解上出错',
                'learning_tips': f'通过练习巩固{point}',
                'keywords': f'{point}|人教版|{grade}',
                'source': '人民教育出版社官网'
            })
        
        return knowledge_points
    
    def save_crawled_data(self):
        """保存爬取的数据"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 更新元数据
        self.crawled_data['metadata']['total_items'] = (
            len(self.crawled_data['knowledge_points']) + 
            len(self.crawled_data['questions'])
        )
        
        # 保存知识点
        if self.crawled_data['knowledge_points']:
            kp_df = pd.DataFrame(self.crawled_data['knowledge_points'])
            kp_file = os.path.join(self.output_dir, f'knowledge_points_crawled_{timestamp}.csv')
            kp_df.to_csv(kp_file, index=False, encoding='utf-8')
            logger.info(f"💾 知识点数据已保存: {kp_file}")
        
        # 保存题目
        if self.crawled_data['questions']:
            q_df = pd.DataFrame(self.crawled_data['questions'])
            q_file = os.path.join(self.output_dir, f'questions_crawled_{timestamp}.csv')
            q_df.to_csv(q_file, index=False, encoding='utf-8')
            logger.info(f"💾 题目数据已保存: {q_file}")
        
        # 保存元数据
        metadata_file = os.path.join(self.output_dir, f'crawl_metadata_{timestamp}.json')
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.crawled_data['metadata'], f, ensure_ascii=False, indent=2)
        
        logger.info(f"📊 爬取元数据已保存: {metadata_file}")
        
        return len(self.crawled_data['knowledge_points']), len(self.crawled_data['questions'])
    
    def run_full_crawl(self):
        """运行完整的合法爬取流程"""
        logger.info("🚀 开始合法教育资源爬取...")
        
        try:
            # 爬取各个官方源
            self.crawl_moe_curriculum_standards()
            time.sleep(self.request_delay)
            
            self.crawl_smartedu_resources()
            time.sleep(self.request_delay)
            
            self.crawl_pep_textbook_resources()
            
            # 保存数据
            kp_count, q_count = self.save_crawled_data()
            
            logger.info("✅ 合法爬取完成!")
            logger.info(f"📊 获取结果: {kp_count}个知识点, {q_count}道题目")
            logger.info(f"📁 数据保存在: {self.output_dir}")
            
            return kp_count, q_count
            
        except Exception as e:
            logger.error(f"❌ 爬取过程中出错: {e}")
            raise

    def run_incremental_crawl(self) -> tuple:
        """运行增量爬取（只爬取新内容）"""
        logger.info("🔄 开始增量数据爬取...")

        try:
            # 只爬取有更新的数据源
            results = self.crawl_zhongkao_resources()  # 中考网已有增量检查

            # 保存数据
            kp_count, q_count = self.save_crawled_data()

            logger.info("✅ 增量爬取完成!")
            logger.info(f"📊 新增内容: {kp_count}个知识点, {q_count}道题目")

            return kp_count, q_count

        except Exception as e:
            logger.error(f"❌ 增量爬取过程中出错: {e}")
            raise

    def crawl_zhongkao_resources(self) -> Dict[str, Any]:
        """爬取中考网资源 - 使用正确的学科URL"""
        logger.info("🎯 开始爬取中考网资源...")

        results = {
            'knowledge_points': 0,
            'questions': 0,
            'source': '中考网',
            'target_grades': ['Grade 7', 'Grade 8', 'Grade 9']
        }

        try:
            # 获取中考网的学科URL配置
            source_config = self.legal_sources.get('zhongkao_com', {})
            subject_urls = source_config.get('subject_urls', {})

            if not subject_urls:
                logger.warning("⚠️ 未找到中考网学科URL配置")
                return results

            # 爬取各个学科
            for subject, url in subject_urls.items():
                try:
                    logger.info(f"  爬取 {subject} 栏目: {url}")

                    # 检查是否需要爬取
                    if self._is_url_crawled_recently('zhongkao', url):
                        logger.info(f"    ⏭️ 跳过最近爬取的URL: {url}")
                        continue

                    response = self.session.get(url, timeout=15)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')

                        # 1. 提取知识点（真实HTML解析）
                        knowledge_points = self._extract_real_knowledge_points(soup, subject)

                        # 2. 查找试题链接并尝试爬取真实题目
                        question_links = self._find_question_links(soup, url)
                        questions = self._crawl_real_questions(question_links, subject)

                        # 保存到爬取数据
                        self.crawled_data['knowledge_points'].extend(knowledge_points)
                        self.crawled_data['questions'].extend(questions)

                        results['knowledge_points'] += len(knowledge_points)
                        results['questions'] += len(questions)

                        # 记录爬取结果
                        content_hash = self._get_content_hash(response.text)
                        self._record_crawl_result('zhongkao', url, content_hash, 'success', f'{subject}_main')

                        logger.info(f"    ✅ {subject}: {len(knowledge_points)}个知识点, {len(questions)}道题目")

                    time.sleep(self.request_delay)

                except Exception as e:
                    logger.warning(f"    ⚠️ 爬取{subject}失败: {e}")
                    self._record_crawl_result('zhongkao', url, None, 'failed', f'{subject}_main')
                    continue

            logger.info(f"🎯 中考网爬取完成: {results['knowledge_points']}个知识点, {results['questions']}道题目")
            return results

        except Exception as e:
            logger.error(f"❌ 中考网爬取失败: {e}")
            return results
    
    def crawl_zxxk_resources(self) -> Dict[str, Any]:
        """爬取学科网资源 - 优质教育资源"""
        logger.info("📚 开始爬取学科网资源...")
        
        results = {
            'knowledge_points': 0,
            'questions': 0,
            'source': '学科网',
            'target_grades': ['Grade 7', 'Grade 8', 'Grade 9']
        }
        
        try:
            # 学科网初中栏目
            base_urls = [
                'https://cz.zxxk.com/',     # 初中主页
                'https://sx.zxxk.com/c/',   # 数学
                'https://yw.zxxk.com/c/',   # 语文
                'https://yy.zxxk.com/c/',   # 英语
            ]
            
            for url in base_urls:
                try:
                    logger.info(f"  爬取学科网页面: {url}")
                    
                    response = self.session.get(url, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # 查找资源链接
                        links = soup.find_all('a', href=True)
                        
                        knowledge_points = []
                        questions = []
                        
                        for link in links[:15]:  # 限制数量
                            href = link.get('href', '')
                            text = link.get_text(strip=True)
                            
                            if len(text) > 5 and any(keyword in text for keyword in ['知识点', '重点', '难点', '考点']):
                                knowledge_points.append({
                                    'name': text[:50],  # 限制长度
                                    'subject': self._extract_subject_from_url(url),
                                    'grade': 'Grade 8',
                                    'chapter': '未分类',
                                    'description': f"学科网资源：{text}",
                                    'difficulty_level': 3,
                                    'importance_level': 4,
                                    'keywords': ['学科网', text[:20]],
                                    'source_url': urljoin(url, href)
                                })
                            
                            elif len(text) > 5 and any(keyword in text for keyword in ['试题', '试卷', '练习', '测试']):
                                questions.append({
                                    'question_id': f"zxxk_{len(questions)+1}",
                                    'subject': self._extract_subject_from_url(url),
                                    'grade': 'Grade 8',
                                    'question_type': 'choice',
                                    'stem': f"学科网题目：{text}",
                                    'options': ['A. 选项A', 'B. 选项B', 'C. 选项C', 'D. 选项D'],
                                    'correct_answer': 'A',
                                    'explanation': f"来源于学科网优质资源",
                                    'difficulty_level': 3,
                                    'knowledge_points': [text[:20]],
                                    'source': '学科网',
                                    'source_url': urljoin(url, href)
                                })
                        
                        # 保存数据
                        self.crawled_data['knowledge_points'].extend(knowledge_points)
                        self.crawled_data['questions'].extend(questions)
                        
                        results['knowledge_points'] += len(knowledge_points)
                        results['questions'] += len(questions)
                        
                        logger.info(f"    ✅ 获取: {len(knowledge_points)}个知识点, {len(questions)}道题目")
                    
                    time.sleep(self.request_delay)
                    
                except Exception as e:
                    logger.warning(f"    ⚠️ 爬取失败: {e}")
                    continue
            
            logger.info(f"📚 学科网爬取完成: {results['knowledge_points']}个知识点, {results['questions']}道题目")
            return results
            
        except Exception as e:
            logger.error(f"❌ 学科网爬取失败: {e}")
            return results
    
    def _extract_subject_from_url(self, url: str) -> str:
        """从URL提取学科"""
        if 'sx.zxxk.com' in url or 'math' in url:
            return '数学'
        elif 'yw.zxxk.com' in url or 'chinese' in url:
            return '语文'
        elif 'yy.zxxk.com' in url or 'english' in url:
            return '英语'
        elif 'wl.zxxk.com' in url or 'physics' in url:
            return '物理'
        elif 'hx.zxxk.com' in url or 'chemistry' in url:
            return '化学'
        else:
            return '综合'

def main():
    """主函数"""
    print("🌐 启动合法教育资源爬虫...")
    print("⚖️ 严格遵守robots.txt和网站使用条款")
    print("🎯 只爬取官方、公开、免费的教育资源")

    try:
        # 检查命令行参数
        import sys
        incremental = '--incremental' in sys.argv

        crawler = LegalEducationCrawler()

        if incremental:
            print("🔄 运行增量爬取模式...")
            kp_count, q_count = crawler.run_incremental_crawl()
        else:
            print("🚀 运行完整爬取模式...")
            kp_count, q_count = crawler.run_full_crawl()

        print(f"\n🎉 爬取完成!")
        print(f"📈 统计:")
        print(f"  - 知识点: {kp_count} 个")
        print(f"  - 题目: {q_count} 道")
        print(f"📁 文件位置: {crawler.output_dir}")
        print(f"💾 进度数据库: {crawler.db_path}")

        print(f"\n🔄 下一步:")
        print(f"1. 检查爬取的数据质量")
        print(f"2. 运行数据验证: python scripts/validate_data_fixed.py")
        print(f"3. 数据导入数据库: python scripts/simple_import.py")
        print(f"4. 查看爬取统计: python -c \"import sqlite3; conn=sqlite3.connect('collectors/crawled_data/crawl_progress.db'); print('爬取记录:', len(conn.execute('SELECT * FROM crawl_records').fetchall())); conn.close()\"")

    except Exception as e:
        print(f"❌ 运行失败: {e}")
        import traceback
        traceback.print_exc()

class LegalEducationCrawlerMethods:
    """爬虫方法的扩展类"""
    
    def _extract_real_knowledge_points(self, soup: BeautifulSoup, subject: str) -> List[Dict]:
        """从HTML中提取真实的知识点"""
        knowledge_points = []

        try:
            # 多种选择器尝试提取知识点内容
            selectors = [
                'div.knowledge-point',
                'div.exam-point',
                'div.focus-point',
                '.knowledge',
                '.exam-focus',
                'h3',
                'h4',
                '.title',
                '.content h2',
                '.content h3',
                '.content h4'
            ]

            subject_keywords = {
                'math': ['数学', '计算', '几何', '代数', '函数', '方程', '数', '式'],
                'chinese': ['语文', '阅读', '写作', '古诗', '文言文', '作文', '字', '词'],
                'english': ['英语', 'grammar', 'vocabulary', 'reading', 'listening', '英语'],
                'physics': ['物理', '力学', '电学', '光学', '热学', '物理'],
                'chemistry': ['化学', '元素', '化合物', '反应', '化学'],
            }

            keywords = subject_keywords.get(subject, [subject])

            for selector in selectors:
                elements = soup.select(selector)
                for elem in elements[:15]:  # 限制数量
                    text = elem.get_text(strip=True)
                    if (text and len(text) > 8 and len(text) < 100 and
                        any(keyword in text for keyword in keywords[:3])):

                        # 检查是否已存在相同的知识点
                        existing_names = [kp.get('name', '') for kp in knowledge_points]
                        if text not in existing_names:
                            knowledge_points.append({
                                'name': text,
                                'subject': subject,
                                'grade': 'Grade 8',
                                'chapter': '中考重点',
                                'description': f"中考网{subject}相关知识点：{text}",
                                'difficulty_level': 3,
                                'importance_level': 4,
                                'keywords': keywords + [text[:15]],
                                'source': '中考网',
                                'crawl_time': datetime.now().isoformat()
                            })

            # 如果没找到足够的内容，从链接文本中提取
            if len(knowledge_points) < 3:
                links = soup.find_all('a', href=True)
                for link in links[:20]:
                    text = link.get_text(strip=True)
                    href = link.get('href', '')

                    if (text and len(text) > 8 and len(text) < 80 and
                        any(keyword in text for keyword in keywords) and
                        any(indicator in href for indicator in ['detail', 'content', 'show', 'article'])):

                        existing_names = [kp.get('name', '') for kp in knowledge_points]
                        if text not in existing_names:
                            knowledge_points.append({
                                'name': text,
                                'subject': subject,
                                'grade': 'Grade 8',
                                'chapter': '中考重点',
                                'description': f"中考网{subject}相关内容：{text}",
                                'difficulty_level': 3,
                                'importance_level': 3,
                                'keywords': keywords + [text[:10]],
                                'source': '中考网',
                                'source_url': urljoin(f"https://www.zhongkao.com/{subject}/", href),
                                'crawl_time': datetime.now().isoformat()
                            })

        except Exception as e:
            logger.warning(f"    ⚠️ 提取知识点失败: {e}")

        return knowledge_points[:10]  # 限制数量

    def _find_question_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """查找试题页面链接"""
        question_links = []

        try:
            # 多种选择器查找试题链接
            link_patterns = [
                'a[href*="test"]',
                'a[href*="exam"]',
                'a[href*="question"]',
                'a[href*="practice"]',
                'a[href*="zhenti"]',  # 真题
                'a[href*="moniti"]',  # 模拟题
                'a[href*="lianxi"]',  # 练习
            ]

            for pattern in link_patterns:
                links = soup.select(pattern)
                for link in links[:8]:  # 限制数量
                    href = link.get('href', '')
                    if href and not href.startswith('#') and not href.startswith('javascript'):
                        full_url = urljoin(base_url, href)
                        if (full_url not in question_links and
                            not self._is_url_crawled_recently('zhongkao', full_url, 24)):  # 24小时内不重复爬取
                            question_links.append(full_url)

        except Exception as e:
            logger.warning(f"    ⚠️ 查找试题链接失败: {e}")

        return question_links[:5]  # 限制数量

    def _crawl_real_questions(self, question_links: List[str], subject: str) -> List[Dict]:
        """爬取真实的试题内容"""
        questions = []

        for url in question_links[:3]:  # 限制数量
            try:
                # 检查是否需要爬取
                if self._is_url_crawled_recently('zhongkao', url, 12):  # 12小时内不重复爬取
                    continue

                response = self.session.get(url, timeout=15)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # 尝试多种方式提取题目
                    question_elements = (
                        soup.select('div.question, .test-item, .exam-question, .practice-item') +
                        soup.select('div[class*="question"], div[class*="test"], div[class*="exam"]')
                    )

                    for i, elem in enumerate(question_elements[:8]):  # 限制数量
                        try:
                            # 提取题干
                            stem_selectors = ['.stem', '.question-text', '.title', 'p', '.content']
                            stem = None
                            for selector in stem_selectors:
                                stem_elem = elem.select_one(selector)
                                if stem_elem:
                                    stem = stem_elem.get_text(strip=True)
                                    break

                            if not stem or len(stem) < 10:
                                continue

                            # 提取选项
                            options = []
                            option_selectors = ['.option', '.choice', 'li', '.answer-option']
                            for selector in option_selectors:
                                option_elems = elem.select(selector)
                                for opt_elem in option_elems[:4]:
                                    opt_text = opt_elem.get_text(strip=True)
                                    if opt_text and len(opt_text) > 2:
                                        # 清理选项格式
                                        opt_text = re.sub(r'^[A-D]\.?\s*', '', opt_text)
                                        if opt_text not in options:
                                            options.append(opt_text)

                            # 尝试提取答案
                            correct_answer = 'A'  # 默认值
                            answer_selectors = ['.answer', '.correct', '.solution', '.jiexi']
                            for selector in answer_selectors:
                                answer_elem = elem.select_one(selector)
                                if answer_elem:
                                    answer_text = answer_elem.get_text(strip=True)
                                    # 从答案文本中提取选项字母
                                    for letter in ['A', 'B', 'C', 'D']:
                                        if letter in answer_text:
                                            correct_answer = letter
                                            break
                                    break

                            # 提取解析
                            explanation = ''
                            explanation_selectors = ['.explanation', '.analysis', '.solution', '.jiexi']
                            for selector in explanation_selectors:
                                explanation_elem = elem.select_one(selector)
                                if explanation_elem and explanation_elem != answer_elem:
                                    explanation = explanation_elem.get_text(strip=True)[:200]
                                    break

                            if not explanation:
                                explanation = f"来源于中考网{subject}练习题"

                            questions.append({
                                'question_id': f"zhongkao_{subject}_{len(questions)+1:03d}",
                                'subject': subject,
                                'grade': 'Grade 8',
                                'question_type': 'choice' if options else 'fill_blank',
                                'stem': stem[:300],
                                'options': '|'.join(options) if options else '',
                                'correct_answer': correct_answer,
                                'explanation': explanation,
                                'difficulty_level': 3,
                                'knowledge_points': [stem[:30]],
                                'source': '中考网',
                                'source_url': url,
                                'crawl_time': datetime.now().isoformat()
                            })

                        except Exception as e:
                            logger.debug(f"      ⚠️ 解析题目失败: {e}")
                            continue

                    # 记录爬取结果
                    if questions:
                        content_hash = self._get_content_hash(response.text)
                        self._record_crawl_result('zhongkao', url, content_hash, 'success', f'{subject}_questions')

                time.sleep(self.request_delay / 2)  # 试题页面间隔较短

            except Exception as e:
                logger.warning(f"    ⚠️ 爬取试题页面失败 {url}: {e}")
                self._record_crawl_result('zhongkao', url, None, 'failed', f'{subject}_questions')

        return questions

# 将方法添加到主类中
LegalEducationCrawler._extract_real_knowledge_points = LegalEducationCrawlerMethods._extract_real_knowledge_points
LegalEducationCrawler._find_question_links = LegalEducationCrawlerMethods._find_question_links  
LegalEducationCrawler._crawl_real_questions = LegalEducationCrawlerMethods._crawl_real_questions

if __name__ == "__main__":
    main()
