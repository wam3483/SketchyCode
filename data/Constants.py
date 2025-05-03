import logging
import platform

import pigpio

from dao.SettingsFileDao import SettingsFileDao
from data.Utils import on_raspberry
from plotter.PlotterContainer import PlotterContainer
from plotter.gpio_pin_null import GPIOPinNull
from plotter.plotter_manager import PlotterManager
from plotter.stepper_motor import StepperMotor
from plotter.xy_plotter import XYPlotter

settings_repo = SettingsFileDao("hardwareSettings.json","configSettings.json")

plotter = PlotterContainer()

display_width = 550
display_height = 400

pigpio_singleton : None | pigpio.pi = None
if on_raspberry:
    pigpio_singleton = pigpio.pi()

plotter.instance = XYPlotter.init_plotter(pigpio_singleton, settings_repo)

plotterManager = PlotterManager()