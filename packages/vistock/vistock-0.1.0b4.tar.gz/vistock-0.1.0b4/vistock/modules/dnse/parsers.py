from vistock.core.interfaces.ivistockparser import IVistockDNSEStockIndexParser
from vistock.core.constants import DEFAULT_DNSE_DOMAIN
from vistock.core.utils import VistockValidator
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

class VistockDNSEStockIndexParser(IVistockDNSEStockIndexParser):
    def __init__(self):
        self._domain = DEFAULT_DNSE_DOMAIN

    def parse_payload(
        self,
        code: str,
        current_datetime: str = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    ) -> Dict[str, Any]:
        if not VistockValidator.validate_code(code=code):
            raise ValueError(
                'Invalid code: "code" must be a non-empty alphanumeric string with exactly 3 characters representing the stock code. Please ensure that the code is specified correctly.'
            )
        
        dt = datetime.strptime(current_datetime, '%Y-%m-%dT%H:%M:%S.%fZ')

        if dt.weekday() == 5:
            dt -= timedelta(days=1)
        elif dt.weekday() == 6:
            dt -= timedelta(days=2)

        date = dt.strftime('%Y-%m-%d')
        current_datetime = dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

        return {
            'query': f'''
                query GetKrxTicksBySymbols {{
                    GetKrxTicksBySymbols(
                        symbols: "{code}", 
                        date: "{date}", 
                        limit: 100000, 
                        before: "{current_datetime}", 
                        board: 2
                    ) {{
                        ticks {{
                            symbol
                            matchPrice
                            matchQtty
                            sendingTime
                            side
                        }}
                    }}
                }}
            '''
        }
        