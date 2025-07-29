#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TinyShare Token 工具模块
提供token类型判断的公共函数
"""

import re


def is_tiny_token(token: str) -> bool:
    """
    判断是否为tiny_token
    
    根据需求文档，tiny_token的特征：
    - 包含大写字母
    - 长度大于40位（实际为64位）
    - tushare的token为小写字母+数字
    
    Args:
        token (str): 要判断的token字符串
        
    Returns:
        bool: 如果是tiny_token返回True，否则返回False
    """
    if not token or not isinstance(token, str):
        return False
    
    # 检查长度是否大于40位
    if len(token) <= 40:
        return False
    
    # 检查是否包含大写字母
    if not any(c.isupper() for c in token):
        return False
    
    # 检查是否包含字母和数字的混合
    has_letter = any(c.isalpha() for c in token)
    has_digit = any(c.isdigit() for c in token)
    
    return has_letter and has_digit


def is_tushare_token(token: str) -> bool:
    """
    判断是否为tushare token
    
    tushare token的特征：
    - 只包含小写字母和数字
    - 不包含大写字母
    
    Args:
        token (str): 要判断的token字符串
        
    Returns:
        bool: 如果是tushare token返回True，否则返回False
    """
    if not token or not isinstance(token, str):
        return False
    
    # tushare token只包含小写字母和数字
    return bool(re.match(r'^[a-z0-9]+$', token))


def is_extract_code(token: str) -> bool:
    """
    判断是否为提取码（包含大写字母，但可能不是64位的tiny_token）
    
    Args:
        token (str): 要判断的token字符串
        
    Returns:
        bool: 如果包含大写字母返回True，否则返回False
    """
    if not token or not isinstance(token, str):
        return False
    
    # 检查是否包含大写字母
    return bool(re.search(r'[A-Z]', token)) 