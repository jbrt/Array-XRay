#!/usr/bin/env python3
# coding: utf-8

"""
A generic configuration file parser
"""

import configparser
import logging
import os
from arrays.errors import ConfigurationError


class ConfigFileParser(object):
    """ Validate the content of the config file """

    def __init__(self, file: str):
        """
        Constructor
        :param file: config file to parse
        """

        self._logger = logging.getLogger('arrayxray')

        if not os.path.isfile(file):
            self._logger.error('Unknown file %s' % file)
            raise ConfigurationError

        if not os.access(file, os.R_OK):
            self._logger.error('Insufficient rights on %s' % file)
            raise ConfigurationError

        self._config = configparser.ConfigParser()

        try:
            self._config.read(file)
        except configparser.MissingSectionHeaderError:
            self._logger.error('Incorrect config file. Please check syntax.')
            raise ConfigurationError

        self._validate()

    def _validate(self):
        """ Validate the configuration file syntax """

        # Values that needs to be present in a right configuration file
        values = ['address', 'user', 'password']
        for section in self._config.sections():
            # TEMPORARY UNUSED: VMAX specific check
            # if not (len(section) == 12 and section.isnumeric()):
            #     self._logger.error('%s is not a valid SID number' % section)
            #     raise ConfigurationError

            for value in values:
                if value not in self._config[section]:
                    msg = '%s not in %s section' % (value, section)
                    self._logger.error(msg)
                    raise ConfigurationError

                if not self._config[section][value]:
                    self._logger.error('%s item cannot be empty' % value)
                    raise ConfigurationError

    def get_arrays(self):
        """ Generator - Extract the configuration items from the configuration """

        for section in self._config.sections():
            address = self._config[section]['address']
            user = self._config[section]['user']
            password = self._config[section]['password']

            yield section, address, user, password
