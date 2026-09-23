from app.config import settings
from app.providers.base import DataProvider
from app.providers.betpawa import BetPawaProvider
from app.providers.demo import DemoDataProvider


def get_provider() -> DataProvider:
    if settings.data_provider.lower() == "demo":
        return DemoDataProvider()
    return BetPawaProvider()
