#!/usr/bin/env python3
# coding: utf-8

import logging
from arrays.vmax.vmax_connector import BaseVMAXArray, VMAX2Array, VMAX3Array
from arrays.vmax.vmax_filters import *
from arrays.xls_injector import XlsInjector


class VMAXInventoryCollector(object):
    """ Describe how to collect information from VMAX array """

    def __init__(self):
        self._formatter = None  # Format the output
        self._vmax = None  # VMAX array
        self._vmax_id = None
        self._logger = logging.getLogger('arrayxray')
        # This list enforce the order of collecting methods
        self._order = [self._get_system,
                       self._get_thin_pools,
                       self._get_srp,
                       self._get_thin_devices,
                       self._get_initiators,
                       self._get_masking_views,
                       self._get_hosts,
                       self._get_host_groups,
                       self._get_port_groups,
                       self._get_storage_groups,
                       self._get_fast_policy]

    def _symid_first(self, dictionary):
        dictionary['Symmetrix Id'] = self._vmax_id
        dictionary.move_to_end('Symmetrix Id', last=False)

    def _get_fast_policy(self):
        if isinstance(self._vmax, VMAX2Array):
            self._logger.info('- Extraction of FAST Policies')
            for policy in VMAXFastPolicy(self._vmax.get_fast_policy()):
                self._symid_first(policy)
                self._formatter.save(name='FAST Policies', data=policy)

    def _get_hosts(self):
        self._logger.info('- Extraction of Hosts')
        for host in VMAXHost(self._vmax.get_hosts()):
            self._symid_first(host)
            self._formatter.save(name='InitiatorGroup', data=host)

    def _get_host_groups(self):
        self._logger.info('- Extraction of Host Groups')
        for host_group in VMAXHostGroup(self._vmax.get_host_groups()):
            self._symid_first(host_group)
            self._formatter.save(name='InitiatorGroupCascaded', data=host_group)

    def _get_initiators(self):
        self._logger.info('- Extraction of Initiators')
        for initiator in VMAXInitiator(self._vmax.get_initiators()):
            self._symid_first(initiator)
            self._formatter.save(name='WWNs', data=initiator)

    def _get_masking_views(self):
        self._logger.info('- Extraction of Masking Views')
        for view in VMAXMaskingView(self._vmax.get_masking_view()):
            self._symid_first(view)
            self._formatter.save(name='Masking Views', data=view)

    def _get_port_groups(self):
        self._logger.info('- Extraction of Port Groups')
        for port_group in VMAXPortGroup(self._vmax.get_port_groups()):
            self._symid_first(port_group)
            self._formatter.save(name='PortGroups', data=port_group)

    def _get_srp(self):
        if isinstance(self._vmax, VMAX3Array):
            self._logger.info('- Extraction of SRPs')
            for pool in VMAXSRPool(self._vmax.get_srp()):
                self._symid_first(pool)
                self._formatter.save(name='SRPs', data=pool)

    def _get_storage_groups(self):
        self._logger.info('- Extraction of Storage Groups')
        for storage_group in VMAXStorageGroup(self._vmax.get_storage_group()):
            self._symid_first(storage_group)
            self._formatter.save(name='StorageGroups', data=storage_group)

    def _get_system(self):
        """
        Must be call in first position
        (system's name must be memorize before using the other methods)
        """
        self._logger.info('- Extraction of System\'s information')
        data = VMAXSystem(self._vmax.get_system()).clean()
        self._formatter.save(name='Arrays', data=data)
        self._vmax_id = data['symmetrixId']  # Memorize the system's name

    def _get_thin_devices(self):
        self._logger.info('- Extraction of TDEVs')
        for device in VMAXThinDevice(self._vmax.get_thin_volumes()):
            self._symid_first(device)
            self._formatter.save(name='TDEVs', data=device)

    def _get_thin_pools(self):
        if isinstance(self._vmax, VMAX2Array):
            self._logger.info('- Extraction of Thin Pools')
            for pool in VMAXThinPool(self._vmax.get_thin_pool()):
                self._symid_first(pool)
                self._formatter.save(name='ThinPools', data=pool)

    def collect(self, formatter: XlsInjector, array: BaseVMAXArray):
        """
        Launch data collection
        :param formatter: Formatter object
        :param array: SVC to collect
        :return:
        """
        self._vmax = array
        self._formatter = formatter

        self._logger.info('Beginning of data extraction %s' % self._vmax)
        for collect_method in self._order:
            collect_method()

        self._logger.info('End of data extraction %s' % self._vmax)
