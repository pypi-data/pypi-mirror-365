from decimal import Decimal
from datetime import datetime
import math

import pytest
import asyncio
from config import CONFIGS
from conftest import assert_debug, css
import numpy as np

@pytest.mark.asyncio
@pytest.mark.parametrize("fundamental_api", CONFIGS, indirect=True)
async def test_css_mry(fundamental_api):
    from ks_eastmoney_fundamental_api.ks_eastmoney_fundamental_api import Indicator
    indicators = ','.join([x.value for x in list(Indicator) if not x == Indicator.HOLDNUM]) # 港股美股没有HOLDNUM，剔除，否则运行是空指标出错
    # indicators = 'CASHFLOWSTATEMENT_NCFO'
    test_css_mrq_samples = [
        # {
        #     # 'vt_symbols': ['600519.SSE', '000001.SZSE', '832735.BSE'], # 先不测试北交所，好像有数据缺失
        #     'vt_symbols': ['600519.SSE', '000001.SZSE'],
        #     'indicators': indicators,
        #     'sub_exchanges': ['SSE', 'SZSE', 'BSE'],
        #     'options': ''
        # },
        # {
        #     'vt_symbols': ['00700.SEHK'],
        #     'indicators': indicators,
        #     'sub_exchanges': ['SEHK'],
        #     'options': ''
        # },
        {
            'vt_symbols': ['NVDA.SMART'],
            'indicators': indicators,
            'sub_exchanges': ['NASDAQ'],
            'options': ''
        }
    ]
    
    for i, config in enumerate(test_css_mrq_samples):
        # report_dates = ['2025-03-31']
        report_dates = ['2024-12-31']
        
        for indicator_str in config['indicators'].split(','):        
            indicator = Indicator(indicator_str)
            for date_i, report_date in enumerate(report_dates):
                year = report_date[:4]
                options = f'ReportDate={report_date},N=4,Year={year},PayYear={year}'
                
                print(f'=========No:{i} == ReportDate:{report_date} == Indicator:{indicator_str} =======')
                
                ret, ks_df = fundamental_api.css_mrq(
                    vt_symbols=config['vt_symbols'],
                    indicators=config['indicators'],
                    sub_exchanges=config['sub_exchanges'],
                    options=options
                )
                ks_df = ks_df.set_index('vt_symbol')
                
                my_df, my_symbols, my_indicator = css(
                    vt_symbols=config['vt_symbols'],
                    sub_exchanges=config['sub_exchanges'],
                    indicator=indicator,
                    options=options
                )
                for symbol_i, vt_symbol in enumerate(config['vt_symbols']):
                    if np.isnan(my_df.loc[my_symbols[symbol_i], my_indicator]):
                        assert_debug(np.isnan(ks_df.loc[vt_symbol, f'{indicator_str}']))
                    else:
                        assert_debug(my_df.loc[my_symbols[symbol_i], my_indicator] == ks_df.loc[vt_symbol, f'{indicator_str}'])
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
