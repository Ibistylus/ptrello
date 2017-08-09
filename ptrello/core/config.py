#!/usr/bin/env python
import logging
import logging.config
import yaml
import sys
import os


logger = logging.getLogger("ptrello."+__name__)
logger.setLevel("DEBUG")
#LogLevel = logging.WARNING
#logging.basicConfig(level=LogLevel)

user_path = os.path.realpath("/etc/")
user_project_path = os.path.realpath("/etc/ptrello/")
cur_rel_path = os.path.relpath(os.path.join(os.path.dirname(__file__), "/../../etc/"))
cur_abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..\\", "..\\", "etc"))
env_var = os.environ.get("BOILERFIDDLER_CONF") or ""
settings = None
locations = [os.curdir, user_path, user_project_path, cur_rel_path, cur_abs_path, env_var]


def logging_configuration(config=None):

    if not config:
        for loc in locations:
            path = (os.path.join(os.path.join(loc,"ptrello.ini")))

            try:
                if os.path.isfile(path):
                    logging.config.fileConfig(os.path.join(loc,"ptrello.ini"), disable_existing_loggers=True) #, disable_existing_loggers=False

                    # logger.debug(str(os.path.exists(loc)) + " folder exists: " + str(os.path.isfile(path)) + " file exists: " + path )

            except IOError:
                logger.warning("A log ini file was not found")
                logging.basicConfig(level=logging.WARNING)
                pass
    else:
        logging.basicConfig(level=logging.WARNING)

    pass



def settings_configuration():

    for loc in locations:
        path = (os.path.join(os.path.join(loc, "ptrello_settings.yaml")))

        try:
            if os.path.isfile(path):

                with open(path, "r") as f:

                    settings = yaml.load(f)
                    # logger.debug(str(os.path.exists(loc)) + " folder exists: " + str(os.path.isfile(path)) + " file exists: " + path)

                    return settings
        except IOError as e:
            logger.warning("A log configuration was not found {}".format(e.args))
            raise e

logging_configuration()
settings = settings_configuration()

if settings is None:
    raise IOError("ptrello_settings.yaml was not found in the follow locations {}".format(locations))

logger.debug("Settings and logs configured")
