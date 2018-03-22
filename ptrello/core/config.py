#!/usr/bin/env python
import logging
import logging.config
import yaml
import os


logger = logging.getLogger("ptrello."+__name__)
logger.setLevel("DEBUG")

# Check environment variable first:
env_var = os.environ.get("PTRELLO") or ""

# Check home directory second
user_path = os.path.join(os.path.expanduser('~'), ".config/ptrello/")

# Check project path last
user_project_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../etc")

settings = None

locations = [env_var, os.curdir, user_path, user_project_path]

def logging_configuration(config=None):

    if not config:
        for loc in locations:
            path = (os.path.join(os.path.join(os.path.normpath(loc), "ptrello.ini")))

            try:
                if os.path.isfile(path):
                    logging.config.fileConfig(path)
            except IOError:
                pass

    else:
        logging.basicConfig(level=logging.WARNING)
        logger.warning("A log ini file was not found")
    pass



def settings_configuration():

    for loc in locations:
        path = os.path.normpath(os.path.join(os.path.join(loc, "ptrello_settings.yaml")))

        try:
            if os.path.isfile(path):

                with open(path, "r") as f:
                    settings = yaml.load(f)
                    return settings

        except IOError as e:
            logger.warning("A log configuration was not found {}".format(e.args))
            raise e


logging_configuration()
settings = settings_configuration()

if settings is None:
    raise IOError("ptrello_settings.yaml was not found in the follow locations {}".format(locations))

logger.debug("Settings and logs configured")
