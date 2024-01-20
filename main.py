import re
from base64 import b64encode
from datetime import date
from ftplib import FTP as ftp
from os import mkdir, path
from uuid import uuid4
from warnings import simplefilter
from requests import post
from urllib3.exceptions import InsecureRequestWarning
from config import Config


def set_authorization_header():
    """Create and return an authorization header for the API server.

    The authorization header is based on the API key stored in the config module.
    It uses the basic authentication scheme with base64 encoding.

    Returns:
        str: The authorization header value.
    """
    login_string = config.api_key + ":"
    encoded_user_pass_sequence = str(b64encode(login_string.encode()), "utf-8")
    authorization_header = "Basic " + encoded_user_pass_sequence
    return authorization_header


def get_package_name_list(authorization_header):
    """Get and return a list of package names from the API server.

    The package names are obtained by sending a JSON-RPC request to the API endpoint.
    The request uses the authorization header and the getPackagesList method.
    The package names are filtered to exclude the default security server package.

    Args:
        authorization_header (str): The authorization header value.

    Returns:
        list: A list of package names as strings.
    """
    request_id = uuid4()
    api_endpoint = f"https://{config.api_server}/api/v1.0/jsonrpc/packages"
    request = f'{{"params": {{}},"jsonrpc": "2.0","method":"getPackagesList","id": "{request_id}"}}'
    result = post(
        api_endpoint,
        data=request,
        verify=False,
        headers={
            "Content-Type": "application/json",
            "Authorization": authorization_header,
        },
    )
    json_result = result.json()
    package_name_list = []
    for package_name in json_result["result"]["items"]:
        if package_name["name"] != "Default Security Server Package":
            package_name_list.append(package_name["name"])
    print(f"Package Name List: {package_name_list}")
    return package_name_list


def get_package_url(authorization_header, package_name):
    """Get and return a list of package URLs from the API server.

    The package URLs are obtained by sending a JSON-RPC request to the API endpoint.
    The request uses the authorization header and the getInstallationLinks method.
    The package URLs are filtered to include only the full kit windows links.

    Args:
        authorization_header (str): The authorization header value.
        package_name (str): The name of the package.

    Returns:
        list: A list of package URLs as strings.
    """
    request_id = uuid4()
    api_endpoint = f"https://{config.api_server}/api/v1.0/jsonrpc/packages"
    request = f'{{"params": {{"packageName":"{package_name}"}},"jsonrpc": "2.0","method": "getInstallationLinks","id": "{request_id}"}}'
    result = post(
        api_endpoint,
        data=request,
        verify=False,
        headers={
            "Content-Type": "application/json",
            "Authorization": authorization_header,
        },
    )
    json_result = result.json()
    package_urls = []
    for key, value in json_result["result"][0].items():
        if key.lower().find("fullkitwindows") != -1:
            package_urls.append(value)
    print(f"{package_name} URLs: {package_urls}")
    return package_urls


def get_package_file(authorization_header, package_url, package_group):
    """Download a package file from the API server and upload it to the FTP server.

    The package file is downloaded by sending a POST request to the package URL.
    The request uses the authorization header and the Content-Type header.
    The package file name and version are extracted from the response headers.
    The package file is saved in a local directory named after the package group.
    The package file is then uploaded to the FTP server using the send_to_ftp function.
    The package file is only uploaded if the FTP server does not have a newer version.

    Args:
        authorization_header (str): The authorization header value.
        package_url (str): The URL of the package file to download.
        package_group (str): The name of the package group.

    Returns:
        bool: True if the FTP repository is up to date, False otherwise.
    """
    result = post(
        package_url,
        verify=False,
        headers={
            "Content-Type": "application/json",
            "Authorization": authorization_header,
        },
    )
    print("Downloading full package")
    filename = result.headers["Content-Disposition"].split("=")[1].rsplit(".zip")[0]
    package_version = filename.split("_")[-1]
    repo_update_status = check_packages_version(package_group, package_version)
    if repo_update_status == False:
        if not path.exists(package_group):
            mkdir(package_group)
        package_filename = f"{filename}-{date.today()}.zip"
        package_filename = path.join(package_group, package_filename)
        with open(package_filename, "wb") as file:
            file.write(result.content)
        print(f"Uploading: {package_group}:{package_filename}")
        send_to_ftp(package_group, package_filename, package_version)
    else:
        print("FTP Repository is update")
        return True


def send_to_ftp(package_group, package_filename, package_version):
    """Upload a package file to the FTP server.

    The package file is uploaded to the FTP server using the FTP class from the ftplib module.
    The FTP server credentials and the root directory are obtained from the config module.
    The package file is stored in a subdirectory named after the package group.
    The FTP connection is closed after the upload is completed.

    Args:
        package_group (str): The name of the package group.
        package_filename (str): The path of the package file to upload.
        package_version (str): The version of the package file.
    """
    ftp_user = config.ftp_user
    ftp_password = config.ftp_password
    ftp_host = config.ftp_server
    root_dir = config.root_dir
    ftp_server = ftp(ftp_host, ftp_user, ftp_password)
    ftp_server.encoding = "utf-8"
    ftp_server.cwd(root_dir)
    ftp_server.mkd(package_group)
    ftp_server.cwd(package_group)
    with open(package_filename, "rb") as file:
        ftp_server.storbinary(f"STOR {path.split(package_filename)[1]}", file)
    ftp_server.quit()


def check_packages_version(package_group, version):
    """Check the package version on the FTP server and delete older files.

    The package version is compared with the existing files on the FTP server using the re module.
    The FTP server credentials and the root directory are obtained from the config module.
    The package files are listed in a subdirectory named after the package group.
    If the package version is newer than the existing files, the older files are deleted.
    If the package version is equal to or older than the existing files, the function returns True.

    Args:
        package_group (str): The name of the package group.
        version (str): The version of the package file.

    Returns:
        bool: True if the FTP server has a newer or equal version, False otherwise.
    """
    ftp_user = config.ftp_user
    ftp_password = config.ftp_password
    ftp_host = config.ftp_server
    root_dir = config.root_dir
    ftp_server = ftp(ftp_host, ftp_user, ftp_password)
    ftp_server.encoding = "utf-8"
    ftp_server.cwd(root_dir)
    dir_list = ftp_server.mlsd()
    ftp_server.cwd(package_group)
    filenames = ftp_server.nlst()
    for filename in filenames:
        file_version = re.search(r"(\d+\.\d+\.\d+\.\d+)", filename)
        print(f"Checking Version: {filename}")
        if file_version.group() < version:
            ftp_server.delete(filename)
            return False
        return True


if __name__ == "__main__":
    simplefilter("ignore", InsecureRequestWarning)
    config = Config()
    bit_server_ip = config.api_server
    api_key = config.api_key
    header = set_authorization_header()
    package_name_list = get_package_name_list(header)
    for package_name in package_name_list:
        package_url_list = get_package_url(header, package_name)
        for package_url in package_url_list:
            status = get_package_file(header, package_url, package_name)
            if status == True:
                exit(1)
            # check_packages_version(package_group=package_name, version="7.9.10.285")
