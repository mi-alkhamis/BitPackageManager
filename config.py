from configparser import ConfigParser
import os
import sys
import re
import logging, coloredlogs
from datetime import datetime


class Config:
    def __init__(self):
        self.config = ConfigParser(allow_no_value=False)
        self.config_file = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "config.ini")
        )
        self.read_config(self.config_file)

    def read_config(self, config_path):
        try:
            with open(config_path, "r") as config_file:
                self.config.read_file(config_file)
        except FileNotFoundError:
            print(f"Error: Config file not found at {config_path}")
            sys.exit(1)
        except Error as e:
            print(f"Error reading config file:\n{e}")
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred: {e} at {config_path}")
            sys.exit(1)

    def get(self, key, fallback="", section="default"):
        return self.config.get(section, key, fallback=fallback)

    def validate_ipv4(self, ip):
        ipv4_pattern = r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        pattern = re.compile(ipv4_pattern)
        if not pattern.match(ip):
            return False
        return True

    @property
    def api_key(self):
        api_key_pattern = re.compile(r"^[0-9a-fA-F]{64}$")
        api_key = str(self.get("APIKEY"))
        if not api_key_pattern.match(api_key):
            raise ValueError("Invalid API key format")
        return api_key

    @property
    def api_server(self):
        api_server = str(self.get("SERVER"))
        if not self.validate_ipv4(api_server):
            raise ValueError("Invalid IP Address")
        return api_server

    @property
    def ftp_server(self):
        ftp_server = str(self.get("FTP"))
        if not self.validate_ipv4(ftp_server):
            raise ValueError("Invalid IP Address")
        return ftp_server

    @property
    def ftp_user(self):
        return str(self.get("FTP_USER"))

    @property
    def ftp_password(self):
        return str(self.get("FTP_PASS"))

    @property
    def root_dir(self):
        return str(self.get("ROOT_DIR"))

    @property
    def log_path(self):
        return os.path.realpath(self.get("LOG_PATH", fallback="./logs"))

    @property
    def log_filename(self):
        log_filename_date_format = "%d-%m-%Y"
        return f"Log-{datetime.now().strftime(log_filename_date_format)}.log"

    @property
    def log_separator(self):
        log_separator = "-" * 100
        return log_separator

    def logging(self):
        logger = logging.getLogger(__name__)
        try:
            os.makedirs(self.log_path, exist_ok=True)
        except PermissionError as e:
            print(
                f"Error: Permission denied while creating log directory at {Config.log_path}"
            )
            sys.exit(1)
        except OSError as e:
            print(
                f"Error: An OS error occurred while creating log directory at {Config.log_path}: {e}"
            )
            sys.exit(1)
        log_path = os.path.join(self.log_path, self.log_filename)
        file_handler = logging.FileHandler(log_path)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] - %(message)s", datefmt=self.date_format
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logging.basicConfig(
            level=logging.DEBUG,
        )
        levelstyles = {
            "critical": {"bold": True, "color": "red"},
            "debug": {"color": "magenta"},
            "error": {"color": "red"},
            "info": {"color": "green"},
            "warning": {"color": "yellow"},
        }
        coloredlogs.install(
            logger=logger,
            fmt="%(message)s",
            level=logging.DEBUG,
            level_styles=levelstyles,
        )
        return logger

    @property
    def date_format(self):
        date_format = "%d-%m-%Y %H:%M:%S"
        return date_format
