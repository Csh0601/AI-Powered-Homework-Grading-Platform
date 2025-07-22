from flask import Blueprint, request, jsonify
from app.services.question_gen import generate_question

generate_bp = Blueprint('generate', __name__)

@generate_bp.route('/generate_exercise', methods=['POST'])
def generate_exercise():
    data = request.get_json()
    knowledge = data.get('knowledge')
    use_gpt = data.get('use_gpt', False)
    if not knowledge:
        return jsonify({'error': 'Missing knowledge'}), 400
    question = generate_question(knowledge, use_gpt=use_gpt)
    return jsonify({'question': question})
