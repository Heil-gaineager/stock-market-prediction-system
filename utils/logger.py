import logging


def setup_logger(name):
    """
    Set up a logger with a specified name.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Create a console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # Create a formatter and set it for the console handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    # Add the console handler to the logger
    logger.addHandler(ch)

    return logger
