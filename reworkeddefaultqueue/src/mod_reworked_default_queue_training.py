from realm import CURRENT_REALM
from constants import QUEUE_TYPE
from gui.prb_control.factories.PreQueueFactory import DefaultEntityHandler


def isClientLesta():
    return CURRENT_REALM == 'RU'


def overrideIn(cls, condition = lambda: True):

    def _overrideMethod(func):
        if not condition():
            return func

        funcName = func.__name__

        if funcName.startswith("__") and funcName != "__init__":
            funcName = "_" + cls.__name__ + funcName

        old = getattr(cls, funcName)

        def wrapper(*args, **kwargs):
            return func(old, *args, **kwargs)

        setattr(cls, funcName, wrapper)
        return wrapper
    return _overrideMethod


@overrideIn(DefaultEntityHandler, condition=isClientLesta)
def getDefaultQueueType(func, self):
    default = func(self)
    if default == QUEUE_TYPE.RANDOMS:
        return QUEUE_TYPE.MAPS_TRAINING
    return default