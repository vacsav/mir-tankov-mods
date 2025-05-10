import Math, math_utils, BigWorld, BattleReplay, constants
from Math import Matrix
from AvatarInputHandler.DynamicCameras.ArcadeCamera import ArcadeCamera, ENABLE_INPUT_ROTATION_INERTIA, _COLLIDE_ANIM_DIST, _COLLIDE_ANIM_INTERVAL
from AvatarInputHandler.DynamicCameras.arcade_camera_helper import EScrollDir
from account_helpers.settings_core.settings_constants import GAME
from gui.battle_control import event_dispatcher

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
def enable(func, self, preferredPos=None, closesDist=False, postmortemParams=None, turretYaw=None, gunPitch=None, camTransitionParams=None, initialVehicleMatrix=None, arcadeState=None):
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
    isPreCommanderCam = self._ArcadeCamera__compareCurrStateSettingsKey(GAME.PRE_COMMANDER_CAM)
    isCommanderCam = self._ArcadeCamera__compareCurrStateSettingsKey(GAME.COMMANDER_CAM)
    if isPreCommanderCam or isCommanderCam or arcadeState is not None:
        state = None
        newCameraDistance = self._cfg['distRange'].max
        if arcadeState is not None:
            self._ArcadeCamera__zoomStateSwitcher.switchToState(arcadeState.zoomSwitcherState)
            state = self._ArcadeCamera__zoomStateSwitcher.getCurrentState()
            newCameraDistance = arcadeState.camDist
        self._ArcadeCamera__updateProperties(state=state)
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


@overrideIn(ArcadeCamera)
def __update(func, self, dx, dy, dz, rotateMode = True, zoomMode = True):
    if self._ArcadeCamera__aimingSystem:
        eScrollDir = EScrollDir.convertDZ(dz)
        prevPos = self._ArcadeCamera__inputInertia.calcWorldPos(self._ArcadeCamera__aimingSystem.matrixProvider)
        prevDist = self._ArcadeCamera__aimingSystem.distanceFromFocus
        distMinMax = self._ArcadeCamera__distRange
        if self._ArcadeCamera__isCamInTransition:
            self._ArcadeCamera__isCamInTransition = self._ArcadeCamera__cameraTransition.isInTransition()
        isColliding = self._ArcadeCamera__cam.hasCollision()
        collisionWhileGlide = False
        isPreCommanderCam = self._ArcadeCamera__compareCurrStateSettingsKey(GAME.PRE_COMMANDER_CAM)
        isCommanderCam = self._ArcadeCamera__compareCurrStateSettingsKey(GAME.COMMANDER_CAM)
        preCommanderCam = self._ArcadeCamera__isSettingsEnabled(GAME.PRE_COMMANDER_CAM)
        commanderCam = self._ArcadeCamera__isSettingsEnabled(GAME.COMMANDER_CAM)
        if self._ArcadeCamera__inputInertia.isGliding() and not isColliding and eScrollDir is EScrollDir.OUT and not (isPreCommanderCam or isCommanderCam):
            cameraPos = self._ArcadeCamera__aimingSystem.matrix.translation
            collisionWhileGlide = self._ArcadeCamera__cam.isColliding(BigWorld.player().spaceID, cameraPos)
        preventScrollOut = (isColliding or collisionWhileGlide) and (eScrollDir is EScrollDir.OUT) and not (isPreCommanderCam or isCommanderCam)
        if preventScrollOut and prevDist == distMinMax.max and (preCommanderCam or commanderCam) and (self._ArcadeCamera__isInArcadeZoomState() or isPreCommanderCam):
            preventScrollOut = False
        if isColliding and eScrollDir is EScrollDir.OUT:
            self._ArcadeCamera__collideAnimatorEasing.start(_COLLIDE_ANIM_DIST, _COLLIDE_ANIM_INTERVAL)
        distChanged = False
        if zoomMode and eScrollDir and not self._ArcadeCamera__overScrollProtector.isProtecting() and not preventScrollOut:
            if eScrollDir is EScrollDir.OUT and not isCommanderCam and commanderCam:
                event_dispatcher.showCommanderCamHint(show = True)
            distDelta = dz * float(self._ArcadeCamera__curScrollSense)
            newDist = math_utils.clamp(distMinMax.min, distMinMax.max, prevDist - distDelta)
            floatEps = 0.001
            if abs(newDist - prevDist) > floatEps:
                self._ArcadeCamera__updateCameraSettings(newDist)
                self._ArcadeCamera__inputInertia.glideFov(self._ArcadeCamera__calcRelativeDist())
                self._ArcadeCamera__aimingSystem.aimMatrix = self._ArcadeCamera__calcAimMatrix()
                distChanged = True
            if abs(newDist - prevDist) < floatEps and math_utils.almostZero(newDist - distMinMax.min):
                if self._ArcadeCamera__isInArcadeZoomState() and self._ArcadeCamera__onChangeControlMode and not self._ArcadeCamera__updatedByKeyboard:
                    self._ArcadeCamera__onChangeControlMode()
                    return
                else:
                    self._ArcadeCamera__changeZoomState(EScrollDir.IN)
            elif abs(newDist - prevDist) < floatEps and math_utils.almostZero(newDist - distMinMax.max):
                self._ArcadeCamera__changeZoomState(EScrollDir.OUT)
        if rotateMode and not self._ArcadeCamera__isCamInTransition:
            self._ArcadeCamera__updateAngles(dx, dy)
        if ENABLE_INPUT_ROTATION_INERTIA and not distChanged:
            self._ArcadeCamera__aimingSystem.update(0.0)
        if ENABLE_INPUT_ROTATION_INERTIA or distChanged:
            self._ArcadeCamera__startInputInertiaTransition(prevPos)
        return
    else:
        return


@overrideIn(ArcadeCamera)
def __updateAdvancedCollision(func, self):
    isPreCommanderCam = self._ArcadeCamera__compareCurrStateSettingsKey(GAME.PRE_COMMANDER_CAM)
    isCommanderCam = self._ArcadeCamera__compareCurrStateSettingsKey(GAME.COMMANDER_CAM)
    enable = isPreCommanderCam or isCommanderCam
    self._ArcadeCamera__cam.setCollisionCheckOnlyAtPos(enable)
    self._ArcadeCamera__aimingSystem.cursorShouldCheckCollisions(not enable)