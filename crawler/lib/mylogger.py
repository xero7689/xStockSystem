import os
import logging
from logging.handlers import SMTPHandler
from logging.handlers import RotatingFileHandler
import time

#PROJECT_DIR = os.path.abspath(os.path.join(os.path.pardir, '..'))
PROJECT_DIR = os.path.abspath('../')
DEFAULT_LOG_DIR = os.path.join(PROJECT_DIR, 'log/')

loggers = {}

def MyLogger(name='__name__', prefix=None, log_dir_path=DEFAULT_LOG_DIR, debug_level=logging.DEBUG):
    global loggers
    if loggers.get(name):
        return loggers.get(name)

    _LOGGING_LEVEL = debug_level
    logger = logging.getLogger(name)

    log_fn = time.strftime("%Y_%m") + ".log"
    if prefix:
        log_fn = prefix + "_" + log_fn
    else:
        log_fn = name + "_" + log_fn

    if log_dir_path:
        if not os.path.isdir(log_dir_path):
            os.mkdir(log_dir_path)
        log_fn = os.path.join(log_dir_path, log_fn)
    
    logger.setLevel(_LOGGING_LEVEL)

    # Mail handler
    """
    mail_handler = SMTPHandler(
            mailhost = "mail.lionic.com",
            fromaddr = "peter.lee@lionic.com",
            toaddrs = "peter.lee@lionic.com",
            subject = '[*] Unhandle Exception {}'.format(prefix)
            )
    mail_handler.setLevel(logging.ERROR)
    logger.addHandler(mail_handler)
    """

    # Set global formatter
    format_string = "%(asctime)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(format_string)
    
    # Stream handler(stdout?)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)
    
    # File handler
    #file_handler = logging.FileHandler(log_fn)
    #file_handler.setFormatter(formatter)
    #logger.addHandler(file_handler)

    # Rotating File Handler
    r_handler = RotatingFileHandler(log_fn, maxBytes=1024*5, backupCount=5)
    logger.addHandler(r_handler)

    # Add handler to logger
    logger.addHandler(stream_handler)

    loggers[name] = logger
    return logger
