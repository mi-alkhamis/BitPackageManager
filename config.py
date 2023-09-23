from configparser import ConfigParser
from os import path


class Config:
    def __init__(self):
        self.config_file = ConfigParser(allow_no_value=False)
        self.config_file.read(path.join(path.dirname(__file__), "config.ini"))

    def get(self, key, fallback=None, section="default"):
        return self.config_file.get(section, key, fallback=fallback)

    @property
    def api_key(self):
        return str(self.get("APIKEY"))

    @property
    def api_server(self):
        return str(self.get("SERVER"))

    @property
    def ftp_server(self):
        return str(self.get("FTP"))

    @property
    def ftp_user(self):
        return str(self.get("FTP_USER"))

    @property
    def ftp_password(self):
        return str(self.get("FTP_PASS"))

    @property
    def root_dir(self):
        return str(self.get("ROOT_DIR"))
