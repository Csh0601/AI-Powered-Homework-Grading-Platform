"""
试卷生成服务
从用户历史记录中提取相似题目，生成PDF格式的试卷
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from io import BytesIO

# ReportLab PDF生成库
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

logger = logging.getLogger(__name__)

# 中文字体配置
FONT_NAME = 'SimSun'  # 宋体
FONT_BOLD_NAME = 'SimHei'  # 黑体（用于标题）

# 尝试注册中文字体
def register_chinese_fonts():
    """注册中文字体，支持多种字体路径"""
    font_paths = [
        # Windows字体路径
        'C:/Windows/Fonts/simsun.ttc',
        'C:/Windows/Fonts/simhei.ttf',
        # Linux字体路径
        '/usr/share/fonts/truetype/simhei.ttf',
        '/usr/share/fonts/truetype/simsun.ttc',
        # 项目本地字体路径（备用）
        os.path.join(os.path.dirname(__file__), '../../fonts/simsun.ttc'),
        os.path.join(os.path.dirname(__file__), '../../fonts/simhei.ttf'),
    ]
    
    font_registered = False
    
    try:
        # 尝试注册宋体
        for path in font_paths:
            if os.path.exists(path) and 'simsun' in path.lower():
                try:
                    pdfmetrics.registerFont(TTFont(FONT_NAME, path))
                    logger.info(f"✅ 成功注册中文字体: {FONT_NAME} from {path}")
                    font_registered = True
                    break
                except Exception as font_err:
                    logger.warning(f"⚠️ 注册字体失败 {path}: {font_err}")
                    continue
        
        if not font_registered:
            logger.warning(f"⚠️ 未找到宋体字体文件，PDF将使用默认字体（中文可能显示为方框）")
            
        # 尝试注册黑体
        for path in font_paths:
            if os.path.exists(path) and 'simhei' in path.lower():
                try:
                    pdfmetrics.registerFont(TTFont(FONT_BOLD_NAME, path))
                    logger.info(f"✅ 成功注册中文粗体字体: {FONT_BOLD_NAME} from {path}")
                    break
                except Exception as font_err:
                    logger.warning(f"⚠️ 注册黑体失败 {path}: {font_err}")
                    continue
        else:
            logger.warning(f"⚠️ 未找到黑体字体文件，将使用宋体代替")
            
    except Exception as e:
        logger.warning(f"⚠️ 中文字体注册过程出现问题: {e}")
        # 不抛出异常，允许系统继续运行

# 初始化时注册字体
try:
    register_chinese_fonts()
except Exception as e:
    logger.warning(f"⚠️ 字体初始化失败，PDF生成可能无法正确显示中文: {e}")


class PaperGenerator:
    """试卷生成器"""
    
    def __init__(self):
        """初始化试卷生成器"""
        self.page_width, self.page_height = A4
        self.margin = 2 * cm
        self.content_width = self.page_width - 2 * self.margin
        
    def extract_similar_questions_from_history(
        self, 
        history_records: List[Dict[str, Any]], 
        max_questions: int = 10
    ) -> List[Dict[str, Any]]:
        """
        从历史记录中提取相似题目
        
        Args:
            history_records: 历史记录列表
            max_questions: 最大题目数量
            
        Returns:
            相似题目列表
        """
        similar_questions = []
        
        try:
            # 遍历所有历史记录
            for record in history_records:
                # 方法1: 检查是否有 similar_questions 字段（新格式）
                if 'similar_questions' in record and record['similar_questions']:
                    for item in record['similar_questions']:
                        if isinstance(item, dict):
                            similar_questions.append(item)
                            
                # 方法2: 检查 grading_result 中的 similar_question 字段（新格式）
                grading_result = record.get('grading_result', {})
                if isinstance(grading_result, dict):
                    results = grading_result.get('grading_result', [])
                    if isinstance(results, list):
                        for result in results:
                            if isinstance(result, dict) and 'similar_question' in result:
                                sq = result['similar_question']
                                if sq:
                                    similar_questions.append({
                                        'question': sq,
                                        'source': result.get('question', ''),
                                        'type': result.get('type', '未知题型')
                                    })
                
                # 方法3: 从 grading_result 直接提取题目（兼容旧格式）
                # 如果没有 similar_questions，就使用原始题目
                if isinstance(grading_result, list):
                    # 直接是数组格式
                    for result in grading_result:
                        if isinstance(result, dict):
                            question_text = result.get('question', '')
                            if question_text and len(question_text) > 3:  # 过滤掉太短的内容
                                similar_questions.append({
                                    'question': question_text,
                                    'type': result.get('type', '未知题型'),
                                    'source': 'history'
                                })
                elif isinstance(grading_result, dict):
                    # 嵌套字典格式
                    results = grading_result.get('grading_result', [])
                    if isinstance(results, list):
                        for result in results:
                            if isinstance(result, dict):
                                question_text = result.get('question', '')
                                if question_text and len(question_text) > 3:
                                    similar_questions.append({
                                        'question': question_text,
                                        'type': result.get('type', '未知题型'),
                                        'source': 'history'
                                    })
                                    
            # 去重（基于题目内容）
            seen = set()
            unique_questions = []
            for q in similar_questions:
                question_text = q.get('question', '') or q.get('similar_question', '')
                if question_text and question_text not in seen and len(question_text) > 3:
                    seen.add(question_text)
                    unique_questions.append(q)
                    
            # 限制数量
            result = unique_questions[:max_questions]
            logger.info(f"📝 从历史记录中提取了 {len(result)} 道题目")
            return result
            
        except Exception as e:
            logger.error(f"❌ 提取题目失败: {e}", exc_info=True)
            return []
            
    def generate_paper_pdf(
        self, 
        questions: List[Dict[str, Any]], 
        title: str = "练习试卷",
        output_path: Optional[str] = None
    ) -> BytesIO:
        """
        生成PDF格式的试卷
        
        Args:
            questions: 题目列表
            title: 试卷标题
            output_path: 输出文件路径（可选，如果不提供则返回BytesIO）
            
        Returns:
            BytesIO对象包含PDF内容
        """
        try:
            # 创建PDF文档
            if output_path:
                pdf_file = output_path
            else:
                pdf_file = BytesIO()
                
            # 创建Canvas对象
            c = canvas.Canvas(pdf_file, pagesize=A4)
            
            # 设置中文字体
            try:
                c.setFont(FONT_BOLD_NAME, 18)
            except:
                try:
                    c.setFont(FONT_NAME, 18)
                except:
                    c.setFont('Helvetica-Bold', 18)  # 最终回退到默认字体
                
            # 当前Y坐标
            y = self.page_height - self.margin
            
            # 1. 绘制试卷标题
            title_text = title
            c.drawCentredString(self.page_width / 2, y, title_text)
            y -= 1.5 * cm
            
            # 2. 绘制试卷信息栏
            try:
                c.setFont(FONT_NAME, 10)
            except:
                c.setFont('Helvetica', 10)
            info_y = y
            c.drawString(self.margin, info_y, f"生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}")
            c.drawString(self.margin, info_y - 0.6*cm, "姓名：__________")
            c.drawString(self.margin + 5*cm, info_y - 0.6*cm, "分数：__________")
            
            # 分割线
            y -= 2 * cm
            c.line(self.margin, y, self.page_width - self.margin, y)
            y -= 1 * cm
            
            # 3. 绘制题目
            try:
                c.setFont(FONT_NAME, 11)
            except:
                c.setFont('Helvetica', 11)
            
            for idx, question in enumerate(questions, 1):
                # 检查是否需要换页
                if y < self.margin + 5*cm:
                    c.showPage()
                    try:
                        c.setFont(FONT_NAME, 11)
                    except:
                        c.setFont('Helvetica', 11)
                    y = self.page_height - self.margin
                    
                # 获取题目内容
                question_text = self._get_question_text(question)
                question_type = question.get('type', '未知')
                
                # 绘制题号和题型
                question_header = f"{idx}. [{question_type}]"
                try:
                    c.setFont(FONT_BOLD_NAME if FONT_BOLD_NAME else FONT_NAME, 11)
                except:
                    try:
                        c.setFont(FONT_NAME, 11)
                    except:
                        c.setFont('Helvetica-Bold', 11)
                c.drawString(self.margin, y, question_header)
                y -= 0.7 * cm
                
                # 绘制题目内容（支持多行）
                try:
                    c.setFont(FONT_NAME, 10)
                except:
                    c.setFont('Helvetica', 10)
                lines = self._wrap_text(question_text, self.content_width - 1*cm)
                for line in lines:
                    if y < self.margin + 3*cm:
                        c.showPage()
                        try:
                            c.setFont(FONT_NAME, 10)
                        except:
                            c.setFont('Helvetica', 10)
                        y = self.page_height - self.margin
                    c.drawString(self.margin + 0.5*cm, y, line)
                    y -= 0.6 * cm
                    
                # 答题空间
                y -= 0.5 * cm
                try:
                    c.setFont(FONT_NAME, 9)
                except:
                    c.setFont('Helvetica', 9)
                c.setStrokeColor(colors.grey)
                c.line(self.margin + 1*cm, y, self.page_width - self.margin - 1*cm, y)
                c.drawString(self.margin + 0.5*cm, y - 0.4*cm, "答：")
                y -= 1.5 * cm
                
                # 题目间距
                y -= 0.5 * cm
                
            # 4. 页脚
            page_num = 1
            try:
                c.setFont(FONT_NAME, 9)
            except:
                c.setFont('Helvetica', 9)
            c.drawCentredString(
                self.page_width / 2, 
                self.margin / 2, 
                f"第 {page_num} 页"
            )
            
            # 保存PDF
            c.save()
            
            # 如果是BytesIO，重置指针
            if not output_path:
                pdf_file.seek(0)
                
            logger.info(f"✅ PDF试卷生成成功，共 {len(questions)} 道题目")
            return pdf_file
            
        except Exception as e:
            logger.error(f"❌ 生成PDF失败: {e}", exc_info=True)
            raise Exception(f"生成PDF试卷失败: {str(e)}")
            
    def _get_question_text(self, question: Dict[str, Any]) -> str:
        """从题目字典中提取题目文本"""
        # 尝试多个可能的字段
        for field in ['question', 'similar_question', 'content', 'text']:
            if field in question and question[field]:
                return str(question[field])
        return "题目内容缺失"
        
    def _wrap_text(self, text: str, max_width_mm: float) -> List[str]:
        """
        将文本按宽度拆分为多行
        
        Args:
            text: 原始文本
            max_width_mm: 最大宽度（毫米）
            
        Returns:
            文本行列表
        """
        # 简单实现：按字符数拆分
        # 假设中文字符宽度约为 4mm，英文约为 2mm
        max_chars = int(max_width_mm / 4)  # 保守估计
        
        lines = []
        current_line = ""
        
        for char in text:
            if len(current_line) >= max_chars:
                lines.append(current_line)
                current_line = char
            else:
                current_line += char
                
        if current_line:
            lines.append(current_line)
            
        return lines if lines else [text]


# 创建全局单例
_paper_generator_instance: Optional[PaperGenerator] = None

def get_paper_generator() -> PaperGenerator:
    """获取试卷生成器单例"""
    global _paper_generator_instance
    
    if _paper_generator_instance is None:
        _paper_generator_instance = PaperGenerator()
        
    return _paper_generator_instance


# 便捷函数
def generate_paper_from_history(
    history_records: List[Dict[str, Any]], 
    max_questions: int = 10,
    title: str = "练习试卷"
) -> BytesIO:
    """
    从历史记录生成试卷PDF
    
    Args:
        history_records: 历史记录列表
        max_questions: 最大题目数量
        title: 试卷标题
        
    Returns:
        包含PDF内容的BytesIO对象
    """
    generator = get_paper_generator()
    
    # 提取相似题目
    questions = generator.extract_similar_questions_from_history(
        history_records, 
        max_questions
    )
    
    if not questions:
        raise ValueError("没有找到足够的题目生成试卷")
        
    # 生成PDF
    return generator.generate_paper_pdf(questions, title)

