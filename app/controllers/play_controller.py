from flask import Blueprint, request
from flask_socketio import emit
from app.models.response import ApiResponse
from app.models.action import Action
from app.services.play_service import play_service

play_bp = Blueprint('play', __name__, url_prefix='/api/play')

@play_bp.route('/action', methods=['POST'])
def handle_action_api():
    """处理动作接口"""
    return handle_action(request.json)

def handle_action_socket(data):
    """处理Socket动作事件"""
    emit('action_result', handle_action(data)) 

def handle_action(data):
    """处理动作"""
    action = data.get('action')
    action = Action(**action)
    play_service.processActionSync(action)
    return ApiResponse({'last_action': play_service.last_action})