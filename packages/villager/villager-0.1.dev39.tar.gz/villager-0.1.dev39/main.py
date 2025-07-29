# -*- coding: utf-8 -*-
from init import init
from interfaces.boot import main
from tools.logging import logging, LoggingToSocket
from config import LOGGING, SERVER_UUID

if __name__ == '__main__':
    logging.set_logging_stream(LoggingToSocket(host=LOGGING['server'], port=int(LOGGING['port']), server_uuid=SERVER_UUID))
    init()
    main()
