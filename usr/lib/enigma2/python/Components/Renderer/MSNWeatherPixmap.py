# Copyright (C) 2023 jbleyel
#
# MSNWeather is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# dogtag is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MSNWeather.  If not, see <http://www.gnu.org/licenses/>.

from Components.Renderer.Renderer import Renderer
from enigma import ePixmap


class MSNWeatherPixmap(Renderer):
	def __init__(self):
		Renderer.__init__(self)
		self.iconFileName = ""

	GUI_WIDGET = ePixmap

	def postWidgetCreate(self, instance):
		instance.setScale(1)
		#instance.setFlag(2)  # BT_KEEP_ASPECT_RATIO
		#instance.setFlag(0x1)  # BT_HALIGN_CENTER
		#instance.setFlag(0x2)  # BT_VALIGN_CENTER

		self.changed((self.CHANGED_DEFAULT,))

	def changed(self, what):
		if self.instance:
			pngname = ""
			if what[0] != self.CHANGED_CLEAR:
				pngname = self.source.iconfilename
			if pngname == "":
				self.instance.hide()
			else:
				self.instance.show()
				if self.iconFileName != pngname:
					self.instance.setPixmapFromFile(pngname)
					self.iconFileName = pngname
