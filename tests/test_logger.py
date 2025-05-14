import logging

logger = logging.getLogger("astrodb_utils") 

def test_logger():    
    print("Logger name:", logger.name)
    print("Logger level:", logger.level)
    print("Logger levelname:", logging.getLevelName(logger.getEffectiveLevel()))
    logger.critical("This is a critical message")
    logger.error("This is an error message")
    logger.warning("This is a warning message")
    logger.info("This is an info message")
    logger.debug("This is a debug message")
    logger.exception("This is an exception message")
    
