from mcp.server.fastmcp import FastMCP

# 初始化MCP服务实例
mcp = FastMCP("My_Mcp_Server")

@mcp.tool()
def sum(a: int,b: int) -> int:
    """ 两个数相加求和
    
    Args:
        a (int): 整数a
        b (int): 整数b
        
    Returns:
        int: 两个数的和
    """
    return a+b

if __name__ == '__main__':
    # 启动MCP服务，使用标准输入输出作为传输方式
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = 8000
    mcp.run(transport='stdio')
    print("MCP服务已启动，等待工具调用...")