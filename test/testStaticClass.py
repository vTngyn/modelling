import logging
from vtnLibs.common_utils.LogUtils import LogUtils as lu, LogEnabledClass as LogEnableClassFromMyLibs
from vtnLibs.DeprecationAnnotation import *

class MetaParentClass(type):
    logger = None
    def __new__(mcls, name, bases, attrs):
        cls = super().__new__(mcls, name, bases, attrs)
        cls.logger = logging.getLogger(name)
        return cls

class LocalLogEnabledClass(metaclass=MetaParentClass):
    count = 0

    @classmethod
    def __initLog__(cls):
        if cls.logger is None:
            print("initializing logger")
            cls.logger = logging.getLogger(cls.__name__)

    @classmethod
    def __genOutput__(cls, m, **kwargs):
        cls.__initLog__()
        cls.logger.debug(m.format(**kwargs))


class MyUtilClass(LocalLogEnabledClass):
    @classmethod
    def jeFaisQqCHoseEtJeLog(cls):
        print("print: je fais qqchose")
        cls.__genOutput__(m="voici mon message de debug {object} !", object="boudin")

class InheritFromLibClass(LogEnableClassFromMyLibs):
    @classmethod
    def jeFaisAussiQqCHoseEtJeLog(cls):
        cls.debug(message="voici mon message de debug {object} !", object="cactus")
    @classmethod
    def jeGenereUneErreur(cls):
        print("je refais qqchose!")
        try:
            div0 = 45645/0
            cls.debug(message="tout va bien {object} !", object="JOhnny")
        except Exception as e:
            cls.error(message="{object}, il y a un stuuuuddd !", object="JOhnny")


if __name__ == "__main__":
    lu.config(level=logging.DEBUG)
    MyUtilClass.jeFaisQqCHoseEtJeLog()
    InheritFromLibClass.jeFaisAussiQqCHoseEtJeLog()
    InheritFromLibClass.jeGenereUneErreur()
