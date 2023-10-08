from datetime import datetime
import time
from .LogUtils import LogEnabledClass as LEC

class DateUtils(LEC):
    @staticmethod
    def getCurrentDate() -> datetime:
        # Current date and time
        return datetime.now()

    @staticmethod
    def date_to_string_format(format: str = "%Y%m%d_%H%M%S") -> str:
        # Format the date using a custom pattern
        """
            %Y: Year (e.g., 2023)
            %m: Month (01-12)
            %d: Day of the month (01-31)
            %H: Hour (24-hour clock, 00-23)
            %M: Minute (00-59)
            %S: Second (00-59)

            %Y: Year with century (e.g., 2023)
            %y: Year without century (e.g., 23 for 2023)
            %m: Month as a zero-padded decimal number (01-12)
            %d: Day of the month as a zero-padded decimal number (01-31)
            %H: Hour (24-hour clock) as a zero-padded decimal number (00-23)
            %M: Minute as a zero-padded decimal number (00-59)
            %S: Second as a zero-padded decimal number (00-59)
            %a: Abbreviated weekday name (e.g., Mon)
            %A: Full weekday name (e.g., Monday)
            %b: Abbreviated month name (e.g., Jan)
            %B: Full month name (e.g., January)
            %c: Preferred date and time representation
            %x: Preferred date representation
            %X: Preferred time representation
            %I: Hour (12-hour clock) as a zero-padded decimal number (01-12)
            %p: AM or PM
        """

        # formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")
        formatted_date = DateUtils.getCurrentDate().strftime(format)
        print("Formatted date:", formatted_date)
        return formatted_date

    @staticmethod
    def get_elapsed_time(start_time: time, stop_time: time):
        elapsed_time = stop_time - start_time
        return elapsed_time

    @staticmethod
    def convert_time_to_datetime(time_seconds: time) -> datetime:
        return datetime.utcfromtimestamp(time_seconds)

    @staticmethod
    def convert_datetime_to_time(current_datetime: datetime) -> time:
        time_seconds = time.mktime(current_datetime.timetuple())
        return time_seconds

    @staticmethod
    def get_time_for_perf_counter() -> time:
        return time.perf_counter()