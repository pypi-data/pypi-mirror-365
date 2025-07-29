#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TinyShare 新闻数据模块
处理 news、major_news、cctv_news 接口的权限验证和API调用
"""

import logging
from typing import Optional
import pandas as pd
import tushare as ts
from .token_utils import is_tiny_token

# 配置日志
logger = logging.getLogger(__name__)

class NewsApiWrapper:
    """新闻API包装器，根据token类型决定是否进行权限验证"""
    
    def __init__(self, auth_code: str):
        """
        初始化新闻API包装器
        
        Args:
            auth_code (str): 权限验证码或tushare token
        """
        self.auth_code = auth_code
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
                logger.info("使用tushare token直接初始化pro_api客户端")
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
                    self.auth_code, ['news']
                )
                
                if not has_permission:
                    raise PermissionError("权限不足，需要 'news' 权限")
                
                if not api_key:
                    raise RuntimeError("权限验证成功但未获取到API密钥")
                
                # 使用获取到的api_key初始化tushare客户端
                self.api_key = api_key
                self.tushare_pro = ts.pro_api(token=api_key)
                logger.info("使用tiny_token权限验证成功，已获取API密钥并初始化tushare客户端")
                
            except Exception as e:
                logger.error(f"权限验证或API密钥获取失败: {e}")
                raise
    
    def news(self, **kwargs) -> Optional[pd.DataFrame]:
        """
        获取新闻数据
        
        Args:
            **kwargs: 传递给tushare news接口的参数
            
        Returns:
            pd.DataFrame: 新闻数据
        """
        try:
            if self.tushare_pro is None:
                raise RuntimeError("tushare_pro客户端初始化失败")
            
            logger.info("调用tushare news接口")
            return self.tushare_pro.news(**kwargs)
        except Exception as e:
            logger.error(f"调用news接口失败: {e}")
            raise
    
    def major_news(self, **kwargs) -> Optional[pd.DataFrame]:
        """
        获取重大新闻数据
        
        Args:
            **kwargs: 传递给tushare major_news接口的参数
            
        Returns:
            pd.DataFrame: 重大新闻数据
        """
        try:
            if self.tushare_pro is None:
                raise RuntimeError("tushare_pro客户端初始化失败")
            
            logger.info("调用tushare major_news接口")
            return self.tushare_pro.major_news(**kwargs)
        except Exception as e:
            logger.error(f"调用major_news接口失败: {e}")
            raise
    
    def cctv_news(self, **kwargs) -> Optional[pd.DataFrame]:
        """
        获取央视新闻数据
        
        Args:
            **kwargs: 传递给tushare cctv_news接口的参数
            
        Returns:
            pd.DataFrame: 央视新闻数据
        """
        try:
            if self.tushare_pro is None:
                raise RuntimeError("tushare_pro客户端初始化失败")
            
            logger.info("调用tushare cctv_news接口")
            return self.tushare_pro.cctv_news(**kwargs)
        except Exception as e:
            logger.error(f"调用cctv_news接口失败: {e}")
            raise

    def news_ts(self, **kwargs) -> Optional[pd.DataFrame]:
        """
        获取新闻数据（_ts后缀接口，需要news_ts权限）
        
        Args:
            **kwargs: 传递给tushare news接口的参数
            
        Returns:
            pd.DataFrame: 新闻数据
        """
        try:
            # 验证_ts权限
            self._validate_ts_permission('news_ts')
            
            if self.tushare_pro is None:
                raise RuntimeError("tushare_pro客户端初始化失败")
            
            logger.info("调用tushare news接口（_ts后缀）")
            return self.tushare_pro.news(**kwargs)
        except Exception as e:
            logger.error(f"调用news_ts接口失败: {e}")
            raise
    
    def major_news_ts(self, **kwargs) -> Optional[pd.DataFrame]:
        """
        获取重大新闻数据（_ts后缀接口，需要major_news_ts权限）
        
        Args:
            **kwargs: 传递给tushare major_news接口的参数
            
        Returns:
            pd.DataFrame: 重大新闻数据
        """
        try:
            # 验证_ts权限
            self._validate_ts_permission('major_news_ts')
            
            if self.tushare_pro is None:
                raise RuntimeError("tushare_pro客户端初始化失败")
            
            logger.info("调用tushare major_news接口（_ts后缀）")
            return self.tushare_pro.major_news(**kwargs)
        except Exception as e:
            logger.error(f"调用major_news_ts接口失败: {e}")
            raise
    
    def cctv_news_ts(self, **kwargs) -> Optional[pd.DataFrame]:
        """
        获取央视新闻数据（_ts后缀接口，需要cctv_news_ts权限）
        
        Args:
            **kwargs: 传递给tushare cctv_news接口的参数
            
        Returns:
            pd.DataFrame: 央视新闻数据
        """
        try:
            # 验证_ts权限
            self._validate_ts_permission('cctv_news_ts')
            
            if self.tushare_pro is None:
                raise RuntimeError("tushare_pro客户端初始化失败")
            
            logger.info("调用tushare cctv_news接口（_ts后缀）")
            return self.tushare_pro.cctv_news(**kwargs)
        except Exception as e:
            logger.error(f"调用cctv_news_ts接口失败: {e}")
            raise

    def _validate_ts_permission(self, ts_interface_name: str):
        """
        验证_ts后缀接口的权限
        
        Args:
            ts_interface_name (str): _ts后缀的接口名称，如 'news_ts'
            
        Raises:
            PermissionError: 权限不足时抛出异常
        """
        if not self.is_tiny:
            # 如果不是tiny_token，则不需要验证_ts权限
            return
        
        from .common_permission import _common_permission_manager
        
        # _ts后缀接口需要对应的_ts权限
        required_permission = ts_interface_name  # 例如 news_ts
        
        try:
            # 验证权限（_ts后缀接口通常不需要API key，只需权限验证）
            has_permission, _ = _common_permission_manager.validate_permission_and_get_api_key(
                self.auth_code, [required_permission]
            )
            
            if not has_permission:
                raise PermissionError(f"权限不足，需要 '{required_permission}' 权限")
            
            logger.info(f"{ts_interface_name}接口权限验证通过")
            
        except PermissionError:
            # 权限错误直接抛出
            raise
        except Exception as e:
            logger.error(f"权限验证时发生错误: {e}")
            raise PermissionError(f"权限验证失败: {e}")

def create_news_api_wrapper(auth_code: str) -> NewsApiWrapper:
    """
    创建新闻API包装器
    
    Args:
        auth_code (str): 权限验证码或tushare token
        
    Returns:
        NewsApiWrapper: 新闻API包装器实例
    """
    return NewsApiWrapper(auth_code) 