import configparser
import hashlib
import logging
import os
import sys

import requests


MOJANG_MANIFEST_URL = 'https://launchermeta.mojang.com/mc/game/version_manifest.json'
DOWNLOADS_VERSIONS_FILENAME = 'servers-infos.txt'


class IntegrityCheckError(Exception):
    """Throwed if the file signature doesn't match with signature expected."""
    pass


def get_versions(manifest_url: str, types=['snapshot', 'release', 'old_beta', 'old_alpha']):
    """Get manifest of mojang."""
    response = requests.request(
        method='GET',
        url=manifest_url,
    )
    response_json = response.json()

    versions = []
    for version in response_json['versions']:
        if version['type'] in types:
            versions.append(version)
    return versions


def download_versions(versions: dict, directory: str, info_filename=DOWNLOADS_VERSIONS_FILENAME):
    """Download specific versions, and verify their integrity."""
    if not os.path.exists(directory):
        os.makedirs(directory)

    infos_file = os.path.join(directory, info_filename)

    with open(infos_file, 'w+') as infos:
        for version in versions:
            # Get informations
            version_manifest_response = requests.request(
                method='GET',
                url=version['url']
            )
            version_manifest_json = version_manifest_response.json()
            try:
                server_file_sha1 = version_manifest_json['downloads']['server']['sha1']
                server_file_url = version_manifest_json['downloads']['server']['url']
            except KeyError:
                logging.warning('Skip %s (%s) downloading, there isn\'t server file' % (version['id'], version['type']))
                continue
            local_filename = os.path.join(
                directory,
                'server-' + version['id'] + '.jar',
            )
            download_file(
                server_file_sha1,
                server_file_url,
                local_filename,
            )

            infos.write('%s %s\n' % (version['id'], local_filename))


def download_file(sha1: str, url: str, filepath: str):
    """Download file and check integrity."""
    filename = os.path.basename(filepath)

    # Check previous if exists
    if os.path.exists(filepath):
        if check_integrity(filepath, sha1):
            return
        else:
            logging.warning(filename + ' integrity check failed, re-downloading in progress')
            os.remove(filepath)
    
    # Download file
    with requests.get(url=url, stream=True) as stream:
        stream.raise_for_status()
        with open(filepath, 'wb') as file:
            for chunk in stream.iter_content(chunk_size=8192):
                file.write(chunk)
    logging.info(filename + ' downloaded successfully')

    # Verify sha1
    if not check_integrity(filepath, sha1):
        raise IntegrityCheckError(filepath + ' : File check integrity failed.')
    else:
        logging.info(filename + ' integrity check successfully')


def check_integrity(filepath: str, sha1: str):
    """Check file integrity."""
    hash_sha1 = hashlib.sha1()
    with open(filepath, 'rb') as file:
        for chunk in iter(lambda: file.read(8192), b''):
            hash_sha1.update(chunk)
    return hash_sha1.hexdigest() == sha1


def get_server_file(directory: str, version: str, info_filename=DOWNLOADS_VERSIONS_FILENAME):
    """Give the file path of a server."""
    file_info = os.path.join(directory, info_filename)
    if os.path.exists(file_info):
        with open(file_info, 'r') as file:
            content = file.read().split('\n')
            for line in content:
                server_version, server_filepath = line.split(' ')
                if version == server_version:
                    return server_filepath
    return None


def get_local_versions(directory: str, info_filename=DOWNLOADS_VERSIONS_FILENAME):
    """Give the local server versions."""
    file_info = os.path.join(directory, info_filename)
    versions = []
    if os.path.exists(file_info):
        with open(file_info, 'r') as file:
            content = file.readlines()
            for line in content:
                server_version, server_filepath = line.split(' ')
                versions.append(server_version)
    return versions
