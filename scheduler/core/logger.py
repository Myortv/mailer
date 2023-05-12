import queue

import logging
from logging.handlers import QueueHandler
from logging.handlers import QueueListener
from logging.handlers import RotatingFileHandler
from logging import StreamHandler

from scheduler.core.configs import settings

INIT_ME_FIRST = None


FORMAT_WITH_SUBS = '{levelname}:{asctime} {module}\t\t{field}:{fieldvalue}\t<{subfield}:{subfieldvalue}>\t\t\t\t{message}'

defaults = {
    'field': 'NoN',
    'fieldvalue': 'NoN',
    'subfield': 'NoN',
    'subfieldvalue': 'NoN',
}

file_formatter = logging.Formatter(
    fmt=FORMAT_WITH_SUBS, 
    defaults=defaults, 
    style='{'
)

log_queue = queue.Queue()
queue_handler = QueueHandler(log_queue)
queue_handler.setFormatter(file_formatter)
queue_handler.setLevel(logging.DEBUG)

filelogger = logging.getLogger('filelogger')
filelogger.addHandler(queue_handler)
filelogger.setLevel(logging.DEBUG)

file_rotation_handler = RotatingFileHandler(
    settings.LOGGING_FILE,
    maxBytes=1048576,
    backupCount=5,
)

queue_listener = QueueListener(
    log_queue,
    file_rotation_handler,
)
queue_listener.start()

def printt(
    msg: str,
    placeholder: str = '-'*20,
):
    print(f'\t\t\t{placeholder} {msg.upper()} {placeholder}')
