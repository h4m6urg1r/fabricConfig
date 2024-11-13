import psutil
import json
from os.path import join, dirname
from loguru import logger

from fabric.widgets import (
	WaylandWindow as Window,
	Button,
	Revealer,
	CenterBox,
	Label,
	Box,
	CircularProgressBar,
	SystemTray,
	Overlay,
)
from fabric.utils import invoke_repeater

from .dateWidget import DateWidget
from .battery import BatteryCircular
from .audio import SpeakerWidget, MicrophoneWidget
from desktop.utils.helpers import applySCSS

class VerticalBar(Window):
	def __init__(
		self,
		services,
		side="left",
		**kwargs
	):
		super().__init__(
			name = f"sideBar-{side}",
			layer = "top",
			anchor = f"top {side} bottom",
			# TODO: check for this shit on update
			# exclusivity = "normal",
			exclusive = True,
			visible = False,
			all_visible = False,
			# open_inspector = True,
			**kwargs
		)
		services["Hyprland"].connect("urgent", self.notify_urgent)

		self.urgent_workspaces = Box (
			name = "urgent-workspaces",
		)

		self.date_time = DateWidget(
			name = "Time",
			orientation = "v",
		)

		self.speaker_widget = SpeakerWidget(
			services,
			v_expand = True,
			h_expand = True,
		)
		self.microphone_widget = MicrophoneWidget(
			services,
			v_expand = True,
			h_expand = True,
		)
		self.cpu_info = CircularProgressBar(
			name = "cpu-progress-bar",
			background_color = False,
			radius_color = False,
			v_expand = True,
			h_expand = True,
			pie = True,
		)
		self.memory_info = CircularProgressBar(
			name = "memory-progress-bar",
			background_color = False,
			radius_color = False,
			v_expand = True,
			h_expand = True,
			pie = True,
		)
		self.system_info = Overlay(
			children = self.memory_info,
			overlays = [
				self.cpu_info,
				Label(
					"",
					style="margin: 0em 0.375em 0em 0em; font-size: 0.75em"
				),
			],
		)
		self.battery_info = BatteryCircular(
			services,
			name = "battery-progress-bar",
			background_color = False,
			radius_color = False,
			v_expand = True,
			h_expand = True,
			pie = True,
		)
		invoke_repeater(
			1000,
			self.updateProgressBar
		)

		self.sys_tray_revealed = False
		self.sys_tray = Box(
			orientation = "v",
			children = [
				Revealer(
					children = SystemTray(
						name = 'system-tray',
						orientation = "v"
					),
				),
				Button(
					name = "revealer-toggle",
					child = Label(label = "")
				)
			]
		)
		for btn in self.sys_tray.get_children():
			if type(btn) == Button and btn.get_name() == "revealer-toggle":
				btn.connect("button-press-event", self.toggleRevealer)

		self.center_box = CenterBox(
			name = "VerticalBar",
			orientation = "v"
		)
		self.populateCB()

		self.add(self.center_box)
		self.show_all()

	def updateProgressBar(self):
		self.cpu_info.percentage = int(psutil.cpu_percent())
		self.memory_info.percentage = int(psutil.virtual_memory().percent)
		self.battery_info.percentage = int(
			psutil.sensors_battery().percent
			if psutil.sensors_battery() is not None
			else 42
		)
		# self.cpu_info.set_tooltip_text(f"CPU usage percentage: {self.cpu_info.percentage}")
		# self.memory_info.set_tooltip_text(f"Memory usage percentage: {self.memory_info.percentage}")
		self.system_info.set_tooltip_text(f"CPU usage percentage: {self.cpu_info.percentage}\nMemory usage percentage: {self.memory_info.percentage}")
		# logger.debug(f"[Bar] CPU percentage: {self.cpu_info.percentage}")
		# logger.debug(f"[Bar] memory percentage: {self.memory_info.percentage}")
		# # logger.info("[Bar] Updated circular progress bar")
		return True

	def populateCB(self):
		self.center_box.add_end(self.sys_tray)
		self.center_box.add_end(self.microphone_widget)
		self.center_box.add_end(self.speaker_widget)
		# self.center_box.add_end(self.cpu_info)
		# self.center_box.add_end(self.memory_info)
		self.center_box.add_end(self.system_info)
		self.center_box.add_end(self.battery_info)
		self.center_box.add_end(self.date_time)
		logger.info("[Bar] Added items to bar (CenterBox)")

	def toggleRevealer(self, button, event):
		if event.button == 1 and event.type == 4:
			self.sys_tray_revealed = not self.sys_tray_revealed
			for rvlr in self.sys_tray.get_children():
				if type(rvlr) == Revealer:
					rvlr.set_reveal_child(self.sys_tray_revealed)
					rvlr.set_child_visible(self.sys_tray_revealed)
			logger.info(f"[Bar] Systray {'revealed' if self.sys_tray_revealed else 'Hidden'}")

	def notify_urgent(self, obj, event):
		logger.info("[Bar] urgent workspaces!!")
		clients = json.loads(
			str(
				self.hyprland_sock.send_command(
					"j/clients",
				).reply.decode()
			)
		)
		clients_map = {client["address"]: client for client in clients}
		urgent_client = clients_map.get(f"0x{event.data[0]}")
		if not urgent_client or not urgent_client.get("workspace"):
			return logger.info(
				f"[Workspaces] we've received an urgent signal, but received data ({event.data[0]}) is uncorrect, skipping..."
			)
		urgent_workspace = int(urgent_client["workspace"]["id"])
		ws_button = Button(
			name = f"urgent-workspace-{urgent_workspace}",
			id = urgent_workspace,
		)
		self.urgent_workspaces.add_children(ws_button)
		# self.buttons_map.get(urgent_workspace - 1).set_urgent() if self.buttons_map.get(
		# 	urgent_workspace - 1
		# ) is not None else None
		return logger.info(
			f"[Workspaces] Workspace {urgent_workspace} setted to urgent"
		)

def main():
	import fabric
	bar = VerticalBar()
	applySCSS(file = join(dirname(__file__), 'assets', 'main.scss'))
	fabric.start()

if __name__ == "__main__":
	main()
