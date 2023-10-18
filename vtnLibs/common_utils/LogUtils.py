import logging
import traceback
from vtnLibs.DecoratorAndAnnotation import *
# from vtnLibs.common_utils.DateTimeUtils import DateUtils as dtU
import pprint

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
    def __genLog__(cls, logMethod, message=None, exception=None, appendTrace= False, **kwargs):
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
    def __addStackTrace__(cls, logMethod=None, exception=None):
        if logMethod:
            # print("__addStackTrace__")
            s = cls .__getStackTrace__(exception)
            # for l in s:
            #     logMethod(l.strip() + "\n")
            logMethod(s)

    @classmethod
    def __getStackTrace__(cls, exception=None):
        # print("__getStackTrace__")
        if exception:
            stack_trace = traceback.format_exc()
        else:
            stack_trace = traceback.format_tb(exception.__traceback__)
        return stack_trace

    @classmethod
    def debug(cls, message, exception=None, appendTrace= False, **kwargs):
        # print("debug called")
        cls.__genLog__(logMethod=cls.logger.debug, message=message, exception=exception, appendTrace= appendTrace, **kwargs)
    @classmethod
    def info(cls, message, exception=None, appendTrace= False, **kwargs):
        cls.__genLog__(logMethod=cls.logger.info, message=message, exception=exception, appendTrace= appendTrace, **kwargs)

    @classmethod
    def warning(cls, message, exception=None, appendTrace= False, **kwargs):
        cls.__genLog__(logMethod=cls.logger.warning, message=message, exception=exception, appendTrace= appendTrace, **kwargs)

    @classmethod
    def error(cls, message, exception=None, appendTrace= False, **kwargs):
        cls.__genLog__(logMethod=cls.logger.error, message=message, exception=exception, appendTrace= appendTrace, **kwargs)

    @classmethod
    def critical(cls, message, exception=None, appendTrace= False, **kwargs):
        cls.__genLog__(logMethod=cls.logger.critical, message=message, exception=exception, appendTrace= appendTrace, **kwargs)

    @classmethod
    def __getStackTrace__(cls, exception=None):
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


