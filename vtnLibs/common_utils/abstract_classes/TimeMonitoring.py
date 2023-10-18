import time
from . import LEC
from . import dtU
from . import ABC, abstractmethod
class TimeMonitoring(LEC):
    TIME_DIM_SEC = "sec."
    TIME_DIM_MSEC = "msec."
    def __init__(self):
        self.start_time = None
        self.stop_time = None
        self.intermediate_time = None
        self.precision = 2
        self.time_dim = TimeMonitoring.TIME_DIM_SEC
        # self.info_message = 'Process completed. Elapsed time: {:.'+str(self.precision)+'f} {:s}'

        self.set_timer_parameters()

    def startTimer(self):
        self.start_time = dtU.get_time_for_perf_counter()
        self.debug(f"start time set at: {self.start_time}")
    def stopTimer(self):
        self.stop_time = dtU.get_time_for_perf_counter()
        self.debug(f"stop time set at: {self.stop_time}")

    def start_intermediate_timer(self):
        self.intermediate_time = dtU.get_time_for_perf_counter()
        self.debug(f"Intermediate time set at: {self.intermediate_time}")

    def set_timer_parameters(self, time_dim=TIME_DIM_SEC, precision: int=2):
        self.precision = precision
        self.time_dim = time_dim

    def __displayElapsedTime__(self, start_time, stop_time, process_message):
        elapsed_time_sec = dtU.get_elapsed_time(start_time, stop_time)
        elapsed_time_ms = elapsed_time_sec * 1e6
        # Convert elapsed time to days, hours, minutes, seconds, and milliseconds
        try:
            self.info(process_message+dtU.get_elpased_time_message(elapsed_time_ms))
            # if self.time_dim == TimeMonitoring.TIME_DIM_MSEC:
            #     self.info((process_message+self.info_message).format(elapsed_time_ms))
            # else:
            #     self.info((process_message+self.info_message).format(elapsed_time_sec))

        except Exception as e:
            self.error(message=f"an error occured {e}", exception=e)

    def show_total_processing_time(self):
        self.__displayElapsedTime__(self.start_time, self.stop_time, 'Process completed: ')

    def show_elapsed_time_since_intermediate_timer(self):
        self.__displayElapsedTime__(self.intermediate_time, dtU.get_time_for_perf_counter(), 'measuring intermediate process: ')

