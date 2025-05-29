from flask import Flask, render_template
from flask_cors import CORS
from app.cores.config import config
from flask_socketio import SocketIO
from app.controllers.play_controller import play_bp, handle_action_socket
from app.controllers.auth_controller import auth_bp
from app.services.cert_service import cert_service
import logging
import sys
from app.cores.exceptions import ApiException
from app.models.response import ApiResponse
from app.services.auth_service import auth_service
import atexit
from app.services.play_service import play_service
import signal

app = Flask(__name__, template_folder='templates', static_folder='templates/assets', static_url_path='/assets')
debug = False

def int_env():
    """初始化环境"""
    if not debug:
        # 禁用 Flask 默认的日志处理器
        log = logging.getLogger('werkzeug')
        log.disabled = True
        
        # 禁用 Flask 的默认启动信息
        app.logger.disabled = True
        cli = sys.modules['flask.cli']
        cli.show_server_banner = lambda *x: None

def init_template():
    """初始化模板"""
    app.jinja_env.variable_start_string = '[['
    app.jinja_env.variable_end_string = ']]'
    app.jinja_env.block_start_string = '[%'
    app.jinja_env.block_end_string = '%]'
    
    # 允许所有跨域请求
    CORS(app, 
         resources=r"/*",  # 匹配所有路由
         origins="*",      # 允许所有来源
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # 允许所有方法
         allow_headers="*",  # 允许所有请求头
         supports_credentials=True)  # 支持认证信息

def init_socket():
    """初始化socket事件"""
    global socketio
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
   
    @socketio.on('connect')
    def handle_connect():
        print('客户端已连接服务端\n')
        auth_service.set_ws_status(True)
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print('客户端已断开服务端\n')
        auth_service.set_ws_status(False)
    
    @socketio.on('action')
    def handle_action_event(data):
        """处理动作事件"""
        handle_action_socket(data)

# 添加页路由处理
@app.route('/')
def index():
    return render_template('index.html')

# 处理所有其他前端路由
@app.route('/<path:path>')
def catch_all(path):
    return render_template('index.html')

# 注册全局异常处理
@app.errorhandler(ApiException)
def handle_api_exception(error):
    """处理API异常"""
    return ApiResponse(
        code=error.code,
        message=error.message,
        data=error.data
    ), error.code

@app.errorhandler(Exception)
def handle_exception(error):
    """处理未捕获的异常"""
    app.logger.error(f"未处理异常: {str(error)}", exc_info=True)
    return ApiResponse(
        code=500,
        message="客户端内部错误"
    ), 500

def init_exit_handler():
    def cleanup():
        """清理资源"""
        play_service.shutdown()
        auth_service.shutdown()

    def signal_handler(signum, frame):
        """信号处理函数"""
        cleanup()
        sys.exit(0)

    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # 终止信号

    if sys.platform == 'win32':
        signal.signal(signal.SIGBREAK, signal_handler)  # Windows Ctrl+Break
    
    # 注册 atexit 处理器
    atexit.register(cleanup)

def create_app():
    # 初始化环境
    int_env()

    # 初始化模板
    init_template()
 
    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(play_bp)
    
    # 初始化Socket
    init_socket()
    
    # 初始化退出处理
    init_exit_handler()

    # 启动应用
    socketio.run(
        app, 
        debug=debug,
        host='0.0.0.0',
        port=config.server['port'],
        log_output=debug,
        ssl_context=cert_service.init_ssl_cert(),
        allow_unsafe_werkzeug=True
    )

    return app
