import datetime
from jetcheck.settings import SUPPORTED_DATE_FORMATES


def string_to_datetime(input_date:str, custom_format:str=None):
    try:
        if custom_format:
            return datetime.datetime.strptime(input_date, custom_format)
        for format in SUPPORTED_DATE_FORMATES:
            try:
                return datetime.datetime.strptime(input_date, format)
            except ValueError as e:
                # print(e)
                pass
    except ValueError as e:
        print(e)


def string_to_date(date:str):
    return string_to_datetime(date).date()
