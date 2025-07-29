# conftest.py
from logging import DEBUG, INFO, WARNING, ERROR
import pytest
import asyncio
from datetime import datetime
import os
from ks_utility.logs import LoggerBase
from ks_utility.jsons import json_load
from logging import DEBUG, INFO
from decimal import Decimal
from typing import Union, Tuple, Optional
import importlib
from pathlib import Path
from time import sleep
from .config import EXCHANGE, PRODUCT, STRATEGY_NAME, POSITION_DIRECTION
import numpy as np
import re

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

@pytest.fixture
def client(request, monkeypatch):
    # 设置环境变量 CONFIG 的值
    CONFIG_NAME = request.param['config_name']
    GATEWAY_NAME = request.param['gateway_name']
    GATEWAY_CONFIG = request.param.get('gateway_config', {})
    SETTING = request.param.get('setting', {})
    TEST_VT_SYMBOLS = request.param.get('test_vt_symbols', {})

    monkeypatch.setenv('CONFIG', CONFIG_NAME)
    assert_debug(os.getenv('CONFIG') == CONFIG_NAME)
    

    from ks_trade_api.utility import load_json, get_file_path, save_json, remove_folder, get_folder_path
    from ks_trade_api.utility import generate_vt_symbol, extract_vt_symbol, trade_side2direction_offset, is_option
    from ks_trade_api.constant import Direction, Offset, DIRECTION_MAP, Exchange, Product, Status,\
          RetCode, RET_ERROR, RET_OK, RET_ASYNC, TradeSide, ErrorCode, StrategyName
    from ks_trade_api.object import MyPositionData, MyBookData, MyOrderRequest, OrderType, MyOrderData, ErrorData, ContractData
    from vnpy_api.my_main_engine import MyMainEngine
    from vnpy_api.ks_longport_gateway import KsLongportGateway
    import importlib
    importlib.import_module('strategies.common.config_manager') 
    
    # 重新在如模块
    import ks_trade_api.utility
    importlib.reload(ks_trade_api.utility)
    from ks_trade_api.utility import load_json, get_file_path, save_json, remove_folder, get_folder_path

    # 先清理spit_trade的持久化文件 C:\Users\Administrator\.ttvntrader_longport\persistence
    remove_folder('persistence')

    class Client(LoggerBase):
        fake_market_order: bool = True
        per_volume: Decimal = Decimal('7000')
        test_vt_symbols: dict = {
            Product.EQUITY.name: {
                Exchange.SMART.name: 'NVDA.SMART',
                Exchange.SEHK.name: '00700.SEHK'
            },
            Product.OPTION.name: {
                Exchange.SMART.name: 'COIN240816P195000.SMART',
                Exchange.SEHK.name: 'TCH240829C210000.SEHK'
            },
            Product.FUTURES.name: {
                Exchange.CZCE.name: 'CJ509.CZCE'
            },
        }

        def __init__(self, CONFIG_NAME) -> None:
            super().__init__()

            split_config_name = f'{STRATEGY_NAME}.test.json'
            super().log(f'使用配置文件')
            super().log(f'ks_trader: {CONFIG_NAME}')
            super().log(f'split_trade: {split_config_name}')

            gateway_config_name = 'gateway_config.json'
            gateway_config_path = get_file_path(gateway_config_name)
            self.gateway_config_path = gateway_config_path
            
            CONFIG = load_json(gateway_config_path)
            if GATEWAY_CONFIG:
                for k, v in GATEWAY_CONFIG['trade_api']['setting'].items():
                    CONFIG['trade_api']['setting'][k] = v
                save_json(gateway_config_name, CONFIG)

            self.GATEWAY_NAME = CONFIG.get('gateway_name')

            # 改写symbol
            tpl_path = Path(__file__).parent.joinpath(f'test_{STRATEGY_NAME}/{split_config_name}')
            with open(tpl_path, encoding='utf8') as fp:
                split_config = json_load(fp)
            if TEST_VT_SYMBOLS:
                self.test_vt_symbols = TEST_VT_SYMBOLS
            vt_symbol = self.test_vt_symbols.get(PRODUCT).get(EXCHANGE)
            symbol, exchange = extract_vt_symbol(vt_symbol)
            split_config[0]['标的代码'] = symbol
            split_config[0]['金融市场'] = exchange.value
            split_config[0]['持仓方向'] = POSITION_DIRECTION

            save_json(split_config_name, split_config)

            cta_config_name = 'cta_strategy_config.json'
            strategy_config = load_json(cta_config_name)
            strategy_config[STRATEGY_NAME]['setting']['config.file_name'] = split_config_name
            strategy_config[STRATEGY_NAME]['setting']['running'] = '已关闭'
            strategy_config[STRATEGY_NAME]['setting']['enable_push'] = False
            for k, v in SETTING.items():
                strategy_config[STRATEGY_NAME]['setting'][k] = v
            save_json(cta_config_name, strategy_config)

            from vnpy_api.cta_trade import CTATrade
            cta_trade: CTATrade = CTATrade(CONFIG)
            self.cta_trade: CTATrade = cta_trade

            # return

            # 启动引擎，未启动策略
            self.cta_trade.start(start_strategies=False)
            assert_debug(cta_trade.is_test == 0)

            from vnpy_api.my_main_engine import MyMainEngine
            main_engine: MyMainEngine = cta_trade.cta_engine.main_engine
            self.main_engine: MyMainEngine = main_engine

            # 先找到split_trade的配置，根据标的来构造相应的持仓，然后再启动策略
            split_trade_config_path = get_file_path(split_config_name)
            SPLIT_CONFIGS = load_json(split_trade_config_path)
            if not SPLIT_CONFIGS:
                assert_debug(False)
                
            SPLIT_CONFIG = SPLIT_CONFIGS[0]
            self.config: dict = SPLIT_CONFIG
            
            self.symbol = SPLIT_CONFIG['标的代码']
            self.exchange: Exchange= Exchange(SPLIT_CONFIG['金融市场'])

            self.pos_direction: Direction = DIRECTION_MAP[POSITION_DIRECTION]
            self.vt_symbol: str = generate_vt_symbol(self.symbol, self.exchange)
            self.position_id = f'{GATEWAY_NAME}.{self.symbol}_{self.exchange.name}_{self.pos_direction.name}_'

            # 将trade_size映射为期货四键
            
            self.direction: Direction
            self.offset: Offset
            self.direction, self.offset = trade_side2direction_offset(TradeSide(SPLIT_CONFIG['交易方向']))

            gateway: KsLongportGateway = main_engine.get_gateway(GATEWAY_NAME)
            self.gateway = gateway

            # 改写代码
            self

        async def close(self, vt_symbol: Optional[str] = None, fake_market_order:bool = fake_market_order, per_volume: Decimal = per_volume) -> None:
            self.log('执行清仓开始...')
            
            GATEWAY_NAME = self.GATEWAY_NAME
            main_engine = self.main_engine
            if not vt_symbol:
                symbol = self.symbol
                exchange = self.exchange
                vt_symbol = generate_vt_symbol(symbol, exchange)
            else:
                symbol, exchange = extract_vt_symbol(vt_symbol)
            pos_direction = self.pos_direction
            
            position_id = f'{GATEWAY_NAME}.{symbol}_{exchange.name}_{pos_direction.name}_'
            position = main_engine.get_position(position_id)
            while position and position.volume:
                self.log(f'当前持仓: {position.volume}')
                
                if position.volume > 0:
                    direction: Direction = Direction.SHORT
                else:
                    direction: Direction = Direction.LONG
                product: Product = Product.OPTION if is_option(vt_symbol) else Product.EQUITY
                if not fake_market_order:
                    order_request: MyOrderRequest = MyOrderRequest(
                        symbol=symbol,
                        exchange=exchange,
                        direction=direction,
                        offset=Offset.CLOSE,
                        type=OrderType.MARKET,
                        volume=abs(position.volume),
                        price=None,
                        product=product
                    )
                else:
                    volume = abs(position.volume)
                    if per_volume:
                        volume = min(abs(per_volume), abs(position.volume))
                    ret, book = main_engine.gateways[GATEWAY_NAME].market_api.query_book(vt_symbol=vt_symbol)
                    order_request: MyOrderRequest = MyOrderRequest(
                        symbol=symbol,
                        exchange=exchange,
                        direction=direction,
                        offset=Offset.CLOSE,
                        type=OrderType.LIMIT,
                        volume=volume,
                        price=book.ask_price_1 if direction == Direction.LONG else book.bid_price_1,
                        product=product
                    )
                ret, data = main_engine.send_order(order_request, GATEWAY_NAME)
                if ret == RET_ERROR:
                    assert_debug(False)
                await asyncio.sleep(3)
                ret, positions = await self.query_position(vt_symbol)
                if ret == RET_ERROR:
                    assert_debug(False)
                position = positions[0]
            self.log(f'执行清仓完成.')
            
            # self.log('执行清仓开始...')
            # while True:
            #     ret, data = await self.async_get_positions(vt_symbol=vt_symbol)
            #     if ret == RET_ERROR:
            #         assert_debug(False)
                
            #     if not data or data[-1].volume == 0:
            #         self.log(f'执行清仓完成.')
            #         return RET_OK, None
            #     position: MyPositionData = self.get_position(position_id=position_id)
            #     self.log(f'当前持仓: {data and data[-1].volume}')
            #     await asyncio.sleep(1)
                
        async def buy(self, target_amount: Decimal, vt_symbol: Optional[str] = None, fake_market_order: bool = fake_market_order) -> None:
            self.log(f'执行买入到持仓为{target_amount}开始...')
            vt_symbol = vt_symbol or self.vt_symbol

            await self.close(vt_symbol=vt_symbol, fake_market_order=fake_market_order)

            self._buy(volume=target_amount, vt_symbol=vt_symbol, fake_market_order=fake_market_order)

            
            while True:
                ret, data = await self.async_get_positions(vt_symbol=vt_symbol)
                if ret == RET_ERROR:
                    assert_debug(False)
              
                if data and data[0].volume == target_amount:
                    self.log(f'执行买入到持仓为{target_amount}结束.')
                    await asyncio.sleep(2) # 由于策略使用timer来更新持仓，需要给定时间来等持仓更新
                    return RET_OK, None
                position: MyPositionData = self.get_position()
                self.log(f'目标持仓:{target_amount}, 当前持仓: {data and data[0].volume}')
                await asyncio.sleep(1)



        # 买入到可用资金不足
        async def buy_out(self, volume: Decimal, price: Decimal=None) -> None:
            self.log(f'执行买到资金不足开始...')

            ret, vt_orderid = self._buy(volume, price=price)
            if ret == RET_ERROR:
                if not vt_orderid.code == ErrorCode.BUY_POWER_EXCEEDED:
                    self.log(vt_orderid, level=ERROR)
                    assert_debug(False)

            if ret == RET_OK:
                while True:
                    if not ret == RET_ERROR:
                        order: MyOrderData = client.get_order(vt_orderid)
                        if order.status == Status.REJECTED:
                            break
                    if ret == RET_ERROR:
                        if not vt_orderid.code == ErrorCode.BUY_POWER_EXCEEDED:
                            self.log(vt_orderid, level=ERROR)
                            assert_debug(False)
                        else:
                            break
                    if order.status == Status.ALLTRADED:
                        ret, vt_orderid = self._buy(volume)
                    await asyncio.sleep(1)

            self.log(f'执行买到资金不足结束.')

        def _buy(self, volume: Decimal, price: Decimal=None, vt_symbol: Optional[str] = None, fake_market_order: bool = fake_market_order) -> tuple[RetCode, Union[str, ErrorData, None]]:
            if price == None:
                type = OrderType.MARKET
            else:
                type = OrderType.LIMIT

            vt_symbol = vt_symbol or self.vt_symbol
            symbol, exchange = extract_vt_symbol(vt_symbol)
            product: Product = Product.OPTION if is_option(vt_symbol) else Product.EQUITY
            if fake_market_order and type == OrderType.MARKET:
                book: MyBookData
                ret, book = self.main_engine.gateways[GATEWAY_NAME].market_api.query_book(vt_symbol=vt_symbol)
                order_request: MyOrderRequest = MyOrderRequest(
                    symbol=symbol,
                    exchange=exchange,
                    direction=Direction.LONG,
                    offset=Offset.OPEN,
                    type=OrderType.LIMIT,
                    volume=volume,
                    price=book.ask_price_1,
                    product=product
                )
            else:
                order_request: MyOrderRequest = MyOrderRequest(
                    symbol=symbol,
                    exchange=exchange,
                    direction=Direction.LONG,
                    offset=Offset.OPEN,
                    type=type,
                    volume=volume,
                    price=price,
                    product=product
                )
            return self.main_engine.send_order(order_request, GATEWAY_NAME)
        
        def _sell(self, volume: Decimal, vt_symbol: Optional[str] = None, fake_market_order: bool = fake_market_order) -> tuple[RetCode, Union[str, ErrorData, None]]:
            vt_symbol = vt_symbol or self.vt_symbol
            symbol, exchange = extract_vt_symbol(vt_symbol)
            product: Product = Product.OPTION if is_option(vt_symbol) else Product.EQUITY
            if fake_market_order and type == OrderType.MARKET:
                book: MyBookData
                ret, book = self.main_engine.gateways[GATEWAY_NAME].market_api.query_book(vt_symbol=vt_symbol)
                order_request: MyOrderRequest = MyOrderRequest(
                    symbol=symbol,
                    exchange=exchange,
                    direction=Direction.SHORT,
                    offset=Offset.CLOSE,
                    type=OrderType.LIMIT,
                    volume=volume,
                    price=book.bid_price_1,
                    product=product
                )
            else:
                order_request: MyOrderRequest = MyOrderRequest(
                    symbol=symbol,
                    exchange=exchange,
                    direction=Direction.SHORT,
                    offset=Offset.CLOSE,
                    type=OrderType.MARKET,
                    volume=volume,
                    price=None,
                    product=product
                )
            return self.main_engine.send_order(order_request, GATEWAY_NAME)
        
        def handify(self, volume: Decimal):
            split_trade = self.get_split_trade()
            return split_trade.handify(self.vt_symbol, volume=volume)
        
        def get_price(self, vt_symbol: Optional[str] = None):
            prices = self.prices.get(vt_symbol or self.vt_symbol)
            price = prices.get(TradeSide(self.config['交易方向']))
            return price

        def get_position(self, position_id: Optional[str] = None) -> MyPositionData:
            position: MyPositionData = self.main_engine.get_position(position_id or self.position_id)
            return position
        
        def get_orders(self, vt_symbol: Optional[str] = None) -> list[MyOrderData]:
            orders: list[MyOrderData] = self.main_engine.get_orders(vt_symbol or self.vt_symbol)
            return orders
        
        def get_open_orders(self, vt_symbol: Optional[str] = None) -> list[MyOrderData]:
            orders: list[MyOrderData] = self.main_engine.get_open_orders(vt_symbol or self.vt_symbol)
            return orders
        
        async def async_get_book(self, vt_symbol: Optional[str] = None) -> tuple[RetCode, MyBookData]:
            vt_symbol = vt_symbol or self.vt_symbol
            ret, data = await self.main_engine.async_get_book(vt_symbol)
            if ret == RET_ERROR:
                assert_debug(False)
            if ret == RET_ASYNC:
                while not self.main_engine.get_book(vt_symbol):
                    await asyncio.sleep(1)
                ret = RET_OK
                data = self.main_engine.get_book(vt_symbol)
            return ret, data
        
        async def async_get_contract(self, vt_symbol: Optional[str] = None) -> tuple[RetCode, ContractData]:
            ret, data = await self.main_engine.async_get_contract(vt_symbol or self.vt_symbol)
            if ret == RET_ERROR:
                assert_debug(False)
            return ret, data

        async def query_position(self, vt_symbol: Optional[str] = None) -> MyPositionData:
            self.main_engine: MyMainEngine
            return self.main_engine.query_position(vt_symbols=[vt_symbol or self.vt_symbol], directions=[self.pos_direction])  
        
        async def async_get_positions(self, vt_symbol: Optional[str] = None) -> tuple[RetCode,  list[MyPositionData]]:
            vt_symbol = vt_symbol or self.vt_symbol
            ret, data = await self.main_engine.async_get_positions(vt_symbols=[vt_symbol], directions=[self.pos_direction]) 
            if ret == RET_ERROR:
                assert_debug(False)
            elif ret == RET_ASYNC:
                while not data:
                    symbol, exchange = extract_vt_symbol(vt_symbol)
                    position_id = f'{self.GATEWAY_NAME}.{symbol}_{exchange.name}_{self.pos_direction.value}_'
                    position = self.get_position(position_id=position_id)
                    data = [position] if position else []
                    await asyncio.sleep(1)
                ret = RET_OK
            return ret, data
        
        async def async_get_orders(self, vt_symbol: Optional[str] = None) -> tuple[RetCode,  list[MyPositionData]]:
            ret, data = await self.main_engine.async_get_orders(vt_symbol=vt_symbol or self.vt_symbol, direction=self.direction, offset=self.offset) 
            if ret == RET_ERROR:
                assert_debug(False)
            elif ret == RET_ASYNC:
                data = self.get_orders(vt_symbol=vt_symbol)
            return ret, data
        
        async def async_get_open_orders(self, vt_symbol: Optional[str] = None) -> tuple[RetCode,  list[MyPositionData]]:
            ret, data = await self.main_engine.async_get_open_orders(vt_symbol=vt_symbol or self.vt_symbol, direction=self.direction, offset=self.offset) 
            if ret == RET_ERROR:
                assert_debug(False)
            elif ret == RET_ASYNC:
                data = self.get_open_orders(vt_symbol=vt_symbol)
            return ret, data
        
        async def async_cancel_orders(self, vt_symbol: Optional[str] = None) -> tuple[RetCode,  list[MyPositionData]]:
            ret, data = await self.main_engine.async_cancel_orders(vt_symbol=vt_symbol or self.vt_symbol) 
            if ret == RET_ERROR:
                assert_debug(False)
            return ret, data

        # def get_orders(self) -> list[MyOrderData]:
        #     orders: list[MyOrderData] = self.main_engine.get_all_orders()
        #     return orders

        # def get_open_orders(self) -> list[MyOrderData]:
        #     orders: list[MyOrderData] = self.main_engine.get_all_active_orders()
        #     return orders 

        def get_order(self, vt_orderid: str) -> list[MyOrderData]:
            return self.main_engine.get_order(vt_orderid)
        
        def get_last_order(self, start_time: datetime) -> MyOrderData:
            strategy = self.get_strategy()
            orders: list[MyOrderData] = strategy.get_orders()
            orders = [x for x in orders if x.datetime >= start_time]
            return orders and orders[-1]

        # def query_position(self, vt_symbol: Optional[str] = None) -> None:
        #     self.gateway.query_position(vt_symbols=[vt_symbol or self.vt_symbol], directions=[self.pos_direction]) 

        def run(self, pause: bool = False) -> None:
            self.cta_trade.start_strategies(strategy_name=STRATEGY_NAME)
            if not pause:
                self.strategy_run()

        def strategy_run(self):
            split_trades = self.get_split_trades()
            for split_trade in split_trades:
                split_trade.update_config({'running': True})

        def get_strategy(self): 
            split_strategy = list(self.cta_trade.cta_engine.strategies.values())[-1]
            return split_strategy
        
        def get_split_trades(self):
            split_strategy = self.get_strategy()
            split_trades: list = split_strategy.split_trades
            return split_trades
        
        def get_split_trade(self, vt_symbol: Optional[str] = None):
            split_strategy = self.get_strategy()
            split_trades: list = split_strategy.split_trades
            
            if not split_trades:
                assert_debug(False)

            vt_symbol = vt_symbol or self.vt_symbol
            split_trades = list(filter(lambda x: x.config['vt_symbol'] == vt_symbol, split_trades))
            if not split_trades or len(split_trades) > 1:
                assert_debug(False)

            return split_trades[0]
        
        # 更新（增加）配置
        async def async_strategy_update(self, data: dict):
            split_strategy = self.get_strategy()
            split_strategy.strategy_update(data)
            await asyncio.sleep(3)

        # 更新（增加）配置
        async def async_strategy_remove(self, data: dict):
            split_strategy = self.get_strategy()
            split_strategy.strategy_remove(data)
            await asyncio.sleep(3)
        
        async def async_split_update_config(self, data: dict, vt_symbol: Optional[str] = None, to_validate: bool = False):
            split_trade = self.get_split_trade(vt_symbol or self.vt_symbol)
            split_trade.update_config(data, to_validate=to_validate)
            await asyncio.sleep(2)
            # 设置了参数之后需要等腰下一拍才能计算更新可有数量等

        async def async_split_config_set_trade_side(self, trade_side = TradeSide.SELL, vt_symbol: Optional[str] = None):
            direction, offset = trade_side2direction_offset(trade_side)
            self.direction = direction
            self.offset = offset
            await client.async_split_update_config({
                'trade_side': trade_side,
                'direction': direction,
                'offset': offset
            }, vt_symbol=vt_symbol or self.vt_symbol)
        
        async def async_strategy_buy(self, volume: Decimal, price: Decimal, vt_symbol: Optional[str] = None) -> tuple[RetCode, Union[str, ErrorData, None]]:
            strategy = self.get_strategy()
            vt_symbol=vt_symbol or self.vt_symbol
            split_trade = self.get_split_trade(vt_symbol=vt_symbol)

            if price == None:
                type = OrderType.MARKET
            else:
                type = OrderType.LIMIT

            ret, data = strategy.send_order(
                vt_symbol=vt_symbol,
                direction=Direction.LONG,
                offset=Offset.OPEN,
                volume=volume,
                price=price,
                reference=split_trade.id
            )
            await asyncio.sleep(1)
            return ret, data
        
        async def async_strategy_sell(self, volume: Decimal, price: Decimal, vt_symbol: Optional[str] = None) -> tuple[RetCode, Union[str, ErrorData, None]]:
            strategy = self.get_strategy()
            vt_symbol=vt_symbol or self.vt_symbol
            split_trade = self.get_split_trade(vt_symbol=vt_symbol)

            if price == None:
                type = OrderType.MARKET
            else:
                type = OrderType.LIMIT

            ret, data = strategy.send_order(
                vt_symbol=vt_symbol,
                direction=Direction.SHORT,
                offset=Offset.CLOSE,
                volume=volume,
                price=price,
                reference=split_trade.id
            )
            await asyncio.sleep(1)
            return ret, data
        
        def get_split_trade_persistence(self, vt_symbol: Optional[str] = None):
            # 先找到split_trade的配置，根据标的来构造相应的持仓，然后再启动策略
            vt_symbol = vt_symbol or self.vt_symbol
            symbol, exchange = extract_vt_symbol(vt_symbol)
            persistence_folder = get_folder_path('persistence')
            data = None
            for file in persistence_folder.iterdir():
                if file.is_file():
                    data = load_json(persistence_folder.joinpath(file.name))
                    if data['code'] == symbol:
                        break
            if not data:
                assert_debug(False)
            return data
        
        async def async_sleep(self, seconds: int = 5, log: bool = True):
            count = seconds
            while count > 0:
                await asyncio.sleep(1)
                count -= 1
                log and self.log(f'--------async_sleep-------->: {count}')

        async def async_done(self, vt_symbol: Optional[str] = None):
            split_trade = self.get_split_trade(vt_symbol or self.vt_symbol)
            while not split_trade.done:
                await asyncio.sleep(1)
            await asyncio.sleep(3) # 由于done的判定(如果订单回调比持仓要晚，会出现交易过量的假提示，这个时候done提前为true了)和update_deal的写入文件是异步的，所以要等待文件写入

        async def async_assert_no_canceled_order(self, start_time: datetime, order_volume: Decimal, order_price: Decimal, vt_symbol: Optional[str] = None):
            ret, orders = await client.async_get_orders(vt_symbol=vt_symbol or self.vt_symbol)
            orders = [x for x in orders if x.datetime >= start_time and x.status == Status.CANCELLED]
            for order in orders:
                assert_debug(not(order.price == order_price))

        async def async_assert_has_canceled_order(self, start_time: datetime, order_volume: Decimal, order_price: Decimal, vt_symbol: Optional[str] = None):
            ret, orders = await client.async_get_orders(vt_symbol=vt_symbol or self.vt_symbol)
            orders = [x for x in orders if x.datetime >= start_time and x.status == Status.CANCELLED]
            assert_debug(len(orders) >= 1)
            assert_debug(orders[-1].volume == order_volume)
            assert_debug(orders[-1].price == order_price)
            assert_debug(orders[-1].traded == Decimal('0'))

        async def async_assert_no_open_order(self, order_volume: Decimal, order_price: Decimal, vt_symbol: Optional[str] = None):
            strategy = self.get_strategy()

            # 对照服务器订单
            vt_symbol = vt_symbol or self.vt_symbol
            ret, open_orders = await client.async_get_open_orders(vt_symbol=vt_symbol)
            assert_debug(len(open_orders) == 0)

            # 对照本地订单
            assert_debug(len(strategy.get_open_orders(vt_symbols=[vt_symbol])) == 0)

        async def async_assert_has_open_order(self, order_volume: Decimal, order_price: Decimal, vt_symbol: Optional[str] = None):
            strategy = self.get_strategy()

            vt_symbol = vt_symbol or self.vt_symbol

            # 对照服务器订单
            ret, open_orders = await client.async_get_open_orders(vt_symbol=vt_symbol)
            assert_debug(len(open_orders) == 1)
            if not order_volume == None:
                assert_debug(open_orders[0].volume == order_volume)
            if not order_price == None:
                assert_debug(open_orders[0].price == order_price)
            assert_debug(open_orders[0].traded == Decimal('0'))

            # 对照本地订单
            assert_debug(len(strategy.get_open_orders(vt_symbols=[vt_symbol])) == 1)
            if not order_volume == None:
                assert_debug(strategy.get_open_orders(vt_symbols=[vt_symbol])[0].volume == order_volume)
            if not order_price == None:
                assert_debug(strategy.get_open_orders(vt_symbols=[vt_symbol])[0].price == order_price)
            assert_debug(strategy.get_open_orders()[0].traded == Decimal('0'))

        async def async_assert_position_volume(self, assert_position_volume: Decimal, vt_symbol: Optional[str] = None):
            ret: RetCode
            positions: list[MyPositionData]
            ret, positions = await client.async_get_positions(vt_symbol or self.vt_symbol)
            position = positions[0]

            assert_debug(position.volume == assert_position_volume)

        def assert_qty(self, assert_qty: Decimal, vt_symbol: Optional[str] = None):
            vt_symbol = vt_symbol or self.vt_symbol
            persistence: dict = client.get_split_trade_persistence(vt_symbol=vt_symbol)
            assert_debug(Decimal(str(persistence['deal_qty'])) == Decimal(str(assert_qty)))
        
        def log(self, msg='hello_log', tag=[], level=INFO, title:str ='', name='', fn_level=2):
            return super().log(msg, tag=self.vt_symbol, level=level, title=title, name=name, fn_level=fn_level)
        
        def stop(self):
            self.cta_trade.stop()
            sleep(1)
              


    client: Client = Client(CONFIG_NAME = CONFIG_NAME)

    assert_debug(GATEWAY_NAME == client.GATEWAY_NAME)
    assert_debug(str(client.gateway_config_path) == f'C:\\Users\\Administrator\\{CONFIG_NAME}\\gateway_config.json')
    return client

