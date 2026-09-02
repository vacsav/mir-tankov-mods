from debug_utils import LOG_NOTE


MOD_LINKAGE = 'extended_sensitivity_adjustment'
SETTINGS_VERSION = 5
HINT_TOOLTIP = '{HEADER}Precise mouse sensitivity{/HEADER}{BODY}Enter the exact sensitivity values stored in your game preferences. These are the same floats written to preferences.xml under controlMode for Arcade, Sniper, Strategic, Assist, Assault camera modes.{/BODY}'
INPUT_TOOLTIP = HINT_TOOLTIP + '{BODY}Valid range: %.1f to %.1f. Use up to six decimal places (for example 0.120000). Changes apply when you click Apply.{/BODY}'


def _get_mods_settings_api():
    try:
        from gui.modsSettingsApi import g_modsSettingsApi
    except ImportError:
        return

    return g_modsSettingsApi


def _build_template():
    from gui.extendedsensitivityadjustment import sensitivity
    from gui.modsSettingsApi import templates
    
    arcade_value = sensitivity.format_sensitivity(sensitivity.get_arcade_sensitivity())
    sniper_value = sensitivity.format_sensitivity(sensitivity.get_sniper_sensitivity())
    strategic_value = sensitivity.format_sensitivity(sensitivity.get_strategic_sensitivity())
    assist_value = sensitivity.format_sensitivity(sensitivity.get_assist_sensitivity())
    assault_value = sensitivity.format_sensitivity(sensitivity.get_assault_sensitivity())
    
    return {
            'modDisplayName': 'Extended Sensitivity Adjustment',
            'settingsVersion': SETTINGS_VERSION,
            'enabled': True,
            'column1': [
                templates.createLabel('Set the precise mouse sensitivity values for the modes:', tooltip=HINT_TOOLTIP),
                templates.createEmpty(),
                templates.createInput('Arcade', 'arcade_sensitivity', arcade_value, tooltip=INPUT_TOOLTIP % (sensitivity.MIN_SENSITIVITY, sensitivity.MAX_SENSITIVITY_ARCADE), width=100),
                templates.createInput('Sniper', 'sniper_sensitivity', sniper_value, tooltip=INPUT_TOOLTIP % (sensitivity.MIN_SENSITIVITY, sensitivity.MAX_SENSITIVITY_SNIPER), width=100),
                templates.createInput('Strategic', 'strategic_sensitivity', strategic_value, tooltip=INPUT_TOOLTIP % (sensitivity.MIN_SENSITIVITY, sensitivity.MAX_SENSITIVITY_STRATEGIC), width=100),
                templates.createInput('Assist', 'assist_sensitivity', assist_value, tooltip=INPUT_TOOLTIP % (sensitivity.MIN_SENSITIVITY, sensitivity.MAX_SENSITIVITY_ASSIST), width=100),
                templates.createInput('Assault', 'assault_sensitivity', assault_value, tooltip=INPUT_TOOLTIP % (sensitivity.MIN_SENSITIVITY, sensitivity.MAX_SENSITIVITY_ASSAULT), width=100)
            ],
            'column2': [
                templates.createLabel('Current values for the modes:'),
                templates.createEmpty(),
                templates.createLabel('Arcade — %s' % arcade_value),
                templates.createLabel('Sniper — %s' % sniper_value),
                templates.createLabel('Strategic — %s' % strategic_value),
                templates.createLabel('Assist — %s' % assist_value),
                templates.createLabel('Assault — %s' % assault_value),
                templates.createEmpty(),
                templates.createLabel('Values are saved to preferences.xml when you click Apply.')
            ]
    }


def _apply_settings(settings):
    from gui.extendedsensitivityadjustment import sensitivity
    
    settings = dict(settings)
    arcade = sensitivity.parse_sensitivity(settings.get('arcade_sensitivity'), sensitivity.get_arcade_sensitivity())
    sniper = sensitivity.parse_sensitivity(settings.get('sniper_sensitivity'), sensitivity.get_sniper_sensitivity())
    strategic = sensitivity.parse_sensitivity(settings.get('strategic_sensitivity'), sensitivity.get_strategic_sensitivity())
    assist = sensitivity.parse_sensitivity(settings.get('assist_sensitivity'), sensitivity.get_assist_sensitivity())
    assault = sensitivity.parse_sensitivity(settings.get('assault_sensitivity'), sensitivity.get_assault_sensitivity())
    sensitivity.apply_sensitivities(arcade, sniper, strategic, assist, assault)


def _on_settings_changed(linkage, settings):
    if linkage != MOD_LINKAGE:
        return

    _apply_settings(settings)

    from gui.extendedsensitivityadjustment import sensitivity
    api = _get_mods_settings_api()

    api.updateModSettings(MOD_LINKAGE, {
        'arcade_sensitivity': sensitivity.format_sensitivity(sensitivity.get_arcade_sensitivity()),
        'sniper_sensitivity': sensitivity.format_sensitivity(sensitivity.get_sniper_sensitivity()),
        'strategic_sensitivity': sensitivity.format_sensitivity(sensitivity.get_strategic_sensitivity()),
        'assist_sensitivity': sensitivity.format_sensitivity(sensitivity.get_assist_sensitivity()),
        'assault_sensitivity': sensitivity.format_sensitivity(sensitivity.get_assault_sensitivity()),
    })


def _on_button_clicked(linkage, varName, value):
    pass


def register_mods_settings():
    api = _get_mods_settings_api()
    
    if api is None:
        LOG_NOTE('ModsSettings API not installed. Extended Sensitivity Adjustment requires ModsSettings API, ModsList, and OpenWG Gameface.')
        return False
    else:
        template = _build_template()
        if api.getModSettings(MOD_LINKAGE, template):
            api.registerCallback(MOD_LINKAGE, _on_settings_changed, _on_button_clicked)
        else:
            api.setModTemplate(MOD_LINKAGE, template, _on_settings_changed, _on_button_clicked)
        return True