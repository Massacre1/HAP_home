from fastapi import HTTPException
EVERY_HEADERS = {'Access-Control-Allow-Origin': '*'}


def check_file_name(
        processable_string: str
):
    '''
    Проверка строки на запрещенный для имен файлов символы.

    :param processable_string: Проверяемая строка.
    :return: Строка без символов, запрещенных в именах файлов.
    '''
    if type(processable_string) != str:
        raise HTTPException(status_code=422, detail='empty query', headers=EVERY_HEADERS)
    chars = '/\:*? «<>|'
    for c in chars:
        processable_string = processable_string.replace(c, ' ')
        response = processable_string.strip()
    if response == '':
        raise HTTPException(status_code=422, detail='invalid query', headers=EVERY_HEADERS)
    return response
