# -*- coding: utf-8 -*-
from mcp.server.fastmcp import FastMCP
from pydantic import Field
import logging
logger = logging.getLogger('mcp')
settings = {
    'log_level': 'DEBUG'
}
# 初始化mcp服务
mcp = FastMCP('mcp-test-1', log_level='ERROR', settings=settings)
# 定义工具
@mcp.tool(name='加分计算器', description='输入两个数，进行加法计算')
async def add_compute(
        num1: str = Field(description='第一个数'),
        num2: str = Field(description='第二个数'),
) -> str:
    """简单的加法器mcp
    Args:
        num1: 第一个数
        num2: 第二个数
    Returns:
        审核后的内容
    """
    logger.info('第一个数：{}'.format(num1))
    logger.info('第二个数：{}'.format(num2))
    # call sync api, will return the result
    print('please wait...')
    num1 = float(num1)
    num2 = float(num2)
    return str(num1 + num2)
def run():
    mcp.run(transport='stdio')
if __name__ == '__main__':
   run()