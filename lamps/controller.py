from pyhap import const
from pyhap.accessory import Accessory
from pyhap.accessory_driver import AccessoryDriver
from yeelight import Bulb, LightType

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

    def props_(self, prop):
        value = self.bulb.get_properties(requested_properties=[prop])
        return value[prop]


class RGBBulb(Accessory):
    brightness = 100
    power = False
    hsv = (320, 100)


class BulbLampESP:
    hue = 360
    sat = 100

    def __init__(self, addr_4):
        self.addr = f'192.168.0.{addr_4}'
        self.bulb = Bulb(self.addr, effect='smooth', duration=1000, auto_on=False)

    def turn_on(self):
        self.bulb.turn_on(light_type=LightType.Ambient)

    def turn_off(self):
        self.bulb.turn_off(light_type=LightType.Ambient)

    def HSV(self, hue=hue, sat=sat):
        self.bulb.set_hsv(light_type=LightType.Ambient, hue=hue, saturation=sat)

    def set_brightness(self, value):
        self.bulb.set_brightness(value, light_type=LightType.Ambient)

    def props_(self, prop):
        value = self.bulb.get_properties(requested_properties=[prop])
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
        self.bulb_rgb = BulbLampESP(addr_4=addr_4)
        rgb = self.add_preload_service('LightbulbRGB', chars=['On', 'Hue', 'Saturation', 'Brightness'])
        self.char_on = rgb.configure_char('On',
                                          setter_callback=self.toggle_power_rgb,
                                          getter_callback=self.get_power_rgb)
        self.char_hue_rgb = rgb.configure_char('Hue',
                                               setter_callback=self.set_hue_rgb,
                                               getter_callback=self.get_hue_rgb)
        self.char_saturation_rgb = rgb.configure_char('Saturation',
                                                      setter_callback=self.set_sat_rgb,
                                                      getter_callback=self.get_sat_rgb)
        self.char_brightness_rgb = rgb.configure_char('Brightness',
                                                      setter_callback=self.set_bright_rgb,
                                                      getter_callback=self.get_bright_rgb)
        self.power_rgb = self.bulb_rgb.props_('power')

    def toggle_power_rgb(self, value: bool):
        if value:
            self.power = True
            self.bulb_rgb.turn_on()
        else:
            self.power = False
            self.bulb_rgb.turn_off()

    def get_power_rgb(self):
        return self.power

    def set_hue_rgb(self, value):
        self.bulb_rgb.HSV(hue=value)
        self.hue = value

    def get_hue_rgb(self):
        return self.hue

    def get_bright_rgb(self):
        return self.bright

    def set_bright_rgb(self, value):
        self.bulb_rgb.set_brightness(value)
        self.bright = value

    def set_sat_rgb(self, value):
        print(value)
        self.bulb_rgb.HSV(sat=value)
        self.sat = value

    def get_sat_rgb(self):
        return self.sat


class Lightbulb(Accessory):
    brightness = 100
    power = False
    temperature = 400
    category = const.CATEGORY_LIGHTBULB
    hue = 360
    bright = 100
    sat = 100

    def __init__(self, addr_4, rgb, *args, **kwargs):
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
        if rgb:
            self.bulb_rgb = BulbLampESP(addr_4=addr_4)
            rgb = self.add_preload_service('Lightbulb', chars=['On', 'Hue', 'Saturation', 'Brightness'])
            self.char_on = rgb.configure_char('On',
                                              setter_callback=self.toggle_power_rgb,
                                              getter_callback=self.get_power_rgb)
            self.char_hue_rgb = rgb.configure_char('Hue',
                                                   setter_callback=self.set_hue_rgb,
                                                   getter_callback=self.get_hue_rgb)
            self.char_saturation_rgb = rgb.configure_char('Saturation',
                                                          setter_callback=self.set_sat_rgb,
                                                          getter_callback=self.get_sat_rgb)
            self.char_brightness_rgb = rgb.configure_char('Brightness',
                                                          setter_callback=self.set_bright_rgb,
                                                          getter_callback=self.get_bright_rgb)
            self.power_rgb = self.bulb_rgb.props_('power')

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

    def toggle_power_rgb(self, value: bool):
        if value:
            self.power = True
            self.bulb_rgb.turn_on()
        else:
            self.power = False
            self.bulb_rgb.turn_off()

    def get_power_rgb(self):
        return self.power

    def set_hue_rgb(self, value):
        self.bulb_rgb.HSV(hue=value)
        self.hue = value

    def get_hue_rgb(self):
        return self.hue

    def get_bright_rgb(self):
        return self.bright

    def set_bright_rgb(self, value):
        self.bulb_rgb.set_brightness(value)
        self.bright = value

    def set_sat_rgb(self, value):
        print(value)
        self.bulb_rgb.HSV(sat=value)
        self.sat = value

    def get_sat_rgb(self):
        return self.sat


def starter(addr_4, port, rgblamp):
    while True:
        try:
            driver = AccessoryDriver(port=port, persist_file=f'{addr_4}.state')
            accessory = Lightbulb(addr_4=addr_4, display_name='Lightbulb', driver=driver, rgb=rgblamp)

            driver.add_accessory(accessory=accessory)
            # if RGBlamp:
            #     accessory = LightESP(addr_4=addr_4, display_name='RGB_bulb', driver=driver)
            #     driver.add_accessory(accessory=accessory)
            driver.start()
        except Exception as e:
            clog(str(e))
