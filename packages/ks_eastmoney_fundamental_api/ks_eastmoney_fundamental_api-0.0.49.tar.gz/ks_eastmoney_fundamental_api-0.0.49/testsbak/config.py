EXCHANGE = 'SMART'
# EXCHANGE = 'CZCE'
PRODUCT = 'EQUITY'
# PRODUCT = 'FUTURES'
# STRATEGY_NAME = 'IcebergStrategy'
# STRATEGY_NAME = 'VwapStrategy'
# STRATEGY_NAME = 'GridStrategy'
STRATEGY_NAME = 'IcebergStrategy'
POSITION_DIRECTION = 'LONG'
CONFIGS = [
    # { 'config_name': '.ttvntrader_ctptest', 'gateway_name': 'KS_CTP', 'setting': {'enable_short': False}},  
    # { 'config_name': '.ttvntrader_futu', 'gateway_name': 'KS_FUTU', 'gateway_config': { "trade_api": {"setting": {"acc_id.us": 9267789, "acc_id.hk": 9267788}}}, 'setting': {'enable_short': False}},
    { 'config_name': '.ttvntrader_tiger', 'gateway_name': 'KS_TIGER', 'setting': {'enable_short': False}},  
]