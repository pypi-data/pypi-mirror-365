#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新闻接口的权限验证功能
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tinyshare as ts

def test_news_interfaces():
    """测试新闻接口"""
    
    print("=== 测试新闻接口权限验证功能 ===\n")
    
    # 测试用的权限验证码（需要替换为实际的验证码）
    test_auth_code = "4Usff45opzN2v6SAtyGbn9ABRuii8Mxe2CGw2uws5R11MU4X0pkWWHmVd008947f"
    
    # 测试news接口
    print("\n2. 测试news接口...")
    try:
        df = ts.pro_api(test_auth_code).news(
            src='',
            start_date='2018-11-21 09:00:00',
            end_date='2018-11-22 10:10:00'
        )
        if df is not None and not df.empty:
            print(f"✓ news接口调用成功，获取到 {len(df)} 条数据")
            print("数据预览:")
            print(df.head())
        else:
            print("✓ news接口调用成功，但未获取到数据")
    except Exception as e:
        print(f"✗ news接口调用失败: {e}")
    
    # # 测试major_news接口
    # print("\n3. 测试major_news接口...")
    # try:
    #     df = ts.pro_api(test_auth_code).major_news(
    #         src='sina',
    #         start_date='2018-11-21 09:00:00',
    #         end_date='2018-11-22 10:10:00'
    #     )
    #     if df is not None and not df.empty:
    #         print(f"✓ major_news接口调用成功，获取到 {len(df)} 条数据")
    #         print("数据预览:")
    #         print(df.head())
    #     else:
    #         print("✓ major_news接口调用成功，但未获取到数据")
    # except Exception as e:
    #     print(f"✗ major_news接口调用失败: {e}")
    
    # # 测试cctv_news接口
    # print("\n4. 测试cctv_news接口...")
    # try:
    #     df = ts.pro_api(test_auth_code).cctv_news(
    #         date='2018-11-21'
    #     )
    #     if df is not None and not df.empty:
    #         print(f"✓ cctv_news接口调用成功，获取到 {len(df)} 条数据")
    #         print("数据预览:")
    #         print(df.head())
    #     else:
    #         print("✓ cctv_news接口调用成功，但未获取到数据")
    # except Exception as e:
    #     print(f"✗ cctv_news接口调用失败: {e}")
    
    # # 测试其他非新闻接口是否正常工作
    # print("\n5. 测试其他接口是否正常...")
    # try:
    #     # 测试一个普通的接口
    #     df = ts.pro_api(test_auth_code).stock_basic(
    #         exchange='',
    #         list_status='L',
    #         fields='ts_code,symbol,name'
    #     )
    #     if df is not None and not df.empty:
    #         print(f"✓ 其他接口正常工作，获取到 {len(df)} 条股票数据")
    #     else:
    #         print("✓ 其他接口调用成功，但未获取到数据")
    # except Exception as e:
    #     print(f"✗ 其他接口调用失败: {e}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_news_interfaces() 