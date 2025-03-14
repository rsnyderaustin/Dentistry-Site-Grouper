
import configparser
import os
import pathlib

config_path = pathlib.Path(__file__).parent.absolute()
config_path = os.path.join(config_path, 'config.ini')
config = configparser.ConfigParser()
config.read(config_path)

