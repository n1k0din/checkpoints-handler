"""
Необходимо сделать tcp сервер, который распознаёт заданный формат данных и отображает его в
требуемом формате. Обязательна запись данных во внешний файл. Интерфейс и способ отображения на
выбор разработчика.

Формат данных BBBBxNNxHH:MM:SS.zhqxGGCR Где
BBBB - номер участника
x - пробельный символ
NN - id канала
HH - Часы
MM - минуты
SS - секунды
zhq - десятые сотые тысячные
GG - номер группы
CR - «возврат каретки» (закрывающий символ)

Пример данных: 0002 C1 01:13:02.877 00[CR] Выводим «спортсмен, нагрудный номер BBBB прошёл отсечку
NN в «время»" до десятых, сотые и тысячные отсекаются. Только для группы 00.
Для остальных групп данные не отображаются, но пишутся в лог полностью.

Язык Python, версия не ниже 3.2, не выше 3.8.
Передача данных должна поддерживаться с помощью telnet клиента.
"""
import json
import logging
import os
import re
import socketserver
import threading
from collections import namedtuple

Datagram = namedtuple(
    'Datagram',
    [
        'competitor_number',
        'channel_id',
        'hours',
        'minutes',
        'seconds',
        'tenths',
        'hundredths',
        'thousandths',
        'group_number',
    ]
)


class CheckpointsHandler(socketserver.StreamRequestHandler):
    def handle(self):
        try:
            input = self.rfile.readline().decode('ascii')
        except UnicodeDecodeError as error:
            logging.debug(error)

        if is_datagram_valid(input):
            datagram = datagram_parse(input)
            dump_datagram(datagram)

            if filter_by_group(datagram):
                print_datagram(datagram)
        else:
            dump_invalid_data(input)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


def is_datagram_valid(datagram_string):
    pattern = re.compile(r'\d{4}\s.{2}\s\d{2}:\d{2}:\d{2}\.\d{3}\s\d{2}\r$')
    return bool(pattern.match(datagram_string))


def datagram_parse(datagram_string):
    competitor_number, channel_id, time, group_number = datagram_string.rstrip().split()
    hhmmss, zhq = time.split('.')
    hours, minutes, seconds = hhmmss.split(':')
    tenths, hundredths, thousandths = zhq

    return Datagram(
        competitor_number,
        channel_id,
        hours,
        minutes,
        seconds,
        tenths,
        hundredths,
        thousandths,
        group_number,
    )


def print_datagram(datagram):
    template = 'спортсмен, нагрудный номер {} прошёл отсечку {} в {}:{}:{}.{}'
    print(template.format(
        datagram.competitor_number,
        datagram.channel_id,
        datagram.hours,
        datagram.minutes,
        datagram.seconds,
        datagram.tenths,
    ))


def dump_datagram(datagram):
    logging.info(json.dumps(datagram._asdict()))


def dump_invalid_data(invalid_string):
    logging.warning('INVALID %s', invalid_string.strip())


def filter_by_group(datagram, group_number='00'):
    return datagram.group_number == group_number


def main():
    global _FINISH

    logfilename = 'competitors.log'
    logging.basicConfig(
        filename=logfilename,
        format='%(asctime)s %(levelname)s:%(message)s',
        level=logging.INFO,
    )

    port = int(os.environ.get('PORT', 9000))
    host = os.environ.get('HOST', '0.0.0.0')

    try:
        with ThreadedTCPServer((host, port), CheckpointsHandler) as server:
            print(f'Server started at {host}:{port}')
            print('CTRL+C to stop server')
            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            server_thread.join()
    except KeyboardInterrupt:
        print('Server stopped')
        server.shutdown()
        return


if __name__ == '__main__':
    main()
