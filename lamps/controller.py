from pyhap import const
from pyhap.accessory import Accessory
from pyhap.accessory_driver import AccessoryDriver
from yeelight import Bulb

from inner_mid.clogger import clog


class BulbLamp:

    def __init__(self, addr_4):
        self.addr = f'192.168.0.{addr_4}'
        self.bulb = Bulb(self.addr, effect='smooth', duration=1000, auto_on=False)

    def turn_on(self):
        self.bulb.turn_on()

    def turn_off(self):
        self.bulb.turn_off()

    def set_brightness(self, value):
        self.bulb.set_brightness(value)

    def set_hue(self):
        self.bulb.set_color_temp()

    def set_c_temp(self, value):
        old_range = (500 - 140)
        new_range = (5700 - 2700)
        new_value = (((old_range - (value - 140)) * new_range) / old_range) + 2700
        self.bulb.set_color_temp(new_value)

    def HSV(self, hue, sat):
        self.bulb.set_hsv(hue, sat)

    def props_(self, prop):
        value = self.bulb.get_properties(requested_properties=[prop])
        return value[prop]


class RGBBulb(Accessory):
    brightness = 100
    power = False
    hsv = (320, 100)


class Lightbulb(Accessory):
    brightness = 100
    power = False
    temperature = 400
    category = const.CATEGORY_LIGHTBULB

    def __init__(self, addr_4, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bulb = BulbLamp(addr_4=addr_4)
        serv = self.add_preload_service('Lightbulb', chars=['On', 'Brightness', 'ColorTemperature'])
        self.char_on = serv.configure_char('On',
                                           setter_callback=self.toggle_power,
                                           getter_callback=self.get_power)
        self.char_brightness = serv.configure_char('Brightness',
                                                   setter_callback=self.set_brightness,
                                                   getter_callback=self.get_brightness)
        self.char_color_temp = serv.configure_char('ColorTemperature',
                                                   setter_callback=self.set_temp,
                                                   getter_callback=self.get_temp)
        self.brightness = int(self.bulb.props_('bright'))
        self.power = True if self.bulb.props_('power') == u'on' else False

    def toggle_power(self, value: bool):
        if value:
            self.power = True
            self.bulb.turn_on()
            self.bulb.set_brightness(self.brightness)
            self.bulb.set_c_temp(self.temperature)
        else:
            self.power = False
            self.bulb.turn_off()

    def get_power(self):
        return self.power

    def set_brightness(self, value):
        self.bulb.set_brightness(value)
        self.brightness = value

    def get_brightness(self):
        return self.brightness

    def set_temp(self, value):
        self.bulb.set_c_temp(value)
        self.temperature = value

    def get_temp(self):
        return self.temperature


def starter(addr_4, port):
    while True:
        try:
            driver = AccessoryDriver(port=port, persist_file=f'{addr_4}.state')
            accessory = Lightbulb(addr_4=addr_4, display_name='Lightbulb', driver=driver)
            driver.add_accessory(accessory=accessory)
            driver.start()
        except Exception as e:
            clog(str(e))
