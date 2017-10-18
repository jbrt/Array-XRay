#!/usr/bin/env python3
# coding: utf-8

"""
Sending REST calls to a VMAX equipment.
Returning, in the most of cases, a list of dictionary for each method.
"""

import abc
import json
import logging
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning, MaxRetryError
from arrays.errors import VMAXConnectionError, VmaxInventoryFactoryError

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def next_range(start, end, pagesize):
    """
    Generate a start and a stop number used in VMAX's iterator concept
    :param start: (int) start at this point
    :param end: (int) last number
    :param pagesize: (int) maximum of values by page
    :return: (int, int)
    """
    if (end-start) < pagesize:
        yield start, end
    else:
        values = [i for i in range(start, end, pagesize-1)]
        for index, value in enumerate(values):
            if value != values[-1]:
                yield value, values[index+1]-1
            else:
                yield value, end


class BaseVMAXArray(object, metaclass=abc.ABCMeta):
    """
    Abstract class of VMAX objects
    """

    def __init__(self, sym_id: str, address: str, user: str, password: str):
        """
        Constructor
        :param sym_id: Symmetrix ID of the VMAX
        :param address: IP address
        :param user: Unipshere user
        :param password: Unisphere password
        """
        self._sym_id = sym_id
        self._address = address
        self._user = user
        self._password = password
        self._logger = logging.getLogger('arrayxray')

        # Sample of UNISPHERE REST API
        # https://126.199.128.46:8443/univmax/restapi/provisioning/symmetrix/000295700220/volume/00A00
        self._url = 'https://%s:8443/univmax/restapi' % self._address

    def __str__(self):
        return self._sym_id

    @property
    def node(self):
        raise NotImplementedError

    def _get_request(self, request: str):
        """
        Send a GET request to the VMAX
        :param request: URI of the request
        :return: JSON payload
        """
        url = '/'.join([self._url, request])
        try:
            self._logger.debug('---> GET %s' % request)
            data = requests.get(url,
                                auth=(self._user, self._password),
                                timeout=600,
                                verify=False)

            if isinstance(data.text, str) and 'Unauthorized' in data.text:
                raise VMAXConnectionError('Authentication failure')

            data = json.loads(data.text)
        except requests.exceptions.ConnectionError as error:
            # If we experience a MaxRetryError, try again ! ;-)
            # UNISPHERE may be slow to respond
            if isinstance(error.args[0], MaxRetryError):
                self._logger.error('/!\ RETRY FOR %s' % request)
                return self._get_request(request)

            self._logger.error('%s' % error)
            raise VMAXConnectionError('Problem while connecting to VMAX')

        except requests.exceptions.ReadTimeout:
            raise VMAXConnectionError('Timeout reached')

        else:
            return data

    def _get_request_recursive(self, request: str, re_type: str, re_name: str):
        """
        Execute a recursive request on each items on a list
        :param request: URI request
        :param re_type: resource type to find
        :param re_name: resource name
        :return: (list)
        """
        response = []
        data = self._get_request(request)
        # if 'message' in data : no data to collect
        if 'message' not in data:
            for item in data[re_type]:
                data = self._get_request('/'.join([request, item]))
                response.append(data[re_name][0])
        return response

    def _get_volumes_iterator(self, iterator: str, count: int, page_size: int):
        """
        Deal with UNISPHERE iterators to make a list all volumes on an array
        :param iterator: ID of the iterator
        :param count: number of devices on array
        :param page_size: maximum size of a respond page
        :return: list of volumes string
        """
        # Sample of iterator request
        # common/Iterator/4f477856-5209-46af-a040-9abeed6d31f3_0/page?from=1999&to=1999
        request = 'common/Iterator/%s/page' % iterator
        volumes = []

        for from_, to_ in next_range(1, count, page_size):
            req_range = request + '?from=%s&to=%s' % (from_, to_)

            for vol in self._get_request(req_range)['result']:
                volumes.append(vol['volumeId'])

        return volumes

    def get_hosts(self):
        request = '%s/symmetrix/%s/host' % (self.node, self._sym_id)
        return self._get_request_recursive(request, 'hostId', 'host')

    def get_host_groups(self):
        request = '%s/symmetrix/%s/hostgroup' % (self.node, self._sym_id)
        return self._get_request_recursive(request, 'hostGroupId', 'hostGroup')

    def get_initiators(self):
        request = '%s/symmetrix/%s/initiator' % (self.node, self._sym_id)
        return self._get_request_recursive(request, 'initiatorId', 'initiator')

    def get_masking_view(self):
        request = '%s/symmetrix/%s/maskingview' % (self.node, self._sym_id)
        return self._get_request_recursive(request, 'maskingViewId', 'maskingView')

    def get_port_groups(self):
        request = '%s/symmetrix/%s/portgroup' % (self.node, self._sym_id)
        return self._get_request_recursive(request, 'portGroupId', 'portGroup')

    def get_storage_group(self):
        request = '%s/symmetrix/%s/storagegroup' % (self.node, self._sym_id)
        return self._get_request_recursive(request, 'storageGroupId', 'storageGroup')

    def get_system(self):
        request = '%s/symmetrix/%s' % (self.node, self._sym_id)
        return self._get_request(request)['symmetrix'][0]

    def get_thin_volumes(self):
        base_request = '%s/symmetrix/%s/volume' % (self.node, self._sym_id)
        request = base_request + '?meta_member=false&tdev=true'
        data = self._get_request(request)
        all_devices = []
        # First of all : get the list of all volumes on the array
        # If there is more than one page : use an iterator
        if data['count'] > data['maxPageSize']:
            all_devices = self._get_volumes_iterator(data['id'],
                                                     data['count'],
                                                     data['maxPageSize'])
        else:
            for volume in data['resultList']['result']:
                all_devices.append(volume['volumeId'])

        # Then for each of volume in the list : run a GET request
        # I know it's slow and not very clean but it's the only way to get all
        # the information i needs
        response = []
        for device in all_devices:
            data = self._get_request('/'.join([base_request, device]))
            response.append(data['volume'][0])
        return response

    def get_version(self):
        request = 'system/version'
        return tuple(self._get_request(request)['version'].split('.'))


class VMAX2Array(BaseVMAXArray):
    """Concrete VMAX-2 array"""

    def __init__(self, sym_id: str, address: str, user: str, password: str):
        super(VMAX2Array, self).__init__(sym_id, address, user, password)

    @property
    def node(self):
        return 'provisioning'

    def get_fast_policy(self):
        request = '%s/symmetrix/%s/fastpolicy' % (self.node, self._sym_id)
        return self._get_request_recursive(request, 'fastPolicyId', 'fastPolicy')

    def get_thin_pool(self):
        request = '%s/symmetrix/%s/thinpool' % (self.node, self._sym_id)
        return self._get_request_recursive(request, 'poolId', 'thinPool')


class VMAX3Array(BaseVMAXArray):
    """Concrete VMAX-3 array"""

    def __init__(self, sym_id: str, address: str, user: str, password: str):
        super(VMAX3Array, self).__init__(sym_id, address, user, password)

    @property
    def node(self):
        return 'sloprovisioning'

    def get_srp(self):
        request = '%s/symmetrix/%s/srp' % (self.node, self._sym_id)
        return self._get_request_recursive(request, 'srpId', 'srp')


class VMAXArrayFactory(object):
    """VMAX Factory"""

    classes = {'26': VMAX2Array,
               '49': VMAX2Array,
               '57': VMAX2Array,
               '59': VMAX2Array,
               '87': VMAX2Array,
               '67': VMAX3Array,
               '68': VMAX3Array,
               '72': VMAX3Array,
               '70': VMAX3Array,
               '75': VMAX3Array,
               '77': VMAX3Array,
               '78': VMAX3Array}

    def __new__(cls, sym_id: str, address: str, user: str, password: str):
        cls._logger = logging.getLogger('arrayxray')

        model_type = sym_id[5:7]  # Model type is in the middle of the SID

        if model_type not in cls.classes:
            msg = "The SID %s doesn't match with any VMAX Array model" % sym_id
            cls._logger.error(msg)
            raise VmaxInventoryFactoryError

        return cls.classes[model_type](sym_id, address, user, password)
