from vistock.core.enums import Vistock24HMoneySectionMapping
from typing import List, Dict, Union, Any, Type
from urllib.parse import urlparse
from datetime import datetime
from tzlocal import get_localzone
from enum import Enum
import pytz
import time

class VistockValidator:
    VNDIRECT_STOCK_INDEX_REQUIRED_FIELDS = {
        'code', 'date', 'time', 'floor', 'type', 'basicPrice', 'ceilingPrice',
        'floorPrice', 'open', 'high', 'low', 'close', 'average', 'adOpen',
        'adHigh', 'adLow', 'adClose', 'adAverage', 'nmVolume', 'nmValue',
        'ptVolume', 'ptValue', 'change', 'adChange', 'pctChange'
    }
    DNSE_STOCK_INDEX_REQUIRED_FIELDS = {
        'symbol', 'matchPrice', 'matchQtty', 'sendingTime', 'side'
    }
    VNDIRECT_INDEX_CODES = {
        'VNINDEX', 'HNX', 'UPCOM', 'VN30', 'VN30F1M'
    }
    VNDIRECT_INDEX_PERIODS = {
        '1D', 'MTD', 'QTD', 'YTD', '5D', '1M', '3M', '6M', '1Y'
    }

    @staticmethod
    def validate_url(url: str) -> bool:
        try:
            parsed = urlparse(url)
            return all([parsed.scheme, parsed.netloc])
        
        except Exception:
            return False

    @staticmethod
    def validate_url_with_domain(url: str, domain: str) -> bool:
        try:
            parsed = urlparse(url)
            if parsed.scheme in ('http', 'https') and parsed.hostname and parsed.hostname.endswith(domain):
                return True
            else:
                return False
            
        except Exception:
            return False    
        
    @staticmethod
    def validate_date_format(date_str: str, date_format: str = '%Y-%m-%d') -> bool:        
        try:
            datetime.strptime(date_str, date_format)
            return True
        
        except ValueError:
            return False
        
    @staticmethod
    def validate_date_range(start_date: str, end_date: str, date_format: str = '%Y-%m-%d') -> bool:
        if not (VistockValidator.validate_date_format(start_date, date_format) and 
                VistockValidator.validate_date_format(end_date, date_format)):
            return False
        
        start_dt = datetime.strptime(start_date, date_format)
        end_dt = datetime.strptime(end_date, date_format)
        
        return start_dt <= end_dt
    
    @staticmethod
    def validate_vndirect_resolution(resolution: str) -> bool:
        valid_resolutions = {'day'}
        return resolution in valid_resolutions if resolution else True
    
    @staticmethod
    def validate_vietstock_resolution(resolution: str) -> bool:
        valid_resolutions = {'1D'}
        return resolution in valid_resolutions if resolution else True
    
    @staticmethod
    def validate_vndirect_stock_index_json_data(data: List[Dict[str, Any]]) -> bool:        
        for entry in data:            
            missing_fields = VistockValidator.VNDIRECT_STOCK_INDEX_REQUIRED_FIELDS - entry.keys()
            if missing_fields:
                return False
            
        return True
    
    @staticmethod
    def validate_dnse_stock_index_json_data(data: List[Dict[str, Any]]) -> bool:
        for entry in data:
            missing_fields = VistockValidator.DNSE_STOCK_INDEX_REQUIRED_FIELDS - entry.keys()
            if missing_fields:
                return False
            
        return True
    
    @staticmethod
    def validate_code(code: str) -> bool:        
        if len(code) == 3:
            return True
        
        return False
    
    @staticmethod
    def validate_enum_value(value: Union[str, Enum], enum_cls: Type[Enum]) -> bool:
        if isinstance(value, enum_cls):
            return True

        if isinstance(value, str):
            if value.upper() in enum_cls.__members__:
                return True
            
            if any(member.value == value for member in enum_cls):
                return True

        return False
    
    @staticmethod
    def validate_year_range(start_year: int, end_year: int) -> bool:
        if start_year > end_year:
            return False
        
        return True
    
    @staticmethod
    def validate_index_code(code: str) -> bool:
        return code in VistockValidator.VNDIRECT_INDEX_CODES if code else True
    
    @staticmethod
    def validate_index_period(period: str) -> bool:
        return period in VistockValidator.VNDIRECT_INDEX_PERIODS if period else True

class VistockNormalizator:
    @staticmethod
    def normalize_enum_value(value: Union[str, Enum], enum_cls: Type[Enum]) -> str:
        if isinstance(value, enum_cls):
            return value.value

        if isinstance(value, str):
            if value.upper() in enum_cls.__members__:
                return enum_cls[value.upper()].value
            for member in enum_cls:
                if member.value == value:
                    return value

        raise ValueError(f"Cannot normalize value '{value}' for enum {enum_cls.__name__}")

class VistockMapper:
    @staticmethod
    def map_english_section(vn_section: str) -> str:
        for section in Vistock24HMoneySectionMapping:
            if section.value == vn_section:
                return section.name.replace('_', ' ').title()
            
        raise ValueError(f'No English mapping found for: {vn_section}')
    
class VistockGenerator:
    QUARTERS = ['03-31', '06-30', '09-30', '12-31']

    @staticmethod
    def generate_annual_dates(start_year: int, end_year: int) -> str:
        dates: List[str] = []

        for year in range(end_year, start_year - 1, -1):
            dates.append(f'{year}-12-31')

        return ','.join(dates)
    
    @staticmethod
    def generate_quarterly_dates(start_year: int, end_year: int) -> str:
        dates: List[str] = []

        for year in range(end_year, start_year - 1, -1):
            for q in reversed(VistockGenerator.QUARTERS):
                dates.append(f'{year}-{q}')

        return ','.join(dates)
    
class VistockConverter:
    @staticmethod
    def convert_utc_to_local(utc_time: str) -> str:
        try:
            utc_time_clean = utc_time.rstrip('Z')

            if '.' in utc_time_clean:
                date_part, ms_part = utc_time_clean.split('.')
                ms_part = (ms_part + '000000')[:6]  # pad to microseconds
                utc_time_clean = f'{date_part}.{ms_part}'
                fmt = '%Y-%m-%dT%H:%M:%S.%f'
            else:
                fmt = '%Y-%m-%dT%H:%M:%S'

            utc_dt = datetime.strptime(utc_time_clean, fmt)
            utc_dt = utc_dt.replace(tzinfo=pytz.utc)

            local_tz = get_localzone()
            local_dt = utc_dt.astimezone(local_tz)

            return local_dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        except Exception:
            return utc_time
        
    @staticmethod
    def convert_date_to_timestamp(date: str) -> int:
        dt = datetime.strptime(date, '%Y-%m-%d')
        return int(time.mktime(dt.timetuple()))
    
    @staticmethod
    def convert_timestamp_to_date(timestamp: int) -> str:
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

        