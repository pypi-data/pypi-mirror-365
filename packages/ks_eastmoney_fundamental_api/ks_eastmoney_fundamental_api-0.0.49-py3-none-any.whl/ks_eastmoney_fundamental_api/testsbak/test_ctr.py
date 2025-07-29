from decimal import Decimal
from datetime import datetime
import math

import pytest
import asyncio
from fundamental_config import CONFIGS
from tests.conftest import assert_debug, css
import numpy as np

# @pytest.mark.asyncio
# @pytest.mark.parametrize("fundamental_api", CONFIGS, indirect=True)
# async def test_css(fundamental_api):
#     # res_cn = fundamental_api.css(
#     #     vt_symbols=['600519.SSE', '000001.SZSE'],
#     #     indicators='ROE,ROETTM,BPS,DIVIDENDYIELDY,LIBILITYTOASSET',
#     #     options='ReportDate=MRQ,TradeDate=2024-12-05'
#     # )
#     res_us = fundamental_api.css(
#         vt_symbols=['00700.SEHK', 'AAPL.SMART', 'AA.SMART', 'FNGZ.SMART'],
#         sub_exchanges=['', 'US_NASDAQ', 'US_NYSE', 'US_AMEX'],
#         indicators='ROE,ROETTM,BPS,DIVIDENDYIELDY,LIBILITYTOASSET',
#         options='ReportDate=MRQ,TradeDate=2024-12-05'
#     )
#     # print(res_cn)
#     print(res_us)
    # print('done')

# @pytest.mark.asyncio
# @pytest.mark.parametrize("fundamental_api", CONFIGS, indirect=True)
# async def test_sector(fundamental_api):
#     # res_cn = fundamental_api.css(
#     #     vt_symbols=['600519.SSE', '000001.SZSE', '430198.BSE'],
#     #     indicators='ROE,YOYOR,YOYNI,CAGRTOR',
#     #     sub_exchanges=['CN_SH', 'CN_SZ', 'CN_BJ'],
#     #     options='ReportDate=2024-12-31,Year=2024,N=3'
#     # )
#     # print(res_cn)

#     # res_hk = fundamental_api.css(
#     #     vt_symbols=['00700.SEHK'],
#     #     indicators='ROE,YOYOR,YOYNI,CAGRTOR',
#     #     sub_exchanges=['HK_MAINBOARD'],
#     #     options='ReportDate=2024-12-31,Year=2024,N=3'
#     # )
#     # print(res_hk)


#     # res_us = fundamental_api.css(
#     #     vt_symbols=['AAPL.SMART'],
#     #     indicators='ROE,YOYOR,YOYNI,CAGRTOR',
#     #     sub_exchanges=['US_NASDAQ'],
#     #     options='ReportDate=2024-12-31,Year=2024,N=3'
#     # )
#     # print(res_us)
    
#     # res_cn = fundamental_api.css(
#     #     vt_symbols=['600519.SSE', '000001.SZSE', '430198.BSE'],
#     #     indicators='PE,PB',
#     #     sub_exchanges=['CN_SH', 'CN_SZ', 'CN_BJ']
#     # )
#     # print(res_cn)

#     # res_hk = fundamental_api.css(
#     #     vt_symbols=['00700.SEHK'],
#     #     indicators='PE,PB',
#     #     sub_exchanges=['HK_MAINBOARD']
#     # )
#     # print(res_hk)


#     # res_us = fundamental_api.css(
#     #     vt_symbols=['AAPL.SMART'],
#     #     indicators='PE,PB',
#     #     sub_exchanges=['US_NASDAQ']
#     # )
#     # print(res_us)

#     # res_cn = fundamental_api.css(
#     #     vt_symbols=['600519.SSE', '000001.SZSE', '430198.BSE'],
#     #     indicators='MV,CIRCULATEMV',
#     #     sub_exchanges=['CN_SH', 'CN_SZ', 'CN_BJ']
#     # )
#     # print(res_cn)

#     # res_hk = fundamental_api.css(
#     #     vt_symbols=['00700.SEHK'],
#     #     indicators='MV,CIRCULATEMV',
#     #     sub_exchanges=['HK_MAINBOARD']
#     # )
#     # print(res_hk)

#     # res_us = fundamental_api.css(
#     #     vt_symbols=['AAPL.SMART'],
#     #     indicators='MV,CIRCULATEMV',
#     #     sub_exchanges=['US_NASDAQ']
#     # )
#     # print(res_us)

#     # res_cn = fundamental_api.css(
#     #     vt_symbols=['AAPL.SMART'],
#     #     indicators='PE',
#     #     sub_exchanges=['US_NASDAQ'],
#     #     options='ReportDate=MRQ,TradeDate=2024-12-14,Year=2023'
#     # )
#     # print(res_cn)
    
#     # res_cn = fundamental_api.css(
#     #     vt_symbols=['600519.SSE', '688001.SZSE'],
#     #     indicators='ROE,ROETTM,BPS,DIVIDENDYIELDY,LIBILITYTOASSET',
#     #     sub_exchanges=['CN_SH', 'CN_STIB'],
#     #     options='ReportDate=MRQ,TradeDate=2024-12-05'
#     # )
#     # print(res_cn)

#     # res_us = fundamental_api.css(
#     #     vt_symbols=['AAPL.SMART', 'AA.SMART'],
#     #     indicators='ROE,ROETTM,BPS,DIVIDENDYIELDY,LIBILITYTOASSET',
#     #     options='ReportDate=MRQ,TradeDate=2024-12-05',
#     #     sub_exchanges=['US_NASDAQ', 'US_NYSE']
#     # )
#     # print(res_us)

#     # from ks_trade_api.constant import Exchange, Product
#     # res_cn = fundamental_api.sector(
#     #     exchange=Exchange.CNSE,
#     #     products=[Product.EQUITY, Product.ETF]
#     # )
#     # print(res_cn)

#     # from ks_trade_api.constant import Exchange, Product
#     # res_hk = fundamental_api.sector(
#     #     exchange=Exchange.SEHK,
#     #     products=[Product.EQUITY, Product.ETF]
#     # )
#     # print(res_hk)

#     # from ks_trade_api.constant import Exchange, Product
#     # res_us = fundamental_api.sector(
#     #     exchange=Exchange.SMART,
#     #     products=[Product.EQUITY, Product.ETF]
#     # )
#     # print(res_us)
    
    
#     print('done')


@pytest.mark.asyncio
@pytest.mark.parametrize("fundamental_api", CONFIGS, indirect=True)
async def test_css_mry(fundamental_api):
    from ks_eastmoney_fundamental_api.ks_eastmoney_fundamental_api import CtrMethod, Params
    indicators = ''.join([x.value for x in list(CtrMethod)])
    # indicators = 'CASHFLOWSTATEMENT_NCFO'
    test_css_mrq_samples = [
        {
            # 'vt_symbols': ['600519.SSE', '000001.SZSE', '832735.BSE'], # 先不测试北交所，好像有数据缺失
            'vt_symbols': ['000043.OF'],
            'indicators': indicators,
            'sub_exchanges': ['CN_SH', 'CN_SZ', 'CN_BJ'],
            'options': ''
        },
        # {
        #     'vt_symbols': ['00700.SEHK'],
        #     'indicators': indicators,
        #     'sub_exchanges': ['HK_MAINBOARD'],
        #     'options': ''
        # },
        # {
        #     'vt_symbols': ['NVDA.SMART'],
        #     'indicators': indicators,
        #     'sub_exchanges': ['US_NASDAQ'],
        #     'options': ''
        # }
    ]
    
    for i, config in enumerate(test_css_mrq_samples):
        for method in config['indicators'].split(','):        
            options = f'{Params.FundCode.value}={config["vt_symbols"][0]}'
            ks_df = fundamental_api.ctr(
                method,
                indicators='FUNDCODE,SECUCODE,HOLDNUMBER,MVRATIO',
                options=options
            )
        print('pass√')

        # print(res[1])
        # assert_css_mry(res_cn)
    
    # res_hk = fundamental_api.css_mry(
    #     vt_symbols=['00700.SEHK'],
    #     indicators='ROE,YOYOR,YOYNI,CAGRTOR,DIVANNUPAYRATE',
    #     sub_exchanges=['HK_MAINBOARD'],
    #     options='MRQN=4,N=4'
    # )
    # print(res_hk)


    # res_us = fundamental_api.css_mry(
    #     vt_symbols=['AAPL.SMART'],
    #     indicators='ROE,YOYOR,YOYNI,CAGRTOR,DIVANNUPAYRATE',
    #     sub_exchanges=['US_NASDAQ'],
    #     options='MRQN=4,N=4'
    # )
    # print(res_us)
    
    print('done')
