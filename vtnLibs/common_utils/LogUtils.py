import logging
import sys
import traceback
from vtnLibs.DecoratorAndAnnotation import *
# from vtnLibs.common_utils.DateTimeUtils import DateUtils as dtU
import pprint
import io
from typing import Callable, Tuple, List
from types import TracebackType
class LogEnabledMetaParentClass(type):
    logger = None
    def __new__(mcls, name, bases, attrs):
        cls = super().__new__(mcls, name, bases, attrs)
        print(f"initialize logger for class:{name}")
        cls.logger = logging.getLogger(name)
        return cls

    # def __init__(mcls, *args, **kwargs):
    #     instance = super().__init__(*args, **kwargs)
    #     name = "LogEnabledMetaParentClass"
    #     if "name" in kwargs.keys():
    #         name = kwargs.get("name")
    #     print(f"Initializing metaclass: {name}")

    # def __init__(mcls, *args, **kwargs):
    #     print("Initializing instance of MetaClass")

def configLogOutput(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'):
    logging.basicConfig(level=level, format=format)

def get_printable_from_tuple(my_tuple: tuple, indent=3) -> str:
    pp = pprint.PrettyPrinter(indent=indent)
    formatted_tuple = pp.pformat(my_tuple)
    return formatted_tuple

class LogEnabledClass(metaclass=LogEnabledMetaParentClass):
    def __init__(self):
        print(f"Initializing instance of BaseClass {self.__class__.__name__}")
    # @classmethod
    # def __genOutput__(cls, m, **kwargs):
    #     cls.__initLog__()
    #     cls.logger.debug(m.format(**kwargs))

    @classmethod
    def __genLog__(cls, logMethod: Callable, message: str=None, exception:Exception=None, appendTrace:bool= False, **kwargs):
        # print(f"__genLog__ {message}")
        # cls.__initLog__()
        if (message):
            logMethod(message.format(**kwargs))
        if appendTrace:
            if exception and logMethod:
                if logMethod:
                    cls.__addStackTrace__(logMethod=logMethod, exception=exception)
                    logMethod(f"{exception.stderr}")
                else:
                    cls.error(f"{exception.stderr}")
    @classmethod
    def get_info_from_sysinfo(self, message:str="") -> Tuple[str, Exception, TracebackType, str, str]:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        exception_message = str(exc_value)
        exception_docstring = exc_type.__doc__

        if exc_type is not None:
            exception_info = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            logging.error(f"{message}\n{exception_info}")
        else:
            logging.error(message)
        return exc_type, exc_value, exc_traceback,exception_message, exception_docstring

    @classmethod
    def get_info_from_exception(cls, exception: Exception) -> Tuple[str, Exception, TracebackType, str, str]:
        exc_type = type(exception)  # Equivalent to exc_type
        exc_value = exception  # Equivalent to exc_value

        exception_args = exception.args
        exception_message = exception_args[0] if exception_args else None
        exception_docstring = exc_type.__doc__

        # You can access the captured traceback as a string

        exc_traceback = exception.__traceback__
        return exc_type, exc_value, exc_traceback, exception_message, exception_docstring

    def traceback_to_str(self, traceback:traceback=None):
        if traceback:
            exception_traceback = io.StringIO()
            traceback.print_tb(traceback, file=exception_traceback)
            exc_traceback = exception_traceback.getvalue()
            return exc_traceback
        return None

    def parse_traceback_to_str(self, traceback: traceback):
        if traceback:
            s = ""
            while exc_traceback:
                s += f"[[Function: {exc_traceback.tb_frame.f_code.co_name}]"
                s += (f", [Line: {exc_traceback.tb_lineno}]")
                s += (f", [File: {exc_traceback.tb_frame.f_code.co_filename}]]")
                exc_traceback = exc_traceback.tb_next
            return s
        return None
    @classmethod
    def __addStackTrace__(cls, logMethod:Callable=None, exception:Exception=None):
        callable = logMethod
        if logMethod:
            callable = logMethod
        else:
            callable=logging.error
        # print("__addStackTrace__")
        s = cls .__getStackTrace__(exception)  #this function should return List[str]
        # for l in s:
        #     logMethod(l.strip() + "\n")
        if isinstance(s, list):
            for l in s:
                logMethod(l)
        else:
            # assuming that s is a string
            logMethod(s)

    @classmethod
    def __getStackTrace__(cls, exception:Exception=None) -> List[str]:
        # print("__getStackTrace__")
        if exception:
            stack_trace = traceback.format_tb(exception.__traceback__)
        else:
            exc_type, exc_value, exc_traceback, exception_message, exception_docstring = cls.get_info_from_sysinfo()
            if exc_type:
                # try to get stacktrace from the context (inside a except block)
                stack_trace = traceback.format_tb(exc_traceback)
            else:
                stack_trace = [traceback.format_exc()]
        return stack_trace

    @classmethod
    def debug(cls, message:str, exception:Exception=None, appendTrace:bool= False, **kwargs):
        # print("debug called")
        cls.__genLog__(logMethod=cls.logger.debug, message=message, exception=exception, appendTrace= appendTrace, **kwargs)
    @classmethod
    def info(cls, message:str, exception:Exception=None, appendTrace:bool= False, **kwargs):
        cls.__genLog__(logMethod=cls.logger.info, message=message, exception=exception, appendTrace= appendTrace, **kwargs)

    @classmethod
    def warning(cls, message:str, exception:Exception=None, appendTrace:bool= False, **kwargs):
        cls.__genLog__(logMethod=cls.logger.warning, message=message, exception=exception, appendTrace= appendTrace, **kwargs)

    @classmethod
    def error(cls, message:str, exception:Exception=None, appendTrace:bool= False, **kwargs):
        cls.__genLog__(logMethod=cls.logger.error, message=message, exception=exception, appendTrace= appendTrace, **kwargs)

    @classmethod
    def critical(cls, message:str, exception:Exception=None, appendTrace:bool= False, **kwargs):
        cls.__genLog__(logMethod=cls.logger.critical, message=message, exception=exception, appendTrace= appendTrace, **kwargs)

    @classmethod
    def __getStackTrace__(cls, exception:Exception=None):
        if exception:
            stack_trace = traceback.format_exc()
        else:
            stack_trace = traceback.format_tb(exception.__traceback__)
        return stack_trace

# @deprecated_class
# class LogUtils:
#     def __int__(self, classInstance):
#         self.logger = None
#         self.className=classInstance.__class__.__name__
#
#         self.__setupLogger__()
#
#     def __setupLogger__(self):
#
#         self.logger = logging.getLogger(self.className)
#         self.logger.setLevel(logging.DEBUG)
#
#     def debug(self, message, exception=None, appendTrace= False, **kwargs):
#         self.__genLog__(logMethod=self.logger.debug, exception=None, appendTrace= False, **kwargs)
#     def info(self, message, exception=None, appendTrace= False, **kwargs):
#         self.__genLog__(logMethod=self.logger.info, exception=None, appendTrace= False, **kwargs)
#     def warning(self, message, exception=None, appendTrace= False, **kwargs):
#         self.__genLog__(logMethod=self.logger.warning, exception=None, appendTrace= False, **kwargs)
#     def error(self, message, exception=None, appendTrace= False, **kwargs):
#         self.__genLog__(logMethod=self.logger.error, exception=None, appendTrace= False, **kwargs)
#     def critical(self, message, exception=None, appendTrace= False, **kwargs):
#         self.__genLog__(logMethod=self.logger.critical, exception=None, appendTrace= False, **kwargs)
#
#     @staticmethod
#     def debug(message, exception=None, appendTrace= False, **kwargs):
#         LogUtils.__genLog__(logMethod=logging.debug, exception=None, appendTrace= False, **kwargs)
#     @staticmethod
#     def info(message, exception=None, appendTrace= False, **kwargs):
#         LogUtils.__genLog__(logMethod=logging.info, exception=None, appendTrace= False, **kwargs)
#         logging.info(format(message, **kwargs))
#     @staticmethod
#     def warning(message, exception=None, appendTrace= False, **kwargs):
#         LogUtils.__genLog__(logMethod=logging.warning, exception=None, appendTrace= False, **kwargs)
#         logging.warning(format(message, **kwargs))
#     @staticmethod
#     def error(message, exception=None, appendTrace= False, **kwargs):
#         LogUtils.__genLog__(logMethod=logging.error, exception=None, appendTrace= False, **kwargs)
#         logging.error(format(message, **kwargs))
#     @staticmethod
#     def critical(message, exception=None, appendTrace= False, **kwargs):
#         LogUtils.__genLog__(logMethod=logging.critical, exception=None, appendTrace= False, **kwargs)
#         logging.critical(format(message, **kwargs))
#
#     @staticmethod
#     def __genLog__(logMethod, message=None, exception=None, appendTrace= False, **kwargs):
#         logMethod(message, **kwargs)
#         if appendTrace:
#             LogUtils.__addStackTrace__(logMethod=logMethod, exception=exception)
#
#     @staticmethod
#     def __addStackTrace__(logMethod=None, exception=None):
#         for l in LogUtils.__getStackTrace__(exception):
#             logMethod(l.strip() + "\n")
#
#     @staticmethod
#     def __getStackTrace__(exception=None):
#         if exception:
#             stack_trace = traceback.format_exc()
#         else:
#             stack_trace = traceback.format_tb(exception.__traceback__)
#         return stack_trace


