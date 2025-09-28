"""
AI作业批改系统 - 数据库配置和连接管理
支持题库管理和知识库功能
"""

import os
import logging
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from app.config import Config

logger = logging.getLogger(__name__)

# 全局数据库引擎和会话工厂
_engine = None
_SessionLocal = None


def init_database():
    """初始化数据库连接"""
    global _engine, _SessionLocal
    
    try:
        # 优先使用SQLite数据库
        database_url = getattr(Config, 'SQLITE_DATABASE_URL', None)
        if not database_url:
            # 默认SQLite数据库路径
            db_dir = os.path.join(os.path.dirname(__file__), '../database')
            os.makedirs(db_dir, exist_ok=True)
            database_url = f"sqlite:///{os.path.join(db_dir, 'knowledge_base.db')}"
        
        # 创建引擎
        if database_url.startswith('sqlite'):
            _engine = create_engine(
                database_url,
                echo=False,
                connect_args={
                    "check_same_thread": False,
                    "timeout": 30
                },
                poolclass=StaticPool,
                pool_reset_on_return=None
            )
            
            # SQLite优化设置
            @event.listens_for(_engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                # 启用外键约束
                cursor.execute("PRAGMA foreign_keys=ON")
                # 设置WAL模式提高并发性能
                cursor.execute("PRAGMA journal_mode=WAL")
                # 优化同步模式
                cursor.execute("PRAGMA synchronous=NORMAL")
                # 增加缓存大小
                cursor.execute("PRAGMA cache_size=10000")
                cursor.close()
        else:
            # MySQL或其他数据库
            _engine = create_engine(
                database_url,
                echo=False,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=3600
            )
        
        # 创建会话工厂
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=_engine
        )
        
        logger.info(f"数据库初始化成功: {database_url}")
        return True
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        raise


def get_engine():
    """获取数据库引擎"""
    if _engine is None:
        init_database()
    return _engine


def get_session() -> Session:
    """获取数据库会话"""
    if _SessionLocal is None:
        init_database()
    return _SessionLocal()


def create_tables():
    """创建所有数据库表"""
    try:
        from app.models.knowledge_base import Base
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建成功")
    except Exception as e:
        logger.error(f"创建数据库表失败: {str(e)}")
        raise


def check_database_connection():
    """检查数据库连接"""
    try:
        session = get_session()
        session.execute("SELECT 1")
        session.close()
        return True
    except Exception as e:
        logger.error(f"数据库连接检查失败: {str(e)}")
        return False


# 上下文管理器
class DatabaseSession:
    """数据库会话上下文管理器"""
    
    def __init__(self):
        self.session = None
    
    def __enter__(self) -> Session:
        self.session = get_session()
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            if exc_type is None:
                try:
                    self.session.commit()
                except Exception:
                    self.session.rollback()
                    raise
            else:
                self.session.rollback()
            self.session.close()


# 装饰器
def with_db_session(func):
    """数据库会话装饰器"""
    def wrapper(*args, **kwargs):
        with DatabaseSession() as session:
            return func(session, *args, **kwargs)
    return wrapper


# 初始化数据库（在模块加载时）
try:
    init_database()
except Exception as e:
    logger.warning(f"模块加载时数据库初始化失败: {str(e)}")
