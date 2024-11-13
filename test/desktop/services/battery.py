import psutil
# from os.path import path
from loguru import logger
from fabric.service import Service, Signal, SignalContainer
from fabric.utils import invoke_repeater

class Battery(Service):
	__gsignals__ = SignalContainer(
		Signal(name = "changed", args = (object,)),
		Signal(name = "charging", args = (bool,)),
	)
	def __init__(self, interval = 1000, **kwargs):
		super().__init__(**kwargs)
		self.file = "/sys/class/power_supply/BAT0/charge_control_end_threshold"
		self.cap = 60
		invoke_repeater(interval, self.update)
	
	def update(self,):
		percent, time, plugged = psutil.sensors_battery()
		self.emit(
			"changed",
			[percent / self.cap*100, time if type(time) is int else -1, plugged, percent, self.cap]
		)
		self.emit(
			"charging",
			plugged
		)
		return True
	
	# def reload_cap(self,):
	# 	with open("")
