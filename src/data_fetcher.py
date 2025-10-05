"""
数据获取模块
使用Tushare fund_daily接口获取ETF历史数据
"""

import tushare as ts
import pandas as pd
import time
from typing import List, Dict, Optional
import logging

from .config import get_config


logger = logging.getLogger(__name__)


class DataFetcher:
    """数据获取类"""
    
    def __init__(self):
        """初始化数据获取器"""
        self.config = get_config()
        self.pro = self._init_tushare()
        self.etf_names_cache = {}  # ETF名称缓存
        
    def _init_tushare(self) -> ts.pro_api:
        """初始化Tushare API"""
        try:
            pro = ts.pro_api(self.config.tushare_token)
            # 测试连接
            pro.query('trade_cal', start_date='20230101', end_date='20230101')
            logger.info("Tushare API连接成功")
            return pro
        except Exception as e:
            logger.error(f"❌ Tushare API连接失败: {e}")
            raise
    
    def validate_etf_codes(self, etf_codes: List[str]) -> List[str]:
        """
        验证ETF代码格式
        
        Args:
            etf_codes: ETF代码列表
            
        Returns:
            有效的ETF代码列表
        """
        valid_codes = []
        for code in etf_codes:
            if self._is_valid_etf_code(code):
                valid_codes.append(code)
            else:
                logger.warning(f"⚠️ 跳过无效的ETF代码: {code}")
        
        if not valid_codes:
            raise ValueError("❌ 没有有效的ETF代码！")
        
        return valid_codes
    
    def _is_valid_etf_code(self, code: str) -> bool:
        """检查ETF代码格式是否有效"""
        # 基本格式检查：数字.SH 或 数字.SZ
        if not isinstance(code, str):
            return False
        
        parts = code.split('.')
        if len(parts) != 2:
            return False
        
        if not parts[0].isdigit():
            return False
        
        if parts[1] not in ['SH', 'SZ']:
            return False
        
        return True
    
    def fetch_etf_data(self, etf_codes: Optional[List[str]] = None, 
                      start_date: Optional[str] = None,
                      end_date: Optional[str] = None,
                      fields: Optional[str] = None) -> pd.DataFrame:
        """
        获取多只ETF的历史数据
        
        Args:
            etf_codes: ETF代码列表，默认为配置中的代码
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            fields: 字段列表
            
        Returns:
            合并后的数据DataFrame
        """
        # 使用配置中的默认值
        etf_codes = etf_codes or self.config.etf_codes
        start_date = start_date or self.config.start_date
        end_date = end_date or self.config.end_date
        fields = fields or self.config.fields
        
        # 验证ETF代码
        valid_codes = self.validate_etf_codes(etf_codes)
        
        logger.info(f"📊 开始获取ETF数据: {valid_codes}")
        logger.info(f"📅 时间范围: {start_date} 至 {end_date}")
        
        data_frames = []
        
        for code in valid_codes:
            try:
                df = self._fetch_single_etf(code, start_date, end_date, fields)
                if df is not None and not df.empty:
                    data_frames.append(df)
                    logger.info(f"✅ 成功获取 {code} 数据，共 {len(df)} 条记录")
                else:
                    logger.warning(f"⚠️ {code} 返回空数据")
                
                # 避免API调用频率限制
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"❌ 获取 {code} 数据失败: {e}")
                continue
        
        if not data_frames:
            raise ValueError("❌ 所有ETF数据获取失败！")
        
        # 合并数据
        combined_df = self._merge_data(data_frames)
        
        logger.info(f"✅ 数据获取完成，共 {len(combined_df)} 个交易日")
        return combined_df
    
    def _fetch_single_etf(self, etf_code: str, start_date: str, 
                         end_date: str, fields: str) -> Optional[pd.DataFrame]:
        """
        获取单只ETF的数据
        
        Args:
            etf_code: ETF代码
            start_date: 开始日期
            end_date: 结束日期
            fields: 字段列表
            
        Returns:
            ETF数据DataFrame
        """
        try:
            df = self.pro.fund_daily(
                ts_code=etf_code,
                start_date=start_date,
                end_date=end_date,
                fields=fields
            )
            
            if df is None or df.empty:
                return None
            
            # 按日期排序
            df = df.sort_values('trade_date')
            
            # 重命名列以避免合并时冲突
            df = df.rename(columns={'close': etf_code})
            
            return df
            
        except Exception as e:
            if "积分不足" in str(e):
                raise ValueError(
                    f"❌ Tushare积分不足！\n"
                    f"获取 {etf_code} 数据需要2000+积分\n"
                    f"请访问 https://tushare.pro 购买积分"
                )
            elif "接口权限" in str(e):
                raise ValueError(
                    f"❌ 接口权限不足！\n"
                    f"请检查fund_daily接口权限或联系Tushare客服"
                )
            else:
                raise
    
    def _merge_data(self, data_frames: List[pd.DataFrame]) -> pd.DataFrame:
        """
        合并多只ETF数据
        
        Args:
            data_frames: ETF数据列表
            
        Returns:
            合并后的DataFrame
        """
        if not data_frames:
            raise ValueError("没有数据可合并")
        
        # 使用第一个DataFrame作为基础
        combined_df = data_frames[0]
        
        # 逐个合并其他DataFrame
        for df in data_frames[1:]:
            combined_df = pd.merge(
                combined_df, 
                df[['trade_date', df.columns[-1]]],  # 只保留日期和价格列
                on='trade_date', 
                how='inner'
            )
        
        # 验证数据完整性
        self._validate_merged_data(combined_df)
        
        return combined_df
    
    def _validate_merged_data(self, df: pd.DataFrame) -> None:
        """
        验证合并后的数据
        
        Args:
            df: 合并后的DataFrame
        """
        if df.empty:
            raise ValueError("合并后的数据为空")
        
        # 检查缺失值
        missing_count = df.isnull().sum().sum()
        if missing_count > 0:
            logger.warning(f"⚠️ 数据中存在 {missing_count} 个缺失值")
            # 可以选择填充或删除，这里选择删除
            df.dropna(inplace=True)
            logger.info(f"✅ 已删除缺失值，剩余 {len(df)} 条记录")
        
        # 检查数据量是否足够
        if len(df) < 100:
            logger.warning("⚠️ 数据量较少，可能影响分析结果")
        
        # 检查日期连续性
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        date_diff = df['trade_date'].diff().dt.days
        if (date_diff > 10).any():
            logger.warning("⚠️ 数据中存在较大的日期间隔")

    def get_etf_names(self, etf_codes: List[str]) -> Dict[str, str]:
        """
        获取ETF中文名称列表

        Args:
            etf_codes: ETF代码列表

        Returns:
            ETF代码到中文名称的映射字典
        """
        etf_names = {}

        logger.info("📋 获取ETF中文名称...")

        for code in etf_codes:
            # 检查缓存
            if code in self.etf_names_cache:
                etf_names[code] = self.etf_names_cache[code]
                continue

            try:
                # 调用Tushare API获取ETF基本信息
                df = self.pro.fund_basic(ts_code=code)

                if not df.empty and 'name' in df.columns:
                    name = df.iloc[0]['name']
                    etf_names[code] = name
                    self.etf_names_cache[code] = name  # 缓存结果
                    logger.info(f"✅ {code}: {name}")
                else:
                    etf_names[code] = f"{code}(未知名称)"
                    logger.warning(f"⚠️ 无法获取 {code} 的名称信息")

                # 避免API调用频率限制
                time.sleep(0.1)

            except Exception as e:
                etf_names[code] = f"{code}(获取失败)"
                logger.error(f"❌ 获取 {code} 名称失败: {e}")

        logger.info(f"✅ 成功获取 {len([k for k, v in etf_names.items() if not '失败' in v and not '未知' in v])}/{len(etf_codes)} 个ETF名称")
        return etf_names

    def get_etf_name(self, etf_code: str) -> str:
        """
        获取单个ETF的中文名称

        Args:
            etf_code: ETF代码

        Returns:
            ETF中文名称
        """
        names = self.get_etf_names([etf_code])
        return names.get(etf_code, f"{etf_code}(未知)")


def get_data_fetcher() -> DataFetcher:
    """获取数据获取器实例"""
    return DataFetcher()