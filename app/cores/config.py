import os
import yaml
from typing import Dict, Any

class Config:
    _instance = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """加载配置文件"""
        # 获取环境变量,默认为dev
        env = os.getenv('ENV', 'dev')
        
        # 基础配置路径
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        # 加载默认配置
        default_config = {}
        default_config_path = os.path.join(base_path, 'config.yaml')
        if os.path.exists(default_config_path):
            with open(default_config_path, 'r', encoding='utf-8') as f:
                default_config = yaml.safe_load(f)
        
        # 加载环境配置
        env_config = {}
        env_config_path = os.path.join(base_path, f'config-{env}.yaml')
        if os.path.exists(env_config_path):
            with open(env_config_path, 'r', encoding='utf-8') as f:
                env_config = yaml.safe_load(f)
                
        # 合并配置,环境配置覆盖默认配置
        self._config = self._merge_config(default_config, env_config)
    
    def _merge_config(self, default: dict, override: dict) -> dict:
        """递归合并配置"""
        result = default.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
                
        return result

    @property
    def api(self) -> Dict[str, Any]:
        return self._config.get('api', {})
    
    @property
    def auth(self) -> Dict[str, Any]:
        return self._config.get('auth', {})
    
    @property
    def server(self) -> Dict[str, Any]:
        return self._config.get('server', {})
    
    @property
    def input(self) -> Dict[str, Any]:
        return self._config.get('input', {})

# 创建全局配置实例
config = Config() 