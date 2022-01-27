import json
from queue import Queue
from threading import Thread

import requests
from pyhap import const
from pyhap.accessory import Accessory
from pyhap.accessory_driver import AccessoryDriver

from inner_mid.clogger import clog


def _status(host):
    try:
        response = requests.get(url=host, timeout=3)
    except Exception as e:
        _ = e
        return False
    else:
        return True, response.content


def _discover(host_queue: Queue, result_queue: Queue):
    while not host_queue.empty():
        url = host_queue.get_nowait()
        url_status = _status(url + 'discover')
        result_queue.put_nowait((url, url_status))
        host_queue.task_done()


def discover():
    host_queue = Queue()
    result_queue = Queue()
    thread_count = 256

    for addr_4 in range(256):
        host_queue.put(f'http://192.168.0.{addr_4}/')

    for i in range(thread_count):
        thread = Thread(target=_discover, args=(host_queue, result_queue))
        thread.daemon = True
        thread.start()

    host_queue.join()
    response = []
    while not result_queue.empty():
        line = result_queue.get_nowait()
        if line[1]:
            response.append(line)
    return response


class BulbLampESP:

    def __init__(self, addr_4):
        self.addr = addr_4

    def turn_on(self):
        requests.post(self.addr, json={'power': True})

    def turn_off(self):
        requests.post(self.addr, json={'power': False})

    def HSV(self, **request):
        requests.post(self.addr, json=request)

    def props_(self, prop):
        value = requests.get(self.addr + 'prop')
        value = json.loads(value.content)
        return value[prop]


class LightESP(Accessory):
    hue = 0
    sat = 0
    power = False
    temperature = 400
    category = const.CATEGORY_LIGHTBULB
    bright = 100.0

    def __init__(self, addr_4, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bulb = BulbLampESP(addr_4=addr_4)
        serv = self.add_preload_service('Lightbulb', chars=['On', 'Hue', 'Saturation', 'Brightness'])
        self.char_on = serv.configure_char('On',
                                           setter_callback=self.toggle_power,
                                           getter_callback=self.get_power)
        self.char_hue = serv.configure_char('Hue',
                                            setter_callback=self.set_hue,
                                            getter_callback=self.get_hue)
        self.char_saturation = serv.configure_char('Saturation',
                                                   setter_callback=self.set_sat,
                                                   getter_callback=self.get_sat)
        self.char_brightness = serv.configure_char('Brightness',
                                                   setter_callback=self.set_bright,
                                                   getter_callback=self.get_bright)
        self.power = self.bulb.props_('power')

    def toggle_power(self, value: bool):
        if value:
            self.power = True
            self.bulb.turn_on()
        else:
            self.power = False
            self.bulb.turn_off()

    def get_power(self):
        return self.power

    def set_hue(self, value):
        self.bulb.HSV(hue=value)
        self.hue = value

    def get_hue(self):
        return self.hue

    def get_bright(self):
        return self.bright

    def set_bright(self, value):
        self.bulb.HSV(bright=value / 200)
        self.bright = value

    def set_sat(self, value):
        print(value)
        self.bulb.HSV(sat=value)
        self.sat = value

    def get_sat(self):
        return self.sat


def starter(addr_4, port, name):
    driver = AccessoryDriver(port=port, persist_file=f'{name}.state')
    accessory = LightESP(addr_4=addr_4, display_name='Lightbulb', driver=driver)
    driver.add_accessory(accessory=accessory)
    driver.start()


def starterESP(addr_4, port):
    all_ = discover()
    print(all_)
    for addr in all_:
        if addr[1][1] == b'wemos':
            while True:
                try:
                    starter(addr[0], port=port, name=addr_4)
                except Exception as e:
                    clog(e)
