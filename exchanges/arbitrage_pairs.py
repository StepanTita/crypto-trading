import sys

import ccxt

from common.utils import *


def dump(*args):
    print(' '.join([str(arg) for arg in args]))


def print_exchanges():
    dump('Supported exchanges:', ', '.join(ccxt.exchanges))


def print_usage():
    dump("Usage: python " + sys.argv[0], green('id1'), yellow('id2'), blue('id3'), '...')


def arbitrage_pairs(exchanges_names, symbols=None):
    dump(exchanges_names)
    dump(yellow(' '.join(exchanges_names)))

    exchanges = dict()

    for name in exchanges_names:
        # instantiate the exchange by id
        exchange = getattr(ccxt, name)()

        # save it in a dictionary under its id for future use
        exchanges[name] = exchange

        # load all markets from the exchange
        markets = exchange.load_markets()

        dump(green(name), 'loaded', green(str(len(exchange.symbols))), 'markets')

    dump(green('Loaded all markets'))

    allSymbols = [symbol for name in exchanges_names for symbol in exchanges[name].symbols]

    # get all unique symbols
    uniqueSymbols = list(set(allSymbols))

    # filter out symbols that are not present on at least two exchanges
    arbitrableSymbols = sorted(
        [symbol for symbol in uniqueSymbols if allSymbols.count(symbol) > 1 and (symbols is None or symbol in symbols)])

    # print a table of arbitrable symbols
    table = []
    dump(green(' symbol          | ' + ''.join([' {:<15} | '.format(name) for name in exchanges_names])))
    dump(green(''.join(['-----------------+-' for _ in range(0, len(exchanges_names) + 1)])))

    for symbol in arbitrableSymbols:
        string = ' {:<15} | '.format(symbol)
        row = {}
        for name in exchanges_names:
            # if a symbol is present on a exchange print that exchange's id in the row
            string += ' {:<15} | '.format(name if symbol in exchanges[name].symbols else '')
        dump(string)


def main():
    ids = ['binanceus', 'kraken', 'bybit', 'kucoin', 'bitmex']
    arbitrage_pairs(ids, symbols=['BTC/USDT', 'LTC/BTC', 'ETH/BTC', 'ETH/USDT', 'LTC/USDT'])


if __name__ == '__main__':
    main()
