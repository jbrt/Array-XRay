#!/usr/bin/env python3
# coding: utf-8

"""
These objects are going to filter the input data and only keep the interesting
attributes. Convert of capacity units may be occur to stay more consistent
between arrays.
"""

import abc
from collections import OrderedDict


class VMAXFilter(object, metaclass=abc.ABCMeta):
    """ Abstract class for all filters objects """

    def __init__(self, data: list):
        """
        Constructor
        :param data: list of data to filter
        """
        self._data = data
        self._f_data = []
        self._clean()

    def __iter__(self):
        return self

    def __next__(self):
        try:
            one_element = self._f_data.pop(0)
        except IndexError:
            raise StopIteration
        return one_element

    @staticmethod
    def _bytes_to_gb(value):
        return int(int(value)/1073741824)

    @abc.abstractmethod
    def _clean(self):
        raise NotImplementedError


class VMAXFastPolicy(VMAXFilter):

    def __init__(self, data):
        super(VMAXFastPolicy, self).__init__(data)

    def _clean(self):
        for to_clean in self._data:
            clean = OrderedDict()
            keys = ['fastPolicyId', 'tier_1_id', 'tier_2_id', 'tier_3_id',
                    'tier_4_id', 'tier_1_capacity', 'tier_2_capacity',
                    'tier_3_capacity', 'tier_4_capacity', 'storage_group']

            for key in keys:
                if key not in to_clean:
                    clean[key] = ''  # Create and fill empty value
                else:
                    clean[key] = to_clean[key]

            self._f_data.append(clean)


class VMAXHost(VMAXFilter):

    def __init__(self, data):
        super(VMAXHost, self).__init__(data)

    def _clean(self):
        for to_clean in self._data:
            clean = OrderedDict()
            keys = ['hostId', 'num_of_initiators', 'num_of_host_groups',
                    'num_of_masking_views', 'consistent_lun', 'hostgroup',
                    'initiator', 'maskingview']

            for key in keys:
                if key not in to_clean:
                    clean[key] = ''  # Create and fill empty value
                else:
                    clean[key] = to_clean[key]

            self._f_data.append(clean)


class VMAXHostGroup(VMAXFilter):

    def __init__(self, data):
        super(VMAXHostGroup, self).__init__(data)

    def _clean(self):
        for to_clean in self._data:
            clean = OrderedDict()
            keys = ['hostGroupId', 'num_of_hosts', 'num_of_initiators',
                    'num_of_masking_views', 'consistent_lun', 'maskingview']

            for key in keys:
                if key in to_clean:
                    clean[key] = to_clean[key]

            hosts = []
            for host in to_clean['host']:
                hosts.append(host['hostId'])
            clean['host'] = hosts

            self._f_data.append(clean)


class VMAXInitiator(VMAXFilter):

    def __init__(self, data):
        super(VMAXInitiator, self).__init__(data)

    def _clean(self):
        for to_clean in self._data:
            clean = OrderedDict()
            keys = ['initiatorId', 'host', 'alias', 'hostGroup', 'on_fabric',
                    'logged_in', 'num_of_masking_views', 'maskingview',
                    'port_flags_override', 'num_of_host_groups', 'flags_in_effect']

            for key in keys:
                if key not in to_clean:
                    clean[key] = ''  # Create and fill empty value
                else:
                    clean[key] = to_clean[key]

            if 'symmetrixPortKey' in to_clean:
                ports = []
                for zoning in to_clean['symmetrixPortKey']:
                    ports.append('%s:%s' % (zoning['directorId'], zoning['portId']))
                clean['symmetrixPortKey'] = ports
            else:
                clean['symmetrixPortKey'] = ''

            self._f_data.append(clean)


class VMAXMaskingView(VMAXFilter):

    def __init__(self, data):
        super(VMAXMaskingView, self).__init__(data)

    def _clean(self):
        for to_clean in self._data:
            clean = OrderedDict()
            keys = ['maskingViewId', 'hostId', 'hostGroupId', 'portGroupId',
                    'storageGroupId']

            for key in keys:
                if key not in to_clean:
                    clean[key] = ''  # Create and fill empty value
                else:
                    clean[key] = to_clean[key]

            self._f_data.append(clean)


class VMAXPortGroup(VMAXFilter):

    def __init__(self, data):
        super(VMAXPortGroup, self).__init__(data)

    def _clean(self):
        for to_clean in self._data:
            clean = OrderedDict()
            keys = ['portGroupId', 'num_of_ports', 'num_of_masking_views']

            for key in keys:
                clean[key] = to_clean[key]

            if 'symmetrixPortKey' in to_clean:
                ports = []
                for zoning in to_clean['symmetrixPortKey']:
                    ports.append('%s:%s' % (zoning['directorId'], zoning['portId']))
                clean['symmetrixPortKey'] = ports
            else:
                clean['symmetrixPortKey'] = ''

            self._f_data.append(clean)


class VMAXSRPool(VMAXFilter):

    def __init__(self, data):
        super(VMAXSRPool, self).__init__(data)

    def _clean(self):
        for to_clean in self._data:
            clean = OrderedDict()
            keys = ['srpId', 'emulation', 'total_usable_cap_gb',
                    'total_subscribed_cap_gb', 'total_allocated_cap_gb',
                    'total_snapshot_allocated_cap_gb',
                    'total_srdf_dse_allocated_cap_gb', 'reserved_cap_percent']

            for key in keys:
                clean[key] = to_clean[key]
            self._f_data.append(clean)


class VMAXStorageGroup(VMAXFilter):

    def __init__(self, data):
        super(VMAXStorageGroup, self).__init__(data)

    def _clean(self):
        for to_clean in self._data:
            clean = OrderedDict()
            keys = ['storageGroupId', 'num_of_masking_views', 'type',
                    'num_of_child_sgs', 'num_of_vols', 'cap_gb',
                    'fast_policy_name', 'parent_storage_groups',
                    'child_storage_groups', 'maskingview']

            for key in keys:
                if key not in to_clean:
                    clean[key] = ''  # Create and fill empty value
                else:
                    clean[key] = to_clean[key]

            self._f_data.append(clean)


class VMAXSystem(object):

    def __init__(self, data):
        self._data = data
        self._response = None
        self._clean()

    def _clean(self):
        clean = OrderedDict()
        keys = ['symmetrixId', 'model', 'ucode', 'device_count', ]
        for key in keys:
            clean[key] = self._data[key]

        # for key, value in self._data['physicalCapacity'].items():
        #    clean['physical_'+key] = value

        for key, value in self._data['virtualCapacity'].items():
            clean['virtual_'+key] = value

        self._response = clean

    def clean(self):
        return self._response


class VMAXThinDevice(VMAXFilter):

    def __init__(self, data):
        super(VMAXThinDevice, self).__init__(data)

    def _clean(self):
        for to_clean in self._data:
            clean = OrderedDict()
            keys = ['volumeId', 'wwn', 'cap_gb', 'cap_mb', 'cap_cyl',
                    'volume_identifier', 'status', 'type', 'allocated_percent',
                    'num_of_front_end_paths', 'num_of_storage_groups',
                    'storageGroupId']

            for key in keys:
                if key not in to_clean:
                    clean[key] = ''  # Create and fill empty value
                else:
                    clean[key] = to_clean[key]

            self._f_data.append(clean)


class VMAXThinPool(VMAXFilter):

    def __init__(self, data):
        super(VMAXThinPool, self).__init__(data)

    def _clean(self):
        for to_clean in self._data:
            clean = OrderedDict()
            keys = ['poolId', 'raid', 'diskTechnology', 'emulation',
                    'percent_allocated', 'percent_subscription',
                    'total_gb', 'enabled_gb', 'used_gb', 'free_gb']

            for key in keys:
                clean[key] = to_clean[key]
            self._f_data.append(clean)
