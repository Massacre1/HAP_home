import datetime

type_options = {  # определение цветов для разных видов информации
    0: ['INFO: ', '\33[0m\33[37m'],
    1: ['SYSTEM: ', '\33[0m\33[33m'],
    2: ['ERROR: ', '\33[0m\33[31m']

}


def clog(data, data_type: int = 0):
    '''
    Вывод данных в консоль с временем и типом информации, отмеченных цветом.

    :param data: Строка для отображения.
    :param data_type: Тип данных:
    0 - По умолчанию. Информационные сообщения.
    1 - Системная информация.
    2 - Отображение ошибок.
    '''
    data = str(data)
    options = type_options[data_type]
    msg = str(datetime.datetime.now()) + ' - ' + options[0] + str(data)
    print(msg)
