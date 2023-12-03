# -*- coding: utf-8 -*-
# Copyright (C) 2023 jbleyel, Mr.Servo, Stein17
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
#
# Some parts are taken from MetrixHD skin and MSNWeather Plugin.

from os import remove, listdir
from os.path import isfile, exists, getmtime, join
from pickle import dump, load
from time import time
from twisted.internet.reactor import callInThread
from xml.etree.ElementTree import tostring, parse
from Components.ConfigList import ConfigListScreen
from Components.MenuList import MenuList
from Components.Button import Button
from Components.config import config
from enigma import eTimer
from Components.ActionMap import ActionMap, HelpableActionMap
from Components.config import  ConfigSubsection, ConfigYesNo, ConfigSelection, ConfigSelectionNumber, ConfigText, getConfigListEntry, configfile, ConfigEnableDisable, ConfigYesNo, ConfigInteger
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from Plugins.Plugin import PluginDescriptor
from Screens.ChoiceBox import ChoiceBox
from Screens.Setup import Setup
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Tools.Weatherinfo import Weatherinfo
from Screens.VirtualKeyBoard import VirtualKeyBoard
import skin
from . import _
import sys
from keymapparser import readKeymap, removeKeymap
from Components.config import getConfigListEntry
from Components.Button import Button

#from Components.List import List


if sys.version_info[0] >= 3:

    from Tools.Directories import SCOPE_CONFIG, SCOPE_PLUGINS, SCOPE_SKINS, resolveFilename

else:

    from Tools.Directories import resolveFilename, SCOPE_SKIN, SCOPE_CONFIG, SCOPE_PLUGINS

################################## Logfile ##################################

from datetime import datetime
from shutil import copyfile
from os import remove
from os.path import isfile
########################### Delete Log file #################################

myfile="/tmp/MSNWeatherplugin.log"

## If file exists, delete it ##
if isfile(myfile):
    remove(myfile)

############################ Create Log file ################################

logstatus = "on"

#############################################################################

def write_log(msg):
    if logstatus == ('on'):
        with open(myfile, "a") as log:

            log.write(datetime.now().strftime("%Y/%d/%m, %H:%M:%S.%f") + ": " + msg + "\n")

            return
    return

############################# test ON/OFF Logfile ############################


def logout(data):
    if logstatus == ('on'):
        write_log(data)
        return
    return


############################# write file command #############################
logout(data="start")


config.plugins.MSNWeather = ConfigSubsection()
config.plugins.MSNWeather.enabled = ConfigYesNo(default=True)

ICONSETS = [("", _("Default"))]

if sys.version_info[0] >= 3:
    logout(data="Python 3")
    ICONSETROOT = join(resolveFilename(SCOPE_SKINS), "WeatherIconSets")
else:
    logout(data="Python 2")
    ICONSETROOT = join(resolveFilename(SCOPE_SKIN), "WeatherIconSets")

if exists(ICONSETROOT):
    for iconset in listdir(ICONSETROOT):
        if isfile(join(ICONSETROOT, iconset, "0.png")):
            ICONSETS.append((iconset, iconset))

config.plugins.MSNWeather.iconset = ConfigSelection(default="", choices=ICONSETS)
config.plugins.MSNWeather.nighticons = ConfigYesNo(default=True)
config.plugins.MSNWeather.cachedata = ConfigSelection(default="0", choices=[("0", _("Disabled"))] + [(str(x), _("%d Minutes") % x) for x in (30, 60, 120)])
config.plugins.MSNWeather.refreshInterval = ConfigSelectionNumber(0, 1440, 30, default=120, wraparound=True)
config.plugins.MSNWeather.apikey = ConfigText(default="", fixed_size=False)
GEODATA = ("Hamburg, DE", "10.000654,53.550341")
config.plugins.MSNWeather.weathercity = ConfigText(default=GEODATA[0], visible_width=250, fixed_size=False)
config.plugins.MSNWeather.owm_geocode = ConfigText(default=GEODATA[1])
config.plugins.MSNWeather.tempUnit = ConfigSelection(default="Celsius", choices=[("Celsius", _("Celsius")), ("Fahrenheit", _("Fahrenheit"))])
config.plugins.MSNWeather.weatherservice = ConfigSelection(default="MSN", choices=[("MSN", _("MSN weather")), ("OpenMeteo", _("Open-Meteo Wetter")), ("openweather", _("OpenWeatherMap"))])

#config.plugins.MSNWeather.weatherservice = ConfigSelection(default="MSN", choices=[("MSN")])

config.plugins.MSNWeather.debug = ConfigYesNo(default=False)

USELOGFILE = config.plugins.MSNWeather.debug

if USELOGFILE.value:
    logout(data="LOGFILE_On")
    logstatus = "on"
    logstatusin = "on"

else:
    logout(data="LOGFILE_Off")
    logstatus = "on"
    logstatusin = "off"

#__all__ = ['logstatusin']

MODULE_NAME = "MSNWeather"
CACHEFILE = resolveFilename(SCOPE_CONFIG, "MSNWeather.dat")
PLUGINPATH = join(resolveFilename(SCOPE_PLUGINS), 'Extensions/MSNWeather')

class WeatherSettingsViewNew(ConfigListScreen, Screen):
    logout(data="WeatherSettingsViewNew")
    skin = """
        <screen name="WeatherSettingsViewNew" title="Weather Plugin Setup" position="center,center" size="1920,1080" backgroundColor="#00000000" transparent="0"  >
            <eLabel position="0,0" size="1920,1080" backgroundColor="#00000000" transparent="0" zPosition="0" />
            <widget name="config" position="100,20" size="1000,450" font="Regular;30" itemHeight="45"  backgroundColor="#00000000" foregroundColor="#00ffffff" transparent="0" zPosition="3" scrollbarMode="showOnDemand" />
            <widget name="status" font="Regular; 25"  position="100,470" size="1000,40" foregroundColor ="#00fff000" transparent="1"  zPosition="3" halign="center" valign="center" />
            <eLabel backgroundColor="#00000000" font="Regular; 28" position="00,475" size="1280,40" text="Enter your City Name - Virtual KeyBoard = Press OK" transparent="1" halign="center" valign="center" zPosition="2" foregroundColor="#0abab5" />
            <eLabel backgroundColor="#00000000" font="Regular; 28" position="00,505" size="1280,40" text="Use Red Button after entering your City Name" transparent="1" halign="center" valign="center" zPosition="2" foregroundColor="#00ffffff" />
            <eLabel backgroundColor="#00000000" font="Regular; 28" position="00,535" size="1280,40" text="Please Restart E2 after saving your City Name" transparent="1" halign="center" valign="center" zPosition="2" foregroundColor="#cc7722" />
            <ePixmap position="30,590" zPosition="3" size="240,50" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MSNWeather/Images/red.png" transparent="1" alphatest="blend" />
            <ePixmap position="330,590" zPosition="3" size="240,50" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MSNWeather/Images/green.png"  transparent="1" alphatest="blend" />
            <ePixmap position="630,590" zPosition="3" size="240,50" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MSNWeather/Images/yellow.png"  transparent="1" alphatest="blend" />
            <ePixmap position="930,590" zPosition="3" size="240,50" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MSNWeather/Images/blue.png"  transparent="1" alphatest="blend" />
            <widget source="key_red" render="Label" position="10,570" zPosition="5" size="280,50" font="Regular;27" halign="center" valign="center" backgroundColor="#00313040" foregroundColor="#00ffffff" transparent="1" />
            <widget source="key_green" render="Label" position="310,570" zPosition="5" size="280,50" font="Regular;27" halign="center" valign="center" backgroundColor="#00313040" foregroundColor="#00ffffff" transparent="1" />
            <widget source="key_yellow" render="Label" position="610,570" zPosition="5" size="280,50" font="Regular;27" halign="center" valign="center" backgroundColor="#00313040" foregroundColor="#00ffffff" transparent="1" />
            <widget source="key_blue" render="Label" position="910,570" zPosition="5" size="280,50" font="Regular;27" halign="center" valign="center" backgroundColor="#00313040" foregroundColor="#00ffffff" transparent="1" />
        </screen>
        """

    def __init__(self, session):
        self.session = session
        Screen.__init__(self, session)
        self.setTitle(_('Setup'))
        self.status=""
        self["status"] = Label()

        New_keymap = '/usr/lib/enigma2/python/Plugins/Extensions/MSNWeather/keymap.xml'
        readKeymap(New_keymap)

        self.list = []
        self.list.append(getConfigListEntry(_("Enabled :"), config.plugins.MSNWeather.enabled))
        self.list.append(getConfigListEntry(_("Weather service :"), config.plugins.MSNWeather.weatherservice))
        self.list.append(getConfigListEntry(_("Weather city name :"), config.plugins.MSNWeather.weathercity))
        self.list.append(getConfigListEntry(_("Weather API key :"), config.plugins.MSNWeather.apikey))
        self.list.append(getConfigListEntry(_("Temperature unit :"), config.plugins.MSNWeather.tempUnit))
        self.list.append(getConfigListEntry(_("Weather icon set :"), config.plugins.MSNWeather.iconset))
        self.list.append(getConfigListEntry(_("Weather icon night switch :"), config.plugins.MSNWeather.nighticons))
        self.list.append(getConfigListEntry(_("Refresh interval :"), config.plugins.MSNWeather.refreshInterval))
        self.list.append(getConfigListEntry(_("Cache data :"), config.plugins.MSNWeather.cachedata))
        self.list.append(getConfigListEntry(_("Enable Debug :"), config.plugins.MSNWeather.debug))

        #logout(data=str(self.list))
        ConfigListScreen.__init__(self, self.list, session=session)

        self["key_green"] = StaticText(_("Save"))
        #self["key_blue"] = StaticText(_("Location Selection"))
        self["key_yellow"] = StaticText(_("Defaults"))
        self["key_red"] = StaticText(_("Location Selection"))

        self["blueActions"] = HelpableActionMap(self, ['ColorActions', 'OkCancelActions', 'MSNWeatherActions'],
        #self["blueActions"] = ActionMap(self, ["OkCancelActions',ColorActions"],
        #self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'],
                                {
                                    'ok': self.keyOK,
                                    "cancel": self.close,
                                    "green": self.keySave,
                                    #"red": (self.keycheckCity, _("Search for your City")),
                                    "red": self.keycheckCity,
                                    #"yellow": (self.defaults, _("Set default values"))
                                    "yellow": self.defaults
                                }, -1)
                                                #prio=0, description=_("Weather Settings Actions"))

        logout(data="WeatherSettingsViewNew-buttons")
        self.old_weatherservice = config.plugins.MSNWeather.weatherservice.value
        logout(data="WeatherSettingsViewNew-old")
        self.citylist = []
        logout(data="WeatherSettingsViewNew-city")
        self.checkcity = False
        logout(data="WeatherSettingsViewNew-check city")
        self.closeonsave = False
        logout(data="WeatherSettingsViewNew-save")

    def keyOK(self):
        logout(data="keyOk")
        current_item = self['config'].getCurrent()
        logout(data=str(current_item))
        if current_item:
            item_text = current_item[0]
            logout(data="keyOk 1")
            if item_text == _("Weather city name :"):
                logout(data="city")
                # Code für Weather city name Einstellung
                title = _('Please enter a valid city name.')
                self.session.openWithCallback(self.VirtualKeyBoardCallBack, VirtualKeyBoard, title=title)

            elif item_text == _("Weather API key :"):
                logout(data="api")
                text = current_item[1].value

                if text == config.plugins.MSNWeather.apikey.value:
                    logout(data="keyboard")
                    title = _('Please enter a valid city name.')
                    self.session.openWithCallback(self.VirtualKeyBoardCallBack, VirtualKeyBoard, title=title)

    def VirtualKeyBoardCallBack(self, callback):
        logout(data="def keyboard")
        try:
            if callback:
                self['config'].getCurrent()[1].value = callback
        except:
            pass

    def keycheckCity(self, closesave=False):
        logout(data="def -----------  keycheckCity")
        weathercity = config.plugins.MSNWeather.weathercity.value.split(",")[0]
        logout(data="--------------------------  weatherCity")
        logout(data=str(weathercity))

        #self.["footnote"].setText(_("Search for City ID please wait..."))

        logout(data="keycheckCity1")
        self.closeonsave = closesave
        logout(data="keycheckCity2")
        callInThread(self.searchCity, weathercity)
        logout(data="keycheckCity3")

    def searchCity(self, weathercity):
        logout(data="searchCity services 1 ")
        services = {"MSN": "msn", "OpenMeteo": "omw", "openweather": "owm"}
        logout(data=str(services))
        service = services.get(config.plugins.MSNWeather.weatherservice.value, "msn")
        logout(data=str(service))
        logout(data="searchCity apikey 2 ")
        apikey = config.plugins.MSNWeather.apikey.value
        logout(data=str(apikey))
        logout(data="apikey 3 ")
        if service == "owm" and len(apikey) < 32:
            logout(data="searchCity services-own")
            self.session.open(MessageBox, text=_("The API key for OpenWeatherMap is not defined or invalid.\nPlease verify your input data.\nOtherwise your settings won't be saved."), type=MessageBox.TYPE_WARNING)
        else:
            logout(data="searchCity services own else 4 ")
            WI = Weatherinfo(service, config.plugins.MSNWeather.apikey.value)
            logout(data=str(WI))
            if WI.error:
                logout(data="searchCity services-error")
                print("[WeatherSettingsViewNew] Error in module 'searchCity': %s" % WI.error)
                #self["footnote"].setText(_("Error in Weatherinfo"))
                self.session.open(MessageBox, text=WI.error, type=MessageBox.TYPE_ERROR)
            else:
                logout(data="searchCity services else 5")
                logout(str(weathercity))
                # Den Wert von config.osd.language.value in eine separate Variable setzen
                language_value = config.osd.language.value
                logout(str(language_value))
                logout(data="searchCity services else 5a")
                weathercity = str(weathercity)
                logout(data="searchCity services else 5b")
                logout(str(weathercity))
                language_value = config.osd.language.value.replace('_', '-').lower()
                logout(str(language_value))
                logout(data="searchCity services else 5c")
                # hier abfrage an Weatherinfo in Tools
                geodatalist = WI.getCitylist(weathercity, language_value)
                # geodatalist = WI.getCitylist(weathercity, config.osd.language.value.replace('_', '-').lower())
                logout(data=str(geodatalist))
                logout(data="searchCity services else 6")
                if WI.error or geodatalist is None or len(geodatalist) == 0:
                    logout(data="searchCity services else wi error")
                    print("[WeatherSettingsViewNew] Error in module 'searchCity': %s" % WI.error)
                    #self["footnote"].setText(_("Error getting City ID"))
                    self.session.open(MessageBox, text=_("City '%s' not found! Please try another wording." % weathercity), type=MessageBox.TYPE_WARNING)
                    logout(data="searchCity services else wi error 1")
#                elif len(geodatalist) == 1:
#					#self["footnote"].setText(_("Getting City ID Success"))
#                    self.saveGeoCode(geodatalist[0])
#                    logout(data="searchCity services else wi error 2")
                else:
                    logout(data="searchCity services wi else 7")
                    self.citylist = []
                    for item in geodatalist:
                        logout(data="searchCity services for 8")
                        lon = " [lon=%s" % item[1] if float(item[1]) != 0.0 else ""
                        lat = ", lat=%s]" % item[2] if float(item[2]) != 0.0 else ""
                        logout(data="searchCity services for 8.1")
                        try:
                            logout(data="searchCity services for try")
                            #self.citylist.append(("%s%s%s" % (item[0], lon, lat), item[0], item[1], item[2]))
                            self.citylist.append((str(item[0]) + lon + lat, str(item[0]), str(item[1]), str(item[2])))
                            logout(data="searchCity services for try 2")
                            logout(data=str(self.citylist))
                        except Exception:
                            logout(data="searchCity services for execpt")
                            print("[WeatherSettingsViewNew] Error in module 'showMenu': faulty entry in resultlist.")


                    logout(data="searchCity services for choicebox zu my screen ")
############################## old Choice Box call #############################
                    #self.session.openWithCallback(self.choiceIdxCallback, ChoiceBox, titlebartext=_("Select Your Location"), title="", list=tuple(self.citylist))
                    self.citylisttest = self.citylist
                    logout(data=str(self.citylisttest))

                    self.testScreen = self.session.open(TestScreen, citylisttest=self.citylisttest, okCallback=self.testScreenOkCallback)
                    logout(data="355 searchCity services for choicebox zurueck my screen ")

                    #selected_city_str = self.selected_city
                    #logout(data=str(selected_city_str))

                    #self.choiceIdxCallback(self.test_screen.selectCity())

    def testScreenOkCallback(self, selected_city_str):
        #selected_city_str = self.test_screen.selectCity()
        logout(data="361 zurueck test screen selecedet ")
        logout(data=str(selected_city_str))
        logout(data="363 zu IDX ")
        self.choiceIdxCallback(selected_city_str)

    def choiceIdxCallback(self, selected_city):
        logout(data="choiceIdxCallback")
        self.selected_city = selected_city
        logout(data=str(self.selected_city))
        logout("self.selected_city:")
        logout(str(self.selected_city))

        if len(self.selected_city) >= 4:
            parts = self.selected_city.split(',')

            city = parts[0]
            longitude =""
            latitude = ""
            for part in parts:
                if 'lon=' in part:
                    longitude = part.split('=')[1].strip()
                elif 'lat=' in part:
                    latitude = part.split('=')[1].strip((']'))

            # You can process or save the values
            logout("Stadt: " + city)
            logout("Längengrad: " + longitude)
            logout("Breitengrad: " + latitude)

            if city and longitude and latitude:
                self.saveGeoCode(city, longitude, latitude)

        else:
            logout("The selected City does not have enough information.")
################################################################################
    def saveGeoCode(self, city, longitude, latitude):
        logout(data="saveGeoCode value ")
        logout(data=str(city))
        logout(data="longitude - lon - laengengrad")
        logout(data=str(longitude))
        logout(data="latitude - lat - breitengrad")
        logout(data=str(latitude))
        config.plugins.MSNWeather.weathercity.value = city
        config.plugins.MSNWeather.owm_geocode.value = "%s,%s" % (longitude, latitude)

        self.old_weatherservice = config.plugins.MSNWeather.weatherservice.value
        self.checkcity = False
        if self.closeonsave:
            config.plugins.MSNWeather.owm_geocode.save()
            weatherhandler.reset()
            #Setup.keySave(self)
            self.keySave()

    def keySelect(self):
        logout(data="keySelect")
        if self.getCurrentItem() == config.plugins.MSNWeather.weathercity:
            self.checkcity = True
        Setup.keySelect(self)

    def keySave(self):
        logout(data="keySave")
        weathercity = config.plugins.MSNWeather.weathercity.value.split(",")[0]
        if len(weathercity) < 3:
            #self["footnote"].setText(_("The city name is too short. More than 2 characters are needed for search."))
            return
        if self.checkcity or self.old_weatherservice != config.plugins.MSNWeather.weatherservice.value:
            self.keycheckCity(True)
            return
        weatherhandler.reset()
        config.plugins.MSNWeather.owm_geocode.save()
        #Setup.keySave(self)
        super(WeatherSettingsViewNew, self).keySave()

    def defaults(self, SAVE=False):
        logout(data="defaults")
        for x in self["config"].list:
            logout(data="defaults1")
            if len(x) > 1:
                logout(data="defaults2")
                self.setInputToDefault(x[1], SAVE)
        logout(data="defaults3")
        self.setInputToDefault(config.plugins.MSNWeather.owm_geocode, SAVE)
        if self.session:
            logout(data="defaults4")
            self.list = []
            self.list.append(getConfigListEntry(_("Enabled :"), config.plugins.MSNWeather.enabled))
            self.list.append(getConfigListEntry(_("Weather service :"), config.plugins.MSNWeather.weatherservice))
            self.list.append(getConfigListEntry(_("Weather city name :"), config.plugins.MSNWeather.weathercity))
            self.list.append(getConfigListEntry(_("Weather API key :"), config.plugins.MSNWeather.apikey))
            self.list.append(getConfigListEntry(_("Temperature unit :"), config.plugins.MSNWeather.tempUnit))
            self.list.append(getConfigListEntry(_("Weather icon set :"), config.plugins.MSNWeather.iconset))
            self.list.append(getConfigListEntry(_("Weather icon night switch :"), config.plugins.MSNWeather.nighticons))
            self.list.append(getConfigListEntry(_("Refresh interval :"), config.plugins.MSNWeather.refreshInterval))
            self.list.append(getConfigListEntry(_("Cache data :"), config.plugins.MSNWeather.cachedata))
            self.list.append(getConfigListEntry(_("Enable Debug :"), config.plugins.MSNWeather.debug))
            self['config'].setList(self.list)
            self['status'].setText(_("Standard finished"))

    def setInputToDefault(self, configItem, SAVE):
        configItem.setValue(configItem.default)
        if SAVE:
            configItem.save()

class TestScreen(Screen):
    skin = """
    <screen name="TestScreen" position="center,center" size="1920,1080" backgroundColor="#00000000" transparent="0"  >
            <eLabel position="0,0" size="1920,1080" backgroundColor="#00000000" transparent="0" zPosition="0" />
            <ePixmap position="10,590" zPosition="3" size="240,50" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MSNWeather/Images/red.png" transparent="1" alphatest="blend" />
            <widget name="meinelist" position="100,20" size="1000,430" font="Regular;30" itemHeight="45" backgroundColor="#00000000" foregroundColor="#00ffffff" transparent="0" zPosition="3" scrollbarMode="showOnDemand" />
            <widget name="status" font="Regular; 25" position="100,470" size="1000,40" foregroundColor ="#0000ff00" backgroundColor="#00000000" transparent="0" zPosition="3" halign="center" valign="center" />
            <widget source="key_red" render="Label" position="10,570" zPosition="5" size="240,50" font="Regular;30" halign="center" valign="center" backgroundColor="#00313040" foregroundColor="#00ffffff" transparent="1" />
    </screen>
    """
#            <widget name="mylist" position="100,20" size="1000,450" font="Regular;30" itemHeight="45"  backgroundColor="#00000000" foregroundColor="#00ffffff" transparent="0" zPosition="3" scrollbarMode="showOnDemand" />

    def __init__(self, session, citylisttest, okCallback=None):
        logout(data="Testscreen init")
        self.session = session
        Screen.__init__(self, session)
        self.citylisttest = citylisttest
        self.okCallback = okCallback

        logout(data=str(self.citylisttest))

        logout(data="Testscreen init 1")
        zeile1 = self.citylisttest
        logout(data=str(zeile1))

        # Create dummy data
        dummy_data = ["Item 1", "Item 2", "Item 3"]
        zeile2 = dummy_data
        logout(data=str(zeile2))
        # Create MenuList widget and add data
        self['meinelist'] = MenuList(citylisttest)

        self.status = ""
        self["status"] = Label()
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'],
                                    {
                                        'ok': self.selectCity,
                                        'cancel': self.close,
                                        'red': self.close,
                                        'green': self.close,
                                        'yellow': self.close,
                                    }, -1)

        self['key_red'] = Label(_('exit'))
        logout(data="Testscreen ende")
        self['status'].setText(_("Select your City and Press OK"))
        logout(data="Testscreen layout finish")

    def selectCity(self):
        logout(data="492 searchCity services for my screen selectCity ")
        selected_city_tuple = self['meinelist'].l.getCurrentSelection()

        if selected_city_tuple:
            selected_city = selected_city_tuple[0]
            self.selected_city = selected_city  # Save selected city
            logout(data="498 Selected City: {}".format(selected_city))  # Write selected city to the log file
            if self.okCallback is not None:
                self.okCallback(selected_city)
            self.close()  # After selecting, close screen

class WeatherHandler():
    logout(data="WeatherHandler")
    def __init__(self):
        logout(data="WeatherHandler init")
        self.session = None
        self.enabledebug = config.plugins.MSNWeather.debug.value
        modes = {"MSN": "msn", "openweather": "owm", "OpenMeteo": "omw"}
        mode = modes.get(config.plugins.MSNWeather.weatherservice.value, "msn")
        logout(data="WeatherHandler mode wetter")
        logout(data=str(mode))
        self.WI = Weatherinfo(mode, config.plugins.MSNWeather.apikey.value)
        logout(data="WeatherHandler Apy Key in WI")
        apy_key = config.plugins.MSNWeather.apikey.value
        logout(str(apy_key))
        self.geocode = config.plugins.MSNWeather.owm_geocode.value.split(",")
        self.weathercity = None
        self.trialcounter = 0
        self.currentWeatherDataValid = 3  # 0= green (data available), 1= yellow (still working), 2= red (no data available, wait on next refresh) 3=startup
        self.refreshTimer = eTimer()
        self.refreshTimer.callback.append(self.refreshWeatherData)
        self.wetterdata = None
        self.onUpdate = []
        self.skydirs = {"N": _("North"), "NE": _("Northeast"), "E": _("East"), "SE": _("Southeast"), "S": _("South"), "SW": _("Southwest"), "W": _("West"), "NW": _("Northwest")}
        self.msnFullData = None

    def sessionStart(self, session):
        logout(data="WeatherHandler session start")
        self.session = session
        logout(data="WeatherHandler session start 1")
        #self.debug("sessionStart")
        logout(data="WeatherHandler session start 2")
        self.getCacheData()
        logout(data="WeatherHandler session start 3")

    def writeData(self, data):
        logout(data="WeatherHandler write data")
        #self.debug("writeData")
        logout(data="WeatherHandler write data 1")
        self.currentWeatherDataValid = 0
        logout(data="WeatherHandler write data 2")
        self.wetterdata = data
        logout(data="WeatherHandler write data 3")
        for callback in self.onUpdate:
            logout(data="WeatherHandler write data 4")
            callback(data)
            logout(data="WeatherHandler write data 5")
        logout(data="WeatherHandler write data 6")
        seconds = int(config.plugins.MSNWeather.refreshInterval.value * 60)
        logout(data="WeatherHandler write data 7")
        self.refreshTimer.start(seconds * 1000, True)
        logout(data="WeatherHandler write data 8")

    def getData(self):
        logout(data="WeatherHandler getdata")
        return self.wetterdata

    if sys.version_info[0] >= 3:
        logout(data="Python 3 getValid")
        def getValid(self):
            return self.currentWeatherDataValid
    else:
        logout(data="Python 2 get valid")
        def getValid(self):
            return self.currentWeatherDataValid

    if sys.version_info[0] >= 3:
        logout(data="Python 3 getSkydirs")
        def getSkydirs(self):
            return self.skydirs
    else:
        logout(data="Python 2 get skydirs")
        def getSkydirs(self):
            return self.skydirs

    def getCacheData(self):
        logout(data="WeatherHandler getcachedata")
        cacheminutes = int(config.plugins.MSNWeather.cachedata.value)
        logout(data="WeatherHandler getcachedata 1")
        if cacheminutes and isfile(CACHEFILE):
            logout(data="WeatherHandler getcachedata 2")
            timedelta = (time() - getmtime(CACHEFILE)) / 60
            logout(data="WeatherHandler getcachedata 3")
            if cacheminutes > timedelta:
                logout(data="WeatherHandler getcachedata 4")
                with open(CACHEFILE, "rb") as fd:
                    logout(data="WeatherHandler getcachedata 5")
                    cache_data = load(fd)
                    logout(data="WeatherHandler getcachedata 6")
                self.writeData(cache_data)
                logout(data="WeatherHandler getcachedata 7")
                return
        logout(data="WeatherHandler getcachedata 8")
        self.refreshTimer.start(3000, True)

    logout(data="getcachedata 9")
    def refreshWeatherData(self, entry=None):
        logout(data="WeatherHandler refresh")
        #self.debug("refreshWeatherData")
        self.refreshTimer.stop()
        if config.misc.firstrun.value:  # don't refresh on firstrun try again after 10 seconds
            logout(data="WeatherHandler refresh 1")
            #self.debug("firstrun")
            self.refreshTimer.start(600000, True)
            return
        if config.plugins.MSNWeather.enabled.value:
            logout(data="WeatherHandler refresh 2")
            self.weathercity = config.plugins.MSNWeather.weathercity.value
            geocode = config.plugins.MSNWeather.owm_geocode.value.split(",")
            # DEPRECATED, will be removed in April 2023
            if geocode == ['0.0', '0.0']:
                logout(data="WeatherHandler refresh 3")
                geodatalist = self.WI.getCitylist(config.plugins.MSNWeather.weathercity.value.split(",")[0], config.osd.language.value.replace('_', '-').lower())
                if geodatalist is not None and len(geodatalist[0]) == 3:
                    geocode = [geodatalist[0][1], geodatalist[0][2]]
                    config.plugins.MSNWeather.weathercity.value = geodatalist[0][0]
                    config.plugins.MSNWeather.weathercity.save()
                    config.plugins.MSNWeather.owm_geocode.value = "%s,%s" % (float(geocode[0]), float(geocode[1]))
                    config.plugins.MSNWeather.owm_geocode.save()
            # DEPRECATED, will be removed in April 2023
            if geocode and len(geocode) == 2:
                logout(data="WeatherHandler refresh 4")
                geodata = (self.weathercity, geocode[0], geocode[1])  # tuple ("Cityname", longitude, latitude)
            else:
                logout(data="WeatherHandler refresh 5")
                geodata = None
            #language = config.osd.language.value.replace("_", "-")
            language = config.osd.language.value.lower().replace('_', '-')
            logout(data=str(language))
            unit = "imperial" if config.plugins.MSNWeather.tempUnit.value == "Fahrenheit" else "metric"
            if geodata:
                logout(data="WeatherHandler refresh 6")
                self.WI.start(geodata=geodata, cityID=None, units=unit, scheme=language, reduced=True, callback=self.refreshWeatherDataCallback)
            else:
                logout(data="WeatherHandler refresh 7")
                print("[%s] error in MSNWeather config" % (MODULE_NAME))
                self.currentWeatherDataValid = 2

    def refreshWeatherDataCallback(self, data, error):
        logout(data="WeatherHandler refresh callback")
        #self.debug("refreshWeatherDataCallback")
        logout(data=str(data))
        logout(data=str(error))
        if error or data is None:
            logout(data="WeatherHandler refresh callback trial 1")
            logout(data=str(self.trialcounter))
            self.trialcounter += 1
            logout(data=str(self.trialcounter))
            if self.trialcounter < 2:
                logout(data="WeatherHandler refresh callback 2")
                print("[%s] lookup for city '%s' paused, try again in 10 secs..." % (MODULE_NAME, self.weathercity))
                self.currentWeatherDataValid = 1
                self.refreshTimer.start(10000, True)
            elif self.trialcounter > 5:
                logout(data="WeatherHandler refresh callback 3")
                print("[%s] lookup for city '%s' paused 1 h, to many errors..." % (MODULE_NAME, self.weathercity))
                self.currentWeatherDataValid = 2
                self.refreshTimer.start(3600000, True)
            else:
                logout(data="WeatherHandler refresh callback 4")
                print("[%s] lookup for city '%s' paused 5 mins, to many errors..." % (MODULE_NAME, self.weathercity))
                self.currentWeatherDataValid = 2
                self.refreshTimer.start(300000, True)
            return
        logout(data="WeatherHandler refresh callback 5")
        self.writeData(data)
        logout(data="WeatherHandler refresh callback 6")
        self.msnFullData = self.WI.info if config.plugins.MSNWeather.weatherservice.value == "MSN" else None
        logout(data="WeatherHandler refresh callback 7")
        # TODO write cache only on close
        if config.plugins.MSNWeather.cachedata.value != "0":
            logout(data="WeatherHandler refresh callback 8")
            with open(CACHEFILE, "wb") as fd:
                dump(data, fd, -1)
        logout(data="WeatherHandler refresh callback 9")

    def reset(self):
        logout(data="WeatherHandler reset")
        self.refreshTimer.stop()
        if isfile(CACHEFILE):
            remove(CACHEFILE)
        modes = {"MSN": "msn", "openweather": "owm", "OpenMeteo": "omw"}
        mode = modes.get(config.plugins.MSNWeather.weatherservice.value, "msn")
        self.WI.setmode(mode, config.plugins.MSNWeather.apikey.value)
        if self.WI.error:
            print(self.WI.error)
            self.WI.setmode()  # fallback to MSN

        if self.session:
            iconpath = config.plugins.MSNWeather.iconset.value
            iconpath = join(ICONSETROOT, iconpath) if iconpath else join(PLUGINPATH, "Icons")
            self.session.screen["MSNWeather"].iconpath = iconpath
        self.refreshWeatherData()

    if sys.version_info[0] >= 3:
        logout(data="Python 3 debug")
        def debug(self, text):
            if self.enabledebug:
               print("[%s] WeatherHandler DEBUG %s" % (MODULE_NAME, text))
    else:
        logout(data="Python 2 debug")
        def debug(self, text):
            if self.enabledebug:
                print("[%s] WeatherHandler DEBUG %s" % (MODULE_NAME, text))

    logout(data="WeatherHandler ende")

def main(session, **kwargs):
    logout(data="main")
    session.open(MSNWeatherPlugin)


def setup(session, **kwargs):
    logout(data="setup")
    session.open(WeatherSettingsViewNew)

def sessionstart(session, **kwargs):
    logout(data="sessionstart")
    from Components.Sources.MSNWeather import MSNWeather
    session.screen["MSNWeather"] = MSNWeather()
    session.screen["MSNWeather"].precipitationtext = _("Precipitation")
    session.screen["MSNWeather"].humiditytext = _("Humidity")
    session.screen["MSNWeather"].feelsliketext = _("Feels like")
    session.screen["MSNWeather"].pluginpath = PLUGINPATH
    iconpath = config.plugins.MSNWeather.iconset.value
    if iconpath:
        iconpath = join(ICONSETROOT, iconpath)
    else:
        iconpath = join(PLUGINPATH, "Icons")
    session.screen["MSNWeather"].iconpath = iconpath
    weatherhandler.sessionStart(session)

def Plugins(**kwargs):
    logout(data="MSNWeatherPlugin")
    logout(data="plugins")
    pluginList = []
    pluginList.append(PluginDescriptor(name="MSNWeather", where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=sessionstart, needsRestart=False))
    pluginList.append(PluginDescriptor(name="Weather Plugin", description=_("Show Weather Forecast"), icon="plugin.png", where=[PluginDescriptor.WHERE_PLUGINMENU], fnc=main))
    return pluginList

class MSNWeatherPlugin(Screen):
    logout(data="MSNWeatherPluginScreen")
    def __init__(self, session):
        params = {
            "picpath": join(PLUGINPATH, "Images")
        }
        skintext = ""
        logout(data="screen")
        xml = parse(join(PLUGINPATH, "skin.xml")).getroot()
        logout(data="screen2")
        for screen in xml.findall('screen'):
            logout(data="screen in xml")
            if screen.get("name") == "MSNWeatherPlugin":
                logout(data="screen get name")
                skintext = tostring(screen).decode()
                for key in list(params.keys()):
                    logout(data="screen key")
                    try:
                        logout(data="screen key try")
                        skintext = skintext.replace('{%s}' % key, params[key])
                    except Exception as e:
                        logout(data="screen key execpt")
                        print("%s@key=%s" % (str(e), key))
                break
        self.skin = skintext
        logout(data="screen skintext")
        Screen.__init__(self, session)
        self.title = _("Weather Plugin")

        New_keymap = '/usr/lib/enigma2/python/Plugins/Extensions/MSNWeather/keymap.xml'
        readKeymap(New_keymap)

        self["key_blue"] = StaticText(_("Menu"))

        self["actions"] = ActionMap(["SetupActions", "DirectionActions", 'ColorActions', 'MSNWeatherActions'],
        {
            "green": self.configmenu,
            "cancel": self.close,
            "menu": self.configmenu,
        }, -1)
        logout(data="screen skintext1")
        self["statustext"] = StaticText()
        self["update"] = Label(_("Update"))
        self["current"] = Label(_("Current Weather"))
        self["today"] = Label(_("Today"))
        logout(data="screen skintext2")
        for i in range(1, 6):
            self["weekday%s_temp" % i] = StaticText()
        logout(data="screen skintext3")
        self.data = None
        self.na = _("n/a")
        logout(data="screen skintext4")
        self.onLayoutFinish.append(self.startRun)
        logout(data="finish")

    def startRun(self):
        logout(data="startrun")
        self.data = weatherhandler.getData() or {}
        logout(data="startrun zurueck daten")
        logout(data=str(self.data))
        if self.data:
            logout(data="startrun-callback")
            self.getWeatherDataCallback()
            logout(data="startrun-callback 1")

    def clearFields(self):
        logout(data="clearfields")
        for i in range(1, 6):
            self["weekday%s_temp" % i].text = ""

    if sys.version_info[0] >= 3:
        logout(data="Python 3 getVal")
        def getVal(self, key):
            return self.data.get(key, self.na) if self.data else self.na
    else:
        logout(data="Python 2 getval")
        def getVal(self, key):
            return self.data.get(key, self.na) if self.data else self.na

    if sys.version_info[0] >= 3:
        logout(data="Python 3 getCurrentVal")
        def getCurrentVal(self, key, default= _("n/a")):
            value = default
            if self.data and "current" in self.data:
               current = self.data.get("current", {})
               if key in current:
                   value = current.get(key, default)
            return value
    else:
        logout(data="Python 2 getCurrentVal")
        def getCurrentVal(self, key, default=_("n/a")):
            value = default
            if self.data and "current" in self.data:
                current = self.data.get("current", {})
                if key in current:
                    value = current.get(key, default)
            return value

    def getWeatherDataCallback(self):
        logout(data="getWeatherDataCallback")
        self["statustext"].text = ""
        forecast = self.data.get("forecast")
        tempunit = self.data.get("tempunit", self.na)
        for day in range(1, 6):

            item = forecast.get(day)
            logout(data="item")
            logout(data=str(item))

            lowTemp = item.get("minTemp")
            logout(data="lowTemp")
            logout(data=str(lowTemp))

            highTemp = item.get("maxTemp")
            logout(data="highTemp")
            logout(data=str(highTemp))

            text = item.get("text")
            logout(data="text")
            logout(data=str(text))
            self["weekday%s_temp" % day].text = "%s %s|%s %s\n%s" % (highTemp, tempunit, lowTemp, tempunit, text)

    def configmenu(self):
        logout(data="configmenu")
        self.session.openWithCallback(self.setupFinished, WeatherSettingsViewNew)

    def setupFinished(self, result=None):
        logout(data="setupFinished")
        self.clearFields()
        self.startRun()

    def error(self, errortext):
        self.clearFields()
        self["statustext"].text = errortext

weatherhandler = WeatherHandler()
