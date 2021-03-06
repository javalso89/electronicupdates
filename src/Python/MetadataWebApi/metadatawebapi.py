#!/usr/bin/env python
# metadatawebapi.py - Copyright (c) Experian. All rights reserved.
# Python script to download data from the QAS Electronic Updates Web API.

import requests # Used to call the Metadata Web API (See: http://docs.python-requests.org/en/latest/index.html)
import json     # Used to parse JSON
import os       # Used to access the file system
import hashlib  # Used to compute MD5 hashes of files
import sys      # Used to get the installed version of Python

# Declare credentials to communicate with the service.
# Override any values hard-coded here by named environment variable.
username = os.getenv('QAS_ElectronicUpdates_UserName', '')
password = os.getenv('QAS_ElectronicUpdates_Password', '')

# Declare User Agent string
version = sys.version_info
userAgent = 'Python/{0}.{1}.{2}'.format(version.major, version.minor, version.micro)

# Declare HTTP request headers
headers = {'accept': 'application/json', 'content-type': 'application/json; charset=UTF-8', 'UserAgent': userAgent}

# Declare directory to download data to
root_download_path = os.path.join('.', 'QASData')

# Get the available package groups from the Web API
request = {'usernamePassword': {'UserName': username, 'Password': password}}
packages_request = requests.post('https://ws.updates.qas.com/metadata/v1/packages', data = json.dumps(request), headers = headers)

if (packages_request.status_code != requests.codes.ok):
    print('Available packages request failed with HTTP Status Code {0}.'.format(packages_request.status_code))
    packages_request.raise_for_status()

packages_json = packages_request.json()
package_groups = packages_json["PackageGroups"]

# Iterate through the package groups
for i in range(0, len(package_groups)):

    # Get the code, vintage and packages in the group
    package_group = package_groups[i]
    code = package_group["PackageGroupCode"]
    vintage = package_group["Vintage"]
    packages = package_group["Packages"]

    print('Package: ''{0:<6}''; Vintage: ''{1}'''.format(code, vintage))

    directory_path = os.path.join(root_download_path, code, vintage)

    # Create a directory to download the files for this package into
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    # Iterate through the packages
    for j in range(0, len(packages)):

        # Get the available files
        package = packages[j]
        data_files = package["Files"]

        # Iterate through the files
        for k in range(0, len(data_files)):
            
            data_file = data_files[k]
            file_name = data_file["FileName"]
            file_hash = data_file["Md5Hash"]
            file_size = data_file["Size"]
            file_path = os.path.join(directory_path, file_name)

            download_file = True

            # Has the file already been downloaded?
            if os.path.exists(file_path):                
                
                size_on_disk = os.path.getsize(file_path)

                # Does the size of the file match that already on disk?
                if (size_on_disk != int(file_size)):
                    print('File ''{0}'' has already been downloaded, but is corrupt due to truncation.'.format(file_path))
                    os.remove(file_path)
                else:
                    # Verify the MD5 hash of the file on disk.
                    # In a fuller solution, the MD5 hashes of the files
                    # that have been downloaded would be cached to disk
                    # and corruption would not be tested every time.
                    md5 = hashlib.md5()
                    with open(file_path,'rb') as existing_file: 
                        for chunk in iter(lambda: existing_file.read(8192), b''): 
                             md5.update(chunk)
                    hash_on_disk = md5.hexdigest()
                    
                    # If the hash does not match, the file needs to be downloaded again
                    if (file_hash == hash_on_disk):                
                        print('File ''{0}'' has already been downloaded.'.format(file_path))
                        download_file = False
                    else:
                        print('File ''{0}'' has already been downloaded, but is corrupt.'.format(file_path))
                        os.remove(file_path)                    

            if (download_file):
                
                print('Requesting download URI for file ''{0}''.'.format(file_path))

                # Request the download URI for this file from the Web API
                request = {'usernamePassword': {'UserName': username, 'Password': password }, 'fileDownloadRequest': {'FileName': file_name, 'FileMd5Hash': file_hash}}
                download_uri_request = requests.post('https://ws.updates.qas.com/metadata/v1/filedownload', data = json.dumps(request), headers = headers)

                if (download_uri_request.status_code != requests.codes.ok):
                    print('Download URI request failed with HTTP Status Code {0}.'.format(download_uri_request.status_code))
                    download_uri_request.raise_for_status()
                
                filedownload_json = download_uri_request.json()
                download_uri = filedownload_json["DownloadUri"]

                # Download the file from the returned download URI
                print('Downloading ''{0}''...'.format(download_uri))

                with open(file_path, 'wb', 4096) as file_handle:
                    download_request = requests.get(download_uri)

                    if (download_request.status_code != requests.codes.ok):
                        print('Download request failed with HTTP Status Code {0}.'.format(download_request.status_code))
                        download_request.raise_for_status()

                    for block in download_request.iter_content(4096):
                        if not block:
                            break

                        file_handle.write(block)

                print('Downloaded file ''{0}''.'.format(file_path))

print('All data files up-to-date.')
