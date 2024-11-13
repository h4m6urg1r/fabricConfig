import time
from gi.repository import GLib
from fabric.widgets import (
	Button,
	Label,
	Box,
)
from fabric.utils import invoke_repeater

class DateWidget(Button):
	def __init__(
		self,
		format = ["hour", "minute", "period"],
		directiveMap = {
			"hour": "%I",
			"minute": "%M",
			"seconds": "%S",
			"period": "%p",
			"date": "%d",
			"day": "%A",
			"month": "%m",
			"year": "%Y",
		},
		tooltip_text = '%a, %d %b %Y %H:%M:%S',
		interval = 1000,
		orientation = "h",
		**kwargs
	):
		self.directiveMap = directiveMap
		self.format = format
		self.interval = interval
		self.tooltip_text = tooltip_text
		ctime = time.localtime()
		self.timeLabels = {
			key: Label(name = key, label = str(time.strftime(self.directiveMap[key], time.localtime()))) for key in self.directiveMap
		}
		super().__init__(
			child = Box(
				orientation = orientation,
				children = [
					self.timeLabels[status] for status in self.format
				]
			),
			**kwargs
		)
		invoke_repeater(self.interval, self.updateTime)

	def updateTime(self,):
		for status in self.format:
			self.timeLabels[status].set_label(str(time.strftime(self.directiveMap[status]))),
		self.set_tooltip_text(time.strftime(self.tooltip_text))
		return True
