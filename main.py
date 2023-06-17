from base64 import b64encode
from datetime import date
from os import mkdir, path
from socket import gethostbyname, gethostname
from uuid import uuid4
from warnings import simplefilter
from requests import post
from urllib3.exceptions import InsecureRequestWarning
from config import Config


def set_authorization_header():
    loginString = config.api_key + ":"
    encodedUserPassSequence = str(b64encode(loginString.encode()), "utf-8")
    authorizationHeader = "Basic " + encodedUserPassSequence
    return authorizationHeader


def get_package_name_list(authorizationHeader):
    request_id = uuid4()
    apiEndpoint_Url = f"https://{config.api_server}/api/v1.0/jsonrpc/packages"
    request = f'{{"params": {{}},"jsonrpc": "2.0","method": "getPackagesList","id": "{request_id}" }}'
    result = post(
        apiEndpoint_Url,
        data=request,
        verify=False,
        headers={
            "Content-Type": "application/json",
            "Authorization": authorizationHeader,
        },
    )
    json_result = result.json()
    package_name_list = []
    for package_name in json_result["result"]["items"]:
        package_name_list.append(package_name["name"])
    return package_name_list


def get_package_url(authorizationHeader, Package_name):
    request_id = uuid4()
    apiEndpoint_Url = f"https://{config.api_server}/api/v1.0/jsonrpc/packages"
    request = f'{{"params": {{"packageName":"{Package_name}"}},"jsonrpc": "2.0","method": "getInstallationLinks","id": "{request_id}"}}'
    result = post(
        apiEndpoint_Url,
        data=request,
        verify=False,
        headers={
            "Content-Type": "application/json",
            "Authorization": authorizationHeader,
        },
    )
    json_result = result.json()
    package_urls = []
    for key, value in json_result["result"][0].items():
        if key.lower().find("fullkitwindows") != -1:
            package_urls.append(value)
    return package_urls


if __name__ == "__main__":
    simplefilter("ignore", InsecureRequestWarning)
    config = Config()
    bit_server_ip = config.api_server
    api_key = config.api_key
    authorizationHeader = set_authorization_header()
    package_name_list = get_package_name_list(authorizationHeader)
    for package_name in package_name_list:
        package_url_list = get_package_url(authorizationHeader, package_name)
        
