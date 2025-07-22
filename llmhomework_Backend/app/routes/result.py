from flask import Blueprint, request, jsonify
from app.models.record import get_records

result_bp = Blueprint('result', __name__)

@result_bp.route('/get_results', methods=['GET'])
def get_results():
    user_id = request.args.get('user_id')
    task_id = request.args.get('task_id')
    records = get_records(user_id=user_id, task_id=task_id)
    # 可按需筛选、格式化返回
    return jsonify({'records': records})
