from trading.strategies.bellman_ford import strategy_bellman_ford_generator
from trading.strategies.between_platforms import strategy_between_platforms_generator
from trading.strategies.simple_triangle import strategy_simple_triangle_generator


def name_to_strategy(name):
    return {
        'simple-single-platform': strategy_simple_triangle_generator,
        'simple-multiple-platforms': strategy_between_platforms_generator,
        'bellman-ford': strategy_bellman_ford_generator
    }[name]
