#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TinyShare - A lightweight wrapper for tushare financial data API

This package provides a drop-in replacement for tushare with additional
features and optimizations while maintaining 100% API compatibility.
"""

import tushare as _tushare
import functools
import logging
import re
import requests
import json
from typing import Any, Optional, List, Dict
from pathlib import Path

# 导入token工具函数
from .token_utils import is_tiny_token, is_tushare_token, is_extract_code

__version__ = "0.5.0"
__author__ = "Your Name"

# Set up logging
logger = logging.getLogger(__name__)

# Global token storage and status
_token = None
_token_set_success = False

# Global tiny token storage and status for permission checking
_tiny_token = None
_tiny_token_set_success = False

# 导入通用权限管理器
try:
    from .common_permission import _common_permission_manager
    _common_permission_available = True
except ImportError:
    _common_permission_available = False
    logger.warning("通用权限管理器不可用，将使用原有的权限管理器")

class PermissionManager:
    """权限管理器，统一使用通用权限管理器"""
    
    def __init__(self):
        # 只保留通用权限管理器
        pass
    
    def validate_permission(self, token, required_permission):
        """
        验证权限，使用通用权限管理器
        
        Args:
            token (str): 权限验证码
            required_permission (str): 需要的权限，如 'stk_mins'
            
        Returns:
            bool: 是否有权限
        """
        # 如果通用权限管理器可用，直接使用
        if _common_permission_available:
            try:
                has_permission, _ = _common_permission_manager.validate_permission_and_get_api_key(
                    token, [required_permission]
                )
                return has_permission
            except Exception as e:
                logger.error(f"通用权限管理器验证失败: {e}")
                return False
        else:
            logger.error("通用权限管理器不可用")
            return False


class TokenManager:
    """Token管理器，用于处理提取码和token转换"""
    
    def __init__(self):
        self.api_url = "https://pro.swiftiny.com/api/extract/getLatestKey"
        self.cache_dir_name = ".tushare"
    
    def get_cache_file_path(self):
        """获取缓存文件路径"""
        cache_dir = Path.home() / self.cache_dir_name
        cache_dir.mkdir(exist_ok=True)
        return cache_dir / "token_cache.json"
    
    def save_token_to_cache(self, token, key_name=None, call_count=None, max_count=None):
        """将token保存到本地缓存"""
        cache_file = self.get_cache_file_path()
        cache_data = {
            'token': token,
            'key_name': key_name,
            'call_count': call_count,
            'max_count': max_count
        }
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Token已缓存到本地: {cache_file}")
        except IOError as e:
            logger.error(f"保存缓存文件失败: {e}")
    
    def get_token_from_extract_code(self, extract_code):
        """通过提取码获取真实token"""
        headers = {"Content-Type": "application/json"}
        data = {"code": extract_code}
        
        try:
            logger.info("正在通过提取码获取token...")
            response = requests.post(self.api_url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('success') and result.get('status') == 200:
                token = result.get('apiKey')
                key_name = result.get('keyName')
                call_count = result.get('callCount')
                max_count = result.get('maxCount')
                
                logger.info(f"获取新token成功: {key_name}")
                logger.info(f"调用次数: {call_count}/{max_count}")
                
                # 保存到缓存
                self.save_token_to_cache(token, key_name, call_count, max_count)
                return token
            else:
                logger.error(f"获取token失败: {result}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"解析响应失败: {e}")
            return None


# 创建管理器实例
_token_manager = TokenManager()
_permission_manager = PermissionManager()


def permission_required(required_permission: str):
    """
    权限检查装饰器
    
    Args:
        required_permission (str): 需要的权限，如 'stk_mins'
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            global _tiny_token
            
            if not _tiny_token:
                raise PermissionError(f"未设置权限验证码，请先调用 set_token_tiny() 设置权限验证码")
            
            # 检查权限
            if not _permission_manager.validate_permission(_tiny_token, required_permission):
                raise PermissionError(f"权限不足，需要 '{required_permission}' 权限")
            
            # 权限检查通过，执行原函数
            return func(*args, **kwargs)
        return wrapper
    return decorator


def is_extract_code(token_str: str) -> bool:
    """
    判断输入的字符串是否为提取码（包含大写字母）
    保留向后兼容性
    
    Args:
        token_str (str): 输入的token字符串
        
    Returns:
        bool: 如果包含大写字母则认为是提取码，返回True；否则返回False
    """
    from .token_utils import is_extract_code as _is_extract_code
    return _is_extract_code(token_str)


def is_normal_token(token_str: str) -> bool:
    """
    判断输入的字符串是否为正常token（全是小写字母+数字）
    保留向后兼容性
    
    Args:
        token_str (str): 输入的token字符串
        
    Returns:
        bool: 如果全是小写字母和数字则返回True；否则返回False
    """
    from .token_utils import is_tushare_token
    return is_tushare_token(token_str)


def set_token_tiny(token: str) -> None:
    """
    设置权限验证码，用于控制自定义接口的权限
    
    Args:
        token (str): 权限验证码
    """
    global _tiny_token, _tiny_token_set_success
    
    if not token or not isinstance(token, str):
        logger.error("权限验证码不能为空且必须是字符串")
        _tiny_token_set_success = False
        return
    
    token = token.strip()

    _tiny_token = token
    _tiny_token_set_success = True
    logger.info("权限验证码设置成功")


def get_token_tiny() -> Optional[str]:
    """
    获取当前设置的权限验证码
    
    Returns:
        str or None: 当前权限验证码，如果未设置则返回 None
    """
    return _tiny_token


def is_token_tiny_set_success() -> bool:
    """
    检查权限验证码是否设置成功
    
    Returns:
        bool: 权限验证码设置成功状态
    """
    return _tiny_token_set_success


def set_token(token: str) -> None:
    """
    Set the tushare API token.
    支持普通token和提取码两种方式。
    
    Args:
        token (str): Your tushare API token or extract code
    """
    global _token, _token_set_success
    
    if not token or not isinstance(token, str):
        logger.error("Token不能为空且必须是字符串")
        _token_set_success = False
        return
    
    token = token.strip()
    
    try:
        # 情况1：如果token全是小写字母+数字，则默认走tushare的set_token方法
        if is_normal_token(token):
            logger.info("检测到普通token格式，直接设置")
            _token = token
            _tushare.set_token(token)
            _token_set_success = True
            logger.info("Token设置成功")
            
        # 情况2：如果token包含大写字母，则认为是提取码，需要调用接口获取真实token
        elif is_extract_code(token):
            logger.info("检测到提取码格式，正在获取真实token")
            
            # 通过提取码获取真实token
            real_token = _token_manager.get_token_from_extract_code(token)
            
            if real_token:
                logger.info("成功获取真实token，正在设置")
                # 获取到真实token后，继续走tushare的set_token方法
                _token = real_token
                _tushare.set_token(real_token)
                _token_set_success = True
                logger.info("Token设置成功")
            else:
                logger.error("无法通过提取码获取真实token")
                _token_set_success = False
                
        else:
            # 其他格式，尝试直接设置
            logger.info("未识别的token格式，尝试直接设置")
            _token = token
            _tushare.set_token(token)
            _token_set_success = True
            logger.info("Token设置成功")
            
    except Exception as e:
        logger.error(f"设置token时发生错误: {e}")
        _token_set_success = False
        raise


def get_token() -> Optional[str]:
    """
    Get the current tushare API token.
    
    Returns:
        str or None: Current token if set, None otherwise
    """
    return _token


def is_token_set_success() -> bool:
    """
    检查token是否设置成功
    
    Returns:
        bool: token设置成功状态
    """
    return _token_set_success


class TinyShareProApi:
    """
    TinyShare Pro API 类，支持链式调用
    提供与tushare pro_api兼容的接口，同时支持tinyshare的自定义功能
    """
    
    def __init__(self, token: str, timeout: int = 30):
        """
        初始化TinyShare Pro API客户端
        
        Args:
            token (str): API token或tiny token
            timeout (int): 请求超时时间，默认30秒
        """
        self.token = token
        self.timeout = timeout
        self._tushare_client = None
        self._enhanced_wrapper = None
        
        # 检查token类型
        if is_tiny_token(token):
            # 这是tiny token，设置给_tiny_token
            global _tiny_token, _tiny_token_set_success
            _tiny_token = token
            _tiny_token_set_success = True
            # 对于tiny_token，不需要初始化tushare客户端，等到实际调用时再处理
        else:
            # 这是tushare token，初始化tushare客户端
            try:
                self._tushare_client = _tushare.pro_api(token=token, timeout=timeout)
                # 使用增强的API包装器来处理所有接口的权限验证
                from .general_api_wrapper import create_enhanced_pro_api_wrapper
                self._enhanced_wrapper = create_enhanced_pro_api_wrapper(self._tushare_client, token)
            except Exception as e:
                logger.error(f"Failed to initialize tushare pro API client: {e}")
                # 即使tushare客户端初始化失败，也允许tiny功能工作
                self._tushare_client = None
                self._enhanced_wrapper = None
    
    def _get_news_wrapper_for_tiny_token(self):
        """为tiny_token获取新闻包装器"""
        from .news_data import create_news_api_wrapper
        return create_news_api_wrapper(self.token)
    
    def news(self, **kwargs):
        """获取新闻数据"""
        if is_tiny_token(self.token):
            # 使用tiny_token逻辑
            wrapper = self._get_news_wrapper_for_tiny_token()
            return wrapper.news(**kwargs)
        elif self._enhanced_wrapper:
            # 使用tushare token的增强包装器
            return self._enhanced_wrapper.news(**kwargs)
        elif self._tushare_client:
            # 直接使用tushare客户端
            return self._tushare_client.news(**kwargs)
        else:
            raise RuntimeError("No valid client available")
    
    def major_news(self, **kwargs):
        """获取重大新闻数据"""
        if is_tiny_token(self.token):
            # 使用tiny_token逻辑
            wrapper = self._get_news_wrapper_for_tiny_token()
            return wrapper.major_news(**kwargs)
        elif self._enhanced_wrapper:
            # 使用tushare token的增强包装器
            return self._enhanced_wrapper.major_news(**kwargs)
        elif self._tushare_client:
            # 直接使用tushare客户端
            return self._tushare_client.major_news(**kwargs)
        else:
            raise RuntimeError("No valid client available")
    
    def cctv_news(self, **kwargs):
        """获取央视新闻数据"""
        if is_tiny_token(self.token):
            # 使用tiny_token逻辑
            wrapper = self._get_news_wrapper_for_tiny_token()
            return wrapper.cctv_news(**kwargs)
        elif self._enhanced_wrapper:
            # 使用tushare token的增强包装器
            return self._enhanced_wrapper.cctv_news(**kwargs)
        elif self._tushare_client:
            # 直接使用tushare客户端
            return self._tushare_client.cctv_news(**kwargs)
        else:
            raise RuntimeError("No valid client available")
    
    def stk_mins_tiny(self, ts_code: str, freq: str, start_date: Optional[str] = None,
                     end_date: Optional[str] = None, adjustflag: Optional[str] = None, 
                     origin: bool = False):
        """
        获取A股分钟数据（支持链式调用）
        
        Args:
            ts_code (str): 股票代码，如 '600000.SH'
            freq (str): 分钟频度，支持 '5min', '15min', '30min', '60min'
            start_date (str, optional): 开始日期，格式 '2023-08-25'
            end_date (str, optional): 结束日期，格式 '2023-08-25'
            adjustflag (str, optional): 复权类型，'hfq'=后复权, 'qfq'=前复权, None=不复权(默认)
            origin (bool): 是否返回原始格式，默认False
            
        Returns:
            pd.DataFrame: 股票分钟数据
        """
        # 导入stk_mins_tiny函数并调用
        from .minute_data import _minute_data_fetcher
        
        # 检查tiny token权限
        global _tiny_token
        if not _tiny_token:
            raise PermissionError("未设置权限验证码，请使用有效的tiny token初始化pro_api")
        
        # 验证权限
        from .common_permission import _common_permission_manager
        has_permission, _ = _common_permission_manager.validate_permission_and_get_api_key(
            _tiny_token, ['stk_mins']
        )
        if not has_permission:
            raise PermissionError("权限不足，需要 'stk_mins' 权限")
        
        return _minute_data_fetcher.get_stock_minute_data(
            ts_code=ts_code,
            freq=freq,
            start_date=start_date,
            end_date=end_date,
            adjustflag=adjustflag,
            origin=origin
        )

    def _call_server_api(self, api_name: str, **kwargs):
        """
        调用服务端代理接口
        
        Args:
            api_name (str): API名称（可能包含_ts后缀）
            **kwargs: 传递给API的参数
            
        Returns:
            pd.DataFrame: API返回的数据
        """
        import requests
        import pandas as pd
        
        # 服务端接口URL
        server_url = "https://pro.swiftiny.com"  # 根据实际部署调整
        # server_url = "http://localhost:1337"  # 本地测试时使用 
        
        # 直接使用完整的api_name，不进行预处理
        api_url = f"{server_url}/api/tushare/{api_name}"
        
        # 准备请求数据
        request_data = {
            "auth_code": self.token,  # 使用tiny_token作为授权码
            "params": kwargs,
            "fields": kwargs.get('fields', '')  # 如果有fields参数
        }
        
        try:
            # 发送POST请求到服务端
            response = requests.post(
                api_url,
                json=request_data,
                headers={'Content-Type': 'application/json'},
                timeout=self.timeout
            )
            
            # 检查HTTP状态码，但不立即抛出异常，先解析响应内容
            if response.status_code != 200:
                try:
                    error_result = response.json()
                    error_message = error_result.get('error', f'HTTP {response.status_code} Error')
                    
                    # 根据不同的错误类型提供更详细的信息
                    if response.status_code == 403:
                        if 'permission_required' in error_result:
                            required_perm = error_result['permission_required']
                            raise PermissionError(f"权限不足：需要 '{required_perm}' 权限。{error_message}")
                        else:
                            raise PermissionError(f"权限不足：{error_message}")
                    elif response.status_code == 401:
                        raise PermissionError(f"授权验证失败：{error_message}")
                    elif response.status_code == 423:
                        remaining_time = error_result.get('remainingTime', 0)
                        raise PermissionError(f"会话冲突：{error_message}。剩余时间：{remaining_time}秒")
                    else:
                        raise ValueError(f"服务端错误 ({response.status_code})：{error_message}")
                except (ValueError, KeyError) as json_error:
                    # 如果解析JSON失败，使用原始错误信息
                    response.raise_for_status()
            
            result = response.json()
            
            if not result.get('success', False):
                error_msg = result.get('error', '未知错误')
                raise ValueError(f"服务端API调用失败: {error_msg}")
            
            # 获取数据
            data = result.get('data', [])
            
            if not data:
                # 返回空的DataFrame
                return pd.DataFrame()
            
            # 将数据转换为DataFrame格式，保持与原tushare一致的格式
            df = pd.DataFrame(data)
            
            # 如果有字段信息，确保列的顺序与原始返回一致
            if 'fields' in result and result['fields']:
                fields = result['fields']
                # 重新排序列以匹配原始字段顺序
                if all(col in df.columns for col in fields):
                    df = df[fields]
            
            logger.info(f"成功从服务端获取{api_name}数据，共{len(df)}条记录")
            return df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"调用服务端API失败: {e}")
            raise ConnectionError(f"连接服务端失败: {e}")
        except (PermissionError, ValueError) as e:
            # 权限错误和值错误直接抛出，保持原始错误信息
            logger.error(f"API调用失败: {e}")
            raise
        except Exception as e:
            logger.error(f"处理服务端响应失败: {e}")
            raise ValueError(f"处理服务端响应失败: {e}")

    def _validate_ts_permission(self, ts_interface_name: str):
        """
        验证_ts后缀接口的权限
        
        Args:
            ts_interface_name (str): _ts后缀的接口名称，如 'news_ts'
            
        Raises:
            PermissionError: 权限不足时抛出异常
        """
        from .common_permission import _common_permission_manager
        
        # _ts后缀接口需要对应的_ts权限
        required_permission = ts_interface_name  # 例如 news_ts
        
        try:
            # 验证权限（_ts后缀接口通常不需要API key，只需权限验证）
            has_permission, _ = _common_permission_manager.validate_permission_and_get_api_key(
                self.token, [required_permission]
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

    def __getattr__(self, name):
        """
        代理其他方法调用到tushare客户端
        
        Args:
            name (str): 方法名
            
        Returns:
            方法对象或属性值
        """
        # 避免递归：首先检查是否为特殊属性
        if name.startswith('_'):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        
        # 检查是否为_ts后缀的方法
        if name.endswith('_ts'):
            # 验证是否为tiny_token
            if not is_tiny_token(self.token):
                raise AttributeError(f"_ts后缀接口只支持tiny_token，当前token类型不支持")
            
            # 所有_ts接口都直接调用服务端API，权限验证交给后端处理
            # 包括新闻接口：news_ts, major_news_ts, cctv_news_ts
            def server_api_wrapper(**kwargs):
                # 直接调用服务端API，传递完整的接口名（包含_ts后缀）
                return self._call_server_api(name, **kwargs)
            
            return server_api_wrapper
        
        # 对于tiny_token，支持所有需要权限验证的接口
        if is_tiny_token(self.token):
            # 导入PERMISSION_REQUIRED_INTERFACES
            from .general_api_wrapper import PERMISSION_REQUIRED_INTERFACES
            
            if name in ['news', 'major_news', 'cctv_news']:
                # 这些方法已经在上面明确定义了，不应该到达这里
                raise AttributeError(f"Method '{name}' should be handled explicitly")
            elif name in PERMISSION_REQUIRED_INTERFACES:
                # 支持所有需要权限验证的接口
                def wrapper(**kwargs):
                    from .general_api_wrapper import GeneralApiWrapper
                    api_wrapper = GeneralApiWrapper(self.token, name)
                    return api_wrapper.call_interface(**kwargs)
                return wrapper
            else:
                raise AttributeError(f"'{self.__class__.__name__}' with tiny_token does not support method '{name}'")
        
        # 对于tushare_token，代理到增强包装器或tushare客户端
        if hasattr(self, '_enhanced_wrapper') and self._enhanced_wrapper:
            # 优先使用增强的包装器
            if hasattr(self._enhanced_wrapper, name):
                return getattr(self._enhanced_wrapper, name)
        
        if hasattr(self, '_tushare_client') and self._tushare_client:
            # 如果有tushare客户端，代理调用
            if hasattr(self._tushare_client, name):
                return getattr(self._tushare_client, name)
        
        # 如果都没有找到，抛出AttributeError
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")


def pro_api(token: Optional[str] = None, timeout: int = 30) -> Any:
    """
    Initialize tushare pro API client.
    支持两种调用方式：
    1. 传统方式：pro_api() 或 pro_api(tushare_token)
    2. 新的链式调用方式：pro_api(tiny_token).stk_mins_tiny(...)
    
    Args:
        token (str, optional): API token或tiny token. If not provided, uses globally set token.
        timeout (int): Request timeout in seconds. Defaults to 30.
    
    Returns:
        TinyShareProApi or Enhanced wrapper: 根据token类型返回相应的API客户端
    """
    if token:
        # 检查是否为tiny token（支持链式调用）
        if is_tiny_token(token):
            # 这是tiny token，返回新的TinyShareProApi实例
            return TinyShareProApi(token, timeout)
        else:
            # 这是tushare token，使用传统方式
            actual_token = token
    elif _token:
        actual_token = _token
    else:
        raise ValueError("Token not set. Please call set_token() first or provide token parameter.")
    
    try:
        client = _tushare.pro_api(token=actual_token, timeout=timeout)
        logger.info("Pro API client initialized successfully")
        
        # 使用增强的API包装器来处理所有接口的权限验证
        from .general_api_wrapper import create_enhanced_pro_api_wrapper
        wrapper = create_enhanced_pro_api_wrapper(client, actual_token)
        return wrapper
    except Exception as e:
        logger.error(f"Failed to initialize pro API client: {e}")
        raise


class ProApiWrapper:
    """
    TuShare Pro API 包装器，用于拦截新闻相关方法并进行权限验证
    已废弃，保留用于向后兼容
    """
    
    def __init__(self, client, token):
        self._client = client
        self._token = token
        self._news_wrapper = None
    
    def _get_news_wrapper(self):
        """获取新闻API包装器"""
        if self._news_wrapper is None:
            # 使用当前的token作为权限验证码
            from .news_data import create_news_api_wrapper
            self._news_wrapper = create_news_api_wrapper(self._token)
        return self._news_wrapper
    
    def news(self, **kwargs):
        """
        获取新闻数据（需要权限验证）
        
        Args:
            **kwargs: 传递给tushare news接口的参数
            
        Returns:
            pd.DataFrame: 新闻数据
        """
        try:
            return self._get_news_wrapper().news(**kwargs)
        except Exception as e:
            logger.error(f"调用news接口失败: {e}")
            raise
    
    def major_news(self, **kwargs):
        """
        获取重大新闻数据（需要权限验证）
        
        Args:
            **kwargs: 传递给tushare major_news接口的参数
            
        Returns:
            pd.DataFrame: 重大新闻数据
        """
        try:
            return self._get_news_wrapper().major_news(**kwargs)
        except Exception as e:
            logger.error(f"调用major_news接口失败: {e}")
            raise
    
    def cctv_news(self, **kwargs):
        """
        获取央视新闻数据（需要权限验证）
        
        Args:
            **kwargs: 传递给tushare cctv_news接口的参数
            
        Returns:
            pd.DataFrame: 央视新闻数据
        """
        try:
            return self._get_news_wrapper().cctv_news(**kwargs)
        except Exception as e:
            logger.error(f"调用cctv_news接口失败: {e}")
            raise
    
    def __getattr__(self, name):
        """
        代理其他所有方法到原始的tushare客户端
        """
        return getattr(self._client, name)


# Proxy all other tushare functions and attributes
def __getattr__(name: str) -> Any:
    """
    Proxy all tushare attributes and functions.
    
    This allows tinyshare to act as a complete drop-in replacement for tushare
    while maintaining the ability to add custom functionality.
    """
    if hasattr(_tushare, name):
        attr = getattr(_tushare, name)
        
        # If it's a callable, wrap it with logging
        if callable(attr):
            @functools.wraps(attr)
            def wrapper(*args, **kwargs):
                logger.debug(f"Calling tushare.{name} with args={args}, kwargs={kwargs}")
                try:
                    result = attr(*args, **kwargs)
                    logger.debug(f"tushare.{name} completed successfully")
                    return result
                except Exception as e:
                    logger.error(f"Error in tushare.{name}: {e}")
                    raise
            return wrapper
        else:
            return attr
    else:
        raise AttributeError(f"module 'tinyshare' has no attribute '{name}'")


# Export commonly used functions directly
from tushare import get_hist_data, get_tick_data, get_today_all, get_realtime_quotes

# Import our custom minute data function
from .minute_data import stk_mins_tiny

# Make sure we export the main functions
__all__ = [
    'set_token',
    'get_token', 
    'is_token_set_success',
    'is_normal_token',
    'is_extract_code',
    'set_token_tiny',
    'get_token_tiny',
    'is_token_tiny_set_success',
    'pro_api',
    'TinyShareProApi',
    'get_hist_data',
    'get_tick_data',
    'get_today_all',
    'get_realtime_quotes',
    'stk_mins_tiny',
    '__version__'
] 