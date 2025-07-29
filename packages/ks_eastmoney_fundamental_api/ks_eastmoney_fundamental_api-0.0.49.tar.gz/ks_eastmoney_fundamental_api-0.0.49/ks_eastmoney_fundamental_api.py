# todo 1. 对于查询的持仓，空的也要推送空的，否则orderplit无法回调.  这对于http请求很容易实现，但是如果是websocket回调，也许空的不会回调？例如ibk

import pandas as pd
from pandas import DataFrame
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from ks_trade_api.base_fundamental_api import BaseFundamentalApi
from ks_trade_api.utility import extract_vt_symbol, generate_vt_symbol
from ks_trade_api.constant import Exchange, RET_OK, RET_ERROR, Product, RetCode, SUB_EXCHANGE2EXCHANGE
from ks_utility.datetimes import get_date_str
from ks_utility import datetimes
from ks_utility.datetimes import DATE_FMT
import sys
import numpy as np
from decimal import Decimal
import uuid
from logging import DEBUG, WARNING, ERROR
from ks_utility.numbers import to_decimal
from enum import Enum
import traceback
import pandas as pd
import numpy as np
import typing
import re

pd.set_option('future.no_silent_downcasting', True) # 关闭df = df.fillna(np.nan)的未来版本提示

from .EmQuantAPI import c

class Params(Enum):
    # 下面是我们的参数
    MRYN = 'MRYN' # MRY的N值
    
    # 下面是东财的标准参数
    N = 'N'
    ReportDate = 'ReportDate'
    TradeDate = 'TradeDate'
    Year = 'Year'
    PayYear = 'PayYear'
    IsPandas = 'IsPandas'
    Type = 'Type'
    CurType = 'CurType'
    TtmType = 'TtmType'
    FundCode = 'FundCode'
    EndDate = 'EndDate'
    
# 我们的标准字段
class MarketIndicator(Enum):
    ## 行情字段
    open = 'open'
    high = 'high'
    low = 'low'
    close = 'close'
    volume = 'volume'
    turnover = 'turnover'
    open_interest = 'open_interest'

class Indicator(Enum):    
    ## 财务字段
    ROE = 'ROE' # 净资产收益率
    ROA = 'ROA' # 总资产收益率
    LIBILITYTOASSET = 'LIBILITYTOASSET' # 资产负债率
    DIVANNUPAYRATE = 'DIVANNUPAYRATE' # 年度股利支付率(年度现金分红比例(已宣告))
    MV = 'MV' # 总市值
    CIRCULATEMV = 'CIRCULATEMV' # 流通市值
    PE = 'PE' # 市盈率
    PETTM = 'PETTM' # PETTM
    PB = 'PB' # 市净率
    YOYOR = 'YOYOR' # 营业收入同比增长率(Year-over-Year Operating Revenue)
    YOYNI = 'YOYNI' # 净利润同步增长率(Year-over-Year Net Income)
    CAGRTOR = 'CAGRTOR' # 营业总收入复合增长率(Compound Annual Growth Rate Total Operating revenue)
    GPMARGIN = 'GPMARGIN' # 毛利率
    NPMARGIN= 'NPMARGIN' # 净利率
    DIVIDENDYIELD = 'DIVIDENDYIELD' # 股息率
    DIVIDENDYIELDTTM = 'DIVIDENDYIELDTTM' # 股息率TTM
    HOLDNUM = 'HOLDNUM' # 股东户数
    
    # 财务报表-利润表
    INCOMESTATEMENT_NI = 'INCOMESTATEMENT_NI' # 净利润
    
    # 财务报表-现金流量表
    CASHFLOWSTATEMENT_NCFO = 'CASHFLOWSTATEMENT_NCFO' # 经营活动产生的现金流量净额
    CASHFLOWSTATEMENT_CASHEND = 'CASHFLOWSTATEMENT_CASHEND' # 会计期末的现金及现金等价物余额
    

    
# ctr专题函数的字段
class CtrIndicator(Enum):
    FUNDCODE = 'FUNDCODE' # 基金代码
    SECUCODE = 'SECUCODE' # 股票代码
    SECUNAME = 'SECUNAME' # 股票名称
    MVRATIO = 'MVRATIO' # 股票持仓市值占比

class MyCurrency(Enum):
    CNY = 2
    USD = 3
    HKD = 4

class MyExchange(Enum):
    SH = 'SH'
    SZ = 'SZ'
    HK = 'HK'
    BJ = 'BJ'

    N = 'N'
    O = 'O'
    A = 'A'
    F = 'F'
    
    DCE = 'DCE'
    SHF = 'SHF'
    CZC = 'CZC'
    GFE = 'GFE'
    INE = 'INE'
    CFE = 'CFE'

EXCHANGE2MY_CURRENCY = {
    Exchange.SSE: MyCurrency.CNY,
    Exchange.SZSE: MyCurrency.CNY,
    Exchange.BSE: MyCurrency.CNY,
    Exchange.SEHK: MyCurrency.HKD,
    Exchange.SMART: MyCurrency.USD
}

# EXCHANGE_KS2MY = {
#     Exchange.SSE: MyExchange.SH,
#     Exchange.SZSE: MyExchange.SZ,
#     Exchange.SEHK: MyExchange.HK,
#     Exchange.BSE: MyExchange.BJ
# }

EXCHANGE_MY2KS = {
    MyExchange.A: Exchange.AMEX,
    MyExchange.O: Exchange.NASDAQ,
    MyExchange.N: Exchange.NYSE,
    MyExchange.F: Exchange.OTC,

    MyExchange.SH: Exchange.SSE,
    MyExchange.SZ: Exchange.SZSE,
    MyExchange.BJ: Exchange.BSE,

    MyExchange.HK: Exchange.SEHK,
    
    MyExchange.DCE: Exchange.DCE,
    MyExchange.SHF: Exchange.SHFE,
    MyExchange.CZC: Exchange.CZCE,
    MyExchange.GFE: Exchange.GFEX,
    MyExchange.INE: Exchange.INE,
    MyExchange.CFE: Exchange.CFFEX
}

EXCHANGE_KS2MY = {v:k for k,v in EXCHANGE_MY2KS.items()}

# 标准字段映射为东财字段(只有需要映射才需要定义，例如ROA就是对应ROA，不需映射)
INDICATORS_KS2MY = {
    # ROE (chice面板上，沪深股票是ROEWA；港股是ROEAVG)
    'ROE.CNSE': 'ROEAVG',
    'ROE.SEHK': 'ROEAVG',
    'ROE.SMART': 'ROEAVG',
    
    'LIBILITYTOASSET.CNSE': 'LIBILITYTOASSETRPT',
    'LIBILITYTOASSET.SEHK': 'LIBILITYTOASSET',
    'LIBILITYTOASSET.SMART': 'LIBILITYTOASSET',

    'DIVANNUPAYRATE.CNSE': 'DIVANNUPAYRATE',
    'DIVANNUPAYRATE.SEHK': 'DIVANNUACCUMRATIO',
    'DIVANNUPAYRATE.SMART': 'DIVANNUACCUMRATIO',

    'MV.CNSE': 'MV',
    'MV.SEHK': 'MV',
    'MV.SMART': 'MV',
    
    'CIRCULATEMV.CNSE': 'CIRCULATEMV',
    'CIRCULATEMV.SEHK': 'LIQMV',
    'CIRCULATEMV.SMART': 'LIQMV',

    'PE.CNSE': 'PELYR',
    'PE.SEHK': 'PELYR',
    'PE.SMART': 'PELYR',

    'PB.CNSE': 'PBMRQ',
    'PB.SEHK': 'PBMRQ',
    'PB.SMART': 'PBMRQ',
    
    'YOYOR.CNSE': 'YOYOR',
    'YOYOR.SEHK': 'GR1YGROWTHRATE',
    'YOYOR.SMART': 'GR1YGROWTHRATE',
    
    'CAGRTOR.CNSE': 'CAGRGR',
    'CAGRTOR.SEHK': 'CAGRGR',
    'CAGRTOR.SMART': 'CAGRGR',
    
    'INCOMESTATEMENT_NI.CNSE': 'INCOMESTATEMENT_61',
    'INCOMESTATEMENT_NI.SEHK': 'NETPROFIT',
    'INCOMESTATEMENT_NI.SMART': 'NETPROFIT',
    
    'CASHFLOWSTATEMENT_NCFO.CNSE': 'CASHFLOWSTATEMENT_39',
    'CASHFLOWSTATEMENT_NCFO.SEHK': 'CASHFLOWSTATEMENT',
    'CASHFLOWSTATEMENT_NCFO.SMART': 'CASHFLOWSTATEMENT',
    
    'CASHFLOWSTATEMENT_CASHEND.CNSE': 'CASHFLOWSTATEMENT_84',
    'CASHFLOWSTATEMENT_CASHEND.SEHK': 'CASHEND',
    'CASHFLOWSTATEMENT_CASHEND.SMART': 'CASHEND',
    
    'DIVIDENDYIELDTTM.CNSE': 'DIVIDENDTTM', # 最近12个月的股息率和股息率TTM不一样！！！ 港美目前只有12个月没有TTM
    'DIVIDENDYIELDTTM.SEHK': 'DIVIDENDYIELDY',
    'DIVIDENDYIELDTTM.SMART': 'DIVIDENDYIELDY',
    
    'HOLDNUM.CNSE': 'STMTHOLDTNUM',
    'HOLDNUM.SEHK': '',
    'HOLDNUM.SMART': '',
    
    ## 下面是行情的
    MarketIndicator.open.name: 'OPEN',
    MarketIndicator.high.name: 'HIGH',
    MarketIndicator.low.name: 'LOW',
    MarketIndicator.close.name: 'CLOSE',
    MarketIndicator.volume.name: 'VOLUME',
    MarketIndicator.turnover.name: 'AMOUNT',
    MarketIndicator.open_interest.name: 'HQOI'
}

INDICATORS_MY2KS = {v:'.'.join(k.split('.')[:-1]) if '.' in k else k for k,v in INDICATORS_KS2MY.items()}

EXCHANGE_PRODUCT2PUKEYCODE = {
    'CNSE.EQUITY': '001071',
    'SEHK.EQUITY': '401001',
    'SMART.EQUITY': '202001004',

    'CNSE.ETF': '507001',
    'SEHK.ETF': '404004',
    'SMART.ETF': '202003009',
    
    'CNFE.FUTURES': '715001'
}

STATEMENT_EXCHANGE2ITEMS_CODE = {
    'CASHFLOWSTATEMENT.SEHK': 39,
    'CASHFLOWSTATEMENT.SMART': 28
}

#  EMI01709159 均价:氧化铝, EMM00195469 国内现货价格:批发价:苹果, EMI01763401 实物黄金:中国黄金:基础金价, EMI00240995 价格:15厘胶合板, EMI00546343 出厂价:顺丁橡胶(BR9000):独山子石化(中石油华北销售), EMI01639663 
# 现货价格:石油沥青, EMI00000271 现货价:棉花:新疆
SPOT_SYMBOL_KS2MY = {
    'AL6': 'EMI01639685', #  豆一
    'ADL6': 'EMI01778933', # 铸造铝合金
    'AGL6': 'EMI01639662', # 白银
    'ALL6': 'EMI01639656', # 沪铝
    'AOL6': 'EMI01709159', # 氧化铝
    'APL6': 'EMI01004652', # 苹果
    'AUL6': 'EMI01639657', # 金
    
    # 大连交易所
    'CL6': 'EM101629225', # 玉米
    'AL6': 'EMI01629226', # 豆一
    'YL6': 'EMI01629228', # 豆油
    'PL6': 'EMI01629229', # 棕榈油
    'LL6': 'EM01629230', # 聚乙烯(塑料)
    'VL6': 'EMI01629231', # 聚氯乙烯(PVC)
    'JL6': 'EMI01629232', # 焦炭
    'PPL6': 'EMI01629233', # 聚丙烯
    
    # 郑商所
    'WHL6': 'EMI01629211', # 强麦
    'CFL6':'EMI01629212', # 棉花
    'SRL6':'EMI01629213', # 白糖
    'OIL6':'EMI01629214', # 菜籽油(菜油)
    'MAL6':'EMI01629215', # 甲醇
    
    # 其他
    'BRL6': 'EMI00546344', # 顺丁橡胶
    'CJL6': 'EMI01907585', # 红枣
    'CYL6': 'EMI01732836', # 棉纱
    'EBL6': 'EMI01727409', # 苯乙烯
    'EGL6': 'EMI00545410', # 乙二醇
    'JMf6': 'EMI01871292', # 焦煤
    'LCL6': 'EMI01814282', # 碳酸锂
    'PRL6': 'EMI01886051', # 瓶片
    'PSL6': 'EMI01774296', # 多晶硅
    'SAL6': 'EMI01646351', # 纯碱
    'SCL6': 'EMI00010844', # 原油
    'SHL6': 'EMI01727410', # 烧碱
    'SIL6': 'EMI01779627', # 工业硅
    'SPL6': 'EMI01734555', # 纸浆
    'SSL6': 'EMI01726944', # 不锈钢
    'URL6': 'EMI01639189', # 尿素
    
    # 生意社
    'CUL6': 'EMI01639653', # 铜
    'RBL6': 'EMI01639654', # 螺纹钢
    'ZNL6': 'EMI01639655', # 锌
    'ALL6': 'EMI01639656', # 铝
    'AUL6': 'EMI01639657', # 黄金
    'WRL6': 'EMI01639658', # 线材
    'RUL6': 'EMI01639660', # 天然橡胶
    'PBL6': 'EMI01639661', # 铅
    'AGL6': 'EMI01639662', # 白银
    'BUL6': 'EMI01639663', # 石油沥青
    'HCL6': 'EMI01639664', # 热卷
    'NIL6': 'EMI01639665', # 镍
    'SNL6': 'EMI01639666', # 锡
    'TAL6': 'EMI01639667', # PTA
    'SRL6': 'EMI01639668', # 白糖
    'CFL6': 'EMI01639669', # 棉花
    'PML6': 'EMI01639670', # 普麦
    'OIL6': 'EMI01639671', # 菜油
    'FGL6': 'EMI01814166', # 玻璃
    'RML6': 'EMI01639674', # 菜粕
    'RSL6': 'EMI01639675', # 菜籽
    'SFL6': 'EMI01639678', # 硅铁
    'SML6': 'EMI01639679', # 锰硅
    'MAL6': 'EMI01639680', # 甲醇
    'PL6': 'EMI01639682',  # 棕榈油
    'VL6': 'EMI01639683',  # PVC
    'LL6': 'EMI01639684',  # 聚乙烯
    'AL6': 'EMI01639685',  # 豆一
    'ML6': 'EMI01639686',  # 豆粕
    'YL6': 'EMI01639687',  # 豆油
    'CL6': 'EMI01639688',  # 玉米
    'IL6': 'EMI01639691',  # 铁矿石
    'JDL6': 'EMI01639692', # 鸡蛋
    'PPL6': 'EMI01639695', # 聚丙烯
    'CSL6': 'EMI01639696', # 玉米淀粉
    
    # 'AGL6': 'EMI01639662',
    # 'AL6': 'EMI01639685',
    # 'ALL6': 'EMI01639656',
    # 'AOL6': 'EMI01709159',
    # 'APL6': 'EMM00195469',
    # 'AUL6': 'EMI01763401',
    # 'BBL6': 'EMI00240995',
    # 'BUL6': 'EMI01639663',
    # 'CFL6': 'EMI01629212',
    # 'CJL6': 'EMI01907585',
    # 'CL6': 'EMI01775207',
    # 'CSL6': 'EMI01773611',
    # 'CUL6': 'EMI01732836',
    # 'CYL6': 'EMI01755856',
    # 'EGL6': 'EMI00545410',
    # 'FGL6': 'EMI01819054',
    # 'FUL6': 'EMI01711023',
    # 'HCL6': 'EMI01809055',
    # 'IL6': 'EMI00064807',
    # 'JDL6': 'EMI01547110',
    # 'JL6': 'EMI01629232',
    # 'JML6': 'EMI01808710',
    # 'LCL6': 'EMI01813613',
    # 'LHL6': 'EMI01669879',
    # 'LL6': 'EMI01629230',
    # 'LRL6': 'EMI01627510',
    # 'MAL6': 'EMI00545353',
    # 'ML6': 'EMI01765340',
    # 'NIL6': 'EMI01639665',
    # 'PBL6': 'EMI01629219',
    # 'PGL6': 'EMI01946149',
    # 'PL6': 'EMI01765356',
    # 'PML6': 'EMI01639670',
    # 'PPL6': 'EMI01629233',
    # 'PRL6': 'EMI01874023',
    # 'PSL6': 'EMI01813883'
}
SPOT_SYMBOL_MY2KS = {v:k for k,v in SPOT_SYMBOL_KS2MY.items()}

class CtrMethod(Enum):
    FundIHolderStockDetailInfo = 'FundIHolderStockDetailInfo'

def extract_my_symbol(my_symbol):
    items = my_symbol.split(".")
    try: 
        exchange = MyExchange(items[-1])
    except:
        exchange = np.nan
    return '.'.join(items[:-1]), exchange

def symbol_ks2my(vt_symbol: str, sub_exchange: Exchange = None):
    if not vt_symbol:
        return ''
    symbol, ks_exchange = extract_vt_symbol(vt_symbol)
    symbol = symbol.replace('.', '_')
    
    # 把KS期货的代码转为东财的标准格式
    if sub_exchange in [Exchange.SHFE, Exchange.DCE, Exchange.CZCE, Exchange.GFEX, Exchange.INE, Exchange.CFFEX]:
        suffix = 'M' if sub_exchange in [Exchange.INE, Exchange.CFFEX, Exchange.GFEX] else '0'
        if symbol[-2:] in ['L8']:
            symbol = symbol[:-2] + suffix
        symbol = symbol
    
    # 现货属于edb，只有id没有交易所后缀
    if ks_exchange in [Exchange.OTC]:
        symbol = SPOT_SYMBOL_KS2MY.get(symbol, symbol)
        return symbol
    
    if not sub_exchange:
        my_symbol = generate_vt_symbol(symbol, ks_exchange)
    else:
        my_symbol = generate_vt_symbol(symbol, EXCHANGE_KS2MY.get(sub_exchange))
    return my_symbol

def symbol_my2ks(my_symbol: str):
    if not my_symbol:
        return ''
    symbol, my_exchange = extract_my_symbol(my_symbol)
    symbol = symbol.replace('_', '.') # 东财使用下划线，而我们根据futu的用了.
    
    # 把期货的代码转为KS的标准格式
    if my_exchange in [MyExchange.SHF, MyExchange.DCE, MyExchange.CZC, MyExchange.GFE, MyExchange.INE, MyExchange.CFE]:
        matched = re.search(r'([a-zA-Z]+)([0-9a-zA-Z])', symbol)
        assert matched
        alphabet = matched.group(1)
        date = matched.group(2)
        # 主力连续合约
        if date in ['0', 'm', 'M']:
            date = 'L8'
        symbol = f'{alphabet.upper()}{date}'
    
    return generate_vt_symbol(symbol, SUB_EXCHANGE2EXCHANGE.get(EXCHANGE_MY2KS.get(my_exchange, Exchange.UNKNOW)))

def symbol_my2sub_exchange(my_symbol: str):
    if not my_symbol:
        return ''
    symbol, my_exchange = extract_my_symbol(my_symbol)
    
    return EXCHANGE_MY2KS.get(my_exchange).value

# 用于mry，把为None的数据剔除，并且补齐性质
def clean_group(indicators: list[str] = [], n: int = 3):
    def fn(group):
        cleaned = pd.DataFrame()
        for col in group.columns:
            group_len = len(group)
            if col in indicators:
                # 把开头和结尾的空值都给去掉
                s = group[col].fillna(np.nan)
                start = s.first_valid_index()
                end = s.last_valid_index()
                non_na = s.loc[start:end]
                # 这里是因为某些指标没有制定日期的数据会往前滚动取数，所以导致重复，所以删除头两行一致的其中一行
                non_na = non_na.drop([x for x in non_na.duplicated()[lambda x: x].index if x < 2]) 
                series = non_na.reset_index(drop=True)
                series = series.reindex(range(len(group)))
                cleaned[col] = series
            else:
                cleaned[col] = group[col].reset_index(drop=True)
        return cleaned.head(n)
    return fn


class KsEastmoneyFundamentalApi(BaseFundamentalApi):
    gateway_name: str = "KS_EASTMONEY_FUNDAMENTAL"

    def __init__(self, setting: dict):
        dd_secret = setting.get('dd_secret')
        dd_token = setting.get('dd_token')
        gateway_name = setting.get('gateway_name', self.gateway_name)
        super().__init__(gateway_name=gateway_name, dd_secret=dd_secret, dd_token=dd_token)

        self.setting = setting
        self.login()

    def login(self):
        username = self.setting.get('username')
        password = self.setting.get('password')
        startoptions = "ForceLogin=1" + ",UserName=" + username + ",Password=" + password;
        loginResult = c.start(startoptions, '')
        self.log(loginResult, '登录结果')

    def _normalization_indicators_input(self, indicators: str, exchange: Exchange):
        indicators_list = indicators.split(',')
        indicators_new = [INDICATORS_KS2MY.get(f'{x}.{exchange.value}', x) for x in indicators_list if INDICATORS_KS2MY.get(f'{x}.{exchange.value}', x)]
        return ','.join(indicators_new)
    
    def _normalization_indicators_output(self, df: DataFrame):
        rename_columns = {x:INDICATORS_MY2KS[x] for x in df.columns if x in INDICATORS_MY2KS}
        return df.rename(columns=rename_columns)

    # 暂时不支持跨市场多标的，使用第一个表的市场来决定所有标的的市场
    # sub_exchange是用来做美股区分，东财
    def css(self, vt_symbols: list[str], indicators: str = '', options: str = '', sub_exchanges: list[str] = []) -> tuple[RetCode, pd.DataFrame]:
        if not vt_symbols:
            return None
        
        _indicators = indicators
        symbol, exchange = extract_vt_symbol(vt_symbols[0])
        indicators = self._normalization_indicators_input(indicators, exchange)

        # 默认pandas返回
        if not 'IsPandas' in options:
            options += ',IsPandas=1'

        if not 'TradeDate' in options:
            options += f',TradeDate={get_date_str()}'
        
        if not 'N=' in options: # CAGRTOR需要N参数
            options += ',N=3'    

        year = datetimes.now().year
        if not 'Year' in options:      
            options += f',Year={year}'

        if not 'PayYear' in options:
            options += f',PayYear={year}'

        if not 'ReportDate' in options:
            options += ',ReportDate=MRQ'

        if not 'CurType' in options:
            # options += f',CurType={EXCHANGE2MY_CURRENCY.get(exchange).value}'
            options += f',CurType=1' # 使用原始币种，港股-人民币

        if 'ROETTM' in indicators:
            options += ',TtmType=1'

        if 'LIBILITYTOASSETRPT' in indicators:
            options += ',Type=3' # 合并报表（调整后）
            
        if 'STATEMENT' in indicators:
            statement_matched = re.search(r'([^,]+STATEMENT\b)', indicators)
            if statement_matched:
                statement_indicator = statement_matched.groups()[0]
                ItemsCode = STATEMENT_EXCHANGE2ITEMS_CODE.get(f'{statement_indicator}.{exchange.value}')
                options += f',ItemsCode={ItemsCode}' # 合并报表（调整后）

        # if 'BPS' in indicators:
        #     options += f',CurType={EXCHANGE2MY_CURRENCY.get(exchange).value}'

        my_symbols = [symbol_ks2my(x, Exchange(sub_exchanges[i]) if len(sub_exchanges) and sub_exchanges[i] else None) for i,x in enumerate(vt_symbols)]
        df = c.css(my_symbols, indicators=indicators, options=options)
        if isinstance(df, c.EmQuantData):
            return RET_ERROR, str(df)
        
        df.reset_index(drop=False, inplace=True)

        # 转换symbol
        df['CODES'] = df['CODES'].transform(symbol_my2ks)
        df.rename(columns={'CODES': 'vt_symbol'}, inplace=True)

        # LIBILITYTOASSET: 港美的是百分号，A股是小数
        if 'LIBILITYTOASSET' in df.columns:
            is_cn = df.vt_symbol.str.endswith('.SSE') | df.vt_symbol.str.endswith('.SZSE') | df.vt_symbol.str.endswith('.CNSE')
            df.loc[is_cn, 'LIBILITYTOASSET'] = df[is_cn]['LIBILITYTOASSET'] * 100

        df = self._normalization_indicators_output(df)
        
        # 把None转为np.nan
        df = df.infer_objects(copy=False).fillna(np.nan)
        
        # 有的字段是没有数据的，例如港美的HOLDNUM，要填充NAN
        # na_columns = [x for x in indicators_str if not x in cleaned.columns]
        # for na_column in na_columns:
        #     cleaned[na_column] = np.nan
        for column in _indicators.split(','):
            if column not in df.columns:
                df[column] = np.nan

        return RET_OK, df
    
    # alisa放阿飞
    css_mrq = css
    
    def _parse_options(self, options: str = '') -> dict:
        ret_options = {}
        for k,v in dict(x.strip().split('=') for x in options.split(',')).items():
            try:
                enumn_key = Params(k)
            except Exception as e:
                raise e
            ret_options[enumn_key] = v if not v.isdigit() else int(v)
        return ret_options
    
    def _generate_options(self, options: dict = {}) -> str:
        return ','.join([f'{k.name if isinstance(k, Enum) else k}={v}' for k,v in options.items()])
    
    def _parse_indicators(self, indicators: str = '', typing: typing = Enum) -> dict:
        ret_indicators = []
        for k in [x.strip() for x in indicators.split(',')]:
            if typing == str:
                key = k
            else:
                try:
                    key = Indicator(k)
                except Exception as e:
                    raise e
            ret_indicators.append(key)
        return ret_indicators
    
    def _generate_indicators(self, indicators: dict = {}) -> str:
        return ','.join([x.name if isinstance(x, Enum) else x for x in indicators])
    
    # 获取最近N年的数据例如2024-12-31, 2023-12-31, 2022-12-31
    def css_mry(self, vt_symbols: list[str], indicators: str = '', options: str = '', sub_exchanges: list[str] = []) -> pd.DataFrame:
        try:
            options = self._parse_options(options)
            n = options[Params.MRYN]
            
            # 因为年报公布延迟，年初的时候没有当年和前一年的数据，所以要取N个数据必须是N+2年
            y0 = datetimes.now().replace(month=12, day=31)
            dates = [(y0-relativedelta(years=i)).strftime(DATE_FMT) for i in range(n+2)]
            del options[Params.MRYN]
            all_df = pd.DataFrame()
            for date in dates:
                options[Params.ReportDate] = date
                options[Params.TradeDate] = date
                year = date[:4]
                options[Params.Year] = year
                options[Params.PayYear] = year
                other_options = self._generate_options(options)
                ret, df = self.css(
                    vt_symbols=vt_symbols,
                    indicators=indicators,
                    options=other_options,
                    sub_exchanges=sub_exchanges
                )
                if ret == RET_ERROR:
                    return RET_ERROR, df
                df['DATES'] = date
                all_df = pd.concat([all_df, df], ignore_index=True)

            indicators_str = self._parse_indicators(indicators, typing=str)
            all_df = all_df.fillna(np.nan)
            cleaned = all_df.groupby('vt_symbol', group_keys=False).apply(clean_group(indicators=indicators_str, n=n))
            
            table = cleaned.reset_index(drop=False).pivot(index='vt_symbol', columns='index', values=indicators_str)
            table.columns = [f"{col[0]}_MRY{col[1]}" for col in table.columns]
            table = table.loc[vt_symbols] # 按照传入的顺序组织顺组，因为pivot把顺序弄乱了
            table.reset_index(drop=False, inplace=True)
            return RET_OK, table
                
            
        except Exception as e:
            return RET_ERROR, traceback.format_exc()
    
    def sector(self, exchange: Exchange, products: list[Product], tradedate: str = None):
        if not tradedate:
            tradedate = get_date_str()
        # 默认pandas返回
        options = 'IsPandas=1'

        all_df = pd.DataFrame()
        for product in products:
            pukeycode = EXCHANGE_PRODUCT2PUKEYCODE.get(f'{exchange.name}.{product.name}')
            df = c.sector(pukeycode, tradedate, options)
            df['vt_symbol'] = df['SECUCODE'].transform(symbol_my2ks)
            df['sub_exchange'] = df['SECUCODE'].transform(symbol_my2sub_exchange)
            df['name'] = df['SECURITYSHORTNAME']
            df['product'] = product.name

            all_df = pd.concat([all_df, df[['vt_symbol', 'name', 'sub_exchange', 'product']]], ignore_index=True)
            
        # 如果是期货，需要增加中金所支持，东财的主力连续期货只有商品期货
        # if Product.FUTURES in products:
        #     cf_df = c.sector('701001', tradedate, options)
        #     cf_df['vt_symbol'] = cf_df['SECUCODE'].transform(symbol_my2ks)
        #     cf_df['sub_exchange'] = cf_df['SECUCODE'].transform(symbol_my2sub_exchange)
        #     cf_df['name'] = cf_df['SECURITYSHORTNAME']
        #     cf_df['product'] = product.name
        #     cf_df = cf_df[cf_df['name'].str.contains('主力连续')]
        #     all_df = pd.concat([all_df, cf_df[['vt_symbol', 'name', 'sub_exchange', 'product']]], ignore_index=True)
            
        return RET_OK, all_df
    
    def ctr(self, method: str, indicators: list[str], options: str = ''):
        try:
            CtrMethod(method)
        except:
            raise Exception(f'{method} not in CtrMethod')
            
        options_dict = self._parse_options(options)
        if not Params.ReportDate in options_dict:
            if Params.FundCode in options_dict:
                # 获取基金最新报告期
                res = c.css(options_dict[Params.FundCode], "LASTREPORTDATE", f"EndDate={get_date_str()},dataType=1")
                if not res.ErrorCode == 0:
                    raise Exception(str(res))
                options_dict[Params.ReportDate] = res.Data[options_dict[Params.FundCode]][0]
        
        if not Params.IsPandas in options_dict:
            options_dict[Params.IsPandas] = 1
        
        if not CtrIndicator.FUNDCODE.value in indicators:
            indicators += f',{CtrIndicator.FUNDCODE.value}'
            
        if not CtrIndicator.SECUCODE.value in indicators:
            indicators += f',{CtrIndicator.SECUCODE.value}'
            
        options_str = self._generate_options(options_dict)
           
        df = c.ctr(method, indicators, options_str)
        if isinstance(df, c.EmQuantData) and df.ErrorCode in [0, 10000009]:
            raise Exception(str(df))
        
        df['vt_symbol'] = df['SECUCODE'].transform(symbol_my2ks)
        
        return df
    
    def csd(self, vt_symbols: list[str], indicators: str = '', start: str = '', end: str = '', options: str = '', sub_exchanges: list[str] = []) -> tuple[RetCode, pd.DataFrame]:
        my_symbols = [symbol_ks2my(x, Exchange(sub_exchanges[i]) if len(sub_exchanges) and sub_exchanges[i] else None) for i,x in enumerate(vt_symbols)]
        
        # 默认pandas返回
        if not 'IsPandas' in options:
            options += ',IsPandas=1'
        
        df = c.csd(codes=my_symbols, indicators=indicators, startdate=start, enddate=end, options=options)
        df = df.reset_index(drop=False)
        df['vt_symbol'] = df['CODES'].transform(symbol_my2ks)
        df['datetime'] = pd.to_datetime(df['DATES']).dt.tz_localize('PRC')
        rename_columns = {x: INDICATORS_MY2KS[x] for x in df.columns if x in INDICATORS_MY2KS}
        df.rename(columns=rename_columns, inplace=True)
        df.drop(columns=['CODES', 'DATES'], inplace=True)
        return df
    
    def edb(self, vt_symbols: list[str], options: str = '', sub_exchanges: list[str] = []) -> tuple[RetCode, pd.DataFrame]:
        my_symbols = [symbol_ks2my(x, Exchange(sub_exchanges[i]) if len(sub_exchanges) and sub_exchanges[i] else None) for i,x in enumerate(vt_symbols)]
        
        # 默认pandas返回
        if not 'IsPandas' in options:
            options += ',IsPandas=1'
        
        df = c.edb(edbids=my_symbols, options=options)
        try:
            df = df.reset_index(drop=False)
        except:
            breakpoint()
        df['symbol'] = df['CODES'].transform(lambda x: SPOT_SYMBOL_MY2KS.get(x))
        df['exchange'] = sub_exchanges[0]
        df['vt_symbol'] = df['symbol'] + '.' + df['exchange']
        df['datetime'] = pd.to_datetime(df['DATES']).dt.tz_localize('PRC')

        df.drop(columns=['CODES', 'DATES'], inplace=True)
        
        # 修正价格 有的是以斤和公斤的价格，交割以吨
        df.loc[df.symbol.isin(['APL6']), 'RESULT'] = df[df.symbol.isin(['APL6'])]['RESULT'] * 1000
        df.loc[df.symbol.isin(['CJL6']), 'RESULT'] = df[df.symbol.isin(['CJL6'])]['RESULT'] * 2000
        df.loc[df.symbol.isin(['CYL6']), 'RESULT'] = df[df.symbol.isin(['CYL6'])]['RESULT'] * 2000
        df.loc[df.symbol.isin(['JDL6']), 'RESULT'] = df[df.symbol.isin(['JDL6'])]['RESULT'] * 500
        df.loc[df.symbol.isin(['PSL6']), 'RESULT'] = df[df.symbol.isin(['PSL6'])]['RESULT'] * 10000
        df.loc[df.symbol.isin(['SHL6']), 'RESULT'] = df[df.symbol.isin(['SHL6'])]['RESULT'] / 0.32
        
        return df
        

    # 关闭上下文连接
    def close(self):
        pass
        # self.quote_ctx.close()
        # self.trd_ctx.close()


        