#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TinyShare 通用API包装器模块
为所有需要权限验证的tushare pro接口提供统一的权限验证和API调用功能
"""

import logging
from typing import Optional, Dict, Any, List
import pandas as pd
import tushare as ts
from .common_permission import BaseApiWrapper
from .token_utils import is_tiny_token

# 配置日志
logger = logging.getLogger(__name__)

# 需要权限验证的接口列表（除了news、major_news、cctv_news）
PERMISSION_REQUIRED_INTERFACES = {
    # 基础数据
    'stock_basic': 'stock_basic',
    'trade_cal': 'trade_cal', 
    'namechange': 'namechange',
    'hs_const': 'hs_const',
    'stk_list': 'stk_list',
    'stk_managers': 'stk_managers',
    'stk_rewards': 'stk_rewards',
    
    # 行情数据
    'daily': 'daily',
    'weekly': 'weekly',  
    'monthly': 'monthly',
    'daily_basic': 'daily_basic',
    'adj_factor': 'adj_factor',
    'suspend_d': 'suspend_d',
    'daily_limit': 'daily_limit',
    'moneyflow': 'moneyflow',
    'stk_limit': 'stk_limit',
    'limit_list': 'limit_list',
    'moneyflow_hsgt': 'moneyflow_hsgt',
    'hsgt_top10': 'hsgt_top10',
    'ggt_top10': 'ggt_top10',
    'bak_daily': 'bak_daily',
    
    # 财务数据  
    'income': 'income',
    'balancesheet': 'balancesheet',
    'cashflow': 'cashflow',
    'forecast': 'forecast',
    'express': 'express',
    'dividend': 'dividend',
    'fina_indicator': 'fina_indicator',
    'fina_audit': 'fina_audit',
    'fina_mainbz': 'fina_mainbz',
    'disclosure_date': 'disclosure_date',
    
    # 市场参考数据
    'pledge_stat': 'pledge_stat',
    'pledge_detail': 'pledge_detail',
    'share_float': 'share_float',
    'block_trade': 'block_trade',
    'stk_holdernumber': 'stk_holdernumber',
    'stk_holdertrade': 'stk_holdertrade',
    'top10_holders': 'top10_holders',
    'top10_floatholders': 'top10_floatholders',
    'top_list': 'top_list',
    'top_inst': 'top_inst',
    'pledged_detail': 'pledged_detail',
    
    # 指数数据
    'index_basic': 'index_basic',
    'index_daily': 'index_daily',
    'index_weekly': 'index_weekly',
    'index_monthly': 'index_monthly',
    'index_weight': 'index_weight',
    'index_dailybasic': 'index_dailybasic',
    'index_classify': 'index_classify',
    'index_member': 'index_member',
    'daily_info': 'daily_info',
    'sz_daily_info': 'sz_daily_info',
    
    # 基金数据
    'fund_basic': 'fund_basic',
    'fund_company': 'fund_company',
    'fund_manager': 'fund_manager',
    'fund_share': 'fund_share',
    'fund_nav': 'fund_nav',
    'fund_div': 'fund_div',
    'fund_portfolio': 'fund_portfolio',
    'fund_daily': 'fund_daily',
    'fund_adj': 'fund_adj',
    
    # 期货数据
    'fut_basic': 'fut_basic',
    'fut_daily': 'fut_daily',
    'fut_holding': 'fut_holding',
    'fut_wsr': 'fut_wsr',
    'fut_settle': 'fut_settle',
    'fut_mapping': 'fut_mapping',
    
    # 期权数据
    'opt_basic': 'opt_basic',
    'opt_daily': 'opt_daily',
    'opt_settle': 'opt_settle',
    
    # 港股数据
    'hk_basic': 'hk_basic',
    'hk_daily': 'hk_daily',
    'hk_mins': 'hk_mins',
    'hk_hold': 'hk_hold',
    'hk_trade': 'hk_trade',
    
    # 美股数据
    'us_basic': 'us_basic',
    'us_daily': 'us_daily',
    'us_monthly': 'us_monthly',
    
    # 宏观数据
    'cn_gdp': 'cn_gdp',
    'cn_cpi': 'cn_cpi',
    'cn_ppi': 'cn_ppi',
    'cn_m': 'cn_m',
    'cn_r': 'cn_r',
    'shibor': 'shibor',
    'libor': 'libor',
    'hibor': 'hibor',
    'wz_index': 'wz_index',
    
    # 行业数据
    'sw_daily': 'sw_daily',
    'sw_index': 'sw_index',
    'ths_daily': 'ths_daily',
    'ths_index': 'ths_index',
    'ths_member': 'ths_member',
    
    # 债券数据
    'cb_basic': 'cb_basic',
    'cb_price': 'cb_price',
    'cb_daily': 'cb_daily',
    'cb_share': 'cb_share',
    
    # 外汇数据
    'fx_oday': 'fx_oday',
    'fx_daily': 'fx_daily',
    
    # 特色数据
    'stk_mins': 'stk_mins',
    'concept': 'concept',
    'concept_detail': 'concept_detail',
    'share_float': 'share_float',
    'bak_basic': 'bak_basic',
    'profit_data': 'profit_data',
    'operation_data': 'operation_data',
    'growth_data': 'growth_data',
    'debtpaying_data': 'debtpaying_data',
    'cashflow_data': 'cashflow_data',
}

class GeneralApiWrapper:
    """通用API包装器，根据token类型决定是否进行权限验证"""
    
    def __init__(self, auth_code: str, interface_name: str):
        """
        初始化通用API包装器
        
        Args:
            auth_code (str): 权限验证码或tushare token
            interface_name (str): 接口名称，用于权限验证
        """
        self.auth_code = auth_code
        self.interface_name = interface_name
        self.is_tiny = is_tiny_token(auth_code)
        self.tushare_pro = None
        self.api_key = None
        
        if self.is_tiny:
            # 如果是tiny_token，需要进行权限验证获取api_key
            self._ensure_permission_and_api_key()
        else:
            # 如果是普通tushare token，直接使用
            try:
                self.tushare_pro = ts.pro_api(token=auth_code)
                logger.info(f"使用tushare token直接初始化pro_api客户端用于{interface_name}接口")
            except Exception as e:
                logger.error(f"初始化tushare pro_api客户端失败: {e}")
                raise
    
    def _ensure_permission_and_api_key(self):
        """确保权限验证和API密钥获取（仅对tiny_token）"""
        if not self.is_tiny:
            return
            
        if self.tushare_pro is None:
            try:
                from .common_permission import _common_permission_manager
                
                # 验证权限并获取api_key
                has_permission, api_key = _common_permission_manager.validate_permission_and_get_api_key(
                    self.auth_code, [self.interface_name]
                )
                
                if not has_permission:
                    raise PermissionError(f"权限不足，需要 '{self.interface_name}' 权限")
                
                if not api_key:
                    raise RuntimeError("权限验证成功但未获取到API密钥")
                
                # 使用获取到的api_key初始化tushare客户端
                self.api_key = api_key
                self.tushare_pro = ts.pro_api(token=api_key)
                logger.info(f"使用tiny_token权限验证成功，已获取API密钥并初始化tushare客户端用于{self.interface_name}接口")
                
            except Exception as e:
                logger.error(f"权限验证或API密钥获取失败: {e}")
                raise
    
    def call_interface(self, **kwargs) -> Optional[pd.DataFrame]:
        """
        通用接口调用方法
        
        Args:
            **kwargs: 传递给tushare接口的参数
            
        Returns:
            pd.DataFrame: 接口返回的数据
        """
        try:
            if self.tushare_pro is None:
                raise RuntimeError("tushare_pro客户端初始化失败")
            
            logger.info(f"调用tushare {self.interface_name}接口")
            # 通过getattr动态调用对应的接口方法
            interface_method = getattr(self.tushare_pro, self.interface_name)
            return interface_method(**kwargs)
        except Exception as e:
            logger.error(f"调用{self.interface_name}接口失败: {e}")
            raise


class EnhancedProApiWrapper:
    """
    增强的 TuShare Pro API 包装器
    为所有需要权限验证的接口提供统一的权限验证和调用
    """
    
    def __init__(self, client, token):
        self._client = client
        self._token = token
        self._api_wrappers = {}  # 缓存API包装器实例
        self._news_wrapper = None
    
    def _get_api_wrapper(self, interface_name: str) -> GeneralApiWrapper:
        """获取或创建API包装器实例"""
        if interface_name not in self._api_wrappers:
            self._api_wrappers[interface_name] = GeneralApiWrapper(self._token, interface_name)
        return self._api_wrappers[interface_name]
    
    def _get_news_wrapper(self):
        """获取新闻API包装器"""
        if self._news_wrapper is None:
            from .news_data import create_news_api_wrapper
            self._news_wrapper = create_news_api_wrapper(self._token)
        return self._news_wrapper
    
    def news(self, **kwargs):
        """获取新闻数据（需要权限验证）"""
        try:
            return self._get_news_wrapper().news(**kwargs)
        except Exception as e:
            logger.error(f"调用news接口失败: {e}")
            raise
    
    def major_news(self, **kwargs):
        """获取重大新闻数据（需要权限验证）"""
        try:
            return self._get_news_wrapper().major_news(**kwargs)
        except Exception as e:
            logger.error(f"调用major_news接口失败: {e}")
            raise
    
    def cctv_news(self, **kwargs):
        """获取央视新闻数据（需要权限验证）"""
        try:
            return self._get_news_wrapper().cctv_news(**kwargs)
        except Exception as e:
            logger.error(f"调用cctv_news接口失败: {e}")
            raise
    
    def __getattr__(self, name):
        """
        代理方法到原始的tushare客户端或权限验证包装器
        """
        # 如果是需要权限验证的接口
        if name in PERMISSION_REQUIRED_INTERFACES:
            def wrapper(**kwargs):
                api_wrapper = self._get_api_wrapper(name)
                return api_wrapper.call_interface(**kwargs)
            return wrapper
        
        # 其他接口直接代理到原始客户端
        return getattr(self._client, name)


def create_enhanced_pro_api_wrapper(client, token: str) -> EnhancedProApiWrapper:
    """
    创建增强的Pro API包装器
    
    Args:
        client: 原始的tushare pro客户端
        token (str): 权限验证码或tushare token
        
    Returns:
        EnhancedProApiWrapper: 增强的API包装器实例
    """
    return EnhancedProApiWrapper(client, token) 