# conftest.py
import pytest
import os
import numpy as np
import re

def assert_debug(something):
    try:
        assert something
    except AssertionError as e:
        breakpoint()
        raise e
    
@pytest.fixture
def fundamental_api(request, monkeypatch):
    # 设置环境变量 CONFIG 的值
    CONFIG_NAME = request.param['config_name']
    GATEWAY_NAME = request.param['gateway_name']
    GATEWAY_CONFIG = request.param.get('gateway_config', {})
    SETTING = request.param.get('setting', {})
    TEST_VT_SYMBOLS = request.param.get('test_vt_symbols', {})

    monkeypatch.setenv('CONFIG', CONFIG_NAME)
    assert_debug(os.getenv('CONFIG') == CONFIG_NAME)

    from ks_trade_api.utility import load_json, get_file_path, save_json, remove_folder, get_folder_path

    gateway_config_name = 'gateway_config.json'
    gateway_config_path = get_file_path(gateway_config_name)
    config = load_json(gateway_config_path)
    file_name = config['fundamental_api']['name']
    setting = config['fundamental_api']['setting']

    import importlib
    module = importlib.import_module(file_name)
    class_name = file_name.title().replace('_', '')
    Class = getattr(module, class_name)
    return Class(setting)

def css(vt_symbols:list[str], sub_exchanges: list[str], indicator, options: str):
    from ks_eastmoney_fundamental_api.EmQuantAPI import c
    from ks_trade_api.constant import Exchange, SubExchange
    from ks_eastmoney_fundamental_api.ks_eastmoney_fundamental_api import symbol_ks2my, INDICATORS_KS2MY, Indicator, STATEMENT_EXCHANGE2ITEMS_CODE
    indicator: Indicator
    from ks_trade_api.utility import extract_vt_symbol
    
    _, exchange = extract_vt_symbol(vt_symbols[0])
    my_symbols = [symbol_ks2my(x, sub_exchange=Exchange(sub_exchanges[i])) for i,x in enumerate(vt_symbols)] 
    my_indicator = INDICATORS_KS2MY.get(f'{indicator.name}.{exchange.name}', indicator.name)
    
    options = f'{options},IsPandas=1'
    
    statement_matched = re.search(r'([^,]+STATEMENT\b)', my_indicator)
    if statement_matched:
        statement_indicator = statement_matched.groups()[0]
        ItemsCode = STATEMENT_EXCHANGE2ITEMS_CODE.get(f'{statement_indicator}.{exchange.value}')
        options += f',ItemsCode={ItemsCode}' # 合并报表（调整后）
                
    res = c.css(codes=my_symbols, indicators=my_indicator, options=options)
    if isinstance(res, c.EmQuantData):
        breakpoint()
    res = res.fillna(np.nan)
    return res, my_symbols, my_indicator

