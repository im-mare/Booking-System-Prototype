import logging

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    file_handler = logging.FileHandler(str(name)+".log")
    
    logging_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    file_handler.setFormatter(logging_formatter)
    
    logger.addHandler(file_handler)
    
    return logger