from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def date_to_num(date: tuple):
    """format: DD.MM.YY"""
    date = date[4]
    day, month, year = date.split(".")
    return int(year+month+day)


def order_role_list(input_list: List[tuple], sort_type: str = "popular") -> Optional[List[tuple]]:
    try:
        reverse = True
        
        if sort_type == "popular":
            func = lambda role: role[3]
            reverse = True
        
        elif sort_type == "not popular":
            func = lambda role: role[3]
            reverse = False

        elif sort_type == "new":
            func = date_to_num
            reverse = True

        elif sort_type == "old":
            func = date_to_num
            reverse = False

        elif sort_type == "expensive":
            func = lambda role: role[2]
            reverse = True
        
        elif sort_type == "cheap":
            func = lambda role: role[2]
            reverse = False

        output_role_list = sorted(input_list, key=func, reverse=reverse)

        return output_role_list
    except Exception as e:
        logger.error(f"Sort role list function error: {e}")
        return