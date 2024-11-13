import re
import subprocess

from loguru import logger

from fabric.widgets import (
	Box,
	CenterBox,
	Entry,
	Label,
	Image,
	Button,
	ScrolledWindow,
)

import gi
from gi.repository import Gtk, GdkPixbuf
gi.require_version("Gtk", '3.0')
gi.require_version("GdkPixbuf", '2.0')

# #!/usr/bin/env python3
#
# import os
# import re
# import subprocess
# import sys
#
# def main():
#     tmp_dir = "/tmp/cliphist"
#     if os.path.exists(tmp_dir):
#         subprocess.run(['rm', '-rf', tmp_dir])
#     os.makedirs(tmp_dir, exist_ok=True)
#
#     if len(sys.argv) > 1:
#         clip_id = sys.argv[1]
#         result = subprocess.run(
#             ['cliphist', 'decode'],
#             input=clip_id.encode(),
#             stdout=subprocess.PIPE
#         )
#         subprocess.run(['wl-copy'], input=result.stdout)
#         sys.exit()
#
#     # Function to process each line
#     def process_line(line):
#         if re.match(r'^[0-9]+\s<meta http-equiv=', line):
#             return None
#         
#         match = re.match(r'^([0-9]+)\s(\[\[\s)?binary.*(jpg|jpeg|png|bmp)', line)
#         if match:
#             clip_id, _, ext = match.groups()
#             file_path = os.path.join(tmp_dir, f"{clip_id}.{ext}")
#             with open(file_path, 'wb') as f:
#                 subprocess.run(
#                     ['cliphist', 'decode', clip_id],
#                     stdout=f
#                 )
#             return f"{line}\0icon\x1f{file_path}"
#         
#         return line
#
#     # Run `cliphist list` and process its output
#     result = subprocess.run(['cliphist', 'list'], stdout=subprocess.PIPE)
#     lines = result.stdout.decode().splitlines()
#
#     for line in lines:
#         processed_line = process_line(line)
#         if processed_line is not None:
#             print(processed_line)
#
# if __name__ == '__main__':
#     main()
####### var me to kuchh bhi store kr sakte hai na. Icon represent krne ke liye #######

class ItemBox(Button):
	def __init__(
			self,
			id: int,
			itemId: str,
			itemContent: str,
			searchBar = None,
			size: tuple[int] | None = None,
			image: GdkPixbuf.Pixbuf = None,
			**kwargs
		):
		super().__init__(
			name = f"ItemBox-{id}",
			v_align = "fill",
			h_align = "fill",
			**kwargs
		)
		self.searchBar = searchBar
		self.center_box = CenterBox(
			v_align = "fill",
			h_align = "fill",
			v_expand = True,
			h_expand = True,
		)
		self.itemId = itemId
		self.itemContent = itemContent
		self.image = image if image is not None else None

		self.pasteId = Label(self.itemId)
		self.content = Label(
			self.itemContent
		) if self.image is None else Image(
			pixbuf = self.image.scale_simple(size[0], size[1], GdkPixbuf.InterpType.BILINEAR) if size is not None else self.image,
		)
		# logger.info(f"{ self.itemId = }{ size = }") if self.image is not None else None

		self.connect('key-press-event', self.interaction)
		self.connect('key-release-event', self.interaction)

		self.center_box.add_start(self.pasteId)
		self.center_box.add_end(self.content)
		self.add(self.center_box)

	def copy(self,):
		subprocess.run([
			"cliphist",
			"decode",
			self.itemId
		])

	def interaction(self, button, event):
		scancode = event.get_scancode()
		# logger.debug(f"{scancode = }")
		# Keycode for escape button
		if scancode == 9 and event.type == 9:
			logger.info("shifting focus?")
			# self.grab_remove()
			# self.searchBar.grab_remove()
			out = self.searchBar.grab_focus() if self.searchBar is not None else None
			logger.info(f"focus result = {out}")

		if scancode == 36:
			self.copy()
		# if event.type == 8:

class ClipboardWidget(Box):
	def __init__(
			self,
			additionalClassName: str = None,
			quit: callable = None,
			**kwargs
		):
		super().__init__(
			name = f"ClipboardWidgetBox{ '-' + additionalClassName if additionalClassName else None }",
			orientation="v",
			**kwargs
		)
		self.quit = quit

		# self.modifiers = {
		# 	"shift": False,
		# 	"shiftL": False,
		# 	"shiftR": False,
		#
		# 	"ctrl": False,
		# 	"ctrlL": False,
		# 	"ctrlR": False,
		#
		# 	"super": False,
		# 	"superL": False,
		# 	"superR": False,
		#
		# 	"alt": False,
		# 	"altL": False,
		# 	"altR": False,
		# }
		self.close = True
		self.ItemBoxList = []
		self._size = (int(1920/2), int(1080/1.5))

		self.searchBox = Entry(
			can_focus = True,
			placeholder_text = "Enter search term"
		)
		self.searchBox.connect("key-press-event", self.search)
		self.searchBox.connect("key-release-event", self.search)
		self.add_children(self.searchBox)

		self.scrolled_window = ScrolledWindow(
			name = "ScrollableWindow",
			min_content_width = self._size[0],
			min_content_height = self._size[1],
		)

		self.load()
		self.scrolled_window.add_children(
			# self.ItemBoxList
			Box(
				orientation = "v",
				children = self.ItemBoxList,
			)
		)
		self.scrolled_window.set_can_focus(False)
		self.add_children(self.scrolled_window)
		# self.set_visible(True)
	
	def load(self,):
		# tmp_dir = "/tmp/cliphist"
		# if os.path.exists(tmp_dir):
		# 	exec_shell_command(f"rm -rf {tmp_dir}")
		# os.makedirs(tmp_dir, exist_ok=True)

		self.cliphistory = [ items.split("\t") for items in subprocess.run(["cliphist", "list"], stdout=subprocess.PIPE).stdout.decode(errors = "ignore").split("\n") ]
		self.cliphistory.remove([''])
		i = 0
		for item in self.cliphistory:
			if re.match(r'^<meta http-equiv=', item[1]):
				continue
			match = re.match(r'^(\[\[\s)?binary.*(jpg|jpeg|png|bmp)', item[1])
			if match:
				_, ext = match.groups()
				# file = os.path.join(tmp_dir, f"{item[0]}.{ext}")
				# with open(file, 'wb') as f:
				loader = GdkPixbuf.PixbufLoader()
				loader.write(subprocess.run(
					[
						'cliphist',
						'decode',
						item[0]
					],
					stdout=subprocess.PIPE
				).stdout)
				loader.close()
				image = loader.get_pixbuf()
				imageH = image.get_height()
				imageW = image.get_width()
				size0 = self._size[0] - 60 #
				size1 = self._size[1] #
				# TODO: shorten this shit
				if imageW > size0 and imageH > size1:
					# logger.info(f"first cond {imageW = } {imageH = }")
					aspect_ratio = size0 / imageW
					size = int(imageW * aspect_ratio), int(imageH * aspect_ratio)
					if (size[0] > size0):
						aspect_ratio = size1 / imageW
						size = int(size[0] * aspect_ratio), int(size[1] * aspect_ratio)
						# logger.info(f"{size = }")

				elif imageW > size0:
					# logger.info(f"second cond {imageW = } {imageH = }")
					aspect_ratio = size0 / imageW
					size = int(imageW * aspect_ratio), int(imageH * aspect_ratio)
					# logger.info(f"{size = }")

				elif imageH > size1:
					# logger.info(f"third cond {imageW = } {imageH = }")
					aspect_ratio = size1 / imageH
					size = int(imageW * aspect_ratio), int(imageH * aspect_ratio)
					# logger.info(f"{size = }")

				else:
					size = imageW, imageH
					# logger.info(f"{size = }")

			else:
				image = None
				size = None
			self.ItemBoxList.append(ItemBox(id = i, itemId = item[0], itemContent = item[1], image = image, size = size, searchBar = self.searchBox))
			i+=1
	
	def reload(self,):
		for i in self.ItemBoxList:
			i.visible = False

		# if self.

	def execute(self,):
		pass

	def search(self, entry, event):
		scancode = event.get_scancode()
		# logger.debug(f"{scancode = }")
		# Keycode for escape button
		if scancode == 9 and event.type == 9:
			if self.close:
				logger.info("Quitting!")
				self.quit()
			else:
				logger.info("Closing popup only")
				self.close = True
		# if entry.get_text() == "":
		# 	logger.info("Why empty?")
		# logger.debug(f"{int(event.type) = }")
		if event.type == 8:
			if scancode == 135:
				self.close = False
				logger.info("Menu button pressed")
			# Keycode for Return
			elif scancode == 36:
				self.execute()
			else:
				pass
		# 	if scancode == 50:
		# 		self.modifiers["shiftL"] = True
		# 		self.modifiers["shift"] = True
		# 		logger.debug(f"{self.modifiers['shift'] = }")
		# 		logger.debug(f"{self.modifiers['shiftL'] = }")
		# 	elif scancode == 37:
		# 		self.modifiers["ctrlL"] = True
		# 		self.modifiers["ctrl"] = True
		# 		logger.debug(f"{self.modifiers['ctrl'] = }")
		# 		logger.debug(f"{self.modifiers['ctrlL'] = }")
		# 	elif scancode == 133:
		# 		self.modifiers["superL"] = True
		# 		self.modifiers["super"] = True
		# 		logger.debug(f"{self.modifiers['super'] = }")
		# 		logger.debug(f"{self.modifiers['superL'] = }")
		# 	elif scancode == 64:
		# 		self.modifiers["altL"] = True
		# 		self.modifiers["alt"] = True
		# 		logger.debug(f"{self.modifiers['alt'] = }")
		# 		logger.debug(f"{self.modifiers['altL'] = }")
		#
		# 	elif scancode == 62:
		# 		self.modifiers["shiftR"] = True
		# 		self.modifiers["shift"] = True
		# 		logger.debug(f"{self.modifiers['shift'] = }")
		# 		logger.debug(f"{self.modifiers['shiftR'] = }")
		# 	elif scancode == 105:
		# 		self.modifiers["ctrlR"] = True
		# 		self.modifiers["ctrl"] = True
		# 		logger.debug(f"{self.modifiers['ctrl'] = }")
		# 		logger.debug(f"{self.modifiers['ctrlR'] = }")
		# 	# elif scancode == 0: # Don't know the code
		# 	# 	self.modifiers["superR"] = True
		# 	# 	self.modifiers["super"] = True
		# 	# 	logger.debug(f"{self.modifiers['super'] = }")
		# 	# 	logger.debug(f"{self.modifiers['superR'] = }")
		# 	elif scancode == 108:
		# 		self.modifiers["altR"] = True
		# 		self.modifiers["alt"] = True
		# 		logger.debug(f"{self.modifiers['alt'] = }")
		# 		logger.debug(f"{self.modifiers['altR'] = }")
		# 	else:
		# 		if True not in self.modifiers.values():
		# 			# Keycode for Menu button
		# 			if scancode == 135:
		# 				self.close = False
		# 			# Keycode for Return
		# 			elif scancode == 36:
		# 				self.execute()
		# 			else:
		# 				# Up
		# 				if scancode == 111:
		# 					self.scrolled_window.get_child().child_focus(Gtk.DirectionType.UP)
		# 					logger.info(f"{self.searchBox.grab_focus() = }")
		# 				# Down
		# 				elif scancode == 116:
		# 					self.scrolled_window.get_child().child_focus(Gtk.DirectionType.DOWN)
		# 					logger.info(f"{self.searchBox.grab_focus() = }")
		# 				logger.debug(f"{scancode = } without modifier is pressed")
		# 		else:
		# 			logger.debug(f"{scancode = } with modifiers is pressed")
		# elif event.type == 9:
		# 	if scancode == 50:
		# 		self.modifiers["shiftL"] = False
		# 		self.modifiers["shift"] = self.modifiers["shiftR"]
		# 		logger.debug(f"{self.modifiers['shift'] = }")
		# 		logger.debug(f"{self.modifiers['shiftL'] = }")
		# 	elif scancode == 37:
		# 		self.modifiers["ctrlL"] = False
		# 		self.modifiers["ctrl"] = self.modifiers["ctrlR"]
		# 		logger.debug(f"{self.modifiers['ctrl'] = }")
		# 		logger.debug(f"{self.modifiers['ctrlL'] = }")
		# 	elif scancode == 133:
		# 		self.modifiers["superL"] = False
		# 		self.modifiers["super"] = self.modifiers["superR"]
		# 		logger.debug(f"{self.modifiers['super'] = }")
		# 		logger.debug(f"{self.modifiers['superL'] = }")
		# 	elif scancode == 64:
		# 		self.modifiers["altL"] = False
		# 		self.modifiers["alt"] = self.modifiers["altR"]
		# 		logger.debug(f"{self.modifiers['alt'] = }")
		# 		logger.debug(f"{self.modifiers['altL'] = }")
		#
		# 	elif scancode == 62:
		# 		self.modifiers["shiftR"] = False
		# 		self.modifiers["shift"] = self.modifiers["shiftL"]
		# 		logger.debug(f"{self.modifiers['shift'] = }")
		# 		logger.debug(f"{self.modifiers['shiftR'] = }")
		# 	elif scancode == 105:
		# 		self.modifiers["ctrlR"] = False
		# 		self.modifiers["ctrl"] = self.modifiers["ctrlL"]
		# 		logger.debug(f"{self.modifiers['ctrl'] = }")
		# 		logger.debug(f"{self.modifiers['ctrlR'] = }")
		# 	# elif scancode == 0: # Don't know the code
		# 	# 	self.modifiers["superR"] = False
		# 	# 	self.modifiers["super"] = self.modifiers["superL"]
		# 	# 	logger.debug(f"{self.modifiers['super'] = }")
		# 	# 	logger.debug(f"{self.modifiers['superR'] = }")
		# 	elif scancode == 108:
		# 		self.modifiers["altR"] = False
		# 		self.modifiers["alt"] = self.modifiers["altL"]
		# 		logger.debug(f"{self.modifiers['alt'] = }")
		# 		logger.debug(f"{self.modifiers['altR'] = }")
		# else:
		# 	logger.info(f"got unmonitored event {event.type = }")
		# logger.info(f"{event.get_keycode() = }")
		# logger.info(f"{event.get_device() = }")
		# logger.info(f"{event.type = }")
		# logger.info(f"{event.get_scancode() = }")
		# # X11 server
		# sdl x11
		# sdl dga
		# 09	53	# Esc
		# 67	122	# F1
		# 68	120	# F2
		# 69	99	# F3
		# 70	118	# F4
		# 71	96	# F5
		# 72	97	# F6
		# 73	98	# F7
		# 74	100	# F8
		# 75	101	# F9
		# 76	109	# F10
		# 95	103	# F11
		# 96	127	# F12
		# 111	105	# PrintScrn
		# 78	107	# Scroll Lock
		# 110	113	# Pause
		# 49	50	# `
		# 10	18	# 1
		# 11	19	# 2
		# 12	20	# 3
		# 13	21	# 4
		# 14	23	# 5
		# 15	22	# 6
		# 16	26	# 7
		# 17	28	# 8
		# 18	25	# 9
		# 19	29	# 0
		# 20	27	# -
		# 21	24	# =
		# 22	51	# Backspace
		# 106	114	# Insert
		# 97	115	# Home
		# 99	116	# Page Up
		# 77	71	# Num Lock
		# 112	75	# KP /
		# 63	67	# KP *
		# 82	78	# KP -
		# 23	48	# Tab
		# 24	12	# Q
		# 25	13	# W
		# 26	14	# E
		# 27	15	# R
		# 28	17	# T
		# 29	16	# Y
		# 30	32	# U
		# 31	34	# I
		# 32	31	# O
		# 33	35	# P
		# 34	33	# [
		# 35	30	# ]
		# 36	36	# Return
		# 107	117	# Delete
		# 103	119	# End
		# 105	121	# Page Down
		# 79	89	# KP 7
		# 80	91	# KP 8
		# 81	92	# KP 9
		# 86	69	# KP +
		# 66	57	# Caps Lock
		# 38	0	# A
		# 39	1	# S
		# 40	2	# D
		# 41	3	# F
		# 42	5	# G
		# 43	4	# H
		# 44	38	# J
		# 45	40	# K
		# 46	37	# L
		# 47	41	# ;
		# 48	39	# '
		# 83	86	# KP 4
		# 84	87	# KP 5
		# 85	88	# KP 6
		# 50	56	# Shift Left
		# 94	50	# International
		# 52	6	# Z
		# 53	7	# X
		# 54	8	# C
		# 55	9	# V
		# 56	11	# B
		# 57	45	# N
		# 58	46	# M
		# 59	43	# ,
		# 60	47	# .
		# 61	44	# /
		# 62	56	# Shift Right
		# 51	42	# \
		# 98	62	# Cursor Up
		# 87	83	# KP 1
		# 88	84	# KP 2
		# 89	85	# KP 3
		# 108	76	# KP Enter
		# 37	54	# Ctrl Left
		# 115	58	# Logo Left (-> Option)
		# 64	55	# Alt Left (-> Command)
		# 65	49	# Space
		# 113	55	# Alt Right (-> Command)
		# 116	58	# Logo Right (-> Option)
		# 117	50	# Menu (-> International)
		# 109	54	# Ctrl Right
		# 100	59	# Cursor Left
		# 104	61	# Cursor Down
		# 102	60	# Cursor Right
		# 90	82	# KP 0
		# 91	65	# KP .
