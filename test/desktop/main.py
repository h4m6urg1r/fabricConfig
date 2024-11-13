import fabric
from os.path import join, dirname
from desktop.bar.bar import VerticalBar
from desktop.WorkspaceStrip.main import Strip
from desktop.utils.helpers import applySCSS
from desktop.services import Battery
from fabric.hyprland import Hyprland
from fabric.audio import Audio

def main():
	services = {
		# "Audio": Audio(max_volume = 150),
		"Speaker": Audio(max_volume = 150),
		"Microphone": Audio(max_volume = 50),
		"Hyprland": Hyprland(),
		"Battery": Battery()
	}
	strip = Strip()
	bar = VerticalBar(
		services,
		# open_inspector = True,
	)
	applySCSS(file = join(dirname(__file__), 'assets', 'main.scss'))
	fabric.start()
