#!/usr/bin/env python3
"""
数据扩展脚本 - 扩展知识点数量和题目数据
"""

import json
import pandas as pd
from pathlib import Path
from typing import List, Dict

class KnowledgeDataExpander:
    """知识点数据扩展器"""
    
    def __init__(self):
        self.base_dir = Path("data_collection")
        self.processed_dir = self.base_dir / "processed"
    
    def expand_math_knowledge_points(self) -> List[Dict]:
        """扩展数学知识点"""
        expanded_points = [
            # 初一数学
            {"subject": "数学", "grade": "初一", "chapter": "有理数", "knowledge_point": "有理数的乘法", "description": "掌握有理数乘法的运算法则", "keywords": "有理数,乘法,运算法则,符号", "difficulty_level": 2, "importance_level": 4},
            {"subject": "数学", "grade": "初一", "chapter": "有理数", "knowledge_point": "有理数的除法", "description": "掌握有理数除法的运算法则", "keywords": "有理数,除法,运算法则,倒数", "difficulty_level": 2, "importance_level": 4},
            {"subject": "数学", "grade": "初一", "chapter": "有理数", "knowledge_point": "有理数的乘方", "description": "理解有理数乘方的概念和运算", "keywords": "有理数,乘方,幂,指数", "difficulty_level": 3, "importance_level": 3},
            {"subject": "数学", "grade": "初一", "chapter": "整式的加减", "knowledge_point": "同类项", "description": "理解同类项的概念，掌握合并同类项的方法", "keywords": "同类项,合并,系数,字母", "difficulty_level": 2, "importance_level": 4},
            {"subject": "数学", "grade": "初一", "chapter": "整式的加减", "knowledge_point": "去括号", "description": "掌握去括号的法则", "keywords": "去括号,分配律,符号", "difficulty_level": 2, "importance_level": 4},
            
            # 初二数学
            {"subject": "数学", "grade": "初二", "chapter": "一元二次方程", "knowledge_point": "一元二次方程的概念", "description": "理解一元二次方程的概念和一般形式", "keywords": "一元二次方程,二次项,一次项,常数项", "difficulty_level": 2, "importance_level": 4},
            {"subject": "数学", "grade": "初二", "chapter": "一元二次方程", "knowledge_point": "配方法", "description": "掌握用配方法解一元二次方程", "keywords": "配方法,完全平方式,配方", "difficulty_level": 3, "importance_level": 4},
            {"subject": "数学", "grade": "初二", "chapter": "一元二次方程", "knowledge_point": "公式法", "description": "掌握用公式法解一元二次方程", "keywords": "公式法,判别式,求根公式", "difficulty_level": 3, "importance_level": 4},
            {"subject": "数学", "grade": "初二", "chapter": "函数", "knowledge_point": "函数的概念", "description": "理解函数的概念和表示方法", "keywords": "函数,自变量,因变量,对应关系", "difficulty_level": 2, "importance_level": 5},
            {"subject": "数学", "grade": "初二", "chapter": "函数", "knowledge_point": "一次函数", "description": "掌握一次函数的概念、图像和性质", "keywords": "一次函数,直线,斜率,截距", "difficulty_level": 3, "importance_level": 5},
            
            # 初三数学
            {"subject": "数学", "grade": "初三", "chapter": "二次函数", "knowledge_point": "二次函数的概念", "description": "理解二次函数的概念和一般形式", "keywords": "二次函数,抛物线,顶点,对称轴", "difficulty_level": 3, "importance_level": 5},
            {"subject": "数学", "grade": "初三", "chapter": "二次函数", "knowledge_point": "二次函数的图像", "description": "掌握二次函数的图像特征", "keywords": "抛物线,开口方向,顶点,对称轴", "difficulty_level": 3, "importance_level": 4},
            {"subject": "数学", "grade": "初三", "chapter": "圆", "knowledge_point": "圆的概念", "description": "理解圆的概念和基本性质", "keywords": "圆,圆心,半径,直径", "difficulty_level": 2, "importance_level": 4},
            {"subject": "数学", "grade": "初三", "chapter": "圆", "knowledge_point": "圆周角定理", "description": "掌握圆周角定理及其推论", "keywords": "圆周角,圆心角,圆周角定理", "difficulty_level": 4, "importance_level": 4},
            {"subject": "数学", "grade": "初三", "chapter": "圆", "knowledge_point": "切线", "description": "理解切线的概念和性质", "keywords": "切线,切点,切线性质", "difficulty_level": 3, "importance_level": 4}
        ]
        return expanded_points
    
    def expand_chinese_knowledge_points(self) -> List[Dict]:
        """扩展语文知识点"""
        expanded_points = [
            # 初一语文
            {"subject": "语文", "grade": "初一", "chapter": "现代文阅读", "knowledge_point": "议论文阅读", "description": "理解议论文的特点，掌握议论文的阅读方法", "keywords": "议论文,论点,论据,论证", "difficulty_level": 3, "importance_level": 4},
            {"subject": "语文", "grade": "初一", "chapter": "现代文阅读", "knowledge_point": "散文阅读", "description": "理解散文的特点，掌握散文的阅读方法", "keywords": "散文,形散神聚,意境,语言", "difficulty_level": 3, "importance_level": 4},
            {"subject": "语文", "grade": "初一", "chapter": "古文阅读", "knowledge_point": "文言实词", "description": "掌握常见文言实词的含义和用法", "keywords": "文言实词,一词多义,古今异义", "difficulty_level": 3, "importance_level": 4},
            {"subject": "语文", "grade": "初一", "chapter": "古文阅读", "knowledge_point": "文言虚词", "description": "掌握常见文言虚词的用法", "keywords": "文言虚词,之,而,以,于", "difficulty_level": 3, "importance_level": 4},
            {"subject": "语文", "grade": "初一", "chapter": "写作", "knowledge_point": "记叙文写作", "description": "掌握记叙文的写作方法和技巧", "keywords": "记叙文,时间,地点,人物,事件", "difficulty_level": 2, "importance_level": 4},
            
            # 初二语文
            {"subject": "语文", "grade": "初二", "chapter": "现代文阅读", "knowledge_point": "小说阅读", "description": "理解小说的特点，掌握小说的阅读方法", "keywords": "小说,人物,情节,环境,主题", "difficulty_level": 3, "importance_level": 4},
            {"subject": "语文", "grade": "初二", "chapter": "古文阅读", "knowledge_point": "文言句式", "description": "掌握常见文言句式的特点", "keywords": "判断句,被动句,倒装句,省略句", "difficulty_level": 4, "importance_level": 4},
            {"subject": "语文", "grade": "初二", "chapter": "写作", "knowledge_point": "议论文写作", "description": "掌握议论文的写作方法和技巧", "keywords": "议论文,论点,论据,论证", "difficulty_level": 3, "importance_level": 4},
            
            # 初三语文
            {"subject": "语文", "grade": "初三", "chapter": "现代文阅读", "knowledge_point": "诗歌鉴赏", "description": "掌握诗歌鉴赏的方法和技巧", "keywords": "诗歌,意象,意境,表现手法", "difficulty_level": 4, "importance_level": 4},
            {"subject": "语文", "grade": "初三", "chapter": "写作", "knowledge_point": "材料作文", "description": "掌握材料作文的写作方法", "keywords": "材料作文,审题,立意,构思", "difficulty_level": 4, "importance_level": 5}
        ]
        return expanded_points
    
    def expand_english_knowledge_points(self) -> List[Dict]:
        """扩展英语知识点"""
        expanded_points = [
            # 初一英语
            {"subject": "英语", "grade": "初一", "chapter": "语法基础", "knowledge_point": "一般过去时", "description": "掌握一般过去时的用法和构成", "keywords": "一般过去时,过去时间,动词过去式", "difficulty_level": 2, "importance_level": 4},
            {"subject": "英语", "grade": "初一", "chapter": "语法基础", "knowledge_point": "一般将来时", "description": "掌握一般将来时的用法和构成", "keywords": "一般将来时,will,be going to", "difficulty_level": 2, "importance_level": 4},
            {"subject": "英语", "grade": "初一", "chapter": "语法基础", "knowledge_point": "形容词比较级", "description": "掌握形容词比较级的变化规则", "keywords": "形容词,比较级,最高级,规则变化", "difficulty_level": 2, "importance_level": 4},
            {"subject": "英语", "grade": "初一", "chapter": "词汇", "knowledge_point": "基础词汇", "description": "掌握基础词汇的拼写和用法", "keywords": "基础词汇,拼写,发音,词义", "difficulty_level": 1, "importance_level": 5},
            
            # 初二英语
            {"subject": "英语", "grade": "初二", "chapter": "语法进阶", "knowledge_point": "现在进行时", "description": "掌握现在进行时的用法和构成", "keywords": "现在进行时,be doing,正在进行", "difficulty_level": 2, "importance_level": 4},
            {"subject": "英语", "grade": "初二", "chapter": "语法进阶", "knowledge_point": "过去进行时", "description": "掌握过去进行时的用法和构成", "keywords": "过去进行时,was/were doing", "difficulty_level": 3, "importance_level": 3},
            {"subject": "英语", "grade": "初二", "chapter": "语法进阶", "knowledge_point": "情态动词", "description": "掌握情态动词的用法", "keywords": "情态动词,can,may,must,should", "difficulty_level": 3, "importance_level": 4},
            
            # 初三英语
            {"subject": "英语", "grade": "初三", "chapter": "语法高级", "knowledge_point": "现在完成时", "description": "掌握现在完成时的用法和构成", "keywords": "现在完成时,have/has done,过去分词", "difficulty_level": 3, "importance_level": 4},
            {"subject": "英语", "grade": "初三", "chapter": "语法高级", "knowledge_point": "被动语态", "description": "掌握被动语态的构成和用法", "keywords": "被动语态,be done,by", "difficulty_level": 4, "importance_level": 4},
            {"subject": "英语", "grade": "初三", "chapter": "语法高级", "knowledge_point": "定语从句", "description": "掌握定语从句的用法", "keywords": "定语从句,关系代词,关系副词", "difficulty_level": 4, "importance_level": 4}
        ]
        return expanded_points
    
    def expand_physics_knowledge_points(self) -> List[Dict]:
        """扩展物理知识点"""
        expanded_points = [
            # 初二物理
            {"subject": "物理", "grade": "初二", "chapter": "力学基础", "knowledge_point": "弹力", "description": "理解弹力的概念和胡克定律", "keywords": "弹力,胡克定律,弹性形变,弹簧", "difficulty_level": 2, "importance_level": 4},
            {"subject": "物理", "grade": "初二", "chapter": "力学基础", "knowledge_point": "摩擦力", "description": "理解摩擦力的概念和影响因素", "keywords": "摩擦力,静摩擦,滑动摩擦,摩擦系数", "difficulty_level": 2, "importance_level": 4},
            {"subject": "物理", "grade": "初二", "chapter": "压强", "knowledge_point": "压强", "description": "理解压强的概念和计算公式", "keywords": "压强,压力,受力面积,帕斯卡", "difficulty_level": 2, "importance_level": 4},
            {"subject": "物理", "grade": "初二", "chapter": "压强", "knowledge_point": "液体压强", "description": "理解液体压强的特点和规律", "keywords": "液体压强,深度,密度,连通器", "difficulty_level": 3, "importance_level": 4},
            
            # 初三物理
            {"subject": "物理", "grade": "初三", "chapter": "电学", "knowledge_point": "电流", "description": "理解电流的概念和测量", "keywords": "电流,电荷,安培,电流表", "difficulty_level": 2, "importance_level": 4},
            {"subject": "物理", "grade": "初三", "chapter": "电学", "knowledge_point": "电压", "description": "理解电压的概念和测量", "keywords": "电压,电势差,伏特,电压表", "difficulty_level": 2, "importance_level": 4},
            {"subject": "物理", "grade": "初三", "chapter": "电学", "knowledge_point": "电阻", "description": "理解电阻的概念和欧姆定律", "keywords": "电阻,欧姆定律,导体,绝缘体", "difficulty_level": 3, "importance_level": 4},
            {"subject": "物理", "grade": "初三", "chapter": "电学", "knowledge_point": "串联电路", "description": "掌握串联电路的特点和计算", "keywords": "串联,电流相等,电压分配", "difficulty_level": 3, "importance_level": 4},
            {"subject": "物理", "grade": "初三", "chapter": "电学", "knowledge_point": "并联电路", "description": "掌握并联电路的特点和计算", "keywords": "并联,电压相等,电流分配", "difficulty_level": 3, "importance_level": 4}
        ]
        return expanded_points
    
    def expand_chemistry_knowledge_points(self) -> List[Dict]:
        """扩展化学知识点"""
        expanded_points = [
            # 初三化学
            {"subject": "化学", "grade": "初三", "chapter": "物质的变化", "knowledge_point": "化学方程式", "description": "掌握化学方程式的书写和配平", "keywords": "化学方程式,配平,质量守恒", "difficulty_level": 3, "importance_level": 4},
            {"subject": "化学", "grade": "初三", "chapter": "空气", "knowledge_point": "空气的成分", "description": "了解空气的主要成分", "keywords": "空气,氮气,氧气,二氧化碳", "difficulty_level": 1, "importance_level": 3},
            {"subject": "化学", "grade": "初三", "chapter": "空气", "knowledge_point": "氧气的性质", "description": "掌握氧气的物理性质和化学性质", "keywords": "氧气,助燃,氧化反应", "difficulty_level": 2, "importance_level": 4},
            {"subject": "化学", "grade": "初三", "chapter": "水", "knowledge_point": "水的组成", "description": "了解水的组成和电解", "keywords": "水,氢元素,氧元素,电解", "difficulty_level": 2, "importance_level": 4},
            {"subject": "化学", "grade": "初三", "chapter": "水", "knowledge_point": "水的净化", "description": "了解水的净化方法", "keywords": "水的净化,过滤,蒸馏,吸附", "difficulty_level": 2, "importance_level": 3},
            {"subject": "化学", "grade": "初三", "chapter": "碳和碳的化合物", "knowledge_point": "碳的性质", "description": "掌握碳的物理性质和化学性质", "keywords": "碳,金刚石,石墨,活性炭", "difficulty_level": 2, "importance_level": 4},
            {"subject": "化学", "grade": "初三", "chapter": "碳和碳的化合物", "knowledge_point": "二氧化碳", "description": "掌握二氧化碳的性质和制法", "keywords": "二氧化碳,温室效应,碳酸钙", "difficulty_level": 2, "importance_level": 4}
        ]
        return expanded_points
    
    def expand_biology_knowledge_points(self) -> List[Dict]:
        """扩展生物知识点"""
        expanded_points = [
            # 初一生物
            {"subject": "生物", "grade": "初一", "chapter": "细胞", "knowledge_point": "细胞膜", "description": "了解细胞膜的结构和功能", "keywords": "细胞膜,选择透过性,保护", "difficulty_level": 2, "importance_level": 3},
            {"subject": "生物", "grade": "初一", "chapter": "细胞", "knowledge_point": "细胞质", "description": "了解细胞质的组成和功能", "keywords": "细胞质,细胞器,新陈代谢", "difficulty_level": 2, "importance_level": 3},
            {"subject": "生物", "grade": "初一", "chapter": "细胞", "knowledge_point": "细胞核", "description": "了解细胞核的结构和功能", "keywords": "细胞核,遗传物质,染色体", "difficulty_level": 2, "importance_level": 4},
            {"subject": "生物", "grade": "初一", "chapter": "生物体的结构层次", "knowledge_point": "组织", "description": "理解组织的概念和类型", "keywords": "组织,上皮组织,结缔组织,肌肉组织", "difficulty_level": 2, "importance_level": 3},
            {"subject": "生物", "grade": "初一", "chapter": "生物体的结构层次", "knowledge_point": "器官", "description": "理解器官的概念和功能", "keywords": "器官,系统,功能", "difficulty_level": 2, "importance_level": 3},
            
            # 初二生物
            {"subject": "生物", "grade": "初二", "chapter": "遗传与变异", "knowledge_point": "基因", "description": "理解基因的概念和作用", "keywords": "基因,遗传,DNA,染色体", "difficulty_level": 3, "importance_level": 4},
            {"subject": "生物", "grade": "初二", "chapter": "遗传与变异", "knowledge_point": "显性性状和隐性性状", "description": "理解显性性状和隐性性状的概念", "keywords": "显性性状,隐性性状,基因型,表现型", "difficulty_level": 3, "importance_level": 4},
            {"subject": "生物", "grade": "初二", "chapter": "进化", "knowledge_point": "自然选择", "description": "理解自然选择的概念和过程", "keywords": "自然选择,适者生存,进化", "difficulty_level": 3, "importance_level": 4}
        ]
        return expanded_points
    
    def expand_history_knowledge_points(self) -> List[Dict]:
        """扩展历史知识点"""
        expanded_points = [
            # 初一历史
            {"subject": "历史", "grade": "初一", "chapter": "中国古代史", "knowledge_point": "隋唐", "description": "了解隋唐时期的历史发展", "keywords": "隋朝,唐朝,统一,繁荣", "difficulty_level": 2, "importance_level": 4},
            {"subject": "历史", "grade": "初一", "chapter": "中国古代史", "knowledge_point": "宋元", "description": "了解宋元时期的历史发展", "keywords": "宋朝,元朝,经济,文化", "difficulty_level": 2, "importance_level": 3},
            {"subject": "历史", "grade": "初一", "chapter": "中国古代史", "knowledge_point": "明清", "description": "了解明清时期的历史发展", "keywords": "明朝,清朝,专制,闭关", "difficulty_level": 2, "importance_level": 4},
            
            # 初二历史
            {"subject": "历史", "grade": "初二", "chapter": "中国近代史", "knowledge_point": "鸦片战争", "description": "了解鸦片战争的背景和影响", "keywords": "鸦片战争,不平等条约,近代史", "difficulty_level": 2, "importance_level": 4},
            {"subject": "历史", "grade": "初二", "chapter": "中国近代史", "knowledge_point": "太平天国运动", "description": "了解太平天国运动的过程和意义", "keywords": "太平天国,农民起义,反封建", "difficulty_level": 2, "importance_level": 3},
            {"subject": "历史", "grade": "初二", "chapter": "中国近代史", "knowledge_point": "洋务运动", "description": "了解洋务运动的内容和影响", "keywords": "洋务运动,自强,求富,近代化", "difficulty_level": 2, "importance_level": 3},
            {"subject": "历史", "grade": "初二", "chapter": "中国近代史", "knowledge_point": "戊戌变法", "description": "了解戊戌变法的内容和失败原因", "keywords": "戊戌变法,维新,改革,失败", "difficulty_level": 2, "importance_level": 3},
            
            # 初三历史
            {"subject": "历史", "grade": "初三", "chapter": "中国现代史", "knowledge_point": "辛亥革命", "description": "了解辛亥革命的过程和意义", "keywords": "辛亥革命,民主革命,中华民国", "difficulty_level": 2, "importance_level": 4},
            {"subject": "历史", "grade": "初三", "chapter": "中国现代史", "knowledge_point": "五四运动", "description": "了解五四运动的过程和意义", "keywords": "五四运动,新文化运动,民主科学", "difficulty_level": 2, "importance_level": 4},
            {"subject": "历史", "grade": "初三", "chapter": "中国现代史", "knowledge_point": "中国共产党成立", "description": "了解中国共产党成立的历史背景", "keywords": "中国共产党,马克思主义,工人阶级", "difficulty_level": 2, "importance_level": 4}
        ]
        return expanded_points
    
    def expand_geography_knowledge_points(self) -> List[Dict]:
        """扩展地理知识点"""
        expanded_points = [
            # 初一地理
            {"subject": "地理", "grade": "初一", "chapter": "地球和地图", "knowledge_point": "经纬网", "description": "掌握经纬网的概念和应用", "keywords": "经纬网,经线,纬线,坐标", "difficulty_level": 2, "importance_level": 4},
            {"subject": "地理", "grade": "初一", "chapter": "地球和地图", "knowledge_point": "等高线地形图", "description": "掌握等高线地形图的判读", "keywords": "等高线,地形,山峰,山谷", "difficulty_level": 3, "importance_level": 4},
            {"subject": "地理", "grade": "初一", "chapter": "陆地和海洋", "knowledge_point": "大洲和大洋", "description": "了解世界大洲和大洋的分布", "keywords": "大洲,大洋,分布,面积", "difficulty_level": 1, "importance_level": 3},
            {"subject": "地理", "grade": "初一", "chapter": "陆地和海洋", "knowledge_point": "板块构造学说", "description": "理解板块构造学说的基本内容", "keywords": "板块,地壳运动,地震,火山", "difficulty_level": 3, "importance_level": 4},
            
            # 初二地理
            {"subject": "地理", "grade": "初二", "chapter": "天气与气候", "knowledge_point": "天气", "description": "理解天气的概念和要素", "keywords": "天气,气温,降水,风力", "difficulty_level": 2, "importance_level": 3},
            {"subject": "地理", "grade": "初二", "chapter": "天气与气候", "knowledge_point": "气候", "description": "理解气候的概念和影响因素", "keywords": "气候,纬度,海陆,地形", "difficulty_level": 2, "importance_level": 4},
            {"subject": "地理", "grade": "初二", "chapter": "居民与聚落", "knowledge_point": "人口", "description": "了解世界人口的分布和增长", "keywords": "人口,分布,增长,密度", "difficulty_level": 2, "importance_level": 3},
            {"subject": "地理", "grade": "初二", "chapter": "居民与聚落", "knowledge_point": "聚落", "description": "理解聚落的概念和类型", "keywords": "聚落,城市,乡村,分布", "difficulty_level": 2, "importance_level": 3}
        ]
        return expanded_points
    
    def expand_politics_knowledge_points(self) -> List[Dict]:
        """扩展政治知识点"""
        expanded_points = [
            # 初一政治
            {"subject": "政治", "grade": "初一", "chapter": "思想品德", "knowledge_point": "自尊自信", "description": "培养自尊自信的品质", "keywords": "自尊,自信,自我价值", "difficulty_level": 1, "importance_level": 3},
            {"subject": "政治", "grade": "初一", "chapter": "思想品德", "knowledge_point": "自立自强", "description": "培养自立自强的精神", "keywords": "自立,自强,独立,奋斗", "difficulty_level": 1, "importance_level": 3},
            {"subject": "政治", "grade": "初一", "chapter": "思想品德", "knowledge_point": "诚实守信", "description": "培养诚实守信的品质", "keywords": "诚实,守信,诚信,道德", "difficulty_level": 1, "importance_level": 4},
            
            # 初二政治
            {"subject": "政治", "grade": "初二", "chapter": "法律基础", "knowledge_point": "法律的特征", "description": "理解法律的基本特征", "keywords": "法律,强制性,规范性,普遍性", "difficulty_level": 2, "importance_level": 4},
            {"subject": "政治", "grade": "初二", "chapter": "法律基础", "knowledge_point": "宪法", "description": "了解宪法的地位和作用", "keywords": "宪法,根本法,最高法律效力", "difficulty_level": 2, "importance_level": 4},
            {"subject": "政治", "grade": "初二", "chapter": "法律基础", "knowledge_point": "未成年人保护法", "description": "了解未成年人保护法的内容", "keywords": "未成年人,保护,权利,义务", "difficulty_level": 2, "importance_level": 4},
            
            # 初三政治
            {"subject": "政治", "grade": "初三", "chapter": "经济生活", "knowledge_point": "市场经济", "description": "理解市场经济的基本特征", "keywords": "市场经济,供求关系,价格,竞争", "difficulty_level": 3, "importance_level": 4},
            {"subject": "政治", "grade": "初三", "chapter": "经济生活", "knowledge_point": "消费", "description": "了解消费的概念和类型", "keywords": "消费,生产,需求,供给", "difficulty_level": 2, "importance_level": 3},
            {"subject": "政治", "grade": "初三", "chapter": "经济生活", "knowledge_point": "投资理财", "description": "了解投资理财的基本知识", "keywords": "投资,理财,储蓄,保险", "difficulty_level": 3, "importance_level": 3}
        ]
        return expanded_points
    
    def expand_all_knowledge_points(self) -> List[Dict]:
        """扩展所有科目的知识点"""
        all_points = []
        all_points.extend(self.expand_math_knowledge_points())
        all_points.extend(self.expand_chinese_knowledge_points())
        all_points.extend(self.expand_english_knowledge_points())
        all_points.extend(self.expand_physics_knowledge_points())
        all_points.extend(self.expand_chemistry_knowledge_points())
        all_points.extend(self.expand_biology_knowledge_points())
        all_points.extend(self.expand_history_knowledge_points())
        all_points.extend(self.expand_geography_knowledge_points())
        all_points.extend(self.expand_politics_knowledge_points())
        return all_points
    
    def merge_with_existing_data(self):
        """合并现有数据和扩展数据"""
        # 读取现有数据
        existing_file = self.processed_dir / "knowledge_points.csv"
        if existing_file.exists():
            existing_df = pd.read_csv(existing_file)
            existing_points = existing_df.to_dict('records')
        else:
            existing_points = []
        
        # 获取扩展数据
        expanded_points = self.expand_all_knowledge_points()
        
        # 合并数据
        all_points = existing_points + expanded_points
        
        # 去重（基于知识点名称）
        seen = set()
        unique_points = []
        for point in all_points:
            key = f"{point['subject']}_{point['grade']}_{point['chapter']}_{point['knowledge_point']}"
            if key not in seen:
                seen.add(key)
                unique_points.append(point)
        
        # 保存合并后的数据
        merged_df = pd.DataFrame(unique_points)
        merged_file = self.processed_dir / "knowledge_points_expanded.csv"
        merged_df.to_csv(merged_file, index=False, encoding='utf-8')
        
        print(f"知识点数据已扩展:")
        print(f"  原有数据: {len(existing_points)} 个")
        print(f"  新增数据: {len(expanded_points)} 个")
        print(f"  合并后数据: {len(unique_points)} 个")
        print(f"  保存文件: {merged_file}")
        
        return unique_points

def main():
    """主函数"""
    print("🚀 开始扩展知识点数据...")
    
    expander = KnowledgeDataExpander()
    
    # 扩展知识点数据
    print("\n📚 扩展各科知识点...")
    expanded_points = expander.merge_with_existing_data()
    
    # 统计各科知识点数量
    subject_counts = {}
    for point in expanded_points:
        subject = point['subject']
        subject_counts[subject] = subject_counts.get(subject, 0) + 1
    
    print("\n📊 各科知识点统计:")
    for subject, count in subject_counts.items():
        print(f"  {subject}: {count} 个知识点")
    
    print(f"\n✅ 知识点数据扩展完成！")
    print(f"  总计: {len(expanded_points)} 个知识点")

if __name__ == "__main__":
    main()
