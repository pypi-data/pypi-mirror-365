from vistock.core.constants import (
    DEFAULT_VNDIRECT_STOCK_INDEX_BASE_URL,
    DEFAULT_VNDIRECT_FUNDAMENTAL_INDEX_BASE_URL, 
    DEFAULT_VNDIRECT_FINANCIAL_MODELS_BASE_URL,
    DEFAULT_VNDIRECT_FINANCIAL_STATEMENTS_BASE_URL,
    DEFAULT_VNDIRECT_MARKET_PRICES_URL,
    DEFAULT_VNDIRECT_CHANGE_PRICES_URL,
    DEFAULT_VNDIRECT_DOMAIN, 
    DEFAULT_TIMEOUT
)
from vistock.core.models import (
    StandardVnDirectStockIndexSearch,
    AdvancedVnDirectStockIndexSearch,
    StandardVnDirectFinancialModelSearch,
    StandardVnDirectStockIndexSearchResults,
    AdvancedVnDirectStockIndexSearchResults,
    StandardVnDirectFundamentalIndexSearchResults,
    StandardVnDirectFinancialModelSearchResults,
    StandardVnDirectFinancialStatementsIndex,
    StandardVnDirectFinancialStatementsIndexSearchResults,
    StandardVnDirectMarketPricesSearch,
    StandardVnDirectMarketPricesSearchResults,
    StandardVnDirectChangePricesSearch,
    StandardVnDirectChangePricesSearchResults
)
from vistock.core.enums import (
    VistockVnDirectFinancialModelsCategory,
    VistockVnDirectReportTypeCategory,
    VistockVnDirectIndexCodeMapping,
    VistockVnDirectChangePricePeriodMapping
)
from vistock.core.interfaces.ivistocksearch import (
    IVistockVnDirectStockIndexSearch,
    AsyncIVistockVnDirectStockIndexSearch,
    IVistockVnDirectFundamentalIndexSearch,
    AsyncIVistockVnDirectFundamentalIndexSearch,
    IVistockVnDirectFinancialModelsSearch,
    AsyncIVistockVnDirectFinancialModelsSearch,
    IVistockVnDirectFinancialStatementsIndexSearch,
    AsyncIVistockVnDirectFinancialStatementsIndexSearch,
    IVistockVnDirectMarketPricesSearch,
    AsyncIVistockVnDirectMarketPricesSearch,
    IVistockVnDirectChangePricesSearch,
    AsyncIVistockVnDirectChangePricesSearch
)
from vistock.modules.vndirect.scrapers import (
    VistockVnDirectStockIndexScraper,
    VistockVnDirectFundamentalIndexScraper,
    VistockVnDirectFinancialModelsScraper,
    VistockVnDirectFinancialStatementsIndexScraper,
    VistockVnDirectMarketPricesScraper,
    VistockVnDirectChangePricesScraper
)
from vistock.modules.vndirect.parsers import (
    VistockVnDirectStockIndexParser,
    VistockVnDirectFundamentalIndexParser,
    VistockVnDirectFinancialModelsParser,
    VistockVnDirectFinancialStatementsIndexParser,
    VistockVnDirectMarketPricesParser,
    VistockVnDirectChangePricesParser
)
from vistock.core.utils import VistockValidator, VistockNormalizator
from typing import List, Dict, Tuple, Union, Literal, Any
from datetime import datetime
import asyncio

class VistockVnDirectStockIndexSearch(IVistockVnDirectStockIndexSearch, AsyncIVistockVnDirectStockIndexSearch):
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
        self._base_url = DEFAULT_VNDIRECT_STOCK_INDEX_BASE_URL
        self._domain = DEFAULT_VNDIRECT_DOMAIN
        self._scraper = VistockVnDirectStockIndexScraper()
        self._parser = VistockVnDirectStockIndexParser()
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
        start_date: str = '2012-01-01',
        end_date: str = datetime.now().strftime('%Y-%m-%d'),
        resolution: Literal['day'] = 'day',
        advanced: bool = True,
        ascending: bool = False
    ) -> Union[StandardVnDirectStockIndexSearchResults, AdvancedVnDirectStockIndexSearchResults]:
        if not VistockValidator.validate_vndirect_resolution(resolution):
            raise ValueError(
                'Invalid resolution: "resolution" must be one of the following values: "day", "week", "month", or "year". Please ensure that the resolution is specified correctly.'
            )

        initial_url = f'{self._base_url}{self._parser.parse_url_path(code=code, start_date=start_date, end_date=end_date)}'
        total_elements = self._scraper.fetch(url=initial_url).get('totalElements', 0)

        url = f'{self._base_url}{self._parser.parse_url_path(code=code, start_date=start_date, end_date=end_date, limit=total_elements)}'
        data: List[Dict[str, Any]] = self._scraper.fetch(url=url).get('data', [])
        
        if not data:
            raise ValueError(
                'No data found for the given parameters. Please check the code, start date, and end date to ensure they are correct and that data exists for the specified range.'
            )
        
        if not VistockValidator.validate_vndirect_stock_index_json_data(data):
            raise ValueError(
                'Invalid data format: The fetched data does not conform to the expected JSON structure. Please ensure that the API response is valid and contains the necessary fields.'
            )
        
        data.sort(key=lambda x: x.get('date', ''), reverse=not ascending)

        if advanced:
            transformed_data: List[Dict[str, Any]] = [
                {
                    'standard': {
                        'code': item.get('code', ''),
                        'date': item.get('date', ''),
                        'time': item.get('time', ''),
                        'tfloor': item.get('floor', ''),
                        'type': item.get('type', ''),
                        'mopen': item.get('adOpen', 0.0),
                        'mhigh': item.get('adHigh', 0.0),
                        'mlow': item.get('adLow', 0.0),
                        'mclose': item.get('adClose', 0.0),
                        'maverage': item.get('adAverage', 0.0),
                        'nmvolume': int(item.get('nmVolume', 0))
                    },
                    'basic': item.get('basicPrice', 0.0),
                    'ceiling': item.get('ceilingPrice', 0.0),
                    'floor': item.get('floorPrice', 0.0),
                    'open': item.get('open', 0.0),
                    'high': item.get('high', 0.0),
                    'low': item.get('low', 0.0),
                    'close': item.get('close', 0.0),
                    'average': item.get('average', 0.0),
                    'nmvalue': item.get('nmValue', 0.0),
                    'ptvolume': item.get('ptVolume', 0.0),
                    'ptvalue': item.get('ptValue', 0.0),
                    'change': item.get('change', 0.0),
                    'mchange': item.get('adChange', 0.0),
                    'pctchange': item.get('pctChange', 0.0)
                }
                for item in data
            ]

            return AdvancedVnDirectStockIndexSearchResults(
                results=[AdvancedVnDirectStockIndexSearch(**item) for item in transformed_data],
                total_results=len(transformed_data)
            )

        return StandardVnDirectStockIndexSearchResults(
            results=[
                StandardVnDirectStockIndexSearch(
                    code=item.get('code', ''),
                    date=item.get('date', ''),
                    time=item.get('time', ''),
                    tfloor=item.get('floor', ''),
                    type=item.get('type', ''),
                    mopen=item.get('adOpen', 0.0),
                    mhigh=item.get('adHigh', 0.0),
                    mlow=item.get('adLow', 0.0),
                    mclose=item.get('adClose', 0.0),
                    maverage=item.get('adAverage', 0.0),
                    nmvolume=int(item.get('nmVolume', 0))
                ) for item in data
            ],
            total_results=len(data)
        ) 

    async def async_search(
        self,
        code: str,
        start_date: str = '2012-01-01',
        end_date: str = datetime.now().strftime('%Y-%m-%d'),
        resolution: Literal['day'] = 'day',
        advanced: bool = True,
        ascending: bool = False
    ) -> Union[StandardVnDirectStockIndexSearchResults, AdvancedVnDirectStockIndexSearchResults]:
        if not VistockValidator.validate_vndirect_resolution(resolution):
            raise ValueError(
                'Invalid resolution: "resolution" must be one of the following values: "day", "week", "month", or "year". Please ensure that the resolution is specified correctly.'
            )

        initial_url = f'{self._base_url}{self._parser.parse_url_path(code=code, start_date=start_date, end_date=end_date)}'
        initial_response = await self._scraper.async_fetch(url=initial_url)
        total_elements = initial_response.get('totalElements', 0)

        url = f'{self._base_url}{self._parser.parse_url_path(code=code, start_date=start_date, end_date=end_date, limit=total_elements)}'
        response = await self._scraper.async_fetch(url=url) 
        data: List[Dict[str, Any]] = response.get('data', [])

        if not data:
            raise ValueError(
                'No data found for the given parameters. Please check the code, start date, and end date to ensure they are correct and that data exists for the specified range.'
            )

        if not VistockValidator.validate_vndirect_stock_index_json_data(data):
            raise ValueError(
                'Invalid data format: The fetched data does not conform to the expected JSON structure. Please ensure that the API response is valid and contains the necessary fields.'
            )

        data.sort(key=lambda x: x.get('date', ''), reverse=not ascending)

        if advanced:
            transformed_data: List[Dict[str, Any]] = [
                {
                    'standard': {
                        'code': item.get('code', ''),
                        'date': item.get('date', ''),
                        'time': item.get('time', ''),
                        'tfloor': item.get('floor', ''),
                        'type': item.get('type', ''),
                        'mopen': item.get('adOpen', 0.0),
                        'mhigh': item.get('adHigh', 0.0),
                        'mlow': item.get('adLow', 0.0),
                        'mclose': item.get('adClose', 0.0),
                        'maverage': item.get('adAverage', 0.0),
                        'nmvolume': int(item.get('nmVolume', 0))
                    },
                    'basic': item.get('basicPrice', 0.0),
                    'ceiling': item.get('ceilingPrice', 0.0),
                    'floor': item.get('floorPrice', 0.0),
                    'open': item.get('open', 0.0),
                    'high': item.get('high', 0.0),
                    'low': item.get('low', 0.0),
                    'close': item.get('close', 0.0),
                    'average': item.get('average', 0.0),
                    'nmvalue': item.get('nmValue', 0.0),
                    'ptvolume': item.get('ptVolume', 0.0),
                    'ptvalue': item.get('ptValue', 0.0),
                    'change': item.get('change', 0.0),
                    'mchange': item.get('adChange', 0.0),
                    'pctchange': item.get('pctChange', 0.0)
                }
                for item in data
            ]

            return AdvancedVnDirectStockIndexSearchResults(
                results=[AdvancedVnDirectStockIndexSearch(**item) for item in transformed_data],
                total_results=len(transformed_data)
            )

        return StandardVnDirectStockIndexSearchResults(
            results=[
                StandardVnDirectStockIndexSearch(
                    code=item.get('code', ''),
                    date=item.get('date', ''),
                    time=item.get('time', ''),
                    tfloor=item.get('floor', ''),
                    type=item.get('type', ''),
                    mopen=item.get('adOpen', 0.0),
                    mhigh=item.get('adHigh', 0.0),
                    mlow=item.get('adLow', 0.0),
                    mclose=item.get('adClose', 0.0),
                    maverage=item.get('adAverage', 0.0),
                    nmvolume=int(item.get('nmVolume', 0))
                ) for item in data
            ],
            total_results=len(data)
        )

class VistockVnDirectFundamentalIndexSearch(IVistockVnDirectFundamentalIndexSearch, AsyncIVistockVnDirectFundamentalIndexSearch):
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
        self._base_url = DEFAULT_VNDIRECT_FUNDAMENTAL_INDEX_BASE_URL
        self._domain = DEFAULT_VNDIRECT_DOMAIN
        self._scraper = VistockVnDirectFundamentalIndexScraper()
        self._parser = VistockVnDirectFundamentalIndexParser()
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

    def search(self, code: str) -> StandardVnDirectFundamentalIndexSearchResults:
        results: List[List[Dict[str, Any]]] = []
        
        urls = self._parser.parse_url_path(code=code)
        for url in urls:
            url = f'{self._base_url}{url}'
            data: List[Dict[str, Any]] = self._scraper.fetch(url).get('data', [])

            if not data:
                raise ValueError(
                    'No data found for the given parameters. Please check the code to ensure they are correct.'
                )
            
            results.append(data)

        merged_results = [item for result in results for item in result]

        field_map = {
            'MARKETCAP': 'marketcap',
            'NMVOLUME_AVG_CR_10D': 'nm_volume_avg_cr_10d',
            'PRICE_HIGHEST_CR_52W': 'price_highest_cr_52w',
            'PRICE_LOWEST_CR_52W': 'price_lowest_cr_52w',
            'OUTSTANDING_SHARES': 'outstanding_shares',
            'FREEFLOAT': 'freefloat',
            'BETA': 'beta',
            'PRICE_TO_EARNINGS': 'price_to_earnings',
            'PRICE_TO_BOOK': 'price_to_book',
            'ROAE_TR_AVG5Q': 'roae_tr_avg_5q',
            'ROAA_TR_AVG5Q': 'roaa_tr_avg_5q',
            'DIVIDEND_YIELD': 'dividend_yield',
            'EPS_TR': 'eps_tr',
            'BVPS_CR': 'bvps_cr'
        }

        model_data: Dict[str, float] = {}
        for item in merged_results:
            key = field_map.get(item.get('ratioCode', ''))
            if key:
                model_data[key] = item.get('value', 0.0)

        return StandardVnDirectFundamentalIndexSearchResults(**model_data)

    async def async_search(self, code: str) -> StandardVnDirectFundamentalIndexSearchResults:           
        results: List[List[Dict[str, Any]]] = []
        
        urls = self._parser.parse_url_path(code=code)
        for url in urls:
            url = f'{self._base_url}{url}'
            response = await self._scraper.async_fetch(url)
            data: List[Dict[str, Any]] = response.get('data', [])

            if not data:
                raise ValueError(
                    'No data found for the given parameters. Please check the code to ensure they are correct.'
                )
            
            results.append(data)

        merged_results = [item for result in results for item in result]

        field_map = {
            'MARKETCAP': 'marketcap',
            'NMVOLUME_AVG_CR_10D': 'nm_volume_avg_cr_10d',
            'PRICE_HIGHEST_CR_52W': 'price_highest_cr_52w',
            'PRICE_LOWEST_CR_52W': 'price_lowest_cr_52w',
            'OUTSTANDING_SHARES': 'outstanding_shares',
            'FREEFLOAT': 'freefloat',
            'BETA': 'beta',
            'PRICE_TO_EARNINGS': 'price_to_earnings',
            'PRICE_TO_BOOK': 'price_to_book',
            'ROAE_TR_AVG5Q': 'roae_tr_avg_5q',
            'ROAA_TR_AVG5Q': 'roaa_tr_avg_5q',
            'DIVIDEND_YIELD': 'dividend_yield',
            'EPS_TR': 'eps_tr',
            'BVPS_CR': 'bvps_cr'
        }

        model_data: Dict[str, float] = {}
        for item in merged_results:
            key = field_map.get(item.get('ratioCode', ''))
            if key:
                model_data[key] = item.get('value', 0.0)

        return StandardVnDirectFundamentalIndexSearchResults(**model_data)

class VistockVnDirectFinancialModelsSearch(IVistockVnDirectFinancialModelsSearch, AsyncIVistockVnDirectFinancialModelsSearch):
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
        self._base_url = DEFAULT_VNDIRECT_FINANCIAL_MODELS_BASE_URL
        self._domain = DEFAULT_VNDIRECT_DOMAIN
        self._scraper = VistockVnDirectFinancialModelsScraper()
        self._parser = VistockVnDirectFinancialModelsParser()
        self._semaphore = asyncio.Semaphore(self._semaphore_limit)

    def search(
        self,
        code: str,
        model_type: Union[VistockVnDirectFinancialModelsCategory, str] = 'all'
    ) -> StandardVnDirectFinancialModelSearchResults:
        if model_type != 'all':
            if not VistockValidator.validate_enum_value(model_type, VistockVnDirectFinancialModelsCategory):
                raise ValueError(f'"{model_type}" is not a recognized model type. Use a valid enum name or code.')
            model_type_code = VistockNormalizator.normalize_enum_value(model_type, VistockVnDirectFinancialModelsCategory)
        else:
            model_type_code = 'all'

        results: List[List[Dict[str, Any]]] = []

        urls = self._parser.parse_url_path(code=code, model_type_code=model_type_code)
        for url in urls:
            url = f'{self._base_url}{url}'
            data: List[Dict[str, Any]] = self._scraper.fetch(url=url).get('data', [])

            if not data:
                raise ValueError(
                    'No data found for the given parameters. Please check the code, and model type to ensure they are correct.'
                )
            
            results.append(data)

        merged_results = [item for result in results for item in result]

        return StandardVnDirectFinancialModelSearchResults(
            results=[
                StandardVnDirectFinancialModelSearch(
                    model_type=item.get('modelType', 0),
                    model_type_name=item.get('modelTypeName', ''),
                    model_vn_desc=item.get('modelVnDesc', ''),
                    model_en_desc=item.get('modelEnDesc', ''),
                    company_form=item.get('companyForm', ''),
                    note=item.get('note', ''),
                    item_code=item.get('itemCode', 0),
                    item_vn_name=item.get('itemVnName', ''),
                    item_en_name=item.get('itemEnName', ''),
                    display_order=item.get('displayOrder', 0),
                    display_level=item.get('displayLevel', 0),
                    form_type=item.get('formType', '')
                ) for item in merged_results
            ],
            total_results=len(merged_results)
        )

    async def async_search(
        self,
        code: str,
        model_type: Union[VistockVnDirectFinancialModelsCategory, str] = 'all'
    ) -> StandardVnDirectFinancialModelSearchResults:
        if model_type != 'all':
            if not VistockValidator.validate_enum_value(model_type, VistockVnDirectFinancialModelsCategory):
                raise ValueError(f'"{model_type}" is not a recognized model type. Use a valid enum name or code.')
            model_type_code = VistockNormalizator.normalize_enum_value(model_type, VistockVnDirectFinancialModelsCategory)
        else:
            model_type_code = 'all'

        results: List[List[Dict[str, Any]]] = []

        urls = self._parser.parse_url_path(code=code, model_type_code=model_type_code)
        for url in urls:
            url = f'{self._base_url}{url}'
            response = await self._scraper.async_fetch(url=url)
            data: List[Dict[str, Any]] = response.get('data', [])

            if not data:
                raise ValueError(
                    'No data found for the given parameters. Please check the code, and model type to ensure they are correct.'
                )
            
            results.append(data)

        merged_results = [item for result in results for item in result]

        return StandardVnDirectFinancialModelSearchResults(
            results=[
                StandardVnDirectFinancialModelSearch(
                    model_type=item.get('modelType', 0),
                    model_type_name=item.get('modelTypeName', ''),
                    model_vn_desc=item.get('modelVnDesc', ''),
                    model_en_desc=item.get('modelEnDesc', ''),
                    company_form=item.get('companyForm', ''),
                    note=item.get('note', ''),
                    item_code=item.get('itemCode', 0),
                    item_vn_name=item.get('itemVnName', ''),
                    item_en_name=item.get('itemEnName', ''),
                    display_order=item.get('displayOrder', 0),
                    display_level=item.get('displayLevel', 0),
                    form_type=item.get('formType', '')
                ) for item in merged_results
            ],
            total_results=len(merged_results)
        )

class VistockVnDirectFinancialStatementsIndexSearch(IVistockVnDirectFinancialStatementsIndexSearch, AsyncIVistockVnDirectFinancialStatementsIndexSearch):
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
        self._base_url = DEFAULT_VNDIRECT_FINANCIAL_STATEMENTS_BASE_URL
        self._domain = DEFAULT_VNDIRECT_DOMAIN
        self._scraper = VistockVnDirectFinancialStatementsIndexScraper()
        self._parser = VistockVnDirectFinancialStatementsIndexParser()
        self._finanical_models_search = VistockVnDirectFinancialModelsSearch()
        self._semaphore = asyncio.Semaphore(self._semaphore_limit)

    def search(
        self,
        code: str,
        start_year: int = 2000,
        end_year: int = datetime.now().year,
        report_type: Union[VistockVnDirectReportTypeCategory, str] = 'ANNUAL',
        model_type: Union[VistockVnDirectFinancialModelsCategory, str] = 'all'
    ) -> StandardVnDirectFinancialStatementsIndexSearchResults:
        financial_models = self._finanical_models_search.search(
            code=code,
            model_type=model_type
        )

        if report_type != 'ANNUAL':
            if not VistockValidator.validate_enum_value(report_type, VistockVnDirectReportTypeCategory):
                raise ValueError(f'"{report_type}" is not a recognized report type. Use a valid enum name or code.')
            report_type_code = VistockNormalizator.normalize_enum_value(report_type, VistockVnDirectReportTypeCategory)
        else:
            report_type_code = 'all'

        if model_type != 'all':
            if not VistockValidator.validate_enum_value(model_type, VistockVnDirectFinancialModelsCategory):
                raise ValueError(f'"{model_type}" is not a recognized model type. Use a valid enum name or code.')
            model_type_code = VistockNormalizator.normalize_enum_value(model_type, VistockVnDirectFinancialModelsCategory)
        else:
            model_type_code = 'all'     

        results: List[StandardVnDirectFinancialStatementsIndex] = []

        urls = self._parser.parse_url_path(
            code=code,
            start_year=start_year,
            end_year=end_year,
            report_type_code=report_type_code,
            model_type_code=model_type_code
        )

        for url in urls:
            url = f'{self._base_url}{url}'
            data: List[Dict[str, Any]] = self._scraper.fetch(url).get('data', [])

            if not data:
                raise ValueError(
                    'No data found for the given parameters. Please check the code, start year, end year, report type, and model type to ensure they are correct and that data exists for the specified range.'
                )

            for model in financial_models.results:
                for item in data:
                    if (
                        item.get('modelType') == model.model_type and
                        item.get('itemCode') == model.item_code
                    ):
                        index = StandardVnDirectFinancialStatementsIndex(
                            code=item.get('code', ''),
                            model=model,
                            report_type=item.get('reportType', ''),
                            numeric_value=item.get('numericValue', 0.0),
                            fiscal_date=item.get('fiscalDate', ''),
                            created_date=item.get('createdDate', ''),
                            modified_date=item.get('modifiedDate', '')
                        )
                        results.append(index)

        return StandardVnDirectFinancialStatementsIndexSearchResults(
            results=results,
            total_results=len(results)
        )

    async def async_search(
        self,
        code: str,
        start_year: int = 2000,
        end_year: int = datetime.now().year,
        report_type: Union[VistockVnDirectReportTypeCategory, str] = 'ANNUAL',
        model_type: Union[VistockVnDirectFinancialModelsCategory, str] = 'all'
    ) -> StandardVnDirectFinancialStatementsIndexSearchResults:
        financial_models = await self._finanical_models_search.async_search(
            code=code,
            model_type=model_type
        )

        if report_type != 'ANNUAL':
            if not VistockValidator.validate_enum_value(report_type, VistockVnDirectReportTypeCategory):
                raise ValueError(f'"{report_type}" is not a recognized report type. Use a valid enum name or code.')
            report_type_code = VistockNormalizator.normalize_enum_value(report_type, VistockVnDirectReportTypeCategory)
        else:
            report_type_code = 'all'

        if model_type != 'all':
            if not VistockValidator.validate_enum_value(model_type, VistockVnDirectFinancialModelsCategory):
                raise ValueError(f'"{model_type}" is not a recognized model type. Use a valid enum name or code.')
            model_type_code = VistockNormalizator.normalize_enum_value(model_type, VistockVnDirectFinancialModelsCategory)
        else:
            model_type_code = 'all'     

        results: List[StandardVnDirectFinancialStatementsIndex] = []

        urls = self._parser.parse_url_path(
            code=code,
            start_year=start_year,
            end_year=end_year,
            report_type_code=report_type_code,
            model_type_code=model_type_code
        )

        model_lookup: Dict[Tuple[int, int], StandardVnDirectFinancialModelSearch] = {
            (model.model_type, model.item_code): model
            for model in financial_models.results
        }

        for url in urls:
            url = f'{self._base_url}{url}'
            response = await self._scraper.async_fetch(url)
            data: List[Dict[str, Any]] = response.get('data', [])

            if not data:
                raise ValueError(
                'No data found for the given parameters. Please check the code, start year, end year, report type, and model type to ensure they are correct and that data exists for the specified range.'
            )

            for item in data:
                model_key = (item.get('modelType', ''), item.get('itemCode', ''))
                model = model_lookup.get(model_key)
                if model is None:
                    continue

                index = StandardVnDirectFinancialStatementsIndex(
                    code=item.get('code', ''),
                    model=model,
                    report_type=item.get('reportType', ''),
                    numeric_value=item.get('numericValue', 0.0),
                    fiscal_date=item.get('fiscalDate', ''),
                    created_date=item.get('createdDate', ''),
                    modified_date=item.get('modifiedDate', '')
                )
                results.append(index)

        return StandardVnDirectFinancialStatementsIndexSearchResults(
            results=results,
            total_results=len(results)
        )
    
class VistockVnDirectMarketPricesSearch(IVistockVnDirectMarketPricesSearch, AsyncIVistockVnDirectMarketPricesSearch):
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
        self._base_url = DEFAULT_VNDIRECT_MARKET_PRICES_URL
        self._domain = DEFAULT_VNDIRECT_DOMAIN
        self._scraper = VistockVnDirectMarketPricesScraper()
        self._parser = VistockVnDirectMarketPricesParser()
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
        code: Union[VistockVnDirectIndexCodeMapping, str],
        start_date: str = '2012-01-01',
        ascending: bool = True
    ) -> StandardVnDirectMarketPricesSearchResults:
        if not VistockValidator.validate_enum_value(code, VistockVnDirectIndexCodeMapping):
            raise ValueError(
                f'Invalid index code: "{code}". Must be one of the supported codes: VNINDEX, HNX, UPCOM, VN30, VN30F1M.'
            )
        
        code = VistockNormalizator.normalize_enum_value(code, VistockVnDirectIndexCodeMapping)

        if code == 'VN30F1M':
            raise ValueError(
                f'The index code "{code}" is not supported for this search operation.'
            )
        
        initial_url = f'{self._base_url}{self._parser.parse_url_path(code=code, start_date=start_date, ascending=ascending)}'
        total_elements = self._scraper.fetch(url=initial_url).get('totalElements', 0)

        url = f'{self._base_url}{self._parser.parse_url_path(code=code, start_date=start_date, ascending=ascending, limit=total_elements)}'
        data: List[Dict[str, Any]] = self._scraper.fetch(url=url).get('data', [])

        if not data:
            raise ValueError(
                'No data found for the given parameters. Please check the code and start date to ensure they are correct and that data exists for the specified range.'
            )
        
        return StandardVnDirectMarketPricesSearchResults(
            results=[
                StandardVnDirectMarketPricesSearch(
                    code=item.get('code', ''),
                    date=item.get('date', ''),
                    time=item.get('time', ''),
                    tfloor=item.get('floor', ''),
                    type=item.get('type', ''),
                    open=item.get('open', 0.0),
                    high=item.get('high', 0.0),
                    low=item.get('low', 0.0),
                    close=item.get('close', 0.0),
                    change=item.get('change', 0.0),
                    pct_change=item.get('pctChange', 0.0),
                    accumulated_volume=item.get('accumulatedVol', 0.0),
                    accumulated_value=item.get('accumulatedVal', 0.0),
                    nmvolume=item.get('nmVolume', 0.0),
                    nmvalue=item.get('nmValue', 0.0),
                    ptvolume=item.get('ptVolume', 0.0),
                    ptvalue=item.get('ptValue', 0.0),
                    advances=item.get('advances', 0.0),
                    declines=item.get('declines', 0.0),
                    no_change=item.get('noChange', 0.0),
                    no_trade=item.get('noTrade', 0.0),
                    ceiling_stocks=item.get('ceilingStocks', 0.0),
                    floor_stocks=item.get('floorStocks', 0.0),
                    val_chg_pct_cr1d=item.get('valChgPctCr1D', 0.0)
                ) for item in data
            ],
            total_results=len(data)
        )
    
    async def async_search(
        self,
        code: Union[VistockVnDirectIndexCodeMapping, str],
        start_date: str = '2012-01-01',
        ascending: bool = True
    ) -> StandardVnDirectMarketPricesSearchResults:
        if not VistockValidator.validate_enum_value(code, VistockVnDirectIndexCodeMapping):
            raise ValueError(
                f'Invalid index code: "{code}". Must be one of the supported codes: VNINDEX, HNX, UPCOM, VN30, VN30F1M.'
            )
        
        code = VistockNormalizator.normalize_enum_value(code, VistockVnDirectIndexCodeMapping)

        if code == 'VN30F1M':
            raise ValueError(
                f'The index code "{code}" is not supported for this search operation.'
            )

        initial_url = f'{self._base_url}{self._parser.parse_url_path(code=code, start_date=start_date, ascending=ascending)}'
        initial_response = await self._scraper.async_fetch(url=initial_url)
        total_elements = initial_response.get('totalElements', 0)

        url = f'{self._base_url}{self._parser.parse_url_path(code=code, start_date=start_date, ascending=ascending, limit=total_elements)}'
        response = await self._scraper.async_fetch(url=url)
        data: List[Dict[str, Any]] = response.get('data', [])

        if not data:
            raise ValueError(
                'No data found for the given parameters. Please check the code and start date to ensure they are correct and that data exists for the specified range.'
            )
        
        return StandardVnDirectMarketPricesSearchResults(
            results=[
                StandardVnDirectMarketPricesSearch(
                    code=item.get('code', ''),
                    date=item.get('date', ''),
                    time=item.get('time', ''),
                    tfloor=item.get('floor', ''),
                    type=item.get('type', ''),
                    open=item.get('open', 0.0),
                    high=item.get('high', 0.0),
                    low=item.get('low', 0.0),
                    close=item.get('close', 0.0),
                    change=item.get('change', 0.0),
                    pct_change=item.get('pctChange', 0.0),
                    accumulated_volume=item.get('accumulatedVol', 0.0),
                    accumulated_value=item.get('accumulatedVal', 0.0),
                    nmvolume=item.get('nmVolume', 0.0),
                    nmvalue=item.get('nmValue', 0.0),
                    ptvolume=item.get('ptVolume', 0.0),
                    ptvalue=item.get('ptValue', 0.0),
                    advances=item.get('advances', 0.0),
                    declines=item.get('declines', 0.0),
                    no_change=item.get('noChange', 0.0),
                    no_trade=item.get('noTrade', 0.0),
                    ceiling_stocks=item.get('ceilingStocks', 0.0),
                    floor_stocks=item.get('floorStocks', 0.0),
                    val_chg_pct_cr1d=item.get('valChgPctCr1D', 0.0)
                ) for item in data
            ],
            total_results=len(data)
        )
    
class VistockVnDirectChangePricesSearch(IVistockVnDirectChangePricesSearch, AsyncIVistockVnDirectChangePricesSearch):
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
        self._base_url = DEFAULT_VNDIRECT_CHANGE_PRICES_URL
        self._domain = DEFAULT_VNDIRECT_DOMAIN
        self._scraper = VistockVnDirectChangePricesScraper()
        self._parser = VistockVnDirectChangePricesParser()
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
        code: Union[VistockVnDirectIndexCodeMapping, str] = 'VNINDEX,HNX,UPCOM,VN30,VN30F1M',
        period: Union[VistockVnDirectChangePricePeriodMapping, str] = '1D'
    ) -> StandardVnDirectChangePricesSearchResults:
        if isinstance(code, str):
            index_codes = code.split(',')
        else:
            index_codes = [code]

        normalized_index_codes: List[str] = []
        for index_code in index_codes:
            if not VistockValidator.validate_enum_value(index_code, VistockVnDirectIndexCodeMapping):
                raise ValueError(
                f'Invalid index code: "{code}". Must be one of the supported codes: VNINDEX, HNX, UPCOM, VN30, VN30F1M.'
            )
            normalized_index_codes.append(
                VistockNormalizator.normalize_enum_value(index_code, VistockVnDirectIndexCodeMapping)
            )

        code = ','.join(normalized_index_codes)

        if not VistockValidator.validate_enum_value(period, VistockVnDirectChangePricePeriodMapping):
            raise ValueError(
                f'Invalid index period: "{period}". Must be one of the supported periods: 1D, MTD, QTD, YTD, 5D, 1M, 3M, 6M, 1Y.'
            )
        
        period = VistockNormalizator.normalize_enum_value(period, VistockVnDirectChangePricePeriodMapping)

        url = f'{self._base_url}{self._parser.parse_url_path(code=code, period=period)}'
        data: List[Dict[str, Any]] = self._scraper.fetch(url=url).get('data', [])

        if not data:
            raise ValueError(
                'No data found for the given parameters. Please check the code and period to ensure they are correct and that data exists for the specified range.'
            )
        
        return StandardVnDirectChangePricesSearchResults(
            results=[
                StandardVnDirectChangePricesSearch(
                    code=item.get('code', ''),
                    name=item.get('name', ''),
                    type=item.get('type', ''),
                    period=item.get('period', ''),
                    price=item.get('price', 0.0),
                    bop_price=item.get('bopPrice', 0.0),
                    change=item.get('change', 0.0),
                    pct_change=item.get('changePct', 0.0),
                    last_updated=item.get('lastUpdated', '')
                ) for item in data
            ],
            total_results=len(data)
        )
        
    async def async_search(
        self,
        code: Union[VistockVnDirectIndexCodeMapping, str] = 'VNINDEX,HNX,UPCOM,VN30,VN30F1M',
        period: Union[VistockVnDirectChangePricePeriodMapping, str] = '1D'
    ) -> StandardVnDirectChangePricesSearchResults:
        if isinstance(code, str):
            index_codes = code.split(',')
        else:
            index_codes = [code]

        normalized_index_codes: List[str] = []
        for index_code in index_codes:
            if not VistockValidator.validate_enum_value(index_code, VistockVnDirectIndexCodeMapping):
                raise ValueError(
                f'Invalid index code: "{code}". Must be one of the supported codes: VNINDEX, HNX, UPCOM, VN30, VN30F1M.'
            )
            normalized_index_codes.append(
                VistockNormalizator.normalize_enum_value(index_code, VistockVnDirectIndexCodeMapping)
            )

        code = ','.join(normalized_index_codes)

        if not VistockValidator.validate_enum_value(period, VistockVnDirectChangePricePeriodMapping):
            raise ValueError(
                f'Invalid index period: "{period}". Must be one of the supported periods: 1D, MTD, QTD, YTD, 5D, 1M, 3M, 6M, 1Y.'
            )
        
        period = VistockNormalizator.normalize_enum_value(period, VistockVnDirectChangePricePeriodMapping)

        url = f'{self._base_url}{self._parser.parse_url_path(code=code, period=period)}'
        response = await self._scraper.async_fetch(url=url)
        data: List[Dict[str, Any]] = response.get('data', [])

        if not data:
            raise ValueError(
                'No data found for the given parameters. Please check the code and period to ensure they are correct and that data exists for the specified range.'
            )
        
        return StandardVnDirectChangePricesSearchResults(
            results=[
                StandardVnDirectChangePricesSearch(
                    code=item.get('code', ''),
                    name=item.get('name', ''),
                    type=item.get('type', ''),
                    period=item.get('period', ''),
                    price=item.get('price', 0.0),
                    bop_price=item.get('bopPrice', 0.0),
                    change=item.get('change', 0.0),
                    pct_change=item.get('changePct', 0.0),
                    last_updated=item.get('lastUpdated', '')
                ) for item in data
            ],
            total_results=len(data)
        )