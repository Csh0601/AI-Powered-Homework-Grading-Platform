#!/usr/bin/env python3
"""
基础数据存储服务
Day 7 任务 - 搭建基础的数据存储服务

主要功能：
1. 知识点数据管理
2. 题目数据管理
3. 批改记录管理
4. 数据导入导出
5. 数据验证和清理

技术要点：
- 数据一致性保证
- 事务管理
- 批量操作优化
- 数据备份恢复
- 性能监控
"""

import os
import json
import sqlite3
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple
import hashlib
import uuid
from pathlib import Path
import shutil
import threading
from contextlib import contextmanager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataStorageService:
    """基础数据存储服务"""
    
    def __init__(self, db_path: str = None, backup_dir: str = None):
        """
        初始化数据存储服务
        
        Args:
            db_path: 数据库文件路径
            backup_dir: 备份目录路径
        """
        # 数据库配置
        self.db_path = db_path or os.path.join(
            os.path.dirname(__file__), '..', '..', 'database', 'knowledge_base.db'
        )
        
        # 备份配置
        self.backup_dir = backup_dir or os.path.join(
            os.path.dirname(__file__), '..', '..', 'backups'
        )
        
        # 确保目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # 线程锁
        self._lock = threading.Lock()
        
        # 初始化数据库
        self._init_database()
        
        # 统计信息
        self.stats = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'last_backup': None,
            'db_size_bytes': 0
        }
        
        logger.info(f"✅ 数据存储服务初始化完成: {self.db_path}")
    
    def _init_database(self):
        """初始化数据库表结构"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 知识点表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS knowledge_points (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        knowledge_point_id TEXT UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        category TEXT,
                        subject TEXT,
                        difficulty_level INTEGER DEFAULT 1,
                        grade_level INTEGER DEFAULT 7,
                        keywords TEXT, -- JSON格式
                        patterns TEXT, -- JSON格式
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 题目表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS questions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        question_id TEXT UNIQUE NOT NULL,
                        number TEXT,
                        stem TEXT NOT NULL,
                        answer TEXT,
                        correct_answer TEXT,
                        type TEXT,
                        subject TEXT,
                        difficulty_level INTEGER DEFAULT 1,
                        timestamp INTEGER,
                        source TEXT,
                        options TEXT, -- JSON格式
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 题目知识点关联表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS question_knowledge_points (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        question_id TEXT NOT NULL,
                        knowledge_point_id TEXT NOT NULL,
                        relevance_score REAL DEFAULT 1.0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (question_id) REFERENCES questions(question_id),
                        FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_points(knowledge_point_id),
                        UNIQUE(question_id, knowledge_point_id)
                    )
                ''')
                
                # 批改记录表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS grading_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        record_id TEXT UNIQUE NOT NULL,
                        task_id TEXT NOT NULL,
                        question_id TEXT NOT NULL,
                        user_id TEXT,
                        is_correct BOOLEAN,
                        score REAL,
                        explanation TEXT,
                        grading_method TEXT,
                        confidence REAL DEFAULT 1.0,
                        processing_time_ms REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (question_id) REFERENCES questions(question_id)
                    )
                ''')
                
                # 用户学习记录表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS learning_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        question_id TEXT NOT NULL,
                        knowledge_point_id TEXT,
                        answer_time INTEGER, -- 答题用时（秒）
                        is_correct BOOLEAN,
                        attempt_count INTEGER DEFAULT 1,
                        confidence_level INTEGER, -- 学生信心等级(1-5)
                        answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (question_id) REFERENCES questions(question_id),
                        FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_points(knowledge_point_id)
                    )
                ''')
                
                # 等待一下确保表创建完成
                conn.commit()
                
                # 创建索引
                indexes = [
                    "CREATE INDEX IF NOT EXISTS idx_kp_subject ON knowledge_points(subject)",
                    "CREATE INDEX IF NOT EXISTS idx_kp_difficulty ON knowledge_points(difficulty_level)",
                    "CREATE INDEX IF NOT EXISTS idx_q_subject ON questions(subject)",
                    "CREATE INDEX IF NOT EXISTS idx_q_type ON questions(type)",
                    "CREATE INDEX IF NOT EXISTS idx_q_difficulty ON questions(difficulty_level)",
                    "CREATE INDEX IF NOT EXISTS idx_qkp_question ON question_knowledge_points(question_id)",
                    "CREATE INDEX IF NOT EXISTS idx_qkp_knowledge ON question_knowledge_points(knowledge_point_id)",
                    "CREATE INDEX IF NOT EXISTS idx_gr_task ON grading_records(task_id)",
                    "CREATE INDEX IF NOT EXISTS idx_gr_user ON grading_records(user_id)",
                    "CREATE INDEX IF NOT EXISTS idx_lr_user ON learning_records(user_id)",
                    "CREATE INDEX IF NOT EXISTS idx_lr_question ON learning_records(question_id)"
                ]
                
                for index_sql in indexes:
                    cursor.execute(index_sql)
                
                conn.commit()
                logger.info("✅ 数据库表结构初始化完成")
                
        except Exception as e:
            logger.error(f"❌ 数据库初始化失败: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接（上下文管理器）"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.row_factory = sqlite3.Row  # 返回字典格式
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"数据库连接错误: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def _update_stats(self, success: bool = True):
        """更新统计信息"""
        with self._lock:
            self.stats['total_operations'] += 1
            if success:
                self.stats['successful_operations'] += 1
            else:
                self.stats['failed_operations'] += 1
            
            # 更新数据库大小
            try:
                self.stats['db_size_bytes'] = os.path.getsize(self.db_path)
            except:
                pass
    
    # ========================================
    # 知识点数据管理
    # ========================================
    
    def save_knowledge_point(self, knowledge_point: Dict[str, Any]) -> bool:
        """保存知识点数据"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 准备数据
                data = {
                    'knowledge_point_id': knowledge_point.get('id', str(uuid.uuid4())),
                    'name': knowledge_point.get('name', ''),
                    'category': knowledge_point.get('category', ''),
                    'subject': knowledge_point.get('subject', ''),
                    'difficulty_level': knowledge_point.get('difficulty_level', 1),
                    'grade_level': knowledge_point.get('grade_level', 7),
                    'keywords': json.dumps(knowledge_point.get('keywords', []), ensure_ascii=False),
                    'patterns': json.dumps(knowledge_point.get('patterns', []), ensure_ascii=False),
                    'description': knowledge_point.get('description', ''),
                    'updated_at': datetime.utcnow().isoformat()
                }
                
                # 插入或更新
                cursor.execute('''
                    INSERT OR REPLACE INTO knowledge_points (
                        knowledge_point_id, name, category, subject, difficulty_level, 
                        grade_level, keywords, patterns, description, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data['knowledge_point_id'], data['name'], data['category'],
                    data['subject'], data['difficulty_level'], data['grade_level'],
                    data['keywords'], data['patterns'], data['description'],
                    data['updated_at']
                ))
                
                conn.commit()
                self._update_stats(True)
                return True
                
        except Exception as e:
            logger.error(f"保存知识点失败: {e}")
            self._update_stats(False)
            return False
    
    def get_knowledge_points(self, subject: str = None, difficulty: int = None, 
                           limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """获取知识点列表"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 构建查询
                sql = "SELECT * FROM knowledge_points WHERE 1=1"
                params = []
                
                if subject:
                    sql += " AND subject = ?"
                    params.append(subject)
                
                if difficulty:
                    sql += " AND difficulty_level = ?"
                    params.append(difficulty)
                
                sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                
                # 转换为字典列表
                results = []
                for row in rows:
                    kp = dict(row)
                    # 解析JSON字段
                    try:
                        kp['keywords'] = json.loads(kp['keywords']) if kp['keywords'] else []
                        kp['patterns'] = json.loads(kp['patterns']) if kp['patterns'] else []
                    except:
                        kp['keywords'] = []
                        kp['patterns'] = []
                    results.append(kp)
                
                self._update_stats(True)
                return results
                
        except Exception as e:
            logger.error(f"获取知识点失败: {e}")
            self._update_stats(False)
            return []
    
    def search_knowledge_points(self, query: str, subject: str = None) -> List[Dict[str, Any]]:
        """搜索知识点"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 构建搜索查询
                sql = '''
                    SELECT * FROM knowledge_points 
                    WHERE (name LIKE ? OR description LIKE ? OR keywords LIKE ?)
                '''
                params = [f'%{query}%', f'%{query}%', f'%{query}%']
                
                if subject:
                    sql += " AND subject = ?"
                    params.append(subject)
                
                sql += " ORDER BY name"
                
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                
                results = []
                for row in rows:
                    kp = dict(row)
                    try:
                        kp['keywords'] = json.loads(kp['keywords']) if kp['keywords'] else []
                        kp['patterns'] = json.loads(kp['patterns']) if kp['patterns'] else []
                    except:
                        kp['keywords'] = []
                        kp['patterns'] = []
                    results.append(kp)
                
                self._update_stats(True)
                return results
                
        except Exception as e:
            logger.error(f"搜索知识点失败: {e}")
            self._update_stats(False)
            return []
    
    # ========================================
    # 题目数据管理
    # ========================================
    
    def save_question(self, question: Dict[str, Any]) -> bool:
        """保存题目数据"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 准备数据
                data = {
                    'question_id': question.get('question_id', str(uuid.uuid4())),
                    'number': question.get('number', ''),
                    'stem': question.get('stem', ''),
                    'answer': question.get('answer', ''),
                    'correct_answer': question.get('correct_answer', ''),
                    'type': question.get('type', ''),
                    'subject': question.get('subject', ''),
                    'difficulty_level': question.get('difficulty_level', 1),
                    'timestamp': question.get('timestamp', int(time.time())),
                    'source': question.get('source', ''),
                    'options': json.dumps(question.get('options', {}), ensure_ascii=False),
                    'updated_at': datetime.utcnow().isoformat()
                }
                
                # 插入或更新
                cursor.execute('''
                    INSERT OR REPLACE INTO questions (
                        question_id, number, stem, answer, correct_answer, type,
                        subject, difficulty_level, timestamp, source, options, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data['question_id'], data['number'], data['stem'], data['answer'],
                    data['correct_answer'], data['type'], data['subject'],
                    data['difficulty_level'], data['timestamp'], data['source'],
                    data['options'], data['updated_at']
                ))
                
                conn.commit()
                self._update_stats(True)
                return True
                
        except Exception as e:
            logger.error(f"保存题目失败: {e}")
            self._update_stats(False)
            return False
    
    def get_questions(self, subject: str = None, question_type: str = None,
                     difficulty: int = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """获取题目列表"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 构建查询
                sql = "SELECT * FROM questions WHERE 1=1"
                params = []
                
                if subject:
                    sql += " AND subject = ?"
                    params.append(subject)
                
                if question_type:
                    sql += " AND type = ?"
                    params.append(question_type)
                
                if difficulty:
                    sql += " AND difficulty_level = ?"
                    params.append(difficulty)
                
                sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                
                # 转换为字典列表
                results = []
                for row in rows:
                    question = dict(row)
                    # 解析JSON字段
                    try:
                        question['options'] = json.loads(question['options']) if question['options'] else {}
                    except:
                        question['options'] = {}
                    results.append(question)
                
                self._update_stats(True)
                return results
                
        except Exception as e:
            logger.error(f"获取题目失败: {e}")
            self._update_stats(False)
            return []
    
    def associate_question_knowledge_points(self, question_id: str, 
                                          knowledge_point_ids: List[str],
                                          relevance_scores: List[float] = None) -> bool:
        """关联题目和知识点"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 删除现有关联
                cursor.execute(
                    "DELETE FROM question_knowledge_points WHERE question_id = ?",
                    (question_id,)
                )
                
                # 插入新关联
                for i, kp_id in enumerate(knowledge_point_ids):
                    relevance = relevance_scores[i] if relevance_scores and i < len(relevance_scores) else 1.0
                    cursor.execute('''
                        INSERT INTO question_knowledge_points 
                        (question_id, knowledge_point_id, relevance_score)
                        VALUES (?, ?, ?)
                    ''', (question_id, kp_id, relevance))
                
                conn.commit()
                self._update_stats(True)
                return True
                
        except Exception as e:
            logger.error(f"关联题目知识点失败: {e}")
            self._update_stats(False)
            return False
    
    # ========================================
    # 批改记录管理
    # ========================================
    
    def save_grading_record(self, record: Dict[str, Any]) -> bool:
        """保存批改记录"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                data = {
                    'record_id': record.get('record_id', str(uuid.uuid4())),
                    'task_id': record.get('task_id', ''),
                    'question_id': record.get('question_id', ''),
                    'user_id': record.get('user_id', ''),
                    'is_correct': record.get('is_correct', False),
                    'score': record.get('score', 0.0),
                    'explanation': record.get('explanation', ''),
                    'grading_method': record.get('grading_method', ''),
                    'confidence': record.get('confidence', 1.0),
                    'processing_time_ms': record.get('processing_time_ms', 0.0)
                }
                
                cursor.execute('''
                    INSERT OR REPLACE INTO grading_records (
                        record_id, task_id, question_id, user_id, is_correct,
                        score, explanation, grading_method, confidence, processing_time_ms
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data['record_id'], data['task_id'], data['question_id'],
                    data['user_id'], data['is_correct'], data['score'],
                    data['explanation'], data['grading_method'], 
                    data['confidence'], data['processing_time_ms']
                ))
                
                conn.commit()
                self._update_stats(True)
                return True
                
        except Exception as e:
            logger.error(f"保存批改记录失败: {e}")
            self._update_stats(False)
            return False
    
    def get_grading_records(self, task_id: str = None, user_id: str = None,
                           limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """获取批改记录"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                sql = "SELECT * FROM grading_records WHERE 1=1"
                params = []
                
                if task_id:
                    sql += " AND task_id = ?"
                    params.append(task_id)
                
                if user_id:
                    sql += " AND user_id = ?"
                    params.append(user_id)
                
                sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                
                results = [dict(row) for row in rows]
                self._update_stats(True)
                return results
                
        except Exception as e:
            logger.error(f"获取批改记录失败: {e}")
            self._update_stats(False)
            return []
    
    # ========================================
    # 数据导入导出
    # ========================================
    
    def import_data_from_json(self, file_path: str, data_type: str = 'auto') -> Dict[str, Any]:
        """从JSON文件导入数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            results = {
                'total_records': 0,
                'successful_imports': 0,
                'failed_imports': 0,
                'errors': []
            }
            
            if data_type == 'auto':
                # 自动检测数据类型
                if isinstance(data, list) and data:
                    sample = data[0]
                    if 'knowledge_point_id' in sample or 'name' in sample:
                        data_type = 'knowledge_points'
                    elif 'question_id' in sample or 'stem' in sample:
                        data_type = 'questions'
                    else:
                        data_type = 'unknown'
            
            if data_type == 'knowledge_points':
                results['total_records'] = len(data)
                for item in data:
                    if self.save_knowledge_point(item):
                        results['successful_imports'] += 1
                    else:
                        results['failed_imports'] += 1
                        results['errors'].append(f"导入知识点失败: {item.get('name', 'Unknown')}")
            
            elif data_type == 'questions':
                results['total_records'] = len(data)
                for item in data:
                    if self.save_question(item):
                        results['successful_imports'] += 1
                    else:
                        results['failed_imports'] += 1
                        results['errors'].append(f"导入题目失败: {item.get('question_id', 'Unknown')}")
            
            logger.info(f"数据导入完成: {results['successful_imports']}/{results['total_records']}")
            return results
            
        except Exception as e:
            logger.error(f"数据导入失败: {e}")
            return {
                'total_records': 0,
                'successful_imports': 0,
                'failed_imports': 0,
                'errors': [str(e)]
            }
    
    def export_data_to_json(self, file_path: str, data_type: str, **filters) -> bool:
        """导出数据到JSON文件"""
        try:
            if data_type == 'knowledge_points':
                data = self.get_knowledge_points(**filters)
            elif data_type == 'questions':
                data = self.get_questions(**filters)
            elif data_type == 'grading_records':
                data = self.get_grading_records(**filters)
            else:
                logger.error(f"不支持的数据类型: {data_type}")
                return False
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"数据导出完成: {len(data)} 条记录 -> {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"数据导出失败: {e}")
            return False
    
    # ========================================
    # 数据备份恢复
    # ========================================
    
    def create_backup(self, backup_name: str = None) -> str:
        """创建数据备份"""
        try:
            if not backup_name:
                backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            
            backup_path = os.path.join(self.backup_dir, backup_name)
            shutil.copy2(self.db_path, backup_path)
            
            self.stats['last_backup'] = datetime.utcnow().isoformat()
            logger.info(f"数据备份创建成功: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"创建备份失败: {e}")
            return ""
    
    def restore_backup(self, backup_path: str) -> bool:
        """恢复数据备份"""
        try:
            if not os.path.exists(backup_path):
                logger.error(f"备份文件不存在: {backup_path}")
                return False
            
            # 创建当前数据的备份
            current_backup = self.create_backup("pre_restore_backup.db")
            
            # 恢复备份
            shutil.copy2(backup_path, self.db_path)
            
            logger.info(f"数据恢复成功: {backup_path}")
            logger.info(f"原数据已备份到: {current_backup}")
            return True
            
        except Exception as e:
            logger.error(f"恢复备份失败: {e}")
            return False
    
    # ========================================
    # 统计和监控
    # ========================================
    
    def get_database_statistics(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                stats = {
                    'database_info': {
                        'db_path': self.db_path,
                        'db_size_mb': round(os.path.getsize(self.db_path) / (1024 * 1024), 2),
                        'last_modified': datetime.fromtimestamp(
                            os.path.getmtime(self.db_path)
                        ).isoformat()
                    },
                    'table_counts': {},
                    'operation_stats': self.stats.copy()
                }
                
                # 获取各表记录数
                tables = ['knowledge_points', 'questions', 'question_knowledge_points', 
                         'grading_records', 'learning_records']
                
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    stats['table_counts'][table] = count
                
                # 获取一些统计信息
                cursor.execute('''
                    SELECT subject, COUNT(*) 
                    FROM knowledge_points 
                    GROUP BY subject
                ''')
                stats['knowledge_points_by_subject'] = dict(cursor.fetchall())
                
                cursor.execute('''
                    SELECT type, COUNT(*) 
                    FROM questions 
                    GROUP BY type
                ''')
                stats['questions_by_type'] = dict(cursor.fetchall())
                
                self._update_stats(True)
                return stats
                
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            self._update_stats(False)
            return {}
    
    def cleanup_old_records(self, days: int = 30) -> int:
        """清理旧记录"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 清理旧的批改记录
                cursor.execute('''
                    DELETE FROM grading_records 
                    WHERE created_at < ?
                ''', (cutoff_date.isoformat(),))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"清理完成: 删除了 {deleted_count} 条旧记录")
                self._update_stats(True)
                return deleted_count
                
        except Exception as e:
            logger.error(f"清理旧记录失败: {e}")
            self._update_stats(False)
            return 0
    
    def validate_data_integrity(self) -> Dict[str, Any]:
        """验证数据完整性"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                validation_results = {
                    'total_checks': 0,
                    'passed_checks': 0,
                    'failed_checks': 0,
                    'issues': []
                }
                
                # 检查孤立的关联记录
                cursor.execute('''
                    SELECT COUNT(*) FROM question_knowledge_points qkp
                    LEFT JOIN questions q ON qkp.question_id = q.question_id
                    WHERE q.question_id IS NULL
                ''')
                orphaned_associations = cursor.fetchone()[0]
                validation_results['total_checks'] += 1
                if orphaned_associations > 0:
                    validation_results['failed_checks'] += 1
                    validation_results['issues'].append(
                        f"发现 {orphaned_associations} 个孤立的题目-知识点关联"
                    )
                else:
                    validation_results['passed_checks'] += 1
                
                # 检查缺少关联的题目
                cursor.execute('''
                    SELECT COUNT(*) FROM questions q
                    LEFT JOIN question_knowledge_points qkp ON q.question_id = qkp.question_id
                    WHERE qkp.question_id IS NULL
                ''')
                unlinked_questions = cursor.fetchone()[0]
                validation_results['total_checks'] += 1
                if unlinked_questions > 0:
                    validation_results['issues'].append(
                        f"发现 {unlinked_questions} 个未关联知识点的题目"
                    )
                    validation_results['failed_checks'] += 1
                else:
                    validation_results['passed_checks'] += 1
                
                # 检查重复数据
                cursor.execute('''
                    SELECT question_id, COUNT(*) 
                    FROM questions 
                    GROUP BY question_id 
                    HAVING COUNT(*) > 1
                ''')
                duplicate_questions = cursor.fetchall()
                validation_results['total_checks'] += 1
                if duplicate_questions:
                    validation_results['failed_checks'] += 1
                    validation_results['issues'].append(
                        f"发现 {len(duplicate_questions)} 个重复的题目ID"
                    )
                else:
                    validation_results['passed_checks'] += 1
                
                logger.info(f"数据完整性检查完成: {validation_results['passed_checks']}/{validation_results['total_checks']} 通过")
                return validation_results
                
        except Exception as e:
            logger.error(f"数据完整性验证失败: {e}")
            return {
                'total_checks': 0,
                'passed_checks': 0,
                'failed_checks': 1,
                'issues': [str(e)]
            }

def test_data_storage_service():
    """测试数据存储服务"""
    print("🧪 测试数据存储服务...")
    
    # 创建服务实例
    service = DataStorageService()
    
    # 测试知识点操作
    test_kp = {
        'id': 'test_kp_001',
        'name': '测试知识点',
        'subject': 'math',
        'difficulty_level': 2,
        'keywords': ['测试', '知识点'],
        'description': '这是一个测试知识点'
    }
    
    print("📝 测试保存知识点...")
    if service.save_knowledge_point(test_kp):
        print("✅ 知识点保存成功")
    else:
        print("❌ 知识点保存失败")
    
    print("🔍 测试查询知识点...")
    kps = service.get_knowledge_points(subject='math', limit=5)
    print(f"✅ 查询到 {len(kps)} 个数学知识点")
    
    # 测试题目操作
    test_question = {
        'question_id': 'test_q_001',
        'stem': '测试题目内容',
        'answer': '测试答案',
        'type': 'choice',
        'subject': 'math',
        'difficulty_level': 2
    }
    
    print("📝 测试保存题目...")
    if service.save_question(test_question):
        print("✅ 题目保存成功")
    else:
        print("❌ 题目保存失败")
    
    # 测试关联
    print("🔗 测试关联题目和知识点...")
    if service.associate_question_knowledge_points('test_q_001', ['test_kp_001']):
        print("✅ 关联创建成功")
    else:
        print("❌ 关联创建失败")
    
    # 测试统计
    print("📊 测试统计信息...")
    stats = service.get_database_statistics()
    print(f"✅ 数据库大小: {stats.get('database_info', {}).get('db_size_mb', 0)} MB")
    print(f"✅ 知识点数量: {stats.get('table_counts', {}).get('knowledge_points', 0)}")
    print(f"✅ 题目数量: {stats.get('table_counts', {}).get('questions', 0)}")
    
    print("🎯 数据存储服务测试完成！")

if __name__ == "__main__":
    test_data_storage_service()
