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
        self.time_dim = TimeMonitoring.TIME_DIM_MSEC
        self.info_message = 'Process completed. Elapsed time: {:.'+str(self.precision)+'f} {:s}'

    def startTimer(self):
        self.start_time = dtU.get_time_for_perf_counter()
    def stopTimer(self):
        self.stop_time = dtU.get_time_for_perf_counter()
    def start_intermediate_timer(self):
        self.intermediate_time = dtU.get_time_for_perf_counter()

    def set_parameters(self, time_dim=TIME_DIM_MSEC, precision: int=2):
        self.precision = precision
        self.time_dim = time_dim
        self.info_message = 'Process completed. Elapsed time: {:.'+str(self.precision)+'f} '+self.time_dim

    def __displayElapsedTime__(self, start_time, stop_time):
        elapsed_time = dtU.get_elapsed_time(start_time, stop_time)
        if self.time_dim==TimeMonitoring.TIME_DIM_MSEC:
            elapsed_time = elapsed_time * 1e6
        self.info(self.info_message.format(elapsed_time))

    def show_total_processing_time(self):
        self.__displayElapsedTime__(self.start_time, self.stop_time)

    def show_elapsed_time_since_intermediate_timer(self):
        self.__displayElapsedTime__(self.intermediate_time, dtU.get_time_for_perf_counter())

