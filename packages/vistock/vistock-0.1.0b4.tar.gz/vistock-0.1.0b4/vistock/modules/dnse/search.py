from vistock.core.constants import (
    DEFAULT_DNSE_DOMAIN,
    DEFAULT_DNSE_STOCK_INDEX_BASE_URL,
    DEFAULT_TIMEOUT
)
from vistock.core.models import (
    StandardDNSEStockIndexSearch,
    StandardDNSEStockIndexSearchResults
)
from vistock.modules.dnse.scrapers import VistockDNSEStockIndexScraper
from vistock.modules.dnse.parsers import VistockDNSEStockIndexParser
from vistock.core.interfaces.ivistocksearch import (
    IVistockDNSEStockIndexSearch,
    AsyncIVistockDNSEStockIndexSearch
)
from vistock.core.utils import VistockValidator, VistockConverter
from typing import List, Dict, Any
from datetime import datetime, timezone
import asyncio

class VistockDNSEStockIndexSearch(IVistockDNSEStockIndexSearch, AsyncIVistockDNSEStockIndexSearch):
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
        self._base_url = DEFAULT_DNSE_STOCK_INDEX_BASE_URL
        self._domain = DEFAULT_DNSE_DOMAIN
        self._scraper = VistockDNSEStockIndexScraper()
        self._parser = VistockDNSEStockIndexParser()
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
        current_datetime: str = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
        ascending: bool = False
    ) -> StandardDNSEStockIndexSearchResults:
            payload = self._parser.parse_payload(
                code=code,
                current_datetime=current_datetime
            )

            data: List[Dict[str, Any]] = self._scraper.fetch(url=self._base_url, payload=payload).get('data', {}).get('GetKrxTicksBySymbols', {}).get('ticks', [])

            if not data:
                raise ValueError(
                    'No data found for the given parameters. Please check the code, and current date to ensure they are correct and that data exists for the specified range.'
                )
            
            if not VistockValidator.validate_dnse_stock_index_json_data(data):
                raise ValueError(
                    'Invalid data format: The fetched data does not conform to the expected JSON structure. Please ensure that the API response is valid and contains the necessary fields.'
                )
            
            data.sort(key=lambda x: x.get('sendingTime', ''), reverse=not ascending)

            return StandardDNSEStockIndexSearchResults(
                results=[
                    StandardDNSEStockIndexSearch(
                        code=item.get('symbol', ''),
                        match_price=item.get('matchPrice', 0.0),
                        match_volume= item.get('matchQtty', 0),
                        sending_time=VistockConverter.convert_utc_to_local(item.get('sendingTime', '')),
                        side=item.get('side', 0)
                    ) for item in data
                ],
                total_results=len(data)
            )
    
    async def async_search(
        self,
        code: str,
        current_datetime: str = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
        ascending: bool = False
    ) -> StandardDNSEStockIndexSearchResults:
        async with self._semaphore:
            payload = self._parser.parse_payload(
                code=code,
                current_datetime=current_datetime
            )

            response = await self._scraper.async_fetch(url=self._base_url, payload=payload)
            data: List[Dict[str, Any]] = response.get('data', {}).get('GetKrxTicksBySymbols', {}).get('ticks', [])

            if not data:
                raise ValueError(
                    'No data found for the given parameters. Please check the code, start date, and end date to ensure they are correct and that data exists for the specified range.'
                )
            
            if not VistockValidator.validate_dnse_stock_index_json_data(data):
                raise ValueError(
                    'Invalid data format: The fetched data does not conform to the expected JSON structure. Please ensure that the API response is valid and contains the necessary fields.'
                )
            
            data.sort(key=lambda x: x.get('sendingTime', ''), reverse=not ascending)

            return StandardDNSEStockIndexSearchResults(
                results=[
                    StandardDNSEStockIndexSearch(
                        code=item.get('symbol', ''),
                        match_price=item.get('matchPrice', 0.0),
                        match_volume= item.get('matchQtty', 0),
                        sending_time=VistockConverter.convert_utc_to_local(item.get('sendingTime', '')),
                        side=item.get('side', 0)
                    ) for item in data
                ],
                total_results=len(data)
            )
            

            

