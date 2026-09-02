MIN_SENSITIVITY = 0.01
MAX_SENSITIVITY_ARCADE = 1.5
MAX_SENSITIVITY_SNIPER = 1.5
MAX_SENSITIVITY_STRATEGIC = 3.0
MAX_SENSITIVITY_ASSIST = 3.0
MAX_SENSITIVITY_ASSAULT = 3.0

MAX_SENSITIVITY_MAP = {
    'arcade': MAX_SENSITIVITY_ARCADE,
    'sniper': MAX_SENSITIVITY_SNIPER,
    'strategic': MAX_SENSITIVITY_STRATEGIC,
    'assist': MAX_SENSITIVITY_ASSIST,
    'assault': MAX_SENSITIVITY_ASSAULT,
}


def _get_settings_core():
    from helpers import dependency
    from skeletons.account_helpers.settings_core import ISettingsCore
    return dependency.instance(ISettingsCore)


def clamp_sensitivity(value, max_sensitivity = None):
    if max_sensitivity is None:
        max_sensitivity = max(MAX_SENSITIVITY_MAP.values())
    return max(MIN_SENSITIVITY, min(max_sensitivity, float(value)))


def parse_sensitivity(value, default):
    try:
        return clamp_sensitivity(float(value))
    except (TypeError, ValueError):
        return clamp_sensitivity(default)


def format_sensitivity(value):
    return '%.6f' % clamp_sensitivity(value)


def get_arcade_sensitivity():
    from account_helpers.settings_core.settings_constants import CONTROLS
    return _get_settings_core().getSetting(CONTROLS.MOUSE_ARCADE_SENS)


def get_sniper_sensitivity():
    from account_helpers.settings_core.settings_constants import CONTROLS
    return _get_settings_core().getSetting(CONTROLS.MOUSE_SNIPER_SENS)
    
    
def get_strategic_sensitivity():
    from account_helpers.settings_core.settings_constants import CONTROLS
    return _get_settings_core().getSetting(CONTROLS.MOUSE_STRATEGIC_SENS)
    
    
def get_assist_sensitivity():
    from account_helpers.settings_core.settings_constants import CONTROLS
    return _get_settings_core().getSetting(CONTROLS.MOUSE_ASSIST_AIM_SENS) 
    
    
def get_assault_sensitivity():
    from account_helpers.settings_core.settings_constants import CONTROLS
    return _get_settings_core().getSetting(CONTROLS.MOUSE_ASSAULT_SENS)


def apply_sensitivities(arcade, sniper, strategic, assist, assault):
    import BigWorld
    from account_helpers.settings_core.settings_constants import CONTROLS

    arcade_value = clamp_sensitivity(arcade, MAX_SENSITIVITY_ARCADE)
    sniper_value = clamp_sensitivity(sniper, MAX_SENSITIVITY_SNIPER)
    strategic_value = clamp_sensitivity(strategic, MAX_SENSITIVITY_STRATEGIC)
    assist_value = clamp_sensitivity(assist, MAX_SENSITIVITY_ASSIST)
    assault_value = clamp_sensitivity(assault, MAX_SENSITIVITY_ASSAULT)

    settings_core = _get_settings_core()
    settings_core.applySetting(CONTROLS.MOUSE_ARCADE_SENS, arcade_value)
    settings_core.applySetting(CONTROLS.MOUSE_SNIPER_SENS, sniper_value)
    settings_core.applySetting(CONTROLS.MOUSE_STRATEGIC_SENS, strategic_value)
    settings_core.applySetting(CONTROLS.MOUSE_ASSIST_AIM_SENS, assist_value)
    settings_core.applySetting(CONTROLS.MOUSE_ASSAULT_SENS, assault_value)

    BigWorld.savePreferences()

    return (arcade_value, sniper_value, strategic_value, assist_value, assault_value)