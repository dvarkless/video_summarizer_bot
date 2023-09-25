import logging
import logging.handlers


def get_handler():
    handler = logging.handlers.RotatingFileHandler(
        'log.log', maxBytes=3*1024*1024, backupCount=3)
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s in %(name)s: %(levelname)s MESSAGE:'%(message)s")

    handler.setFormatter(formatter)

    return handler
