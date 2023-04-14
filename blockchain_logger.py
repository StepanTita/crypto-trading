import logging

from common.utils import grey, cyan, yellow, red, bold

logger = logging.getLogger('blockchain')


class CustomFormatter(logging.Formatter):
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    reset = '\033[0m'

    FORMATS = {
        logging.DEBUG: grey(format) + reset,
        logging.INFO: cyan(format) + reset,
        logging.WARNING: yellow(format) + reset,
        logging.ERROR: red(format) + reset,
        logging.CRITICAL: bold(red(format)) + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


wh = logging.StreamHandler()
wh.setLevel(logging.WARN)

eh = logging.StreamHandler()
eh.setLevel(logging.ERROR)
# create formatter and add it to the handlers
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

dh = logging.StreamHandler()
dh.setLevel(logging.DEBUG)

dh.setFormatter(CustomFormatter())

# link handler to logger
logger.addHandler(dh)

# Set logging level to the logger
logger.setLevel(logging.DEBUG)
