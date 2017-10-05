#!/usr/bin/env python3
# coding: utf-8

import logging
from arrays.vplex.vplex_connector import VPLEXCommunicator
from arrays.vplex.vplex_filters import *
from arrays.xls_injector import XlsInjector


class VPLEXInventoryCollector(object):
    """ Describe how to collect information from VPLEX products """

    def __init__(self):
        self._formatter = None  # Format the output
        self._vp = None  # VPLEX array
        self._logger = logging.getLogger('arrayxray')
        self._order = [self._get_clusters,
                       self._get_volumes,
                       self._get_initiators,
                       self._get_views,
                       self._get_storage_arrays]

    def _get_clusters(self):
        self._logger.info('- Extraction of clusters')
        for cluster in VPLEXCluster(self._vp.get_clusters()):
            self._formatter.save(name='Clusters', data=cluster)

    def _get_initiators(self):
        self._logger.info('- Extraction of initiators')
        for init in VPLEXInitiator(self._vp.get_initiators()):
            self._formatter.save(name='Initiators', data=init)

    def _get_storage_arrays(self):
        self._logger.info('- Extraction of Storage Arrays')
        for array in VPLEXStorageArray(self._vp.get_storage_arrays()):
            self._formatter.save(name='Storage Arrays', data=array)

    def _get_views(self):
        self._logger.info('- Extraction of masking views')
        for view in VPLEXView(self._vp.get_storage_views()):
            self._formatter.save(name='Storage Views', data=view)

    def _get_volumes(self):
        self._logger.info('- Extraction of TDEVs')
        for volume in VPLEXVolume(self._vp.get_virtual_volumes()):
            self._formatter.save(name='Virtual Volumes', data=volume)

    def collect(self, formatter: XlsInjector, array: VPLEXCommunicator):
        self._vp = array
        self._formatter = formatter

        self._logger.info('Beginning of data extraction %s' % self._vp)
        for collect_method in self._order:
            collect_method()

        self._logger.info('End of data extraction %s' % self._vp)
