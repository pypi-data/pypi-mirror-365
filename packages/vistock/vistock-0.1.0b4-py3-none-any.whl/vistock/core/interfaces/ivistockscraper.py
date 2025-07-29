from typing import Dict, Any

class IVistockVnDirectStockIndexScraper:
    def fetch(self, url: str) -> Dict[str, Any]:
        ...

class AsyncIVistockVnDirectStockIndexScraper:
    async def async_fetch(self, url: str) -> Dict[str, Any]:
        ...

class IVistockVnDirectFundamentalIndexScraper:
    def fetch(self, url: str) -> Dict[str, Any]:
        ...

class AsyncIVistockVnDirectFundamentalIndexScraper:
    async def async_fetch(self, url: str) -> Dict[str, Any]:
        ...

class IVistockVnDirectFinancialModelsScraper:
    def fetch(self, url: str) -> Dict[str, Any]:
        ...

class AsyncIVistockVnDirectFinancialModelsScraper:
    async def async_fetch(self, url: str) -> Dict[str, Any]:
        ...

class IVistockVnDirectFinancialStatementsIndexScraper:
    def fetch(self, url: str) -> Dict[str, Any]:
        ...

class AsyncIVistockVnDirectFinancialStatementsIndexScraper:
    async def async_fetch(self, url: str) -> Dict[str, Any]:
        ...

class IVistockVnDirectMarketPricesScraper:
    def fetch(self, url: str) -> Dict[str, Any]:
        ...

class AsyncIVistockVnDirectMarketPricesScraper:
    async def async_fetch(self, url: str) -> Dict[str, Any]:
        ...

class IVistockVnDirectChangePricesScraper:
    def fetch(self, url: str) -> Dict[str, Any]:
        ...

class AsyncIVistockVnDirectChangePricesScraper:
    async def async_fetch(self, url: str) -> Dict[str, Any]:
        ...

class IVistock24HMoneyStockSectionScraper:
    def fetch(self, url: str) -> Dict[str, Any]:
        ...

class AsyncIVistock24HMoneyStockSectionScraper:
    async def async_fetch(self, url: str) -> Dict[str, Any]:
        ...

class IVistockVietstockStockIndexScraper:
    def fetch(self, url: str) -> Dict[str, Any]:
        ...

class AsyncIVistockVietstockStockIndexScraper:
    async def async_fetch(self, url: str) -> Dict[str, Any]:
        ...

class IVistockDNSEStockIndexScraper:
    def fetch(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        ...

class AsyncIVistockDNSEStockIndexScraper:
    async def async_fetch(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        ...