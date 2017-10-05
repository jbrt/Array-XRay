#!/usr/bin/env python3
# coding: utf-8

"""
Sending SSH commands to an SVC equipment (works also with FlashSystem products).
Returning, in the most of cases, a list of dictionary for each method.
"""

import csv
import paramiko
from arrays.errors import SVCConnectorError


class SVCCommunicator(object):
    """ Class used to collect information over a SSH connection """

    def __init__(self, address: str, login: str, password: str):
        self._address = address
        self._user = login
        self._password = password

        self._client = paramiko.SSHClient()
        self._client.load_system_host_keys()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            self._client.connect(hostname=self._address,
                                 username=self._user,
                                 password=self._password)
        except paramiko.ssh_exception.AuthenticationException:
            msg = 'Authentication Error on SVC %s' % self._address
            raise SVCConnectorError(msg)

        except TimeoutError:
            msg = 'Timeout connection on SVC %s' % self._address
            raise SVCConnectorError(msg)

    def __str__(self):
        return 'SVC(%s)' % self._address

    def close(self):
        if self._client:
            self._client.close()

    def _send_command(self, command: str):
        stdin, stdout, stderr = self._client.exec_command(command)
        return stdout

    def get_controller(self):
        stdout = self._send_command('lscontroller -delim ,')
        return [line for line in csv.DictReader(stdout)]

    def get_fabric(self):
        stdout = self._send_command('lsfabric -delim ,')
        return [line for line in csv.DictReader(stdout)]

    def get_hosts(self):
        stdout = self._send_command('lshost -delim ,')
        return [line for line in csv.DictReader(stdout)]

    def get_mapping(self):
        stdout = self._send_command('lshostvdiskmap -delim ,')
        return [line for line in csv.DictReader(stdout)]

    def get_nodes(self):
        stdout = self._send_command('lsnode -delim ,')
        return [line for line in csv.DictReader(stdout)]

    def get_mdisks(self):
        stdout = self._send_command('lsmdisk -bytes -delim ,')
        return [line for line in csv.DictReader(stdout)]

    def get_mdiskgroups(self):
        stdout = self._send_command('lsmdiskgrp -bytes -delim ,')
        return [line for line in csv.DictReader(stdout)]

    def get_system(self):
        stdout = self._send_command('lssystem -bytes -delim ,')
        reader = csv.reader(stdout)
        return {line[0]: line[1] for line in reader if line}

    def get_users(self):
        stdout = self._send_command('lsuser -delim ,')
        return [line for line in csv.DictReader(stdout)]

    def get_vdisks(self):
        stdout = self._send_command('lsvdisk -bytes -delim ,')
        return [line for line in csv.DictReader(stdout)]
