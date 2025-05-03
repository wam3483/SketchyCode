import warnings
from dataclasses import asdict
from typing import Any

from flask import json

from data.ConfigSettings import ConfigSettings
from data.HardwareSettings import HardwareSettings

class SettingsFileDao:
    def __init__(self, hardware_settings_file_path: str, config_settings_file_path: str):
        self._hardware_settings_file_path = hardware_settings_file_path
        self._config_settings_file_path = config_settings_file_path

    def set_config_settings(self, config_settings : ConfigSettings) -> bool:
        try:
            with open(self._config_settings_file_path, 'w') as f:
                json.dump(asdict(config_settings), f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to save config settings: {e}")
            return False

    def get_config_settings(self) -> ConfigSettings:
        try:
            with open(self._config_settings_file_path, 'r') as f:
                data: dict[str, Any] = json.load(f)
                return ConfigSettings(**data)
        except Exception as e:
            warnings.warn(f"Failed to load config settings. Filepath=[{self._config_settings_file_path}]: {e}")

        return ConfigSettings(
            xBacklashPixels = 2.5,
            yBacklashPixels = 2.5,
            xDegreesPerPixel = 3.8,
            yDegreesPerPixel = 3.4,
            drawSpeed_PixelsPerSec = 200
        )

    def set_hardware_settings(self, hardware_settings : HardwareSettings) -> bool:
        try:
            with open(self._hardware_settings_file_path, 'w') as f:
                json.dump(asdict(hardware_settings), f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to save hardware settings: {e}")
            return False

    def get_hardware_settings(self) -> HardwareSettings:
        try:
            with open(self._hardware_settings_file_path, 'r') as f:
                data: dict[str, Any] = json.load(f)
                return HardwareSettings(**data)
        except Exception as e:
            warnings.warn(f"Failed to load hardware settings. Filepath=[{self._hardware_settings_file_path}]: {e}")
            # Return a default instance
            return HardwareSettings(
                xStepPin=27,
                xEnablePin=22,
                xDirectionPin=17,
                yStepPin=24,
                yEnablePin=25,
                yDirectionPin=23,
                stepsPerCycle=3200
            )