from loguru import logger
from fabric.widgets import (
	Box,
	Label,
	Overlay,
	EventBox,
	CircularProgressBar
)

class SpeakerWidget(Box):
	def __init__(self, services, **kwargs):
		super().__init__(**kwargs)
		self.speaker_icons = [ "󰖁", "󰕿", "󰖀", "󰕾", "󱄠", "󰸈", "󰝝", "󰝞", "󰝟" ]
		self.audio = services["Speaker"]

		self.circular_progress_bar = CircularProgressBar(
			name="speaker-circular-progress-bar",
			# v_expand = kwargs.get("v_expand", False),
			# h_expand = kwargs.get("h_expand", False),
		)
		self.label_widget = Label(
			label="",
			# style="margin: 0em 0.375em 0em 0em; font-size: 0.75em",
		)

		self.event_box = EventBox(
			events = [ "button-press", "scroll"],
			v_expand = kwargs.get("v_expand", False),
			h_expand = kwargs.get("h_expand", False),
			children=Overlay(
				# v_expand = kwargs.get("v_expand", False),
				# h_expand = kwargs.get("h_expand", False),
				children=self.circular_progress_bar,
				overlays=self.label_widget,
			),
		)

		self.event_box.connect("scroll-event", self.on_scroll)
		self.event_box.connect("button-press-event", self.on_button_press)
		self.audio.connect("speaker-changed", self.update)
		self.add(self.event_box)

	def on_scroll(self, widget, event):
		if event.direction == 0:
			self.audio.speaker.volume += 1
		elif event.direction == 1:
			self.audio.speaker.volume -= 1

	def on_button_press(self, widget, event):
		if event.button == 3 and event.type == 4:
			self.audio.speaker.is_muted = not self.audio.speaker.is_muted
			logger.info(f"[SpeakerWidget] {'Muted' if self.audio.speaker.is_muted else 'Unmuted'} speaker")
		return

	def update(self, *args):
		if self.audio.speaker is not None:
			volume = self.audio.speaker.volume
			icon = -1
			if self.audio.speaker.is_muted:
				icon = 5
			else:
				if volume == 0:
					icon = 0
				elif volume <= 33:
					icon = 1
				elif volume <= 66:
					icon = 2
				elif volume <= 100:
					icon = 3
				elif volume >= 100:
					icon = 4
			self.label_widget.set_label(self.speaker_icons[icon])
			self.circular_progress_bar.percentage = volume
			self.set_tooltip_text(f"{self.audio.speaker.name} Volume: {int(volume)}%")
		return

class MicrophoneWidget(Box):
	def __init__(self, services, **kwargs):
		super().__init__(**kwargs)
		self.microphone_icons = [ "󰍭", "󰍬", "󰢴", "󰢳" ]
		self.audio = services["Microphone"]

		self.circular_progress_bar = CircularProgressBar(
			name="microphone-circular-progress-bar",
			# background_color=False,  # false = disabled
			# radius_color=False,
			# v_expand = kwargs.get("v_expand", False),
			# h_expand = kwargs.get("h_expand", False),
			# pie=True,
		)
		self.label_widget = Label(
			label="",
			# style="margin: 0em 0.375em 0em 0em; font-size: 0.75em",
		)

		self.event_box = EventBox(
			events = [ "button-press", "scroll"],
			v_expand = kwargs.get("v_expand", False),
			h_expand = kwargs.get("h_expand", False),
			children=Overlay(
				# v_expand = kwargs.get("v_expand", False),
				# h_expand = kwargs.get("h_expand", False),
				children=self.circular_progress_bar,
				overlays=self.label_widget,
			),
		)

		self.event_box.connect("scroll-event", self.on_scroll)
		self.event_box.connect("button-press-event", self.on_button_press)
		self.audio.connect("microphone-changed", self.update)
		self.add(self.event_box)

	def on_scroll(self, widget, event):
		if event.direction == 0:
			self.audio.microphone.volume += 1
		elif event.direction == 1:
			self.audio.microphone.volume -= 1

	def on_button_press(self, widget, event):
		if event.button == 3 and event.type == 4:
			self.audio.microphone.is_muted = not self.audio.microphone.is_muted
			logger.info(f"[Microphone] {'Muted' if self.audio.microphone.is_muted else 'Unmuted'} microphone")
		return

	def update(self, *args):
		if self.audio.microphone is not None:
			volume = self.audio.microphone.volume
			icon = -1
			if self.audio.microphone.is_muted:
				icon = 0
			else:
				if volume == 0:
					icon = 0
				else:
					icon = 1
			self.label_widget.set_label(self.microphone_icons[icon])
			self.circular_progress_bar.percentage = volume
			self.set_tooltip_text(f"{self.audio.microphone.name} Volume: {int(volume)}%")
		return
