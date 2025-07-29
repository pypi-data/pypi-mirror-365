#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TinyShare 通用权限管理模块
提供统一的权限验证、API key管理等功能
"""

import requests
import json
import logging
from typing import Optional, Dict, List
import tushare as ts

# 配置日志
logger = logging.getLogger(__name__)

class CommonPermissionManager:
    """通用权限管理器，用于处理权限验证和API key管理"""
    
    def __init__(self):
        self.auth_api_url = "https://pro.swiftiny.com/api/auth/validate"
        # self.auth_api_url = "http://localhost:1337/api/auth/validate"
        self.api_key_cache = {}  # API key缓存
        self.permission_cache = {}  # 权限缓存
    
    def validate_permission_and_get_api_key(self, auth_code: str, required_permissions: List[str]) -> tuple[bool, Optional[str]]:
        """
        验证权限并获取API key
        
        Args:
            auth_code (str): 权限验证码
            required_permissions (List[str]): 需要的权限列表，如 ['news', 'major_news', 'cctv_news'] 或 ['stk_mins'] 或 ['news_ts']
            
        Returns:
            tuple[bool, Optional[str]]: (权限验证是否通过, API key或None)
        """
        if not auth_code:
            logger.error("权限验证码不能为空")
            return False, None
        
        # 检查缓存
        cache_key = f"{auth_code}_{'-'.join(required_permissions)}"
        if cache_key in self.api_key_cache:
            logger.info("使用缓存的API key")
            return True, self.api_key_cache[cache_key]
        
        # 对于_ts后缀权限或某些特定权限，只需权限验证不需要API key
        needs_only_permission = (
            len(required_permissions) == 1 and 
            (required_permissions[0] in ['stk_mins'] or required_permissions[0].endswith('_ts'))
        )
        
        if needs_only_permission and cache_key in self.permission_cache:
            logger.info("使用缓存的权限验证结果")
            return self.permission_cache[cache_key], None
        
        headers = {"Content-Type": "application/json"}
        data = {"code": auth_code}
        
        try:
            logger.info(f"正在验证权限: {required_permissions}")
            response = requests.post(self.auth_api_url, headers=headers, json=data, timeout=60)            
            response.raise_for_status()
            result = response.json()
            # print(result)
            
            if result.get('success') and result.get('valid'):
                # 检查是否有所需的权限
                auth_arr = result.get('authArr', [])

                logger.debug(f"获取到的权限数组: {auth_arr}")
                
                # 检查是否有任何所需权限
                has_permission = any(perm in auth_arr for perm in required_permissions)
                
                if has_permission:
                    logger.info(f"权限验证通过: {required_permissions}")
                    
                    # 获取API key（如果有）
                    api_key = result.get('apiKey')

                    logger.debug(f"API key是否存在: {bool(api_key)}")
                    
                    if api_key and not needs_only_permission:
                        # 需要API key且获取到了API key
                        self.api_key_cache[cache_key] = api_key
                        logger.info("成功获取并缓存API key")
                        return True, api_key
                    else:
                        # 不需要API key的情况（如stk_mins、_ts后缀权限）
                        self.permission_cache[cache_key] = True
                        logger.info("权限验证通过，无需API key")
                        return True, None
                else:
                    logger.error(f"权限不足，需要以下权限之一: {required_permissions}，当前权限: {auth_arr}")
                    return False, None
            else:
                logger.error(f"权限验证失败: {result.get('message', '未知错误')}")
                return False, None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"权限验证请求失败: {e}")
            return False, None
        except json.JSONDecodeError as e:
            logger.error(f"权限验证响应解析失败: {e}")
            return False, None
        except Exception as e:
            logger.error(f"权限验证时发生未知错误: {e}")
            return False, None
    
    def get_tushare_pro_client(self, api_key: str):
        """
        获取tushare Pro客户端
        
        Args:
            api_key (str): API key
            
        Returns:
            tushare Pro客户端
        """
        if not api_key:
            raise ValueError("API key不能为空")
        
        try:
            return ts.pro_api(api_key)
        except Exception as e:
            logger.error(f"初始化tushare Pro客户端失败: {e}")
            raise RuntimeError(f"tushare_pro客户端初始化失败: {e}")

# 创建全局实例
_common_permission_manager = CommonPermissionManager()

class BaseApiWrapper:
    """API包装器基类"""
    
    def __init__(self, auth_code: str, required_permissions: List[str]):
        self.auth_code = auth_code
        self.required_permissions = required_permissions
        self.api_key = None
        self.tushare_pro = None
        self._permission_verified = False
    
    def _ensure_permission_and_api_key(self):
        """确保权限验证通过并获取API key（如果需要）"""
        if not self._permission_verified:
            has_permission, api_key = _common_permission_manager.validate_permission_and_get_api_key(
                self.auth_code, self.required_permissions
            )
            
            if not has_permission:
                raise PermissionError(f"权限验证失败，需要以下权限之一: {self.required_permissions}")
            
            self.api_key = api_key
            self._permission_verified = True
        
        # 如果需要API key但还没有初始化tushare_pro客户端
        if self.api_key and not self.tushare_pro:
            self.tushare_pro = _common_permission_manager.get_tushare_pro_client(self.api_key) 