#!/usr/bin/env python3
"""测试优化后的爬虫"""

from collectors.legal_education_crawler import LegalEducationCrawler
import sqlite3

def test_crawler():
    print("🧪 测试优化后的爬虫...")

    try:
        crawler = LegalEducationCrawler()
        print("✅ 爬虫初始化完成")
        print(f"📁 输出目录: {crawler.output_dir}")
        print(f"💾 数据库: {crawler.db_path}")

        print("🌐 浏览器驱动: 已禁用 (需要时可启用)")

        # 测试数据库连接
        try:
            conn = sqlite3.connect(crawler.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM crawl_records')
            count = cursor.fetchone()[0]
            conn.close()
            print(f"📊 爬取记录数量: {count}")
        except Exception as e:
            print(f"⚠️ 数据库测试失败: {e}")

        print("\n🎉 爬虫测试完成!")

    except Exception as e:
        print(f"❌ 爬虫测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_crawler()
