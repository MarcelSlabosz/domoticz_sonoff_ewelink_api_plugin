# Sonoff Original Soft eWeLink API
#
# Author: Marcel Słabosz
#
"""
<plugin key="sonoff_ewelink_api" name="Sonoff Original Soft eWeLink API"
    author="Marcel Słabosz" version="0.1.0"
    wikilink=""
    externallink="https://github.com/MarcelSlabosz/domoticz_sonoff_ewelink_api_plugin">
    <description>
        <h2>Sonoff Original Soft eWeLink API</h2><br/>
        <p>This plugin is designed to interact with sonoff devices
        that isn't flashed with alternative firmware (Tasmota etc.)
        Using this plugin you can control your devices via physical button,
        Domoticz interface as well as Original eWeLinkAPI</p>

        <h3>Features</h3>
        <ul style="list-style-type:square">
            <li>Turn on and off via Domoticz switch device</li>
            <li>Periodically refreshes the switch status in case of turn on/off via original soft or button.</li>
        </ul>
        <h3>Devices</h3>
        <ul style="list-style-type:square">
            <li>{Name} - Switch</li>
        </ul>
        <h3>Configuration</h3>
        <p>Read (<a href="https://github.com/MarcelSlabosz/domoticz_sonoff_ewelink_api_plugin/blob/master/README.md"
        target="_blank">README.md file</a>)
        to find out how to get parameters for configuration</p>
    </description>
    <params>
        <param field="Password" label="Application token" width="400px" required="true"/>
        <param field="Username" label="Application key" width="400px" required="true"/>
        <param field="Mode1" label="Region" width="100px">
            <options>
                <option label="eu" value="eu" dafault="true"/>
                <option label="us" value="us"/>
                <option label="as" value="as"/>
            </options>
        </param>
        <param field="Mode2" label="Device id" width="100px" required="true"/>
    </params>
</plugin>
"""
import Domoticz
import subprocess
import json
import os.path


def _(text):
    i10n = {
        'pl': {
            'Switch': "Włącznik",
            'on': 'włączony',
            'off': 'wyłączony',
            'N/A': 'N/D'
        }
    }

    return i10n.get(Settings["Language"], {}).get(text, text)


class SonoffEwelinkApi:
    enabled = False

    def __init__(self):
        self.UNIT_SWITCH = 1
        self._heartbeat_iterator = 5

    def on_start(self):
        # here we should add devices if not exists.
        Domoticz.Log("Starting Sonoff API plugin. language: %s" % Settings["Language"])

        self.variables = {
                self.UNIT_SWITCH: {
                    "Name": _("Switch"),
                    "TypeName": "Selector Switch",
                    "Switchtype": 0,
                    "Used": 1,
                    "nValue": 0,
                    "sValue": _('off')
                    }
            }

        self._create_devices()

    def _create_devices(self):
        """Create devices if not exists yet"""
        for unit, value in self.variables.items():
            try:
                device = Devices[unit]
            except KeyError as err:
                Domoticz.Log("Device %i is not created yet. Creating...." % unit)
                self._create_device(unit)

    def _create_device(self, unit):
        """Create singe device base on predefined variable"""
        try:
            unit_data = self.variables[unit]
        except KeyError as error:
            Domoticz.Log("Unknown device id")
            return False

        if unit in Devices:
            Domoticz.Debug("Device Unit=%i, Name=%s already exists" % (unit, unit_data.get('Name', 'N/A')))
            return True

        _name = unit_data.get('Name', 'N/A')
        _typename = unit_data['TypeName']
        _switch_type = unit_data['Switchtype']
        _image = unit_data.get('Image', 0)
        _options = unit_data.get('Options', {})
        _used = unit_data.get('Used', 0)

        device = Domoticz.Device(
                Name=_name,
                Unit=unit,
                TypeName=unit_data['TypeName'],
                Image=_image,
                Options=_options,
                Used=_used,
                Switchtype=_switch_type
            )

        device.Create()

        Domoticz.Log("Device %i created. Name: %s" % (unit, self.variables[unit]['Name']))
        return True

#    def on_stop(self):
#        Domoticz.Log("onStop called")

#    def on_connect(self, Connection, Status, Description):
#        Domoticz.Log("onConnect called")

#    def on_message(self, Connection, Data):
#        Domoticz.Log("onMessage called")

    def on_command(self, unit, command, level, hue):
        Domoticz.Log("onCommand called for Unit " + str(unit) + ": Parameter '"
                     + str(command) + "', Level: " + str(level))
        Domoticz.Debug(repr(Parameters))
        if command == 'On':
            self.variables[unit]["nValue"] = 1
            self.variables[unit]["sValue"] = _('on')
            status = self._call_api(Parameters['Password'], Parameters['Username'],
                                    Parameters['Mode1'], Parameters['Mode2'], 'on')
        else:
            self.variables[unit]["nValue"] = 0
            self.variables[unit]["sValue"] = _('off')
            status = self._call_api(Parameters['Password'], Parameters['Username'],
                                    Parameters['Mode1'], Parameters['Mode2'], 'off')
        Domoticz.Log("Api call response status: %s" % repr(status))
        self._update_ewelink_status(status, unit)

    # def on_notification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
    #     Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + ","
    #     + str(Priority) + "," + Sound + "," + ImageFile)

#    def on_disconnect(self, Connection):
#        Domoticz.Log("onDisconnect called")

    def on_heartbeat(self):
        Domoticz.Debug("onHeartbeat called %s" % self._heartbeat_iterator)
        self._heartbeat_iterator += 1
        if self._heartbeat_iterator >= 6:
            self._heartbeat_iterator = 0
            self._refresh_state()

    def _call_api(self, access_token, api_key, region, device, action):
        status = {}
        try:
            with subprocess.Popen(["node", "%scall_ewelink_api.js" % Parameters['HomeFolder'],
                                   access_token, api_key, region, device, action], stdout=subprocess.PIPE) as proc:
                line = proc.stdout.read().decode("utf-8", "strict")
                if line.startswith(device):
                    stat = line.split(" ", 1)
                    status = json.loads(stat[1])
        except FileNotFoundError as er:
            if er.filename == 'node':
                Domoticz.Error("Node.js is not installed or not added to PATH!")
            elif str(er.filename).endswith("call_ewelink_api.js"):
                if not os.path.exists("%scall_ewelink_api.js" % Parameters['HomeFolder']):
                    Domoticz.Error("Plugin file call_ewelink_api.js was deleted! Revert changes in plugin dir.")
                else:
                    Domoticz.Error("Something goes wrong. \
                    Please report the issue: https://github.com/MarcelSlabosz/domoticz_sonoff_ewelink_api_plugin/issues.\
                    %s" % repr(er))
            else:
                Domoticz.Error("Something goes wrong. \
                Please report an issue: https://github.com/MarcelSlabosz/domoticz_sonoff_ewelink_api_plugin/issues. %s"\
                               % repr(er))
        return status

    def _refresh_state(self):
        Domoticz.Log('Try to refresh device status...')
        status = self._call_api(Parameters['Password'], Parameters['Username'],
                                Parameters['Mode1'], Parameters['Mode2'], 'status')
        self._update_ewelink_status(status, self.UNIT_SWITCH)

    def _update_ewelink_status(self, status, unit):
        state = status.get('state', 'na')
        if state == 'off':
            Devices[unit].Update(nValue=0, sValue=_('off'))
        elif state == 'on':
            Devices[unit].Update(nValue=1, sValue=_('on'))
        else:
            Devices[unit].Update(nValue=-1, sValue=_('N/A'))


global _plugin
_plugin = SonoffEwelinkApi()


def onStart():
    global _plugin
    _plugin.on_start()


#def onStop():
#    global _plugin
#    _plugin.on_stop()


#def onConnect(Connection, Status, Description):
#    global _plugin
#    _plugin.on_connect(Connection, Status, Description)


#def onMessage(Connection, Data):
#    global _plugin
#    _plugin.on_message(Connection, Data)


def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.on_command(Unit, Command, Level, Hue)


# def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
#     global _plugin
#     _plugin.on_notification(Name, Subject, Text, Status, Priority, Sound, ImageFile)


#def onDisconnect(Connection):
#    global _plugin
#    _plugin.on_disconnect(Connection)


def onHeartbeat():
    global _plugin
    _plugin.on_heartbeat()


# Generic helper functions
def dump_config_to_log():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
        Domoticz.Debug("Device count: " + str(len(Devices)))
