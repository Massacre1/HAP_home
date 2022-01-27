from multiprocessing import freeze_support, Process

from inner_mid.clogger import clog
from lamps.controller import starter
from lamps.controllerESP import starterESP

coms = [
    (starter, 'Lamp 1', [200, 51826], False),
    (starter, 'Lamp 2', [202, 51827], True),
    (starterESP, 'Wemos 1', [256, 51829], True),
    (starter, 'Lamp 3', [204, 51824], True)
]

if __name__ == '__main__':
    if __name__ == '__main__':
        proc = {}
        clog('Pub started, fill your pint!')
        clog(str(len(coms)) + ' processes ready to start.', 1)
        freeze_support()
        for com in coms:
            clog('Process ' + str(com[1]) + " starting.", 1)
            # noinspection PyTypeChecker
            proc[com[1]] = Process(target=com[0], name=com[1], args=com[2])
        for com in coms:
            proc[com[1]].start()
            clog('Process ' + str(com[1]) + ' started.', 1)
        for com in coms:
            proc[com[1]].join()