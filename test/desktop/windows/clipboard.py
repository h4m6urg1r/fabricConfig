from os.path import dirname, join

from desktop.widgets.clipboard import ClipboardWidget
from fabric.widgets import (
	WaylandWindow as Window,
	CenterBox,
)

from desktop.utils.helpers import applySCSS

class Clipboard(Window):
	def __init__(
			self,
			**kwargs
		):
		super().__init__(
			name = "Clipboard",
			layer = "overlay",
			anchor = "top bottom left right",
			exclusive = False,
			keyboard_mode = "on-demand",
			visible = False,
			all_visible = False,
			open_inspector=True,
			**kwargs
		)

		self.center_box = CenterBox(
			name = "ClipboardMainBoxWrapper",
			orientation = "v",
			v_align="center",
			h_align="center",
		)

		self.CBW = ClipboardWidget(
			quit = self.destroy
		)
		self.center_box.add_center(self.CBW)
		self.set_keyboard_mode("exclusive")

		self.add(self.center_box)
		self.show_all()

def main():
	import fabric
	clipboard = Clipboard()
	applySCSS(file = join(dirname(__file__), 'assets', 'main.scss'))
	fabric.start()
