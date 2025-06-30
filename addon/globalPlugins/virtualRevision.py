# Virtual Revision NVDA plugin
# Copyright (C) 2012-2020 Rui Batista and contributors
# Copyright (C) 2021-2023 Rui Fontes, Rui Batista and contributors
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import globalPluginHandler
import globalVars
import api
import textInfos
import ui
import scriptHandler
import addonHandler
addonHandler.initTranslation()

import wx

try:
	from globalCommands import SCRCAT_TEXTREVIEW
except:
	SCRCAT_TEXTREVIEW = None

def get_all_text(obj):
	"""Attempt to extract as much visible text as possible from obj and descendants."""
	lines = []

	# Try grabbing editable or text content directly if available
	try:
		info = obj.makeTextInfo(textInfos.POSITION_ALL)
		text = info.text
		if text and text.strip():
			return text
	except Exception:
		pass

	# Fallback: Recursively walk children, grabbing their .name/.value
	def recurse(o, depth=0):
		try:
			if o.name and o.name.strip():
				lines.append(o.name.strip())
			elif hasattr(o, "value") and o.value and o.value.strip():
				lines.append(o.value.strip())
		except Exception:
			pass
		try:
			for child in o.children:
				recurse(child, depth + 1)
		except Exception:
			pass

	recurse(obj)
	# Remove empty lines, join
	final = "\n".join(l for l in lines if l.strip())
	return final

class ReviewWindow(wx.Dialog):
	def __init__(self, parent, text):
		super().__init__(parent, title=_("Virtual Review"), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.text_ctrl = wx.TextCtrl(
			self,
			value=text,
			style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 | wx.HSCROLL
		)
		sizer.Add(self.text_ctrl, 1, wx.EXPAND | wx.ALL, 10)
		btn_sizer = self.CreateButtonSizer(wx.OK)
		sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
		self.SetSizerAndFit(sizer)
		self.SetSize((800, 600))
		self.CentreOnScreen()

	def ShowAndFocus(self):
		self.Show()
		self.text_ctrl.SetFocus()

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	scriptCategory = SCRCAT_TEXTREVIEW

	@scriptHandler.script(
		# Translators: Message presented in input help mode.
		description=_("Opens a window containing the text of the currently focused window for easy review."),
		gesture="kb:nvda+control+w"
	)
	def script_virtualWindowReview(self, gesture):
		# Try to get as much text as possible from the focused window
		obj = api.getFocusObject()
		text = get_all_text(obj)

		if not text or text.strip() == "":
			ui.message(_("No text found to review."))
			return

		def showDialog():
			win = ReviewWindow(None, text)
			win.ShowAndFocus()

		wx.CallAfter(showDialog)
