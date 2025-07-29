from decimal import Decimal
from datetime import datetime
import math

import pytest
import asyncio
from config import CONFIGS
from conftest import assert_debug, css
import numpy as np
import re    
    
indicators = 'ROE,GPMARGIN,NPMARGIN,YOYOR,YOYNI,CAGRTOR,DIVANNUPAYRATE,DIVIDENDYIELD,CASHFLOWSTATEMENT_NCFO,CASHFLOWSTATEMENT_CASHEND'
test_css_mry_samples = [
    {
        # 'vt_symbols': ['600519.SSE', '000001.SZSE', '832735.BSE'], # 先不测试北交所，好像有数据缺失
        'vt_symbols': ['600519.CNSE', '000001.CNSE'],
        'indicators': indicators,
        'sub_exchanges': ['SSE', 'SZSE', 'BSE'],
        'options': 'MRYN=5,N=4'
    },
     {
        'vt_symbols': ['00700.SEHK'],
        'indicators': indicators,
        'sub_exchanges': ['SEHK'],
        'options': 'MRYN=5,N=4'
    },
      {
        'vt_symbols': ['AAPL.SMART'],
        'indicators': indicators,
        'sub_exchanges': ['NASDAQ'],
        'options': 'MRYN=5,N=4'
    }
]

@pytest.mark.asyncio
@pytest.mark.parametrize("fundamental_api", CONFIGS, indirect=True)
async def test_css_mry(fundamental_api):
    from ks_eastmoney_fundamental_api.ks_eastmoney_fundamental_api import Indicator
    from ks_trade_api.utility import extract_vt_symbol
    from ks_trade_api.constant import Exchange, RET_OK
    
    for i, config in enumerate(test_css_mry_samples):
        ret, ks_df = fundamental_api.css_mry(
            vt_symbols=config['vt_symbols'],
            indicators=config['indicators'],
            sub_exchanges=config['sub_exchanges'],
            options=config['options']
        )
        assert_debug(ret == RET_OK)
        ks_df = ks_df.set_index('vt_symbol')
        print(f'=========No:{i}=========')
        
        report_dates = ['2024-12-31', '2023-12-31', '2022-12-31', '2021-12-31']
        
        symbol, exchange = extract_vt_symbol(config['vt_symbols'][0])
        ItemsCode = 28 if exchange == Exchange.SEHK else 29 # 美股28，港股29
        
        for indicator_str in config['indicators'].split(','):
            indicator = Indicator(indicator_str)
            for date_i, report_date in enumerate(report_dates):
                year = report_date[:4]
                my_df, my_symbols, my_indicator = css(
                    vt_symbols=config['vt_symbols'],
                    sub_exchanges=config['sub_exchanges'],
                    indicator=indicator,
                    options=f'ReportDate={report_date},N=4,Year={year},PayYear={year},ItemsCode={ItemsCode},TradeDate={report_date}'
                )
                for symbol_i, vt_symbol in enumerate(config['vt_symbols']):
                    if np.isnan(my_df.loc[my_symbols[symbol_i], my_indicator]):
                        assert_debug(np.isnan(ks_df.loc[vt_symbol, f'{indicator_str}_MRY{date_i}']))
                    else:
                        assert_debug(my_df.loc[my_symbols[symbol_i], my_indicator] == ks_df.loc[vt_symbol, f'{indicator_str}_MRY{date_i}'])
        print('pass√')

        # print(res[1])
        # assert_css_mry(res_cn)
    
    # res_hk = fundamental_api.css_mry(
    #     vt_symbols=['00700.SEHK'],
    #     indicators='ROE,YOYOR,YOYNI,CAGRTOR,DIVANNUPAYRATE',
    #     sub_exchanges=['SEHK'],
    #     options='MRYN=4,N=4'
    # )
    # print(res_hk)


    # res_us = fundamental_api.css_mry(
    #     vt_symbols=['AAPL.SMART'],
    #     indicators='ROE,YOYOR,YOYNI,CAGRTOR,DIVANNUPAYRATE',
    #     sub_exchanges=['SMART'],
    #     options='MRYN=4,N=4'
    # )
    # print(res_us)
    
    print('done')
