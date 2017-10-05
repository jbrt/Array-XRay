#!/usr/bin/env python3
# coding: utf-8

"""
These objects are going to filter the input data and only keep the interesting
attributes. Convert of capacity units may be occur to stay more consistent
between arrays.
"""

from collections import OrderedDict


class VPLEXFilter(object):
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

    def _clean(self):
        raise NotImplementedError


class VPLEXCluster(VPLEXFilter):

    def __init__(self, data):
        super(VPLEXCluster, self).__init__(data)

    def _clean(self):
        for to_clean in self._data:
            clean = OrderedDict()
            keys = ['name', 'top-level-assembly', 'health-state',
                    'operational-status', 'cluster-id', 'island-id',
                    'default-cache-mode', 'director-names',
                    'default-xcopy-template']

            for key in keys:
                clean[key.capitalize()] = to_clean[key]
            self._f_data.append(clean)


class VPLEXInitiator(VPLEXFilter):

    def __init__(self, data):
        super(VPLEXInitiator, self).__init__(data)

    def _clean(self):
        for to_clean in self._data:
            clean = OrderedDict()
            clean['Cluster'] = to_clean['parent'].split('/')[2]
            keys = ['name', 'node-wwn', 'port-wwn',
                    'suspend-on-detach', 'target-ports']

            for key in keys:
                clean[key.capitalize()] = to_clean[key]
            self._f_data.append(clean)


class VPLEXStorageArray(VPLEXFilter):

    def __init__(self, data):
        super(VPLEXStorageArray, self).__init__(data)

    def _clean(self):
        for to_clean in self._data:
            clean = OrderedDict()
            clean['Cluster'] = to_clean['parent'].split('/')[2]
            clean['Array'] = to_clean['parent'].split('/')[5]
            keys = ['storage-volume', 'name', 'visibility',
                    'connectivity-status', 'alua-support',
                    'active-aao-visibility', 'luns']

            for key in keys:
                clean[key.capitalize()] = to_clean[key]
            self._f_data.append(clean)


class VPLEXView(VPLEXFilter):

    def __init__(self, data: list):
        super(VPLEXView, self).__init__(data)

    def _clean(self):
        for to_clean in self._data:
            for volume in to_clean['virtual-volumes']:
                clean = OrderedDict()
                members = volume.strip('(').strip(')').split(',')
                clean['Cluster'] = to_clean['parent'].split('/')[2]
                clean['Name'] = to_clean['name']
                clean['LUN-ID'] = members[0]
                clean['Volume'] = members[1]
                clean['NAA'] = members[2]
                clean['Size'] = members[3]
                lst = ['operational-status', 'initiators',
                       'ports', 'xcopy-enabled']

                for l in lst:
                    clean[l.capitalize()] = to_clean[l]

                self._f_data.append(clean)


class VPLEXVolume(VPLEXFilter):

    def __init__(self, data):
        super(VPLEXVolume, self).__init__(data)

    def _clean(self):
        for to_clean in self._data:
            clean = OrderedDict()
            clean['Cluster'] = to_clean['parent'].split('/')[2]
            clean['Name'] = to_clean['name']
            clean['Capacity_GB'] = int(int(to_clean['capacity'].split('B')[0]) / 1073741824)
            keys = ['locality', 'service-status', 'health-state',
                    'operational-status', 'consistency-group',
                    'supporting-device', 'vpd-id', 'expandable',
                    'expandable-capacity']

            for key in keys:
                clean[key.capitalize()] = to_clean[key]
            self._f_data.append(clean)
