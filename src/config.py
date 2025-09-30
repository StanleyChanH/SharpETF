"""
配置管理模块
处理项目配置参数和Tushare Token管理
"""

import json
import os
from typing import Dict, Any, List


class Config:
    """配置管理类"""
    
    def __init__(self, config_file: str = "config.json"):
        """
        初始化配置
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except FileNotFoundError:
            # 如果配置文件不存在，使用默认配置
            config = self._get_default_config()
            self._save_config(config)
        
        # 检查Tushare Token
        self._validate_tushare_token(config)
        
        return config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "tushare_token": "YOUR_TUSHARE_TOKEN",
            "etf_codes": ["510050.SH", "510300.SH", "510500.SH"],
            "start_date": "20200101",
            "end_date": "20231231",
            "risk_free_rate": 0.02,
            "trading_days": 252,
            "fields": "trade_date,close",
            "output_dir": "outputs"
        }
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """保存配置到文件"""
        os.makedirs(os.path.dirname(self.config_file) or '.', exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    
    def _validate_tushare_token(self, config: Dict[str, Any]) -> None:
        """验证Tushare Token"""
        token = config.get("tushare_token", "")
        
        # 首先检查环境变量
        env_token = os.getenv("TUSHARE_TOKEN")
        if env_token:
            config["tushare_token"] = env_token
            return
        
        # 检查配置文件中的Token
        if not token or token == "YOUR_TUSHARE_TOKEN":
            raise ValueError(
                "❌ Tushare Token未配置！\n"
                "请执行以下操作之一：\n"
                "1. 在config.json中设置tushare_token\n"
                "2. 设置环境变量 TUSHARE_TOKEN\n"
                "3. 访问 https://tushare.pro 注册获取Token\n"
                "⚠️ 注意：需要2000+积分才能使用fund_daily接口"
            )
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        self.config[key] = value
        self._save_config(self.config)
    
    @property
    def tushare_token(self) -> str:
        """获取Tushare Token"""
        return self.get("tushare_token")
    
    @property
    def etf_codes(self) -> List[str]:
        """获取ETF代码列表"""
        return self.get("etf_codes", [])
    
    @property
    def start_date(self) -> str:
        """获取开始日期"""
        return self.get("start_date")
    
    @property
    def end_date(self) -> str:
        """获取结束日期"""
        return self.get("end_date")
    
    @property
    def risk_free_rate(self) -> float:
        """获取无风险利率"""
        return self.get("risk_free_rate", 0.02)
    
    @property
    def trading_days(self) -> int:
        """获取年交易天数"""
        return self.get("trading_days", 252)
    
    @property
    def fields(self) -> str:
        """获取数据字段"""
        return self.get("fields", "trade_date,close")
    
    @property
    def output_dir(self) -> str:
        """获取输出目录"""
        return self.get("output_dir", "outputs")


# 全局配置实例
config = Config()


def get_config() -> Config:
    """获取全局配置实例"""
    return config