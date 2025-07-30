import click
from fastmcp import FastMCP
from alibabacloud_ims_editing_mcp_server.tools.tool_registration import *
import logging
from dotenv import load_dotenv
import asyncio
import sys

logging.basicConfig(level=logging.INFO)


def create_new_mcp_server(level):
    mcp = FastMCP("IMS Editing MCP")

    if level:
        if level == "Basic":
            for tool in basic_tools:
                mcp.tool(tool['tool_func'], **tool['tool_info'])
        elif level == "Standard":
            for tool in standard_tools:
                mcp.tool(tool['tool_func'], **tool['tool_info'])
        elif level == "Premium":
            for tool in premium_tools:
                mcp.tool(tool['tool_func'], **tool['tool_info'])
        elif level == "Trial":
            for tool in trial_tools:
                mcp.tool(tool['tool_func'], **tool['tool_info'])
        else:
            raise ValueError("level value is invalid.")
    else:
        for tool in premium_tools:
            mcp.tool(tool['tool_func'], **tool['tool_info'])

    print(" - In basic_tools:", [f['tool_func'].__name__ for f in basic_tools])
    print(" - In standard_tools:", [f['tool_func'].__name__ for f in standard_tools])
    print(" - In premium_tools:", [f['tool_func'].__name__ for f in premium_tools])
    print(" - In trial_tools:", [f['tool_func'].__name__ for f in trial_tools])

    return mcp


@click.command()
@click.option(
    "--level",
    type=str,
    default=None,
    help="Subscription level, i.e. Basic or Standard or Premium or Trial",
)
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse", "streamable-http"]),
    default="stdio",
    help="Transport type",
)
def main(transport: str, level: str):
    """命令行入口点，用于启动 IMS Video Editing MCP 服务器"""
    # 加载环境变量
    load_dotenv()

    try:
        # 创建MCP服务器
        mcp = create_new_mcp_server(level)
        print("start mcp server")
        asyncio.run(mcp.run(transport=transport))
    except Exception as e:
        print(f"启动服务器时出错: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
