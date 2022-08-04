import os

# 所有常量与环境变量
ENV_TOML_PATH = os.getcwd() + '/env.toml'
E_CACHED_DIR = 'cached_dir'
E_BY_COMPANY_PATH = 's_by_company_path'
E_ROE = 'ROE'
E_FOC = 'FOC'
E_OPM = 'OPM'
E_EXCELLENT = 'excellent'
E_WANDERFUL = 'wanderful'

CSV_DEFULT_INDEX = '序号'
REPORT_DATE_NAME = '报告日期'
ZCFZ_TABLE_NAME = '资产负债表'
LRB_TABLE_NAME = '利润表'
XJLL_TABLE_NAME = '现金流量表'
STOCK_CODE = '股票代码'

# 报表列名
C_ROE = 'ROE'
C_NET_PROFIT = '净利润'
C_EQUITY = '股东权益合计'
C_OPER_NET_CASH = '经营性现金流-现金流量净额'
C_STOCK_S_NAME = '股票简称'
C_TOTAL_ASSETS = '资产-总资产'
C_TOTAL_DEBTS = '负债-总负债'
C_DEBTS_DIV_ASSETS = '资产负债率'
C_FOC = 'FOC'  # (C_OPER_NET_CASH-C_CAPITAL_COST)/C_EQUITY
C_OPER_NET_CASH = '经营性现金流-现金流量净额'
C_CAPITAL_COST = '投资性现金流-现金流量净额'
C_FREE_CASH = '自由现金流'
C_OPERATING_PROFIT = '营业利润'
C_TOTAL_OPER_PROFIT = '营业总收入'
C_OPER_PROFIT_MARGIN = '主营业务利润率'
C_NET_PROFIT_MARGIN = '净利润率'

# Voted
V_OPM = '近十年平均毛利率'
TOTAL_SCORE = '总得分'
V_ROE_SCORE = 'ROE得分'
V_10Y_MEDIAN = '最近十年中位数'
V_ANY_ROW_NOT_LT_EXPECTED = '任意一年不低于标准'
V_10Y_STD = '最近十年波动程度'
V_FOC_SCORE = 'FOC得分'
V_OPM_SCORE = '主营业务利润得分'
V_CAGR = '年化增长%'
V_NPM = '近十年净利润率'
V_NPM_SCORE = '净利润率得分'

# 第一个位非常棒，第二个为很优秀
V_Median_Standard = {C_ROE: [0.2, 0.15], C_FOC: [0.2, 0.15],
                     C_OPER_PROFIT_MARGIN: [0.6, 0.4],
                     C_NET_PROFIT_MARGIN: [0.2, 0.15]}

# Plot
# P_ROE = 'ROE_display'
