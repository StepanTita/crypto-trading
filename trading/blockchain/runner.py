from typing import List

from .asset import Asset
from .blockchain import Blockchain, get_blocktime
from trading.common.blockchain_logger import logger
from trading.common.utils import conform_timestamp, get_blockchain


class Runner:
    def __init__(self, blockchain: Blockchain):
        self.blockchain = blockchain

    def dry_run(self, timestamp, assets_chain: List[Asset], trade: float):
        assert len(assets_chain) >= 3

        target = assets_chain[0]

        prev_coin = target
        intermediate_trade = trade
        for i in range(1, len(assets_chain)):
            curr_coin = assets_chain[i]
            logger.debug(f'Exchanging {prev_coin.symbol} {curr_coin.symbol}')
            intermediate_trade = self.blockchain.calc_transaction(timestamp, prev_coin, curr_coin, intermediate_trade)
            prev_coin = curr_coin

        result = self.blockchain.calc_transaction(timestamp, prev_coin, target, intermediate_trade)
        return result

    def run(self, timestamp, assets_chain, trade):
        assert len(assets_chain) >= 3

        target = assets_chain[0]

        prev_coin = target
        intermediate_trade = trade

        times_history = []
        for i in range(1, len(assets_chain)):
            curr_coin = assets_chain[i]
            logger.debug(f'Exchanging {prev_coin.symbol} {curr_coin.symbol}')
            intermediate_trade = self.blockchain.calc_transaction(timestamp, prev_coin, curr_coin, intermediate_trade)
            prev_coin = curr_coin
            timestamp = conform_timestamp(
                timestamp,
                timestamp + get_blocktime(get_blockchain(prev_coin)) + get_blocktime(get_blockchain(curr_coin))
            )
            times_history.append(timestamp)

        result = self.blockchain.calc_transaction(timestamp, prev_coin, target, intermediate_trade)
        return result, timestamp, times_history
