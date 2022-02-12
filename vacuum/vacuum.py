from miio import DreameVacuumMiot
from miio.integrations.vacuum.dreame.dreamevacuum_miot import DeviceStatus
from pyhap import const
from pyhap.accessory import Accessory
from pyhap.accessory_driver import AccessoryDriver

from inner_mid.clogger import clog


class Vacuum:

    def __init__(self, addr_4):
        self.addr = addr_4
        self.vac = DreameVacuumMiot(f'192.168.0.{addr_4}',
                                   '327241466b697a4a626f6d6d54513377',
                                   model='dreame.vacuum.mc1808')

    def turn_on(self):
        self.vac.start()

    def turn_off(self):
        self.vac.home()

    def get_power(self):
        status = self.vac.status()
        if status.device_status == DeviceStatus(6):
            return False
        else:
            return True


class Vacuum_HAP(Accessory):
    power = False
    category = const.CATEGORY_FAN

    def __init__(self, addr_4, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bulb = Vacuum(addr_4=addr_4)
        serv = self.add_preload_service('Fan', chars=['On'])
        self.char_on = serv.configure_char('On',
                                           setter_callback=self.toggle_power,
                                           getter_callback=self.get_power)

    def toggle_power(self, value: bool):
        if value:
            self.power = True
            self.bulb.turn_on()
        else:
            self.power = False
            self.bulb.turn_off()

    def get_power(self):
        return self.bulb.get_power()


def starter(addr_4, port, name):
    driver = AccessoryDriver(port=port, persist_file=f'{name}.state')
    accessory = Vacuum_HAP(addr_4=addr_4, display_name='Vacuum', driver=driver)
    driver.add_accessory(accessory=accessory)
    driver.start()

