import psutil
import time
from loguru import logger
from fabric.widgets import (
	Overlay,
	Label,
	CircularProgressBar,
)
from fabric.utils import invoke_repeater

class BatteryCircular(Overlay):
	def __init__(
		self,
		services,
		animation = False,
		**kwargs
	):
		super().__init__()
		self.battery_icons = [ "󰂎", "󰁺", "󰁻", "󰁼", "󰁽", "󰁾", "󰁿", "󰂀", "󰂁", "󰂂", "󰁹" ]
		self.progress_bar = CircularProgressBar(
			**kwargs
		)
		self.set_children(self.progress_bar)
		self.label_widget = Label("󰁹")
		self.set_overlays(self.label_widget)
		services["Battery"].connect("changed", self.update)
		# services["Battery"].connect("charging", self.update)

	def update(self, obj, data):
		if data[0] < 10:
			icon = 0
		elif data[0] < 20:
			icon = 1
		elif data[0] < 30:
			icon = 2
		elif data[0] < 40:
			icon = 3
		elif data[0] < 50:
			icon = 4
		elif data[0] < 60:
			icon = 5
		elif data[0] < 70:
			icon = 6
		elif data[0] < 80:
			icon = 7
		elif data[0] < 90:
			icon = 8
		elif data[0] < 95:
			icon = 9
		else:
			icon = 10
		self.progress_bar.percentage = data[0]
		self.label_widget.set_label(self.battery_icons[icon])
		sp1 = "Charging: "
		sp2 = str(int(data[0])) + "%" + (f" | {int(data[-2])}%" if data[-1] is not 100 else "")
		sp3 = ""
		if not data[2]:
			sp1 = "Discharging: "
			sp3 = "\nTime left: " + (time.strftime('%H:%M:%S',time.gmtime(data[1])) if type(data[1]) is int else "???")
		# tt = ("charging" if data[2] else "discharging") + ": " + str(data[0]) + (f"\nTime left: {data[1] if type(data[1]) is int else '?'}" if not data[2] else "")
		tt = sp1 + sp2 + sp3
		self.set_tooltip_text(tt)
