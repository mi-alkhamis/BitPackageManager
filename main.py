import re
import signal
import sys
from base64 import b64encode
from datetime import date
from ftplib import FTP as ftp, error_perm
from os import makedirs, path, removedirs
from uuid import uuid4
from warnings import simplefilter
import requests
from packaging import version
from urllib3.exceptions import InsecureRequestWarning
from config import Config
import readchar


def set_authorization_header():
    login_string = f"{config.api_key}:"
    encoded_user_pass_sequence = str(b64encode(login_string.encode()), "utf-8")
    authorization_header = "Basic " + encoded_user_pass_sequence
    return authorization_header


def get_package_name_list(authorization_header):
    request_id = uuid4()
    api_endpoint = f"https://{config.api_server}/api/v1.0/jsonrpc/packages"
    data = f'{{"params": {{}},"jsonrpc": "2.0","method":"getPackagesList","id": "{request_id}"}}'
    try:
        result = requests.post(
            api_endpoint,
            data=data,
            verify=False,
            headers={
                "Content-Type": "application/json",
                "Authorization": authorization_header,
            },
        )
    except requests.exceptions.ConnectTimeout as e:
        logger.error(f"Connection timeout: {e}")
        sys.exit(1)

    json_result = result.json()
    package_name_list = []
    for package_name in json_result["result"]["items"]:
        if package_name["name"] != "Default Security Server Package":
            package_name_list.append(package_name["name"])
    logger.info(f"Package Name List: {', '.join(package_name_list)}")
    return package_name_list


def get_package_url(authorization_header, package_name):
    request_id = uuid4()
    api_endpoint = f"https://{config.api_server}/api/v1.0/jsonrpc/packages"
    data = f'{{"params": {{"packageName":"{package_name}"}},"jsonrpc": "2.0","method": "getInstallationLinks","id": "{request_id}"}}'
    try:
        result = requests.post(
            api_endpoint,
            data=data,
            verify=False,
            headers={
                "Content-Type": "application/json",
                "Authorization": authorization_header,
            },
        )
    except requests.exceptions.ConnectTimeout as e:
        logger.error(f"{e}")
        sys.exit(1)
    json_result = result.json()
    package_urls = []
    for key, value in json_result["result"][0].items():
        if key.lower().startswith('fullkitwindowsx'):
            package_urls.append(value)
    logger.info(f"{package_name} URLs: {package_urls}")
    return package_urls


def get_package_file(authorization_header, package_url, package_group):
    logger.info("Downloading Full Package...")
    try:
        result = requests.post(
            package_url,
            verify=False,
            headers={
                "Content-Type": "application/json",
                "Authorization": authorization_header,
            },
        )
    except requests.exceptions.ConnectTimeout as e:
        logger.error(f"{e}")
        sys.exit(1)
    filename = result.headers["Content-Disposition"].split("=")[1].rsplit(".zip")[0]
    package_version = filename.split("_")[-1]
    repo_update_status = check_packages_version(package_group, package_version)
    if not repo_update_status:
        package_location = path.join("Bit Packages", package_group)
        makedirs(package_location, exist_ok=True)
        package_filename = f"{filename}-{date.today()}.zip"
        package_filename = path.join(package_location, package_filename)
        with open(package_filename, "wb") as file:
            file.write(result.content)
        logger.info(f"Uploading {package_filename} To FTP Server.")
        send_to_ftp(package_group, package_filename)
    else:
        logger.info("FTP Repository is update")
        return True


def ftp_connection():
    ftp_user = config.ftp_user
    ftp_password = config.ftp_password
    ftp_host = config.ftp_server
    root_dir = config.root_dir
    ftp_server = ftp(ftp_host, ftp_user, ftp_password)
    logger.info("connected To FTP Server")
    ftp_server.encoding = "utf-8"
    ftp_server.cwd(root_dir)
    logger.info(f"Directory changed to {root_dir}")
    return ftp_server


def send_to_ftp(package_group, package_filename):
    ftp_server = ftp_connection()
    ftp_server.mkd(package_group)
    logger.info(f"Folder {package_group} created.")
    ftp_server.cwd(package_group)
    logger.info(f"Directory changed to {package_group}.")
    logger.info(f"STOR {path.split(package_filename)[1]}...")
    with open(package_filename, "rb") as file:
        ftp_server.storbinary(f"STOR {path.split(package_filename)[1]}", file)
    ftp_server.close()
    logger.info("FTP coneection has been closed.")


def check_packages_version(package_group, raw_bit_version):
    ftp_server = ftp_connection()
    try:
        ftp_server.cwd(package_group)
    except error_perm as e:
        logger.error(f'{e}')
        return False
    try:
        filenames = ftp_server.nlst()
    except error_perm as e:
        logger.warning(f'{e}')
        return False
    for filename in filenames:
        file_version = re.search(r"(\d+\.\d+\.\d+\.\d+)", filename).group()
        logger.info(f"Checking Version: {filename}")
        bit_version = version.parse(raw_bit_version)
        file_version = version.parse(file_version)
        if file_version < bit_version:
            ftp_server.delete(filename)



def exit_handler(signum, frame):
    messsage = "Ctrl+C was pressed. Do you really want to exit? y/n "
    print(messsage, end="", flush=True)
    respond = readchar.readchar()
    while readchar.readchar() != b"\n":
        pass
    if respond == "y":
        print("")
        exit(1)
    else:
        print("", end="\r", flush=True)
        print(" " * len(messsage), end="", flush=True)
        print("    ", end="\r", flush=True)


if __name__ == "__main__":
    simplefilter("ignore", InsecureRequestWarning)
    config = Config()
    logger = config.logging()
    signal.signal(signal.SIGINT, exit_handler)
    api_key = config.api_key
    header = set_authorization_header()
    package_name_list = get_package_name_list(header)
    for package_name in package_name_list:
        print (package_name)
        package_url_list = get_package_url(header, package_name)
        for package_url in package_url_list:
            get_package_file(header, package_url, package_name)