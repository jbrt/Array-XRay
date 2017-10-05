#!/usr/bin/env python3
# coding: utf-8

"""
These objects are going to filter the input data and only keep the interesting
attributes. Convert of capacity units may be occur to stay more consistent
between arrays.
"""

import abc
from collections import OrderedDict


class SVCFilter(object, metaclass=abc.ABCMeta):
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


class SVCController(SVCFilter):

    def __init__(self, data):
        super(SVCController, self).__init__(data)

    def _clean(self):
        for to_clean in self._data:
            clean = OrderedDict()
            keys = ['id', 'controller_name', 'ctrl_s/n', 'vendor_id',
                    'product_id_low', 'product_id_high', 'site_id',
                    'site_name']

            for key in keys:
                clean[key.capitalize()] = to_clean[key]
            self._f_data.append(clean)


class SVCFabric(SVCFilter):

    def __init__(self, data):
        super(SVCFabric, self).__init__(data)

    def _clean(self):
        for to_clean in self._data:
            clean = OrderedDict()
            keys = ['remote_wwpn', 'remote_nportid', 'id', 'node_name',
                    'local_wwpn', 'local_port', 'local_nportid', 'state',
                    'name', 'cluster_name', 'type']

            for key in keys:
                clean[key.capitalize()] = to_clean[key]
            self._f_data.append(clean)


class SVCHost(SVCFilter):

    def __init__(self, data):
        super(SVCHost, self).__init__(data)

    def _clean(self):
        for to_clean in self._data:
            clean = OrderedDict()
            keys = ['id', 'name', 'port_count', 'iogrp_count', 'status',
                    'site_id', 'site_name']

            for key in keys:
                clean[key.capitalize()] = to_clean[key]
            self._f_data.append(clean)


class SVCHostVdiskMap(SVCFilter):

    def __init__(self, data):
        super(SVCHostVdiskMap, self).__init__(data)

    def _clean(self):
        for to_clean in self._data:
            clean = OrderedDict()
            keys = ['id', 'name', 'SCSI_id', 'vdisk_id', 'vdisk_name',
                    'vdisk_UID', 'IO_group_id', 'IO_group_name']

            for key in keys:
                clean[key.capitalize()] = to_clean[key]
            self._f_data.append(clean)


class SVCMdisk(SVCFilter):

    def __init__(self, data):
        super(SVCMdisk, self).__init__(data)

    def _clean(self):
        for to_clean in self._data:
            clean = OrderedDict()
            keys = ['id', 'name', 'status', 'mode', 'mdisk_grp_id',
                    'mdisk_grp_name']

            for key in keys:
                clean[key.capitalize()] = to_clean[key]

            clean['Capacity_GB'] = self._bytes_to_gb(to_clean['capacity'])

            keys = ['ctrl_LUN_#', 'controller_name', 'UID', 'tier', 'encrypt',
                    'site_id', 'site_name']

            for key in keys:
                clean[key.capitalize()] = to_clean[key]
            self._f_data.append(clean)


class SVCMdiskGroup(SVCFilter):

    def __init__(self, data):
        super(SVCMdiskGroup, self).__init__(data)

    def _clean(self):
        for to_clean in self._data:
            clean = OrderedDict()
            keys = ['id', 'name', 'status', 'mdisk_count', 'vdisk_count',
                    'extent_size']

            for key in keys:
                clean[key.capitalize()] = to_clean[key]

            keys = ['capacity', 'free_capacity', 'virtual_capacity',
                    'used_capacity', 'real_capacity']

            for key in keys:
                clean[key.capitalize() + '_GB'] = self._bytes_to_gb(to_clean[key])

            keys = ['overallocation', 'warning', 'easy_tier', 'easy_tier_status',
                    'compression_active', 'parent_mdisk_grp_id',
                    'parent_mdisk_grp_name', 'child_mdisk_grp_count',
                    'child_mdisk_grp_capacity', 'type', 'encrypt', 'owner_type',
                    'site_id', 'site_name']

            for key in keys:
                clean[key.capitalize()] = to_clean[key]
            self._f_data.append(clean)


class SVCNode(SVCFilter):

    def __init__(self, data):
        super(SVCNode, self).__init__(data)

    def _clean(self):
        for to_clean in self._data:
            clean = OrderedDict()
            keys = ['id', 'name', 'UPS_serial_number', 'WWNN', 'status',
                    'IO_group_id', 'IO_group_name', 'config_node',
                    'UPS_unique_id', 'hardware', 'iscsi_name', 'iscsi_alias',
                    'panel_name', 'enclosure_id', 'canister_id',
                    'enclosure_serial_number', 'site_id', 'site_name']

            for key in keys:
                clean[key.capitalize()] = to_clean[key]
            self._f_data.append(clean)


class SVCSystem(object):
    """
    This object filters data's from a lssystem command.
    The output of this command is slightly different
    from the other ones. There is no list here to
    processing, only a dictionary. No iterator needed.
    """

    def __init__(self, data):
        self._data = data
        self._f_data = None
        self._bytes_to_gb = lambda x: int(int(x) / 1073741824)
        self._clean()

    def _clean(self):
        clean = OrderedDict()
        keys = ['id', 'product_name', 'name', 'location', 'total_overallocation']

        for key in keys:
            clean[key.capitalize()] = self._data[key]

        keys = ['total_mdisk_capacity',
                'space_in_mdisk_grps', 'space_allocated_to_vdisks',
                'total_free_space', 'total_vdiskcopy_capacity',
                'total_used_capacity', 'total_vdisk_capacity',
                'total_allocated_extent_capacity', 'compression_virtual_capacity',
                'compression_compressed_capacity',
                'compression_uncompressed_capacity']

        for key in keys:
            clean[key.capitalize() + '_GB'] = self._bytes_to_gb(self._data[key])

        keys = ['time_zone', 'code_level', 'email_reply', 'email_contact',
                'cluster_ntp_IP_address', 'compression_active',
                'email_organization', 'email_machine_address', 'email_machine_city']

        for key in keys:
            clean[key.capitalize()] = self._data[key]

        self._f_data = clean

    def clean(self):
        return self._f_data


class SVCUser(SVCFilter):

    def __init__(self, data):
        super(SVCUser, self).__init__(data)

    def _clean(self):
        for to_clean in self._data:
            clean = OrderedDict()
            keys = ['id', 'name', 'password', 'ssh_key', 'remote',
                    'usergrp_id', 'usergrp_name']

            for key in keys:
                clean[key.capitalize()] = to_clean[key]
            self._f_data.append(clean)


class SVCVdisk(SVCFilter):

    def __init__(self, data):
        super(SVCVdisk, self).__init__(data)

    def _clean(self):
        for to_clean in self._data:
            clean = OrderedDict()
            keys = ['id', 'name', 'IO_group_id', 'IO_group_name', 'status',
                    'mdisk_grp_id', 'mdisk_grp_name']

            for key in keys:
                clean[key.capitalize()] = to_clean[key]

            clean['Capacity_GB'] = self._bytes_to_gb(to_clean['capacity'])

            keys = ['type', 'vdisk_UID', 'fc_map_count', 'copy_count',
                    'fast_write_state', 'se_copy_count', 'RC_change',
                    'compressed_copy_count', 'parent_mdisk_grp_id',
                    'parent_mdisk_grp_name', 'formatting']

            for key in keys:
                clean[key.capitalize()] = to_clean[key]
            self._f_data.append(clean)
