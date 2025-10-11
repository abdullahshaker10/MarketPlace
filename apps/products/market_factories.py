from .factories import UsMarketFactory, EuMarketFactory


def get_marketplace_factory(market: str):
    if market.upper() == "US":
        return UsMarketFactory()
    elif market.upper() == "EU":
        return EuMarketFactory()
    else:
        raise ValueError("Unsupported market")
