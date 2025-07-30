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


ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
if ACCESS_TOKEN is None:
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

@mcp.tool(name='callPostInvestmentGuide', description='用于为用户提供 RBF 投资领域投后管理相关的投后管理方法论、日常投后管理动作、资管委外体系等方面的信息')
async def callPostInvestmentGuide(query):
    """
    -- 帮助用户解决投后管理方法论相关的问题。
    -- 帮助用户解决日常投后管理动作相关的问题。
    -- 帮助用户解决资管委外体系相关的问题。
    :param query:
    :return:
    """
    return _call_message( query, "7503667080626421786")

@mcp.tool(name='callARM', description='用于解答用户在滴灌通澳交所分账方案授权、开户过程中遇到的问题，提供分账开户授权细节、方案对比及信息流和资金流领域的专业解答，解答用户在滴灌通澳交所ARM（自动还款机制）业务中信息流和资金流相关问题，提供准确专业的知识回复')
async def callARM(query):
    """
    用于解答用户在滴灌通澳交所分账方案授权、开户过程中遇到的问题，提供分账开户授权细节、方案对比及信息流和资金流领域的专业解答，解答用户在滴灌通澳交所ARM（自动还款机制）业务中信息流和资金流相关问题，提供准确专业的知识回复，
    -- 帮助用户解决分账方案开户及授权细节相关的问题。
    -- 帮助用户解决不同分账方案对比相关的问题。
    -- 帮助用户解决分账方案信息流和资金流对接相关的问题。
    -- 帮助用户解决ARM信息流模块相关的问题。
    -- 帮助用户解决ARM资金流模块相关的问题。
    -- 帮助用户解决ARM机制功能及数据质量相关的问题。
    :param query:
    :return:
    """
    return _call_message( query, "7504593385425420342")

@mcp.tool(name='callDcfValuation', description='用于解答滴灌通RBF产品的公允价值计量相关问题，特别是贴现现金流法（DCF法），提供模型阐释与实际案例')
async def callDcfValuation(query):
    """
    用于解答滴灌通RBF产品的公允价值计量相关问题，特别是贴现现金流法（DCF法），提供模型阐释与实际案例，
    -- 帮助用户解决RBF产品公允价值计量方法相关的问题。
    -- 帮助用户解决DCF法模型及主要参数相关的问题。
    -- 帮助用户解决RBF产品估值示例及组合产品(SPAC)估值相关的问题。
    :param query:
    :return:
    """
    return _call_message( query, "7503851231537037322")


@mcp.tool(name='callRbcLaw', description='用于聚焦滴灌通澳交所RBC协议的法律性质、法律效力、与其他法律关系的区别及不同司法管辖区的法律安排等内容，为用户提供专业解答')
async def callRbcLaw(query):
    """
    用于聚焦滴灌通澳交所RBC协议的法律性质、法律效力、与其他法律关系的区别及不同司法管辖区的法律安排等内容，为用户提供专业解答，
    -- 帮助用户解决RBC法律性质相关的问题。
    -- 帮助用户解决RBC与其他法律形式区别相关的问题。
    -- 帮助用户解决不同司法管辖区RBC法律安排相关的问题。
    :param query:
    :return:
    """
    return _call_message( query, "7503860857768558603")


@mcp.tool(name='callRbfRating', description='用于解答滴灌通澳交所RBF评级相关问题，分析RBF产品未来现金流的产生能力、稳定性与可持续性，以及覆盖投资本金并分配收益的能力及风险')
async def callRbfRating(query):
    """
    用于解答滴灌通澳交所RBF评级相关问题，分析RBF产品未来现金流的产生能力、稳定性与可持续性，以及覆盖投资本金并分配收益的能力及风险，
    -- 帮助用户解决RBF产品风险水平评估相关的问题。
    -- 帮助用户解决RBF评级核心分析要素相关的问题。
    -- 帮助用户解决RBF评级评估细节和计算细节相关的问题。
    :param query:
    :return:
    """
    return _call_message( query, "7505803609318244404")

@mcp.tool(name="callRBFProductAccountingProcedures", description='用于为滴灌通澳交所（MCEX）的投资者和融资者提供准确、清晰且简洁的MCEX金融产品收入分成财务会计处理相关问题的解答')
async def callRBFProductAccountingProcedures(query):
    """
    用于为滴灌通澳交所（MCEX）的投资者和融资者提供准确、清晰且简洁的MCEX金融产品收入分成财务会计处理相关问题的解答，
    -- 帮助用户解决MCEX金融产品初始投资期间财务会计处理相关的问题。
    -- 帮助用户解决MCEX金融产品收入分成期间/持有期间财务会计处理相关的问题。
    -- 帮助用户解决MCEX金融产品结束期间财务会计处理相关的问题。
    :param query:
    :return:
    """
    return _call_message( query, "7503466419804684327")


@mcp.tool(name='callMarketPlayers', description='用于协助投资者全面了解滴灌通澳交所的各类市场参与角色、相应资质要求、不同会员类型与账户的选择标准，以及提交会员申请的流程')
async def callMarketPlayers(query):
    """
    用于协助投资者全面了解滴灌通澳交所的各类市场参与角色、相应资质要求、不同会员类型与账户的选择标准，以及提交会员申请的流程，
    -- 帮助用户解决滴灌通澳交所市场参与角色识别相关的问题。
    -- 帮助用户解决会员资质要求查询相关的问题。
    -- 帮助用户解决会员类型与账户选择及申请流程相关的问题。
    :param query:
    :return:
    """
    return _call_message(query, "7504120297151791114")


@mcp.tool(name='callProductLaw', description='用于为用户提供滴灌通澳交所核心投资产品（RBO、RBV及其细分类型SPV、SPAC等）的法律性质、主体关系、权利义务、合约管辖及交易所职能等内容的准确、清晰且简洁的解答，确保无基本法律知识的人也能理解')
async def callProductLaw(query):
    """
    用于为用户提供滴灌通澳交所核心投资产品（RBO、RBV及其细分类型SPV、SPAC等）的法律性质、主体关系、权利义务、合约管辖及交易所职能等内容的准确、清晰且简洁的解答，确保无基本法律知识的人也能理解，
    -- 帮助用户解决滴灌通澳交所核心投资产品法律性质相关的问题。
    -- 帮助用户解决滴灌通澳交所核心投资产品主体关系及权利义务相关的问题。
    -- 帮助用户解决滴灌通澳交所核心投资产品合约管辖及交易所职能相关的问题。
    :param query:
    :return:
    """
    return _call_message(query, "7504221556093304886")


@mcp.tool(name='callMCEXLaw', description='用于以通俗易懂的语言为用户精准解答滴灌通澳交所法律地位、挂牌资产类型、交易规则及投资者权益等合规问题')
async def callMCEXLaw(query):
    """
    用于以通俗易懂的语言为用户精准解答滴灌通澳交所法律地位、挂牌资产类型、交易规则及投资者权益等合规问题，
    -- 帮助用户解决滴灌通澳交所法律地位相关的问题。
    -- 帮助用户解决滴灌通澳交所挂牌资产类型及交易规则相关的问题。
    -- 帮助用户解决滴灌通澳交所投资者权益等合规相关的问题。
    :param query:
    :return:
    """
    return _call_message(query, "7504611813091524619")


@mcp.tool(name='callExchangeIssuance', description='用于为用户解答滴灌通交易所SPV、RBO和SPAC的挂牌发行规则及流程相关问题，包括市场主体、挂牌准入、KYC规则、发行流程和管理等内容')
async def callExchangeIssuance(query):
    """
    用于为用户解答滴灌通交易所SPV、RBO和SPAC的挂牌发行规则及流程相关问题，包括市场主体、挂牌准入、KYC规则、发行流程和管理等内容，
    -- 帮助用户解决SPV和RBO融资发行相关的问题。
    -- 帮助用户解决SPAC的设立及管理相关的问题。
    -- 帮助用户解决挂牌准入和KYC规则相关的问题。
    :param query:
    :return:
    """
    return _call_message(query, "7504479881523396627")


@mcp.tool(name='callRiskManage', description='用于从金融风控专家角度，解答滴灌通澳交所RBF产品及相关投资、融资活动中关于风险管理、评级、业绩评价的问题')
async def callRiskManage(query):
    """
    用于从金融风控专家角度，解答滴灌通澳交所RBF产品及相关投资、融资活动中关于风险管理、评级、业绩评价的问题，
    -- 帮助用户解决RBF产品风险管理相关的问题。
    -- 帮助用户解决RBF产品评级相关的问题。
    -- 帮助用户解决RBF投资与融资的业绩评价相关的问题。
    :param query:
    :return:
    """
    return _call_message(query, "7506170754804350987")


@mcp.tool(name='callTransactionAssistant', description='用于为用户解答在滴灌通澳交所进行交易的相关流程问题，依据知识库内容精准判断用户交易意图（买单或卖单）及产品类型（SPAC份额、SPV份额、SPAC优先凭证、RBO），并提供准确回答')
async def callTransactionAssistant(query):
    """
    用于为用户解答在滴灌通澳交所进行交易的相关流程问题，依据知识库内容精准判断用户交易意图（买单或卖单）及产品类型（SPAC份额、SPV份额、SPAC优先凭证、RBO），并提供准确回答，
    -- 帮助用户解决SPAC份额交易流程相关的问题。
    -- 帮助用户解决SPV份额交易流程相关的问题。
    -- 帮助用户解决SPAC优先凭证及RBO交易流程相关的问题。
    :param query:
    :return:
    """
    return _call_message(query, "7505377123679617051")


@mcp.tool(name='callExchangeSettlement', description='用于为用户解答滴灌通交易所结算业务相关问题，重点围绕资金、费用、交易价格计算，份额计算，风险等客户关心的业务流程方面')
async def callExchangeSettlement(query):
    """
    用于为用户解答滴灌通交易所结算业务相关问题，重点围绕资金、费用、交易价格计算，份额计算，风险等客户关心的业务流程方面，
    -- 帮助用户解决订单的清结算相关的问题。
    -- 帮助用户解决每天的收入分成清结算相关的问题。
    -- 帮助用户解决应收/实收相关的问题。
    :param query:
    :return:
    """
    return _call_message(query, "7503802881519927332")


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


@mcp.tool(name='callCrossBorderFunds', description='')
async def callCrossBorderFunds(query):
    """
    用于为各类身份对话者准确、清晰地解答滴灌通跨境资金相关问题，包括境外投资者通过滴灌通澳交所投资境内企业的资金流程、资金通道运作等，
    -- 帮助用户解决境外投资者成为滴灌通澳交所会员投资境内企业的资金流程相关问题。
    -- 帮助用户解决滴灌通澳交所代表境外投资者与境内企业开展投资业务的资金运作相关问题。
    -- 帮助用户解决滴灌通跨境资金通道的安全合规性及高頻高效运作相关问题。
    :param query:
    :return:
    """
    return _call_message(query, "7503846322882560012")


@mcp.tool(name='callMCEXProductTaxArrangements', description='帮助用户解决不同地区投资人投资中国境内资产的税务处理相关问题。帮助用户解决被投企业开票及发票类型相关的问题。帮助用户解决RBF产品涉及的税费种类及纳税义务相关的问题')
async def callMCEXProductTaxArrangements(query):
    """
    用于解答各类身份对话者有关滴灌通RBF产品税相关问题，提供准确、清晰的税务知识回复，
    -- 帮助用户解决不同地区投资人投资中国境内资产的税务处理相关问题。
    -- 帮助用户解决被投企业开票及发票类型相关的问题。
    -- 帮助用户解决RBF产品涉及的税费种类及纳税义务相关的问题。

    :param query:
    :return:
    """
    return _call_message(query, "7508560581432426530")



@mcp.tool(name='callPreInvestment', description='用于结合滴灌通集团在样板房阶段积累的投资经验，从评估支持和决策辅助角度，为交易所投资者、融资方及其他相关方提供RBF投资领域的参考与指导')
async def callPreInvestment(query):
    """
    用于结合滴灌通集团在样板房阶段积累的投资经验，从评估支持和决策辅助角度，为交易所投资者、融资方及其他相关方提供RBF投资领域的参考与指导，
    -- 帮助用户解决RBF投资历史洞察相关的问题。
    -- 帮助用户解决RBF投资准入筛选和尽调标准相关的问题。
    -- 帮助用户解决RBF投资评估模型相关的问题。

    :param query:
    :return:
    """
    return _call_message(query, "7504495994173194292")


@mcp.tool(name='callInvestmentCase', description='用于对滴灌通过往大消费领域的投资经验、投资案例进行总结和思考，将实战经验归纳沉淀并进行定量特征分析，为投资决策提供参考')
async def callInvestmentCase(query):
    """
    用于对滴灌通过往大消费领域的投资经验、投资案例进行总结和思考，将实战经验归纳沉淀并进行定量特征分析，为投资决策提供参考，
    -- 帮助用户解决大消费投资案例相关的问题。
    -- 帮助用户解决投前决策相关的问题。
    -- 帮助用户解决投资案例定量特征分析相关的问题。

    :param query:
    :return:
    """
    return _call_message(query, "7503696889385713676")


@mcp.tool(name='callInvestorStarterGuide', description='帮助用户解决滴灌通澳交所投资者参与交易所的准备工作相关的问题。帮助用户解决滴灌通澳交所投资者参与交易所的具体操作流程相关的问题。')
async def callInvestorStarterGuide(query):
    """
    用于为 0 基础刚接触滴灌通澳交所的投资者，详细介绍参与交易所的准备工作和有关具体操作流程，
    -- 帮助用户解决滴灌通澳交所投资者参与交易所的准备工作相关的问题。
    -- 帮助用户解决滴灌通澳交所投资者参与交易所的具体操作流程相关的问题。
    :param query:
    :return:
    """
    return _call_message(query, "7503486270208114729")

@mcp.tool(name='callFinancialCustody', description='用于为用户解答滴灌通澳交所的托管业务相关问题')
async def callFinancialCustody(query):
    """
    用于为用户解答滴灌通澳交所的托管业务相关问题，以知识库中托管流程优先，
    -- 帮助用户解决资产托管相关的问题。
    -- 帮助用户解决资金隔离措施相关的问题。
    -- 帮助用户明确滴灌通澳交所托管业务中资产托管与资金隔离的区别相关的问题。
    :param query:
    :return:
    """
    return _call_message(query, "7503830484691238924")

@mcp.tool(name='callDisputeResolution', description='用于为用户解答滴灌通相关的法务问题，重点围绕RBC争议解决，包括仲裁程序、裁决时限、执行、费用及案例参考等')
async def callDisputeResolution(query):
    """
    用于为用户解答滴灌通相关的法务问题，重点围绕RBC争议解决，包括仲裁程序、裁决时限、执行、费用及案例参考等，
    -- 帮助用户解决RBC争议解决方法相关的问题。
    -- 帮助用户解决仲裁程序、裁决时限、执行、上诉及费用相关的问题。
    -- 帮助用户解决RBC争议解决实际操作案例和经验相关的问题。
    :param query:
    :return:
    """
    return _call_message(query, "7504213845918629897")

@mcp.tool(name='callRWA', description='用于从投资者或融资者角度，精准回复用户关于RWA、区块链、DeFi、Web 3领域的各类问题，着重强调MCEX在RWA中的关键作用及作为中小微企业通向DeFi世界“合规网关”的意义')
async def callRWA(query):
    """
    用于从投资者或融资者角度，精准回复用户关于RWA、区块链、DeFi、Web 3领域的各类问题，着重强调MCEX在RWA中的关键作用及作为中小微企业通向DeFi世界“合规网关”的意义，
    -- 帮助用户解决RWA（现实世界资产上链）相关概念的问题。
    -- 帮助用户解决区块链技术在RWA中的应用问题。
    -- 帮助用户解决DeFi、Web 3生态与RWA结合的问题。
    :param query:
    :return:
    """
    return _call_message(query, "7504483726618427392")

@mcp.tool(name='callMIFC', description='Used for warmly greeting users and professionally answering all inquiries about Chapter 21 Company( Micro Connect International Finance Company Limited "MIFC" ) by accurately searching the knowledge base and generating comprehensive responses based on the retrieved content')
async def callMIFC(query):
    """
    Used for warmly greeting users and professionally answering all inquiries about Chapter 21 Company( Micro Connect International Finance Company Limited "MIFC" ) by accurately searching the knowledge base and generating comprehensive responses based on the retrieved content,
    -- Helping users solve any questions related to Chapter 21 Company(MIFC).
    :param query:
    :return:
    """
    return _call_message(query, "7504127961319145513")

@mcp.tool(name='callProductMetrics', description='用于为用户解答滴灌通澳交所金融产品在估值、指标计算过程中遇到的问题，依据滴灌秤估值流程及指标计算知识提供准确回答')
async def callProductMetrics(query):
    """
    用于为用户解答滴灌通澳交所金融产品在估值、指标计算过程中遇到的问题，依据滴灌秤估值流程及指标计算知识提供准确回答，
    -- 帮助用户解决滴灌通澳交所金融产品估值相关的问题。
    -- 帮助用户解决滴灌通澳交所金融产品指标计算相关的问题。
    -- 帮助用户解决滴灌通澳交所金融产品估值与指标计算综合类相关的问题
    :param query:
    :return:
    """
    return _call_message(query, "7503819153171038244")

def run():
    mcp.run(transport='stdio')
if __name__ == '__main__':
    run()
