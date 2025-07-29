#!/usr/bin/env python3
"""
测试MCP客户端连接
"""

import asyncio
import json
import aiohttp

async def test_mcp_connection():
    """测试MCP连接"""
    print("🔗 测试MCP客户端连接...")
    
    # MCP端点URL
    url = "http://127.0.0.1:8000/mcp"
    
    # 测试工具列表请求
    mcp_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"📡 发送请求到: {url}")
            print(f"📋 请求内容: {json.dumps(mcp_request, indent=2)}")
            
            async with session.post(
                url,
                json=mcp_request,
                headers={"Content-Type": "application/json"}
            ) as response:
                print(f"📊 响应状态: {response.status}")
                print(f"📋 响应头: {dict(response.headers)}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ 成功响应:")
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                else:
                    text = await response.text()
                    print(f"❌ 错误响应: {text}")
                    
    except Exception as e:
        print(f"❌ 连接失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp_connection())