from realm import CURRENT_REALM
from constants import QUEUE_TYPE
from gui.prb_control.factories.PreQueueFactory import PreQueueFactory
from gui.prb_control.factories.PreQueueFactory import DefaultEntityHandler
from gui.prb_control.storages.local_storage import SessionStorage
from gui.prb_control.entities.random.pre_queue.entity import RandomEntity
from gui.prb_control.storages import prequeue_storage_getter, makeQueueName, registerPrbStorage


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


class RandomStorage(SessionStorage):
    def _determineSelection(self, arenaVisitor):
        return arenaVisitor.gui.isRandomBattle()
registerPrbStorage(makeQueueName(QUEUE_TYPE.RANDOMS), RandomStorage())


origPreQueueFactoryInit = PreQueueFactory.__init__
def modPreQueueFactoryInit(self, *args, **kwargs):
    origPreQueueFactoryInit(self, *args, **kwargs)
    self.randomStorage = prequeue_storage_getter(QUEUE_TYPE.RANDOMS)()
PreQueueFactory.__init__ = modPreQueueFactoryInit


@overrideIn(PreQueueFactory, condition = isClientLesta)
def __createDefaultEntity(func, self):
    if self.recentPrbStorage.queueType == QUEUE_TYPE.RANDOMS:
        return RandomEntity()
    return func(self)


@overrideIn(DefaultEntityHandler, condition = isClientLesta)
def getDefaultQueueType(func, self):
    default = func(self)
    if default == QUEUE_TYPE.RANDOMS:
        return QUEUE_TYPE.MAPS_TRAINING
    return default