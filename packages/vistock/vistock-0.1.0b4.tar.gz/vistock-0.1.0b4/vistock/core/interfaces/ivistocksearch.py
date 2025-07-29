from vistock.core.models import (
    StandardVnDirectStockIndexSearchResults, 
    AdvancedVnDirectStockIndexSearchResults,
    StandardVnDirectFundamentalIndexSearchResults,
    Standard24HMoneyStockSectionSearchResults,
    StandardVnDirectFinancialModelSearchResults,
    StandardVnDirectFinancialStatementsIndexSearchResults,
    StandardDNSEStockIndexSearchResults,
    StandardVietstockStockIndexSearchResults,
    StandardVnDirectMarketPricesSearchResults,
    StandardVnDirectChangePricesSearchResults
)
from vistock.core.enums import (
    Vistock24HMoneyIndustryCategory,
    Vistock24HMoneyFloorCategory,
    Vistock24HMoneyCompanyCategory,
    Vistock24HMoneyLetterCategory,
    VistockVnDirectFinancialModelsCategory,
    VistockVnDirectReportTypeCategory,
    VistockVnDirectIndexCodeMapping,
    VistockVnDirectChangePricePeriodMapping
)
from typing import Union, Protocol, Literal
from datetime import datetime, timezone

class IVistockVnDirectStockIndexSearch(Protocol):
    def search(
        self, 
        code: str,
        start_date: str = '2012-01-01',
        end_date: str = datetime.now().strftime('%Y-%m-%d'),
        resolution: Literal['day'] = 'day',
        advanced: bool = True,
        ascending: bool = False
    ) -> Union[StandardVnDirectStockIndexSearchResults, AdvancedVnDirectStockIndexSearchResults]:
        ...

class AsyncIVistockVnDirectStockIndexSearch(Protocol):
    async def async_search(
        self, 
        code: str,
        start_date: str = '2012-01-01',
        end_date: str = datetime.now().strftime('%Y-%m-%d'),
        resolution: Literal['day'] = 'day',
        advanced: bool = True,
        ascending: bool = False
    ) -> Union[StandardVnDirectStockIndexSearchResults, AdvancedVnDirectStockIndexSearchResults]:
        ...

class IVistockVnDirectFundamentalIndexSearch(Protocol):
    def search(
        self,
        code: str
    ) -> StandardVnDirectFundamentalIndexSearchResults:
        ...

class AsyncIVistockVnDirectFundamentalIndexSearch(Protocol):
    async def async_search(
        self,
        code: str
    ) -> StandardVnDirectFundamentalIndexSearchResults:
        ...

class IVistockVnDirectFinancialModelsSearch(Protocol):
    def search(
        self,
        code: str,
        model_type: Union[VistockVnDirectFinancialModelsCategory, str] = 'all'
    ) -> StandardVnDirectFinancialModelSearchResults:
        ...

class AsyncIVistockVnDirectFinancialModelsSearch(Protocol):
    async def async_search(
        self,
        code: str,
        model_type: Union[VistockVnDirectFinancialModelsCategory, str] = 'all'
    ) -> StandardVnDirectFinancialModelSearchResults:
        ...

class IVistockVnDirectFinancialStatementsIndexSearch(Protocol):
    def search(
        self,
        code: str,
        start_year: int = 2000,
        end_year: int = datetime.now().year,
        report_type: Union[VistockVnDirectReportTypeCategory, str] = 'ANNUAL',
        model_type: Union[VistockVnDirectFinancialModelsCategory, str] = 'all'
    ) -> StandardVnDirectFinancialStatementsIndexSearchResults:
        ...

class AsyncIVistockVnDirectFinancialStatementsIndexSearch(Protocol):
    async def async_search(
        self,
        code: str,
        start_year: int = 2000,
        end_year: int = datetime.now().year,
        report_type: Union[VistockVnDirectReportTypeCategory, str] = 'ANNUAL',
        model_type: Union[VistockVnDirectFinancialModelsCategory, str] = 'all'
    ) -> StandardVnDirectFinancialStatementsIndexSearchResults:
        ...

class IVistockVnDirectMarketPricesSearch(Protocol):
    def search(
        self,
        code: Union[VistockVnDirectIndexCodeMapping, str],
        start_date: str = '2012-01-01',
        ascending: bool = True
    ) -> StandardVnDirectMarketPricesSearchResults:
        ...

class AsyncIVistockVnDirectMarketPricesSearch(Protocol):
    async def async_search(
        self,
        code: Union[VistockVnDirectIndexCodeMapping, str],
        start_date: str = '2012-01-01',
        ascending: bool = True
    ) -> StandardVnDirectMarketPricesSearchResults:
        ...

class IVistockVnDirectChangePricesSearch(Protocol):
    def search(
        self,
        code: Union[VistockVnDirectIndexCodeMapping, str] = 'VNINDEX,HNX,UPCOM,VN30,VN30F1M',
        period: Union[VistockVnDirectChangePricePeriodMapping, str] = '1D'
    ) -> StandardVnDirectChangePricesSearchResults:
        ...

class AsyncIVistockVnDirectChangePricesSearch(Protocol):
    async def async_search(
        self,
        code: Union[VistockVnDirectIndexCodeMapping, str] = 'VNINDEX,HNX,UPCOM,VN30,VN30F1M',
        period: Union[VistockVnDirectChangePricePeriodMapping, str] = '1D'
    ) -> StandardVnDirectChangePricesSearchResults:
        ...

class IVistock24HMoneyStockSectionSearch(Protocol):
    def search(
        self,
        industry: Union[Vistock24HMoneyIndustryCategory, str] = 'all',
        floor: Union[Vistock24HMoneyFloorCategory, str] = 'all',
        company_type: Union[Vistock24HMoneyCompanyCategory, str] = 'all',
        letter: Union[Vistock24HMoneyLetterCategory, str] = 'all',
        limit: int = 2000
    ) -> Standard24HMoneyStockSectionSearchResults:
        ...

class AsyncIVistock24HMoneyStockSectionSearch(Protocol):
    async def async_search(
        self,
        industry: Union[Vistock24HMoneyIndustryCategory, str] = 'all',
        floor: Union[Vistock24HMoneyFloorCategory, str] = 'all',
        company_type: Union[Vistock24HMoneyCompanyCategory, str] = 'all',
        letter: Union[Vistock24HMoneyLetterCategory, str] = 'all',
        limit: int = 2000 
    ) -> Standard24HMoneyStockSectionSearchResults:
        ...

class IVistockVietstockStockIndexSearch(Protocol):
    def search(
        self,
        code: str,
        resolution: Literal['1D'] = '1D',
        start_date: str = '2000-01-01',
        end_date: str = datetime.now().strftime('%Y-%m-%d'),
        ascending: bool = False
    ) -> StandardVietstockStockIndexSearchResults:
        ...

class AsyncIVistockVietstockStockIndexSearch(Protocol):
    async def async_search(
        self,
        code: str,
        resolution: Literal['1D'] = '1D',
        start_date: str = '2000-01-01',
        end_date: str = datetime.now().strftime('%Y-%m-%d'),
        ascending: bool = False
    ) -> StandardVietstockStockIndexSearchResults:
        ...

class IVistockDNSEStockIndexSearch(Protocol):
    def search(
        self,
        code: str,
        current_datetime: str = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
        ascending: bool = False
    ) -> StandardDNSEStockIndexSearchResults:
        ...

class AsyncIVistockDNSEStockIndexSearch(Protocol):
    async def async_search(
        self,
        code: str,
        current_datetime: str = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
        ascending: bool = False
    ) -> StandardDNSEStockIndexSearchResults:
        ...