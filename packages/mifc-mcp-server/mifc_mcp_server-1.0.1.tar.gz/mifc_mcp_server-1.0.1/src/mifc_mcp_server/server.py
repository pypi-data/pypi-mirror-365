# -*- coding: utf-8 -*-
import json
import os
from mcp.server.fastmcp import FastMCP
from pydantic import Field
import requests
import os
import logging
import dashscope

import sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcex_mcp_server.chat_message import chat,list_message, retrieve

logger = logging.getLogger('mcp')
settings = {
    'log_level': 'DEBUG'
}


# ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
# if ACCESS_TOKEN is None:
ACCESS_TOKEN =  "pat_Z59qmyXJwkwoF6QgajrMilObZ8OW5ZZ4qM09opZ9QMBoNyiv6an0kNn6h5xuOamH"


# 初始化mcp服务
mcp = FastMCP('mcex-mcp-server', log_level='ERROR', settings=settings)
# 定义工具

def _call_message(query, bot_id):
    chat_rsp = chat(query, bot_id,ACCESS_TOKEN)
    if chat_rsp['code'] == 0:
        chat_id = chat_rsp['data']['id']
        conversation_id = chat_rsp['data']['conversation_id']
        completed = False
        while not completed:
            retrieve_rsp = retrieve(chat_id, conversation_id, ACCESS_TOKEN)
            if retrieve_rsp['code'] == 0:
                chatV3ChatDetail = retrieve_rsp['data']
                status = chatV3ChatDetail['status']
                if status == 'completed':
                    completed = True
                    messages = list_message(chat_id, conversation_id, ACCESS_TOKEN)
                    if messages['code'] == 0:
                        chatV3MessageDetail = messages['data']
                        for item in chatV3MessageDetail:
                            if item['type'] == 'answer':
                                print(item['content'])
                                return item['content']

        return "对不起，您的问题我暂时还无法回答"
    return "对不起，您的问题我暂时还无法回答"

@mcp.tool(name='callMIFC', description='Used for warmly greeting users and professionally answering all inquiries about Chapter 21 Company( Micro Connect International Finance Company Limited "MIFC" ) by accurately searching the knowledge base and generating comprehensive responses based on the retrieved content')
async def callMIFC(query):
    """
    Used for warmly greeting users and professionally answering all inquiries about Chapter 21 Company( Micro Connect International Finance Company Limited "MIFC" ) by accurately searching the knowledge base and generating comprehensive responses based on the retrieved content,
    -- Helping users solve any questions related to Chapter 21 Company(MIFC).
    :param query:
    :return:
    """
    return _call_message(query, "7504127961319145513")


@mcp.tool(name='callFinancialProducts', description='帮助用户解决滴灌通交易所上市金融产品的类型、特点、申购、收费及合适投资者等相关问题。-- 帮助用户解决SPAC相关问题，包括永续型和期限型SPAC的信息。-- 帮助用户解决SPV份额相关问题，包括其分类、回购触发条件、申购发行安排及合适投资者等。')
async def callFinancialProducts(query):
    """
    用于为用户解答滴灌通交易所上市的金融产品相关问题，根据知识库内容精准提取、整理并优化信息进行回复，
    -- 帮助用户解决滴灌通交易所上市金融产品的类型、特点、申购、收费及合适投资者等相关问题。
    -- 帮助用户解决SPAC相关问题，包括永续型和期限型SPAC的信息。
    -- 帮助用户解决SPV份额相关问题，包括其分类、回购触发条件、申购发行安排及合适投资者等。
    :param query:
    :return:
    """
    return _call_message(query, "7503835097859637282")

def run():
    mcp.run(transport='stdio')
if __name__ == '__main__':
    run()
