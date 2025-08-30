import logging
import os
import re
import sys
from configparser import ConfigParser
from datetime import datetime

import coloredlogs


class Config:
    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "production")
        self.config = ConfigParser(allow_no_value=False)
        self.logger = self.logging()
        self.config_file = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "config.ini")
        )
        self.read_config(self.config_file)

    def read_config(self, config_path):
        try:
            with open(config_path, "r") as config_file:
                self.config.read_file(config_file)
        except FileNotFoundError as e:
            self.logger.error(f"Error: Config file not found. {e}")
            sys.exit(1)
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
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
        try:
            if not api_key_pattern.match(api_key):
                raise ValueError("Invalid API key format")
        except ValueError as e:
            self.logger.error(f"{e}")
            sys.exit(1)
        return api_key

    @property
    def api_server(self):
        api_server = str(self.get("SERVER"))
        try:
            if not self.validate_ipv4(api_server):
                raise ValueError("Invalid IP Address")
        except ValueError as e:
            self.logger.error(f"Enterd a Wrong IP Address. {e}")
            sys.exit(1)
        return api_server

    @property
    def ftp_server(self):
        ftp_server = str(self.get("FTP"))
        if not self.validate_ipv4(ftp_server):
            raise ValueError("Invalid IP Address")
        return ftp_server

    @property
    def ftp_user(self):
        return str(self.get("FTP_USER", fallback="user"))

    @property
    def ftp_password(self):
        return str(self.get("FTP_PASS", fallback="pass"))

    @property
    def root_dir(self):
        return str(self.get("ROOT_DIR", fallback="Bitdefender"))

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
        if self.environment == "development":
            logging.getLogger("urllib3").setLevel(logging.DEBUG)
        else:
            logging.getLogger("urllib3").setLevel(logging.WARNING)
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
            level=logging.INFO,
        )
        levelstyles = {
            "critical": {"bold": True, "color": "red"},
            "debug": {"bold": True, "color": "magenta"},
            "error": {"color": "red"},
            "info": {"color": "green"},
            "warning": {"color": "yellow"},
        }
        coloredlogs.install(
            logger=logger,
            fmt="[%(levelname)s]:%(message)s",
            level=logging.INFO,
            level_styles=levelstyles,
        )
        return logger

    @property
    def date_format(self):
        date_format = "%d-%m-%Y %H:%M:%S"
        return date_format
