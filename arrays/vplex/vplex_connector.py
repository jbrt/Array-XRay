#!/usr/bin/env python3
# coding: utf-8

"""
Sending REST calls to a VPLEX equipment.
Returning, in the most of cases, a list of dictionary for each method.
"""

import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from arrays.errors import VPLEXConnectionError

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class VPLEXCommunicator(object):
    """
    Send requests to VPLEX array
    """

    def __init__(self, address: str, user: str, password: str, port=443):
        """
        Constructor
        :param address: IP address of the VPLEX
        :param user: Username
        :param password: Password
        :param port: TCP port (by default 443)
        """
        self._address = 'https://%s:%s/vplex' % (address, port)
        self._headers = {'Username': user,
                         'Password': password,
                         'Accept': 'application/json;format=1'}

    def __str__(self):
        return 'VPlex(%s)' % self._address

    def _send_request(self, request: str):
        url = '/'.join([self._address, request])
        try:
            data = requests.get(url, headers=self._headers, timeout=600, verify=False)
            data = json.loads(data.text)
            if data['response']['message']:
                if 'User authentication failed.' in data['response']['message']:
                    raise VPLEXConnectionError('Authentication failure')
        except requests.exceptions.ConnectionError:
            raise VPLEXConnectionError('Problem while connecting to VPLEX')
        except requests.exceptions.ReadTimeout:
            raise VPLEXConnectionError('Connection timeout occurs')
        else:
            return data['response']['context']

    def get_clusters(self):
        return self._send_request('clusters/*')

    def get_initiators(self):
        return self._send_request('clusters/*/exports/initiator-ports/*')

    def get_storage_arrays(self):
        url = 'clusters/*/storage-elements/storage-arrays/*/logical-units/*'
        return self._send_request(url)

    def get_storage_views(self):
        return self._send_request('clusters/*/exports/storage-views/*')

    def get_virtual_volumes(self):
        return self._send_request('clusters/*/virtual-volumes/*')
