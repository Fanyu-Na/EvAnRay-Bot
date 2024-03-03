import logging
import logging.config

logging.config.fileConfig("conf/logging.ini")
log = logging.getLogger("root")