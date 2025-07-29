from vistock.core.interfaces.ivistockparser import IVistockVietstockStockIndexParser
from vistock.core.constants import DEFAULT_VIETSTOCK_DOMAIN
from vistock.core.utils import VistockValidator, VistockConverter
from datetime import datetime

class VistockVietstockStockIndexParser(IVistockVietstockStockIndexParser):
    def __init__(self):
        self._domain = DEFAULT_VIETSTOCK_DOMAIN

    def parse_url_path(
        self,
        code: str,
        resolution: str,
        start_date: str = '2000-01-01',
        end_date: str = datetime.now().strftime('%Y-%m-%d')
    ) -> str:
        if not VistockValidator.validate_code(code=code):
            raise ValueError(
                'Invalid code: "code" must be a non-empty alphanumeric string with exactly 3 characters representing the stock code. Please ensure that the code is specified correctly.'
            )
        
        if not VistockValidator.validate_vietstock_resolution(resolution=resolution):
            raise ValueError(
                'Invalid resolution: "resolution" must be "1D". Please ensure that the resolution is specified correctly.'
            )
        
        if not VistockValidator.validate_date_range(start_date=start_date, end_date=end_date):
            raise ValueError(
                'Invalid date range: "start_date" must be earlier than "end_date". Please ensure that the start date precedes the end date to maintain a valid chronological order.'
            )
        
        if not VistockValidator.validate_date_format(date_str=start_date):
            raise ValueError(
                f'Invalid start_date format: "{start_date}". Please use "YYYY-MM-DD".'
            )
        start_date_timestamp: int = VistockConverter.convert_date_to_timestamp(date=start_date)

        if not VistockValidator.validate_date_format(date_str=end_date):
            raise ValueError(
                f'Invalid end_date format: "{end_date}". Please use "YYYY-MM-DD".'
            )
        end_date_timestamp: int = VistockConverter.convert_date_to_timestamp(date=end_date)

        return f'?symbol={code}&resolution={resolution}&from={start_date_timestamp}&to={end_date_timestamp}&countback=2'

