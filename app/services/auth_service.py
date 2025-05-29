import requests
import socket
import threading
import time
from app.cores.config import config
import urllib3
from datetime import datetime
import base64
from Crypto.Cipher import AES
from app.cores.exceptions import AuthException, ValidationException

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AuthService:
    def __init__(self):
        # 初始化配置
        self.api_base_url = config.api['base_url']
        
        # 认证相关
        self.access_token = None
        self.refresh_token = None
        self.user = None  # 存储用户信息
        
        # 自动登录相关
        self.auto_login_thread = None
        self.auto_login_stop = False
        self.auto_login_failed = False  # 标记自动登录是否失败

        # 上报相关
        self.report_thread = None
        self.report_stop = False
        self.last_client_url = None  # 存储上次上报的客户端URL
        self.last_report_time = None

        # 状态相关
        self.client_status = "未连接"  # 客户端状态
        self.ws_connect_status = False  # WS连接状态
        self.last_heartbeat_time = None  # 最后一次心跳时间

        print("启动成功！\n")
        print("客户端地址：" + self._get_client_url()+"\n")

        self.start()
    
    def start(self):
        # 添加线程引用
        self.auto_login_thread = threading.Thread(
            target=self.auto_login_worker,
            daemon=True
        )
        self.report_thread = threading.Thread(
            target=self.report_worker,
            daemon=True
        )
        
        # 启动线程
        self.auto_login_thread.start()
        self.report_thread.start()

    def auto_login_worker(self):
        """自动登录工作线程"""
        while not self.auto_login_stop:  # 使用停止标志
            if not self.access_token:
                try:
                    if not self.auto_login_failed:
                        self.auto_login()
                    else:
                        # 自动登录失败，等待用户手动输入
                        time.sleep(1)
                except Exception as e:
                    print(f"自动登录失败: {str(e)}\n")
                    self.auto_login_failed = True
                    self.prompt_login()
                    time.sleep(5)
            time.sleep(10)

    def prompt_login(self):
        """提示用户输入账号密码"""
        while True:
            print("\n请输入账号密码 >>>\n")
            username = input("用户名: ").strip()
            password = input("密码: ").strip()
            print("\n")
            
            try:
                self.login(username, password)
                config.auth['username'] = username
                config.auth['password'] = password
                self.auto_login_failed = False
                break  # 登录成功，退出循环
            except Exception as e:
                print(f"登录失败: 用户名 或 密码 错误\n")
                self.auto_login_failed = True
                # 登录失败，继续循环，让用户重新输入

    def report_worker(self):
        """上报工作线程"""
        while not self.report_stop:  # 使用停止标志
            if self.access_token:
                self.report_client()
            time.sleep(5)

    # === 认证相关方法 ===
    def auto_login(self):
        """自动登录"""
        username = config.auth['username']
        password = config.auth['password']
        
        # 如果用户名是your_username或为空，不进行自动登录
        if not username or username == 'your_username':
            self.auto_login_failed = True
            self.prompt_login()
            return
            
        print("自动登录中...\n")
        self.login(username, password)
    
    def login(self, username: str, password: str) -> tuple[bool, dict]:
        """登录并获取token"""
        if not username or not password:
            raise ValidationException("用户名和密码不能为空")

        # 构造登录请求
        headers = {
            'Authorization': self._get_basic_auth(),
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'password',
            'username': username,
            'password': self._encrypt('front_encode_key', password)
        }
        
        response = requests.post(
            self._get_api_url('auth/oauth2/token'),
            headers=headers,
            data=data
        )
        
        data = response.json()
        
        if 'access_token' in data:
            self.access_token = data['access_token']
            self.refresh_token = data['refresh_token']
            # 获取用户信息
            userInfo = self.get_user_info()
            self.user = {
                'username': userInfo['sysUser']['username'],
                'nickname': userInfo['sysUser']['nickname'],
                'avatar': userInfo['sysUser']['avatar']
            }
            print(f"✓ 用户 {self.user.get('nickname') or self.user.get('username')} 登录成功\n")
            
            # 立即上报一次客户端信息
            self.report_client()
            return data
        
        raise AuthException(data.get('msg', '登录失败'))
    
    def logout(self):
        """退出登录"""
        if self.user:
            print(f"✓ 用户 {self.user.get('nickname') or self.user.get('username')} 退出登录\n")
        self.access_token = None
        self.refresh_token = None
        self.user = None
        self.last_client_url = None
        self.ws_connect_status = False
        self.last_heartbeat_time = None
        self.client_status = "未连接"

    def refresh_access_token(self) -> bool:
        """刷新访问令牌"""
        if not self.refresh_token:
            raise AuthException("刷新令牌不存在")

        headers = {
            'Authorization': self._get_basic_auth(),
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }
        
        response = requests.post(
            self._get_api_url('auth/oauth2/token'),
            headers=headers,
            data=data
        )
        
        data = response.json()
        
        if 'access_token' in data:
            self.access_token = data['access_token']
            self.refresh_token = data['refresh_token']
            print("✓ 令牌刷新成功\n")
            return True
        
        # 刷新失败，清理状态可重新登录
        self.shutdown()
        self.start()

        raise AuthException(data.get('msg', '令牌刷新失败'))

    def get_user_info(self) -> dict:
        """获取用户信息"""
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        
        response = requests.get(
            self._get_api_url('sys/user/me'),
            headers=headers
        )
        
        data = response.json()
        if data['code'] == 0 and data['success']:
            return data['data']
        raise AuthException("获取用户信息失败")

    # === 客户端信息上报相关方法 ===
    def report_client(self, client_url: str = None):
        """上报客户端信息"""
        if not self.access_token:
            return
            
        current_url = client_url or self._get_client_url()
        # 只有当URL发生变化时才上报
        if current_url != self.last_client_url:
            # 使用更新配置接口上报客户端地址
            if self.update_client_config(current_url):
                print(f"✓ 客户端地址：{current_url}\n")
                self.last_client_url = current_url
                self.last_report_time = datetime.now()
            else:
                # 如果更新失败，可能是token过期
                if self.refresh_access_token():
                    # 刷新token成功后重试
                    self.report_client(current_url)
    
    def update_client_config(self, client_url: str) -> bool:
        """更新客户端配置"""
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.put(
            self._get_api_url('ai-sense/config'),
            headers=headers,
            json={'clientUrl': client_url}
        )
        
        data = response.json()
        return data['code'] == 0 and data['success']
    
    # === 状态管理相关方法 ===
    def update_client_status(self):
        """更新客户端状态"""
        if self.ws_connect_status or (
            self.last_heartbeat_time and 
            (datetime.now() - self.last_heartbeat_time).seconds < 10  # 10秒内有动作就认为是连接状态
        ):
            self.client_status = "已连接"
        else:
            self.client_status = "未连接"
    
    def set_ws_status(self, connected: bool):
        """设置WS状态"""
        self.ws_connect_status = connected
        self.update_client_status()
    
    def set_heartbeat(self):
        """设置心跳"""
        self.last_heartbeat_time = datetime.now()
        self.update_client_status()
    
    # === 工具方法 ===
    def _encrypt(self, key: str, content: str) -> str:
        """使用AES-CFB模式加密密码，匹配Java hutool的AES实现"""
        # 使用密钥和IV
        key = key.encode('utf-8')
        # 确保key是16字节
        key = key[:16].ljust(16, b'\0')
        
        # 创建cipher对象，使用CFB模式
        cipher = AES.new(key, AES.MODE_CFB, iv=key, segment_size=128)
        
        # 加密（不需要padding，因为CFB模式不需要）
        encrypted = cipher.encrypt(content.encode('utf-8'))
        
        # Base64编码
        return base64.b64encode(encrypted).decode('utf-8')

    def _get_api_url(self, endpoint: str) -> str:
        """获取完整的API URL"""
        base = self.api_base_url.rstrip('/')
        return f"{base}/api/{endpoint.lstrip('/')}"
    
    def _get_basic_auth(self) -> str:
        """获取Basic认证头"""
        return "Basic Y2xpZW50OmNsaWVudA=="
    
    def _get_local_ip(self) -> str:
        """获取本机内网IP"""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            return ip
        finally:
            s.close()
        return "127.0.0.1"
    
    def _get_client_url(self) -> str:
        """获取客户端完整URL"""
        server_config = config.server
        return f"https://{self._get_local_ip()}:{server_config['port']}"

    # === 停止方法 ===
    def stop_auto_login(self):
        """停止自动登录线程"""
        self.auto_login_stop = True
        if self.auto_login_thread.is_alive():
            self.auto_login_thread.join(timeout=1)

    def stop_report(self):
        """停止上报线程"""
        self.report_stop = True
        if self.report_thread.is_alive():
            self.report_thread.join(timeout=1)

    def shutdown(self):
        """关闭服务时清理资源"""
        self.stop_auto_login()
        self.stop_report()
        self.logout()

    # === 新增 API 响应方法 ===
    def handle_login_request(self, data: dict) -> dict:
        """处理登录请求"""
        config.auth['username'] = data['username']  
        config.auth['password'] = data['password']
        self.auto_login()
        self.start()
        return {
            'client_url': self._get_client_url(),
            'api_url': config.api['base_url'],
            'client_status': self.client_status,
            'last_report_time': self.last_report_time,
            'user': self.user
        }

    def handle_config_request(self) -> dict:
        """处理获取配置请求"""
        return {
            'username': config.auth['username'],
            'password': config.auth['password']
        }

    def handle_ping_request(self) -> dict:
        """处理ping请求"""
        self.set_heartbeat()

    def handle_status_request(self) -> dict:
        """处理状态获取请求"""
        if not self.access_token:
            raise AuthException("未登录")
        self.update_client_status()
        return {
            'client_url': self._get_client_url(),
            'api_url': config.api['base_url'],
            'client_status': self.client_status,
            'last_report_time': self.last_report_time.isoformat() if self.last_report_time else None,
            'user': self.user
        }

    def handle_logout_request(self) -> dict:
        """处理退出登录请求"""
        self.shutdown()

auth_service = AuthService()