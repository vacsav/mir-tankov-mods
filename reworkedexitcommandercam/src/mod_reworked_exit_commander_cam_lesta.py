import Math, BattleReplay, BigWorld, constants
from Math import Matrix
from account_helpers.settings_core.settings_constants import GAME
from AvatarInputHandler.DynamicCameras.ArcadeCamera import ArcadeCamera

def overrideIn(cls, condition=lambda : True):

    def _overrideMethod(func):
        if not condition():
            return func
        funcName = func.__name__
        if funcName.startswith('__'):
            prefix = '_' if not cls.__name__.startswith('_') else ''
            funcName = prefix + cls.__name__ + funcName
        old = getattr(cls, funcName)

        def wrapper(*args, **kwargs):
            return func(old, *args, **kwargs)

        setattr(cls, funcName, wrapper)
        return wrapper

    return _overrideMethod


@overrideIn(ArcadeCamera)
def enable(func, self, preferredPos = None, closesDist = False, postmortemParams = None, turretYaw = None, gunPitch = None, camTransitionParams = None, initialVehicleMatrix = None, arcadeState = None):
    replayCtrl = BattleReplay.g_replayCtrl
    if replayCtrl.isRecording:
        replayCtrl.setAimClipPosition(self._ArcadeCamera__aimOffset)
    self.measureDeltaTime()
    player = BigWorld.player()
    vehicle = player.getVehicleAttached()
    if player.observerSeesAll() and player.arena.period == constants.ARENA_PERIOD.BATTLE and vehicle and vehicle.id == player.playerVehicleID:
        self.delayCallback(0.0, self.enable, preferredPos, closesDist, postmortemParams, turretYaw, gunPitch, camTransitionParams, initialVehicleMatrix)
        return
    elif initialVehicleMatrix is None:
        initialVehicleMatrix = player.getOwnVehicleMatrix(Math.Matrix(self.vehicleMProv)) if vehicle is None else vehicle.matrix
    vehicleMProv = initialVehicleMatrix
    if not self._ArcadeCamera__isInArcadeZoomState() or arcadeState is not None:
        if arcadeState is None:
            state = None
            newCameraDistance = self._cfg['distRange'].max
        else:
            self._ArcadeCamera__zoomStateSwitcher.switchToState(arcadeState.zoomSwitcherState)
            state = self._ArcadeCamera__zoomStateSwitcher.getCurrentState()
            newCameraDistance = arcadeState.camDist
        self._ArcadeCamera__updateProperties(state = state)
        self._ArcadeCamera__updateCameraSettings(newCameraDistance)
        self._ArcadeCamera__inputInertia.glideFov(self._ArcadeCamera__calcRelativeDist())
        if arcadeState is None:
            self._ArcadeCamera__aimingSystem.aimMatrix = self._ArcadeCamera__calcAimMatrix()
    camDist = None
    if self._ArcadeCamera__postmortemMode:
        if postmortemParams is not None:
            self._ArcadeCamera__aimingSystem.yaw = postmortemParams[0][0]
            self._ArcadeCamera__aimingSystem.pitch = postmortemParams[0][1]
            camDist = postmortemParams[1]
        else:
            camDist = self._ArcadeCamera__distRange.max
    elif closesDist:
        camDist = self._ArcadeCamera__distRange.min
    replayCtrl = BattleReplay.g_replayCtrl
    if replayCtrl.isPlaying and not replayCtrl.isServerSideReplay:
        camDist = None
        vehicle = BigWorld.entity(replayCtrl.playerVehicleID)
        if vehicle is not None:
            vehicleMProv = vehicle.matrix
    if camDist is not None:
        self.setCameraDistance(camDist)
    else:
        self._ArcadeCamera__inputInertia.teleport(self._ArcadeCamera__calcRelativeDist())
    self.vehicleMProv = vehicleMProv
    self._ArcadeCamera__setDynamicCollisions(True)
    self._ArcadeCamera__aimingSystem.enable(preferredPos, turretYaw, gunPitch)
    self._ArcadeCamera__aimingSystem.aimMatrix = self._ArcadeCamera__calcAimMatrix()
    if camTransitionParams is not None and BigWorld.camera() is not self._ArcadeCamera__cam:
        cameraTransitionDuration = camTransitionParams.get('cameraTransitionDuration', -1)
        if cameraTransitionDuration > 0:
            self._ArcadeCamera__setupCameraTransition(cameraTransitionDuration)
        else:
            self._ArcadeCamera__setCamera()
    else:
        self._ArcadeCamera__setCamera()
    self._ArcadeCamera__cameraUpdate()
    self.delayCallback(0.0, self._ArcadeCamera__cameraUpdate)
    from gui import g_guiResetters
    g_guiResetters.add(self._ArcadeCamera__onRecreateDevice)
    self._ArcadeCamera__updateAdvancedCollision()
    self._ArcadeCamera__updateLodBiasForTanks()
