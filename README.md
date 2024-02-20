# Bitdefender Package Downloader and FTP Uploader

## Overview

This Python script serves as a tool to automate the process of downloading Bitdefender antivirus packages from the Bitdefender Antivirus server and subsequently uploading them to a designated FTP server. This automation streamlines the task of keeping a local repository up to date with the latest antivirus packages provided by Bitdefender.

The script leverages the Bitdefender API for obtaining package information, and it interacts with an FTP server to manage the storage and organization of downloaded packages. By using this script, administrators can ensure that their antivirus packages repository is consistently updated, allowing for efficient distribution and deployment across their network.

Key features of the script include:

- **Bitdefender API Integration**: Utilizes the Bitdefender API to retrieve a list of available packages, ensuring the script remains synchronized with the latest offerings.

- **FTP Interaction**: Establishes a connection to an FTP server to upload downloaded packages. This enables seamless integration with existing repository management systems.

- **Version Control**: Checks the version of packages on the FTP server and deletes older files, ensuring that the repository maintains the most recent and relevant antivirus packages.

- **Configuration Flexibility**: Allows users to configure the script by specifying parameters such as API key, API server, FTP credentials, etc., providing adaptability to diverse network environments.

By employing this script, system administrators can enhance the efficiency of managing Bitdefender antivirus packages, reduce manual intervention, and ensure that their antivirus solutions are always up to date.

## Prerequisites

Before using this script, make sure you have the following:

- Python 3.x installed on your machine.
- Required Python packages installed. You can install them using:

  ```bash
  pip install requests
  ```

## Configuration

Ensure you have a valid configuration set up in the `config.ini` file with the required parameters:

```ini
[default]
APIKEY = your_bitdefender_api_key
SERVER = your_bitdefender_api_server
FTP = your_ftp_server
FTP_USER = your_ftp_username
FTP_PASS = your_ftp_password
ROOT_DIR = your_ftp_root_directory
```

Replace the placeholder values (`your_bitdefender_api_key`, `your_bitdefender_api_server`, `your_ftp_server`, `your_ftp_username`, `your_ftp_password`, `your_ftp_root_directory`) with your actual configuration details.

## Usage

1. Run the script by executing the following command:

   ```bash
   python script_name.py
   ```

2. The script will fetch the list of available Bitdefender packages from the Bitdefender API server.

3. For each package, it will download the package file and upload it to the specified FTP server.

4. The script will check the version on the FTP server and delete older files to keep the repository up to date.

5. The process continues for all available packages.

## To-Do List

...

## How to Contribute

Contributions to this project are welcome! To contribute, follow these steps:

1. Fork the repository.

2. Create a new branch with a descriptive name:

   ```bash
   git checkout -b feature/new-feature
   ```

3. Make your changes and commit them:

   ```bash
   git commit -m "Add new feature"
   ```

4. Push your changes to your fork:

   ```bash
   git push origin feature/new-feature
   ```

5. Create a pull request on the original repository.

6. Ensure your pull request provides a clear description of the changes made and why they are beneficial.

Feel free to open issues, discuss potential features, or report bugs. Your contributions help improve this script for everyone!