# TCP сервер, распознающий заданный формат данных #

## Задача ##

Необходимо сделать tcp сервер, который распознаёт заданный формат данных и отображает его в требуемом формате. Обязательна запись данных во внешний файл. Интерфейс и способ отображения на выбор разработчика.

Формат данных `BBBBxNNxHH:MM:SS.zhqxGGCR`

- `BBBB` - номер участника
- `x` - пробельный символ
- `NN` - id канала
- `HH` - Часы
- `MM` - минуты
- `SS` - секунды
- `zhq` - десятые сотые тысячные
- `GG` - номер группы
- `CR` - «возврат каретки» (закрывающий символ)

Пример данных:
`0002 C1 01:13:02.877 00[CR]`
Вывод: `спортсмен, нагрудный номер BBBB прошёл отсечку
NN в «время»` до десятых, сотые и тысячные отсекаются. Только для группы `00`. Для остальных групп данные не отображаются, но пишутся в лог полностью

Язык Python, версия не ниже 3.2, не выше 3.8.
Передача данных должна поддерживаться с помощью telnet клиента.

## Решение ##

Скрипт использует синхронный TCP-сервер, после получения данных закрывает соединение и ждёт следующего. Все полученные данные записываются в log-файл `competitors.log`: валидные в формате `json`, невалидные в виде строк.

### Пример лог-файла ###

  ```
  2021-08-16 15:31:26,668 WARNING:INVALID hello
  2021-08-16 15:31:28,890 WARNING:INVALID world
  2021-08-16 15:31:41,332 INFO:{"competitor_number": "0003", "channel_id": "G2", "hours": "01", "minutes": "13", "seconds": "03", "tenths": "8", "hundredths": "7", "thousandths": "7", "group_number": "01"}
  2021-08-16 15:31:47,307 INFO:{"competitor_number": "0002", "channel_id": "C1", "hours": "01", "minutes": "13", "seconds": "02", "tenths": "8", "hundredths": "7", "thousandths": "7", "group_number": "00"}

  ```

### Пример вывода на экран ###

  ```
  Server started at 0.0.0.0:9000
  CTRL+C to stop server
  спортсмен, нагрудный номер 0002 прошёл отсечку G1 в 02:16:01.0
  Server stopped
  ```


## Установка и запуск ##
0. Установите, если нужно, переменные окружения HOST и PORT (по-умолчанию `0.0.0.0:9000`)

1. Скачайте код и перейдите в папку проекта.
    ```bash
    git clone https://github.com/n1k0din/checkpoints-handler.git
    ```  
    ```bash
    cd checkpoints-handler
    ```

2. Запустите сервер.
    ```bash
    python3 checkpoints_handler.py
    ```