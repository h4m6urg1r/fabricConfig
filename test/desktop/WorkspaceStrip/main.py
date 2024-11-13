# import types
import json
from loguru import logger
from fabric.hyprland.service import Hyprland, HyprlandEvent
from fabric.widgets import (
	EventBox,
	Box,
	Button,
	WaylandWindow as Window,
	# TODO: override workspaces changing function https://stackoverflow.com/a/42154067
	# HyprlandWorkspaces as Workspaces,
	# HyprlandWorkspaceButton as WorkspaceButton,
)
from fabric.utils.string_formatter import FormattedString
from gi.repository import Gdk, GLib
from fabric.utils import bulk_connect

connection = Hyprland()

# def button_click_handler(self, button: WorkspaceButton, event):
# 	if event.button == 1 and event.type == 4:
# 		connection.send_command(
# 			f"/dispatch workspace {button.id + 1}",
# 		)
# 		logger.info(":)")
# 		logger.info(f"[Workspaces] Moved to workspace {button.id + 1}")
# 	return

# def initialize_buttons(self, workspaces_buttons: list[WorkspaceButton]):
# 	for button in workspaces_buttons:
# 		if not button.can_appear and button.visible:
# 			button.show()
# 		else:
# 			button.hide()
# 		button.bake_label()
# 		button.connect(
# 			"button-press-event",
# 			# lambda _, __, obj=button: self.button_click_handler(obj),
# 			self.button_click_handler
# 		)
# 		self.add(button)
# 	return workspaces_buttons





class WorkspacesEventBox(EventBox):
	"""
	a subclass of Gtk.EventBox that is designed to hold buttons for workspaces.

	provides methods for adding, removing, and managing child widgets within the box.
	"""

	def __init__(self, **kwargs):
		self.children_box = Box(**kwargs)
		super().__init__(children=self.children_box, events="scroll")

	def show(self):
		return super().show(), self.children_box.show()

	def show_all(self):
		return super().show_all(), self.children_box.show_all()

	def get_children(self):
		return self.children_box.get_children()

	def remove(self, widget=None):
		return self.children_box.remove(widget)

	def add(self, widget=None):
		return self.children_box.add(widget)

	def set_name(self, name=None):
		return self.children_box.set_name(name)

	def get_name(self):
		return self.children_box.get_name()


class WorkspaceButton(Button):
	def __init__(
		self,
		label: FormattedString | str | None = None,
		visible: bool = True,
		can_appear: bool = True,
		id: int | None = None,
		name: str | None = None,
		**kwargs,
	):
		"""
		A Button that will get rendered on a workspaces widget, this contians the button properties

		:param label: the label for the normal state of this button. if not passed it will fallback to the button `id + 1`, we expose the button object to you via the `button` variable, defaults to None
		:type label: FormattedString, optional
		:param active_label: the label for this button when it gets activated. if not passed it will fallback to the normal `label`, we expose the button object to you via the `button` variable, defaults to None
		:type active_label: FormattedString, optional
		:param visible: makes you able to make this button invisible and only show up if the open workspace is the same as this button `id`, defaults to True
		:type visible: bool, optional
		:param can_appear: optional, set to false to make this workspace unable to appear whatever happens, useful if you want to make some specific workspace invisible to the widget, defaults to True
		:type can_appear: bool, optional
		:param id: this will make you able to select a specific workspace, optional since it can get assigend automatically via the index of this button in the buttons list, NOTE: the value the id should starts with 0 as a first index value., defaults to None
		:type id: int, optional
		"""
		super().__init__(
			**kwargs,
		)
		self.label = FormattedString(label) if isinstance(label, str) else label
		self.visible = visible
		self.can_appear = can_appear
		self.id = id
		self.name = name
		self._active: bool = False
		self._urgent: bool = False
		self._empty: bool = False

	def set_active(self):
		self._active = True
		if self.can_appear:
			self.show()
		self.add_class("active")
		self.remove_class("urgent")
		return

	def unset_active(self):
		self.active = False
		if not self.visible:
			self.hide()
		self.bake_label()
		self.remove_class("active")
		return

	def add_class(self, class_name: str):
		GLib.idle_add(self.get_style_context().add_class, class_name)
		return

	def remove_class(self, class_name: str):
		GLib.idle_add(self.get_style_context().remove_class, class_name)
		return

	def bake_label(self):
		return self.set_label(self.label.get_formatted(button=self))

	def set_urgent(self):
		self._urgent = True
		self.add_class("urgent")
		return

	def unset_urgent(self):
		self._urgent = False
		self.remove_class("urgent")
		return

	def set_empty(self):
		self._empty = True
		self.add_class("empty")
		return

	def unset_empty(self):
		self._empty = False
		self.remove_class("empty")
		return


class Workspaces(WorkspacesEventBox):
	"""
	a widget provides you the workspaces controls, it uses the hyprland IPC.
	"""

	def __init__(
		self,
		buttons_list: list[WorkspaceButton] = None,
		default_button: WorkspaceButton = None,
		**kwargs,
	):
		"""
		:param button_list: a list of `WorkspaceButton` objects, defaults to None and if none it will use a built-in list.
		:type button_list: list[WorkspaceButton], optional
		"""
		super().__init__(**kwargs)
		# TODO: use default_button to map a new button if it was not passed in the butttons list.
		self.buttons_list = (
			self.setup_buttons(
				[
					WorkspaceButton(),
					WorkspaceButton(),
					WorkspaceButton(),
					WorkspaceButton(),
					WorkspaceButton(),
					WorkspaceButton(),
					WorkspaceButton(),
				]
			)
			if not buttons_list
			else self.setup_buttons(buttons_list)
		)
		self._last_workspace_id: int = None
		self.buttons_map = {obj.id: obj for obj in self.buttons_list}
		bulk_connect(
			connection,
			{
				"ready": self.on_ready,
				"workspace": self.on_workspace,
				"createworkspace": self.on_createworkspace,
				"destroyworkspace": self.on_destroyworkspace,
				"urgent": self.on_urgent,
			},
		)
		self.connect("scroll-event", self.scroll_handler)

	def on_ready(self, obj):
		logger.info("[Workspaces] Connected to the hyprland socket")
		return self.initialize_workspaces()

	def on_workspace(self, obj, event: HyprlandEvent):
		GLib.idle_add(self.set_active_workspace, (int(event.data[0]) - 1))
		return logger.info(f"[Workspaces] Active workspace changed to {event.data[0]}")

	def on_createworkspace(self, obj, event: HyprlandEvent):
		button_obj = self.buttons_map.get((int(event.data[0]) - 1))
		if not button_obj:
			return logger.info(
				f"[Workspaces] we've received a createworkspace signal, but WorkspaceButton with id {event.data[0]} does not exist, skipping..."
			)
		button_obj.unset_empty()
		return logger.info(f"[Workspaces] Workspace {event.data[0]} created")

	def on_destroyworkspace(self, obj, event):
		button_obj = self.buttons_map.get((int(event.data[0]) - 1))
		if not button_obj:
			return logger.info(
				f"[Workspaces] we've received a destroyworkspace signal, but WorkspaceButton with id {event.data[0]} does not exist, skipping..."
			)
		button_obj.set_empty()
		return logger.info(f"[Workspaces] Workspace {event.data[0]} destroyed")

	def on_urgent(self, obj, event: HyprlandEvent):
		clients = json.loads(
			str(
				connection.send_command(
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
		self.buttons_map.get(urgent_workspace - 1).set_urgent() if self.buttons_map.get(
			urgent_workspace - 1
		) is not None else None
		return logger.info(
			f"[Workspaces] Workspace {urgent_workspace} setted to urgent"
		)

	def initialize_workspaces(self):
		open_ws = json.loads(
			str(
				connection.send_command(
					"j/workspaces",
				).reply.decode()
			)
		)
		current_ws: int = json.loads(
			str(
				connection.send_command(
					"j/activeworkspace",
				).reply.decode()
			)
		)["id"]
		open_workspaces = tuple(
			workspace["id"] - 1 for workspace in open_ws
		)  # a generator
		for ws_button in self.buttons_list:
			if ws_button.id in open_workspaces:
				pass
			else:
				ws_button.set_empty()
			self.unset_active_workspace(ws_button.id)
		# The current workspace is based on the hyprland specs (1 indexed.)
		self.set_active_workspace(current_ws - 1)

	def unset_active_workspace(self, workspace_id):
		button_obj = self.buttons_map.get(workspace_id)
		if button_obj is not None and button_obj.can_appear:
			button_obj.unset_active()
		return

	def set_active_workspace(self, workspace_id):
		if self._last_workspace_id is not None:
			# TODO: good place for log
			self.buttons_map.get(
				self._last_workspace_id
			).unset_active() if self.buttons_map.get(
				self._last_workspace_id
			) is not None else None
		button_obj = self.buttons_map.get(workspace_id)
		if button_obj and button_obj.can_appear:
			self._last_workspace_id = button_obj.id
			button_obj.set_active()
		return

	def setup_buttons(
		self, button_list: list[WorkspaceButton]
	) -> list[WorkspaceButton]:
		workspaces_buttons = []
		for index, button in enumerate(button_list):
			button.id = index if button.id is None else button.id
			button.can_appear = (
				button.can_appear if button.can_appear is not None else True
			)
			button.visible = button.visible if button.visible is not None else True
			button.label = (
				button.label
				if button.label is not None
				else FormattedString(f"{button.id + 1}")
				if button.id
				else FormattedString(f"{index + 1}")
			)
			button._active = False
			button._empty = False
			button._urgent = False
			# button.bake_label()
			workspaces_buttons.append(button)
		return self.initialize_buttons(workspaces_buttons)

	def initialize_buttons(self, workspaces_buttons: list[WorkspaceButton]):
		for button in workspaces_buttons:
			if not button.can_appear and button.visible:
				button.show()
			else:
				button.hide()
			# button.bake_label()
			button.connect(
				"button-press-event",
				self.button_click_handler
			)
			self.add(button)
		return workspaces_buttons

	def button_click_handler(self, button: WorkspaceButton, event):
		if event.button == 1 and event.type == 4:
			connection.send_command(
				f"batch/dispatch workspace {button.id + 1}",
			)
			logger.info(f"[Workspaces] Moved to workspace {button.id + 1}")
		return

	def scroll_handler(self, widget, event: Gdk.EventScroll):
		match event.direction:
			case Gdk.ScrollDirection.UP:
				connection.send_command(
					"batch/dispatch workspace e+1",
				)
				logger.info("[Workspaces] Moved to the next workspace")
			case Gdk.ScrollDirection.DOWN:
				connection.send_command(
					"batch/dispatch workspace e-1",
				)
				logger.info("[Workspaces] Moved to the previous workspace")
			case _:
				logger.info(
					f"[Workspaces] Unknown scroll direction ({event.direction})"
				)
		return






class Strip(Window):
	def __init__(self, length = 5, side="top"):
		super().__init__(
			name = f"workspacesStrip-{side}",
			layer = "top",
			anchor = f"left {side} right",
			exclusive = True,
			visible = False,
			all_visible = False,
			# open_inspector = True,
		)

		ws = Workspaces(
			buttons_list = [
				WorkspaceButton(v_expand = False, h_expand = True) for num in range(length)
			],
		)
		# ws.button_click_handler = types.MethodType(button_click_handler, ws)
		# ws.initialize_buttons = types.MethodType(initialize_buttons, ws)

		self.add(ws)

		self.show_all()
