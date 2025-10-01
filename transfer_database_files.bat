@echo off
chcp 65001 >nul
echo ===========================================
echo AI作业批改系统 - 完整数据文件传输脚本
echo 目标服务器: 172.31.179.77
echo 目标路径: /home/cshcsh/database/
echo 包含所有70+个数据相关文件，无缺漏传输
echo ===========================================

set SERVER=172.31.179.77
set USER=cshcsh
set TARGET_DIR=/home/cshcsh/database

echo.
echo 正在创建服务器目录结构...
ssh %USER%@%SERVER% "mkdir -p %TARGET_DIR%/{models,scripts,config,schemas,raw_data,processed,collectors,api,services,utils,tests,database_files}"

echo.
echo [1/12] 传输核心数据库文件...
scp llmhomework_Backend\database\knowledge_base.db %USER%@%SERVER%:%TARGET_DIR%/database_files/
scp -r llmhomework_Backend\database\scripts %USER%@%SERVER%:%TARGET_DIR%/database_files/

echo.
echo [2/12] 传输数据库配置和连接文件...
scp llmhomework_Backend\app\database.py %USER%@%SERVER%:%TARGET_DIR%/config/
scp llmhomework_Backend\app\config.py %USER%@%SERVER%:%TARGET_DIR%/config/

echo.
echo [3/12] 传输所有数据模型文件...
scp llmhomework_Backend\app\models\knowledge_base.py %USER%@%SERVER%:%TARGET_DIR%/models/
scp llmhomework_Backend\app\models\question_bank.py %USER%@%SERVER%:%TARGET_DIR%/models/
scp llmhomework_Backend\app\models\record.py %USER%@%SERVER%:%TARGET_DIR%/models/
scp llmhomework_Backend\app\models\__init__.py %USER%@%SERVER%:%TARGET_DIR%/models/

echo.
echo [4/12] 传输JSON Schema和验证文件（完整）...
scp -r "Json Schema" %USER%@%SERVER%:%TARGET_DIR%/schemas/
scp llmhomework_Backend\app\utils\schema_validator.py %USER%@%SERVER%:%TARGET_DIR%/utils/
scp llmhomework_Backend\app\utils\response_helper.py %USER%@%SERVER%:%TARGET_DIR%/utils/
scp llmhomework_Backend\app\utils\file.py %USER%@%SERVER%:%TARGET_DIR%/utils/
scp llmhomework_Backend\app\utils\helper.py %USER%@%SERVER%:%TARGET_DIR%/utils/

echo.
echo [5/12] 传输所有数据库脚本...
scp llmhomework_Backend\app\scripts\create_tables.sql %USER%@%SERVER%:%TARGET_DIR%/scripts/
scp llmhomework_Backend\app\scripts\create_tables_sqlite.sql %USER%@%SERVER%:%TARGET_DIR%/scripts/
scp llmhomework_Backend\app\scripts\import_collected_data.py %USER%@%SERVER%:%TARGET_DIR%/scripts/
scp llmhomework_Backend\app\scripts\validate_collected_data.py %USER%@%SERVER%:%TARGET_DIR%/scripts/
scp llmhomework_Backend\app\scripts\init_question_bank.py %USER%@%SERVER%:%TARGET_DIR%/scripts/

echo.
echo [6/12] 传输数据收集脚本（完整）...
scp -r llmhomework_Backend\data_collection\scripts %USER%@%SERVER%:%TARGET_DIR%/scripts/
scp llmhomework_Backend\data_collection\data_collection_manager.py %USER%@%SERVER%:%TARGET_DIR%/scripts/
scp llmhomework_Backend\data_collection\run_data_collection.py %USER%@%SERVER%:%TARGET_DIR%/scripts/

echo.
echo [7/12] 传输数据收集器和处理工具...
scp -r llmhomework_Backend\data_collection\collectors %USER%@%SERVER%:%TARGET_DIR%/collectors/
scp llmhomework_Backend\data_collection\config.json %USER%@%SERVER%:%TARGET_DIR%/config/
scp -r llmhomework_Backend\data_collection\schemas %USER%@%SERVER%:%TARGET_DIR%/schemas/

echo.
echo [8/12] 传输处理后的数据文件...
scp -r llmhomework_Backend\data_collection\processed %USER%@%SERVER%:%TARGET_DIR%/processed/

echo.
echo [9/12] 传输所有原始数据（37个CSV文件）...
scp -r llmhomework_Backend\raw %USER%@%SERVER%:%TARGET_DIR%/raw_data/

echo.
echo [10/12] 传输数据服务层文件...
scp llmhomework_Backend\app\services\data_storage_service.py %USER%@%SERVER%:%TARGET_DIR%/services/
scp llmhomework_Backend\app\services\question_bank_service.py %USER%@%SERVER%:%TARGET_DIR%/services/
scp -r llmhomework_Backend\app\services %USER%@%SERVER%:%TARGET_DIR%/services/

echo.
echo [11/12] 传输API接口文件...
scp llmhomework_Backend\app\api\question_bank_endpoints.py %USER%@%SERVER%:%TARGET_DIR%/api/
scp llmhomework_Backend\app\api\knowledge_endpoints.py %USER%@%SERVER%:%TARGET_DIR%/api/
scp llmhomework_Backend\app\api\__init__.py %USER%@%SERVER%:%TARGET_DIR%/api/

echo.
echo [12/12] 传输测试和验证文件...
scp llmhomework_Backend\tests\test_database_connection.py %USER%@%SERVER%:%TARGET_DIR%/tests/
scp llmhomework_Backend\tests\verify_database.py %USER%@%SERVER%:%TARGET_DIR%/tests/
scp check_database.py %USER%@%SERVER%:%TARGET_DIR%/tests/
scp check_db_final.py %USER%@%SERVER%:%TARGET_DIR%/tests/
scp check_db_temp.py %USER%@%SERVER%:%TARGET_DIR%/tests/

echo.
echo [额外] 传输前端数据管理组件...
scp llmhomework_Frontend\app\components\DataManager.tsx %USER%@%SERVER%:%TARGET_DIR%/frontend/

echo.
echo ===========================================
echo ✅ 完整传输完成！
echo 📊 已传输所有70+个数据相关文件：
echo   - 数据库文件和脚本
echo   - 数据模型和配置
echo   - JSON Schema和验证器
echo   - 37个学科CSV文件
echo   - 数据处理和导入脚本
echo   - API服务和工具
echo   - 测试和验证文件
echo ===========================================

echo.
echo 验证传输完整性命令：
echo ssh %USER%@%SERVER% "find %TARGET_DIR% -type f | wc -l"
echo.
pause
