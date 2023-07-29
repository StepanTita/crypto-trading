from trading.asset import Asset


class Edge:
    def __init__(self, from_asset: Asset, from_node: int, to_asset: Asset, to_node: int, weight: float):
        self.from_asset = from_asset
        self.to_asset = to_asset

        self.from_node = from_node

        self.to_node = to_node
        self.weight = weight

    def __eq__(self, other):
        return self.from_asset == other.from_asset and self.to_asset == other.to_asset and self.from_node == other.from_node and self.to_node == other.to_node
