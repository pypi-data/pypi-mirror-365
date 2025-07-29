from vistock.core.constants import (
    DEFAULT_VIETSTOCK_STOCK_INDEX_BASE_URL,
    DEFAULT_VIETSTOCK_DOMAIN,
    DEFAULT_TIMEOUT
)
from vistock.core.models import (
    StandardVietstockStockIndexSearch,
    StandardVietstockStockIndexSearchResults
)
from vistock.core.interfaces.ivistocksearch import (
    IVistockVietstockStockIndexSearch,
    AsyncIVistockVietstockStockIndexSearch
)
from vistock.modules.vietstock.scrapers import VistockVietstockStockIndexScraper
from vistock.modules.vietstock.parsers import VistockVietstockStockIndexParser
from vistock.core.utils import VistockConverter
from typing import List, Dict, Literal, Any
from datetime import datetime
import asyncio

class VistockVietstockStockIndexSearch(IVistockVietstockStockIndexSearch, AsyncIVistockVietstockStockIndexSearch):
    def __init__(self, timeout: float = DEFAULT_TIMEOUT, **kwargs: Any) -> None:
        if timeout <= 0:
            raise ValueError(
                'Invalid configuration: "timeout" must be a strictly positive integer value representing the maximum allowable wait time for the operation.'
            )
        self._timeout = timeout

        if 'semaphore_limit' in kwargs and (not isinstance(kwargs['semaphore_limit'], int) or kwargs['semaphore_limit'] <= 0):
            raise ValueError(
                'Invalid configuration: "semaphore_limit" must be a positive integer, indicating the maximum number of concurrent asynchronous operations permitted.'
            )

        self._semaphore_limit = kwargs.get('semaphore_limit', 5)
        self._base_url = DEFAULT_VIETSTOCK_STOCK_INDEX_BASE_URL
        self._domain = DEFAULT_VIETSTOCK_DOMAIN
        self._scraper = VistockVietstockStockIndexScraper()
        self._parser = VistockVietstockStockIndexParser()
        self._semaphore = asyncio.Semaphore(self._semaphore_limit)

    @property
    def timeout(self) -> float:
        return self._timeout
    
    @timeout.setter
    def timeout(self, value: int) -> None:
        if value <= 0:
            raise ValueError(
                'Invalid value: "timeout" must be a positive integer greater than zero.'
            )
        self._timeout = value

    def search(
        self,
        code: str,
        resolution: Literal['1D'] = '1D',
        start_date: str = '2000-01-01',
        end_date: str = datetime.now().strftime('%Y-%m-%d'),
        ascending: bool = False
    ) -> StandardVietstockStockIndexSearchResults:
        url = f'{self._base_url}{self._parser.parse_url_path(code=code, resolution=resolution, start_date=start_date, end_date=end_date)}'
        response: Dict[str, Any] = self._scraper.fetch(url=url)

        data: List[StandardVietstockStockIndexSearch] = []
        if response.get('s') == 'ok':
            mopens = response.get('o', [])
            mhighs = response.get('h', [])
            mlows = response.get('l', [])
            mcloses = response.get('c', [])
            mvolumes = response.get('v', [])
            timestamps = response.get('t', [])

            for mopen, mhigh, mlow, mclose, mvolume, timestamp in zip(mopens, mhighs, mlows, mcloses, mvolumes, timestamps):
                data.append(StandardVietstockStockIndexSearch(
                    mopen=mopen,
                    mhigh=mhigh,
                    mlow=mlow,
                    mclose=mclose,
                    mvolume=int(mvolume),
                    timestamp=VistockConverter.convert_timestamp_to_date(timestamp),
                ))

        data.sort(key=lambda x: x.timestamp, reverse=not ascending)

        return StandardVietstockStockIndexSearchResults(
            results=data,
            total_results=len(data)
        )
    
    async def async_search(
        self,
        code: str,
        resolution: Literal['1D'] = '1D',
        start_date: str = '2000-01-01',
        end_date: str = datetime.now().strftime('%Y-%m-%d'),
        ascending: bool = False
    ) -> StandardVietstockStockIndexSearchResults:
        url = f'{self._base_url}{self._parser.parse_url_path(code=code, resolution=resolution, start_date=start_date, end_date=end_date)}'
        response: Dict[str, Any] = await self._scraper.async_fetch(url=url)

        data: List[StandardVietstockStockIndexSearch] = []
        if response.get('s') == 'ok':
            mopens = response.get('o', [])
            mhighs = response.get('h', [])
            mlows = response.get('l', [])
            mcloses = response.get('c', [])
            mvolumes = response.get('v', [])
            timestamps = response.get('t', [])

            for mopen, mhigh, mlow, mclose, mvolume, timestamp in zip(mopens, mhighs, mlows, mcloses, mvolumes, timestamps):
                data.append(StandardVietstockStockIndexSearch(
                    mopen=mopen,
                    mhigh=mhigh,
                    mlow=mlow,
                    mclose=mclose,
                    mvolume=int(mvolume),
                    timestamp=VistockConverter.convert_timestamp_to_date(timestamp),
                ))

        data.sort(key=lambda x: x.timestamp, reverse=not ascending)

        return StandardVietstockStockIndexSearchResults(
            results=data,
            total_results=len(data)
        ) 

