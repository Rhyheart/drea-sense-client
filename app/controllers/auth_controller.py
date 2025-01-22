from flask import Blueprint, request
from app.models.response import ApiResponse
from app.services.auth_service import auth_service

auth_bp = Blueprint('auth', __name__, url_prefix='/api')

@auth_bp.route('/login', methods=['POST'])
def login():
    """登录接口"""
    return ApiResponse(auth_service.handle_login_request(request.json))

@auth_bp.route('/config')
def get_config():
    """获取配置信息"""
    return ApiResponse(auth_service.handle_config_request())

@auth_bp.route('/ping', methods=['GET'])
def ping():
    """ping接口"""
    auth_service.handle_ping_request()
    return ApiResponse()

@auth_bp.route('/auth/status', methods=['GET'])
def get_status():
    """获取状态信息"""
    return ApiResponse(auth_service.handle_status_request())

@auth_bp.route('/auth/logout', methods=['POST'])
def logout():
    """退出登录"""
    auth_service.handle_logout_request()
    return ApiResponse()