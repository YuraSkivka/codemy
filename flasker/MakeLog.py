import logging


class MakeLog:
    logger = logging.getLogger()

    c_handler = logging.StreamHandler()
    c_format = logging.Formatter("%(levelname)s - %(name)s - %(filename)s - %(message)s")
    logger.addHandler(c_handler)

    # logger.setLevel(logging.DEBUG)  # or whatever
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('file.log', 'a', 'utf-8')  # or whatever
    handler.setFormatter(
        logging.Formatter(u"%(asctime)s : %(levelname)s - %(name)s - %(filename)s - %(message)s"))  # or whatever
    logger.addHandler(handler)
