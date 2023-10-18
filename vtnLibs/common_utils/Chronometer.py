from .DateTimeUtils import DateUtils as dtU
from .LogUtils import LogEnabledClass as LEC
class LoggingChronometer(LEC):
    def __init__(self):
        self.start_time = None
        self.stop_time = None

    def startTimer(self):
        self.start_time = dtU.get_time_for_perf_counter()
        self.debug(f"start time set at: {self.start_time}")
    def stopTimer(self):
        self.stop_time = dtU.get_time_for_perf_counter()
        self.debug(f"stop time set at: {self.stop_time}")

    def __displayElapsedTime__(self, start_time, stop_time, process_message):
        elapsed_time_sec = dtU.get_elapsed_time(start_time, stop_time)
        elapsed_time_ms = elapsed_time_sec * 1e6
        # Convert elapsed time to days, hours, minutes, seconds, and milliseconds
        try:
            self.info(process_message+dtU.get_elpased_time_message(elapsed_time_ms))
        except Exception as e:
            self.error(message=f"an error occured {e}", exception=e)
    def display_elapsed_time(self):
        intermediate_time = dtU.get_time_for_perf_counter()
        if(self.stop_time):
            self.__displayElapsedTime__(self.start_time, self.stop_time, 'Complete process duration: ')
        else:
            self.__displayElapsedTime__(intermediate_time, dtU.get_time_for_perf_counter(), 'Current since start: ')
