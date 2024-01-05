# Importing libraries
import os
import time

# Importing modules
from logging import getLogger, Formatter, INFO, WARNING, ERROR
from logging.handlers import TimedRotatingFileHandler 

# Creating a customized logger
class CustomTimedRotatingFileHandler(TimedRotatingFileHandler):
    """
    Custom handler that extends TimedRotatingFileHandler to rename log files with a date format
    after rollover occurs.
    """
    def doRollover(self):
        """
        Perform a rollover, during which the current log file is closed, renamed with a timestamp,
        and a new log file is opened.
        """
        current_log_filename = self.baseFilename
        super().doRollover()
        
        date_format = '%d.%m.%Y'
        new_log_filename = time.strftime(date_format, time.localtime()) + "_" + os.path.basename(current_log_filename)
        os.rename(current_log_filename, os.path.join('logs/old-logs'), new_log_filename)


# Creating a logger's
def setup_loggers():
    """
    Set up and configure multiple loggers for different purposes.

    Returns:
        tuple: A tuple containing all configured logger instances.
    """
    log_formatter = '%(asctime)s [%(levelname)s] - [%(filename)s] - %(message)s'
    date_formatter = '%H:%M:%S | %d-%m-%Y'
    
    # Setting up a logger for the server
    run_logger = getLogger('run_logger')
    req_logger = getLogger('req_logger')
    db_logger = getLogger('db_logger')
    check_logger = getLogger('check_logger')
    func_logger = getLogger('func_logger')
    warn_logger = getLogger('warn_logger')
    err_logger = getLogger('err_logger')
    bot_logger = getLogger('bot_logger')
    # Setting up level for the server's logger
    run_logger.setLevel(INFO)
    req_logger.setLevel(INFO)
    db_logger.setLevel(INFO)
    check_logger.setLevel(INFO)
    func_logger.setLevel(INFO)
    warn_logger.setLevel(WARNING)
    err_logger.setLevel(ERROR)
    bot_logger.setLevel(INFO)
    # Setting up a handler for the server's logger
    if not run_logger.hasHandlers():
        run_handler = CustomTimedRotatingFileHandler(
            filename='logs/run-server.log', when='midnight', interval=2, backupCount=30, encoding='utf-8')
        run_handler.setFormatter(Formatter(log_formatter, datefmt=date_formatter))
        run_logger.addHandler(run_handler)
    if not req_logger.hasHandlers():
        req_handler = CustomTimedRotatingFileHandler(
            filename='logs/requests.log', when='midnight', interval=2, backupCount=30, encoding='utf-8')
        req_handler.setFormatter(Formatter(log_formatter, datefmt=date_formatter))
        req_logger.addHandler(req_handler)
    if not db_logger.hasHandlers():
        db_handler = CustomTimedRotatingFileHandler(
            filename='logs/db-requests.log', when='midnight', interval=2, backupCount=30, encoding='utf-8')
        db_handler.setFormatter(Formatter(log_formatter, datefmt=date_formatter))
        db_logger.addHandler(db_handler)
    if not check_logger.hasHandlers():
        check_handler = CustomTimedRotatingFileHandler(
            filename='logs/check-requests.log', when='midnight', interval=2, backupCount=30, encoding='utf-8')
        check_handler.setFormatter(Formatter(log_formatter, datefmt=date_formatter))
        check_logger.addHandler(check_handler)
    if not func_logger.hasHandlers():
        func_handler = CustomTimedRotatingFileHandler(
            filename='logs/func-requests.log', when='midnight', interval=2, backupCount=30, encoding='utf-8')
        func_handler.setFormatter(Formatter(log_formatter, datefmt=date_formatter))
        func_logger.addHandler(func_handler)
    if not warn_logger.hasHandlers():
        warn_handler = CustomTimedRotatingFileHandler(
            filename='logs/warn-requests.log', when='midnight', interval=2, backupCount=30, encoding='utf-8')
        warn_handler.setFormatter(Formatter(log_formatter, datefmt=date_formatter))
        warn_logger.addHandler(warn_handler)
    if not err_logger.hasHandlers():
        err_handler = CustomTimedRotatingFileHandler(
            filename='logs/err-requests.log', when='midnight', interval=2, backupCount=30, encoding='utf-8')
        err_handler.setFormatter(Formatter(log_formatter, datefmt=date_formatter))
        err_logger.addHandler(err_handler)
    if not bot_logger.hasHandlers():
        bot_handler = CustomTimedRotatingFileHandler(
            filename='logs/bot-requests.log', when='midnight', interval=2, backupCount=30, encoding='utf-8')
        bot_handler.setFormatter(Formatter(log_formatter, datefmt=date_formatter))
        bot_logger.addHandler(bot_handler)
    
    return run_logger, req_logger, db_logger, check_logger, func_logger, warn_logger, err_logger, bot_logger


# * Starting a logger's
run_logger, req_logger, db_logger, check_logger, func_logger, warn_logger, err_logger, bot_logger = setup_loggers()

# * Creating a logger's
def run_log(message):
    """
    Log a message with the severity 'INFO' using the 'run_logger'.

    Parameters:
        message (str): The message to be logged.
    """
    run_logger.info(message)

def req_log(message):
    """
    Log a message with the severity 'INFO' using the 'req_logger'.

    Parameters:
        message (str): The message to be logged.
    """
    req_logger.info(message)

def db_log(message):
    """
    Log a message with the severity 'INFO' using the 'db_logger'.

    Parameters:
        message (str): The message to be logged.
    """
    db_logger.info(message)

def check_log(message):
    """
    Log a message with the severity 'INFO' using the 'check_logger'.

    Parameters:
        message (str): The message to be logged.
    """
    check_logger.info(message)

def func_log(message):
    """
    Log a message with the severity 'INFO' using the 'func_logger'.

    Parameters:
        message (str): The message to be logged.
    """
    func_logger.info(message)

def warn_log(message):
    """
    Log a message with the severity 'WARNING' using the 'warn_logger'.

    Parameters:
        message (str): The message to be logged.
    """
    warn_logger.warning(message)

def err_log(message):
    """
    Log a message with the severity 'ERROR' using the 'err_logger'.

    Parameters:
        message (str): The message to be logged.
    """
    err_logger.error(message)

def bot_log(message):
    """
    Log a message with the severity 'INFO' using the 'bot_logger'.

    Parameters:
        message (str): The message to be logged.
    """
    bot_logger.info(message)
