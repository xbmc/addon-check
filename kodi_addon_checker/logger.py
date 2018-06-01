import logging
import logging.handlers


class Logger:

    @staticmethod
    def create_logger(debug_filename, logger_name):

        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s:%(name)s:%(funcName)s: %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')

        # DEBUG log to 'kodi-addon-checker.log'
        debug_log_handler = logging.handlers.RotatingFileHandler(debug_filename, encoding='utf-8', mode="w")
        debug_log_handler.setLevel(logging.DEBUG)
        debug_log_handler.setFormatter(formatter)
        logger.addHandler(debug_log_handler)

        return logger
