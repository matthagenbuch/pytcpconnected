__author__ = 'hagenbuch'

import requests
import xml.etree.ElementTree as ET
import urllib.parse as url
import logging


class TcpController:
    def __init__(self, host):
        # populate the individual lights (assumes single room)
        self.host = host
        self.lights = {}
        self.logger = logging.getLogger(__name__)

    def get_lights(self):
        try:
            response = requests.get(make_request(self.host, BATCH_CMD, SCAN_DATA))
            root = ET.fromstring(response.text)
            for device in root.iter('device'):
                light_info = {e.tag: e.text for e in device.getiterator()}
                self.lights['did'] = light_info

        except requests.exceptions.RequestException:
            self.logger.error("Scan request to gateway failed!")

        return self.lights

    def turn_on(self, did):
        return self._set_state(did, '1')

    def turn_off(self, did):
        return self._set_state(did, '0')

    def _set_state(self, did, value):
        try:
            response = requests.post(
                make_request(self.host),
                POST_FORMAT.format(
                    cmd=DEV_CMD,
                    data=STATE_DATA_FORMAT.format(
                        did=did,
                        value=value
                    ),
                    fmt=DATA_FMT
                ))
            if response.status_code == 200:
                return True
            else:
                self.logger.error("Gateway refused request set light state.  Status code = "
                                  + str(response.status_code))
                return False

        except requests.exceptions.RequestException:
            self.logger.error("Request to set light state failed!")
            return False

    def set_brightness(self, did, value):
        try:
            response = requests.post(
                make_request(self.host),
                POST_FORMAT.format(
                    cmd=DEV_CMD,
                    data=BRIGHTNESS_DATA_FORMAT.format(
                        did=did,
                        value=value
                    ),
                    fmt=DATA_FMT
                ))
            if response.status_code == 200:
                return True
            else:
                self.logger.error("Gateway refused request set light brightness.  Status code = "
                                  + str(response.status_code))
                return False

        except requests.exceptions.RequestException:
            self.logger.error("Request to set light brightness failed!")
            return False


def make_request(hostname, command_type=None, data=None):
    command = ''
    if command_type is not None and data is not None:
        data = data.strip().replace('\n', '').replace(' ', '').replace('\t', ' ')
        command = "?" + url.urlencode({'cmd': command_type, 'data': data, 'fmt': DATA_FMT})
    return REQUEST_FORMAT.format(
        hostname=hostname,
        cmd=command)

BATCH_CMD = 'GWRBatch'

DEV_CMD = 'DeviceSendCommand'

DATA_FMT = 'xml'

SCAN_DATA = \
    '''
    <gwrcmds>
        <gwrcmd>
            <gcmd>RoomGetCarousel</gcmd>
            <gdata>
                <gip>
                    <version>1</version>
                    <token>1234567890</token>
                    <fields>
                        name,
                        control,
                        power,
                        product,
                        class,
                        realtype,
                        status
                    </fields>
                </gip>
            </gdata>
        </gwrcmd>
    </gwrcmds>
    '''

STATE_DATA_FORMAT = \
    '''
    <gip>
        <version>1</version>
        <token>1234567890</token>
        <did>{did}</did>
        <value>{value}</value>
    </gip>
    '''

BRIGHTNESS_DATA_FORMAT = \
    '''
    <gip>
        <version>1</version>
        <token>1234567890</token>
        <did>{did}</did>
        <value>{value}</value>
        <type>level</type>
    </gip>
    '''

REQUEST_FORMAT = "http://{hostname}/gwr/gop.php{cmd}"

POST_FORMAT = "cmd={cmd}&data{data}=&fmt={fmt}"