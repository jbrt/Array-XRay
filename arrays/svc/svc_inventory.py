#!/usr/bin/env python3
# coding: utf-8

import logging
from arrays.svc.svc_connector import SVCCommunicator
from arrays.svc.svc_filters import *
from arrays.xls_injector import XlsInjector


class SVCInventoryCollector(object):
    """ Describe how to collect information from SVC product """

    def __init__(self):
        self._formatter = None  # Format the output
        self._svc = None  # SVC array
        self._svc_name = None
        self._logger = logging.getLogger('arrayxray')
        # This list enforce the order of collecting methods
        self._order = [self._get_system,
                       self._get_vdisk,
                       self._get_mdisk_group,
                       self._get_mdisk,
                       self._get_host_map,
                       self._get_hosts,
                       self._get_fabric,
                       self._get_controller,
                       self._get_node,
                       self._get_users]

    def _system_first(self, dictionary):
        dictionary['System'] = self._svc_name
        dictionary.move_to_end('System', last=False)

    def _get_controller(self):
        self._logger.info('- Extraction of Controller')
        for controller in SVCController(self._svc.get_controller()):
            self._formatter.save(name='Controller', data=controller)
            self._system_first(controller)

    def _get_fabric(self):
        self._logger.info('- Extraction of Fabric')
        for fabric in SVCFabric(self._svc.get_fabric()):
            self._formatter.save(name='Fabric', data=fabric)
            self._system_first(fabric)

    def _get_hosts(self):
        self._logger.info('- Extraction of Hosts')
        for host in SVCHost(self._svc.get_hosts()):
            self._formatter.save(name='Hosts', data=host)
            self._system_first(host)

    def _get_host_map(self):
        self._logger.info('- Extraction of Host\'s mapping')
        for link in SVCHostVdiskMap(self._svc.get_mapping()):
            self._formatter.save(name='Mapping', data=link)
            self._system_first(link)

    def _get_mdisk(self):
        self._logger.info('- Extraction of Managed Disks')
        for disk in SVCMdisk(self._svc.get_mdisks()):
            self._formatter.save(name='Managed disks', data=disk)
            self._system_first(disk)

    def _get_mdisk_group(self):
        self._logger.info('- Extraction of Pools')
        for pool in SVCMdiskGroup(self._svc.get_mdiskgroups()):
            self._formatter.save(name='Pools', data=pool)
            self._system_first(pool)

    def _get_node(self):
        self._logger.info('- Extraction of Nodes')
        for node in SVCNode(self._svc.get_nodes()):
            self._formatter.save(name='Nodes', data=node)
            self._system_first(node)

    def _get_system(self):
        """
        Must be call in first position
        (system's name must be memorize before using the other methods)
        """
        self._logger.info('- Extraction of System\'s information')
        data = SVCSystem(self._svc.get_system()).clean()
        self._formatter.save(name='System', data=data)
        self._svc_name = data['Name']  # Memorize the system's name

    def _get_users(self):
        self._logger.info('- Extraction of Users')
        for user in SVCUser(self._svc.get_users()):
            self._formatter.save(name='Users', data=user)
            self._system_first(user)

    def _get_vdisk(self):
        self._logger.info('- Extraction of Vdisks')
        for disk in SVCVdisk(self._svc.get_vdisks()):
            self._formatter.save(name='Volumes', data=disk)
            self._system_first(disk)

    def collect(self, formatter: XlsInjector, array: SVCCommunicator):
        """
        Launch data collection
        :param formatter: Formatter object
        :param array: SVC to collect
        :return:
        """
        self._svc = array
        self._formatter = formatter

        self._logger.info('Beginning of data extraction %s' % self._svc)
        for collect_method in self._order:
            collect_method()

        self._logger.info('End of data extraction %s' % self._svc)
