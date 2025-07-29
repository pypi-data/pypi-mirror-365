#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试通用API权限验证功能
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tinyshare as ts

def test_general_api_permissions():
    """测试通用API权限验证功能"""
    
    print("=== 测试通用API权限验证功能 ===\n")
    
    # 测试用的权限验证码（需要替换为实际的验证码）
    test_auth_code = "4Usff45opzN2v6SAtyGbn9ABRuii8Mxe2CGw2uws5R11MU4X0pkWWHmVd008947f"
    
    # 测试不同类型的接口
    test_interfaces = [
        ('stock_basic', 'exchange=&list_status=L&fields=ts_code,symbol,name,area,industry,list_date'),
        ('trade_cal', 'exchange=&start_date=20250101&end_date=20250131'),
        ('daily', 'ts_code=000001.SZ&start_date=20250620&end_date=20250628'),
        ('daily_basic', 'ts_code=000001.SZ&start_date=20250620&end_date=20250628'),
        ('index_daily', 'ts_code=000001.SH&start_date=20250620&end_date=20250628'),
    ]
    
    try:
        # 创建API客户端
        pro = ts.pro_api(test_auth_code)
        print("✓ API客户端创建成功\n")
        
        for interface_name, test_params in test_interfaces:
            print(f"测试接口: {interface_name}")
            try:
                # 解析参数
                kwargs = {}
                if test_params:
                    for param in test_params.split('&'):
                        if '=' in param:
                            key, value = param.split('=', 1)
                            if value:
                                kwargs[key] = value
                
                # 动态调用接口
                interface_method = getattr(pro, interface_name)
                df = interface_method(**kwargs)
                
                if df is not None and not df.empty:
                    print(f"✓ {interface_name}接口调用成功，获取到 {len(df)} 条数据")
                    print("数据预览:")
                    print(df.head(3))
                else:
                    print(f"✓ {interface_name}接口调用成功，但未获取到数据")
                print()
                
            except Exception as e:
                print(f"✗ {interface_name}接口调用失败: {e}")
                print()
    
    except Exception as e:
        print(f"✗ API客户端创建失败: {e}")
        return
    
    # 测试新闻接口是否依然正常工作
    print("测试新闻接口...")
    try:
        df_news = pro.news(
            src='',
            start_date='2018-11-21 09:00:00',
            end_date='2018-11-22 10:10:00'
        )
        if df_news is not None and not df_news.empty:
            print(f"✓ news接口调用成功，获取到 {len(df_news)} 条数据")
            print("数据预览:")
            print(df_news.head(3))
        else:
            print("✓ news接口调用成功，但未获取到数据")
    except Exception as e:
        print(f"✗ news接口调用失败: {e}")
    
    print("\n=== 测试完成 ===")
    print("所有需要权限验证的接口现在都会先进行权限验证，")
    print("然后获取相应的API key，最后调用tushare的对应方法。")

if __name__ == "__main__":
    test_general_api_permissions() 