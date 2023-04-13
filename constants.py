AVG_BLOCK_TIME = {
    'bitcoin': 10 * 60,
    'ethereum': 15,
    'binance_smart_chain': 3,
    'doge': 60,
    'litecoin': 2.5 * 60,
    'tron': 3
}

AVG_FEES = {
    'relative': {
        'trading': {
            'binance-fee': 0.001,
            'coinbase-fee': 0.006,
        }
    },
    'absolute': {
        'transaction': {
            'bitcoin-fee': 0.00004541,
            'ethereum-fee': 0.0023,
            'litecoin-fee': 0.018,
            'tron-fee': 0,  # *has some nuances
        },
        'withdrawal': {
            # binance
            'binance-ethereum-fee': 0.0012,
            'binance-bitcoin-fee': 0.0002,
            'binance-litecoin-fee': 0.001,
            'binance-tron-fee': 1,

            # binanceus
            'binanceus-ethereum-fee': 0.0012,
            'binanceus-bitcoin-fee': 0.0002,
            'binanceus-litecoin-fee': 0.001,
            'binanceus-tron-fee': 1,

            # bybit
            'bybit-ethereum-fee': 0.0012,
            'bybit-bitcoin-fee': 0.0002,
            'bybit-litecoin-fee': 0.001,
            'bybit-tron-fee': 1,

            # huobi
            'huoby-ethereum-fee': 0.0012,
            'huoby-bitcoin-fee': 0.0004,
            'huoby-litecoin-fee': 0.07717469,
            'huoby-tron-fee': 5.377886,

            # gemini
            'gemini-ethereum-fee': 0.0012,
            'gemini-bitcoin-fee': 0.0001,
            'gemini-litecoin-fee': 0.001,
            'gemini-tron-fee': 5.377886,

            # kraken
            'kraken-ethereum-fee': 0.05,
            'kraken-bitcoin-fee': 0.00001,
            'kraken-litecoin-fee': 0.002,
            'kraken-tron-fee': 1,
        },
        'deposit': {}

    }
}
