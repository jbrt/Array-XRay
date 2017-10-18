#!/usr/bin/env python3
# coding: utf-8

import argparse
import logging
import sys
from arrays.parser import ConfigFileParser
from arrays.vmax.vmax_connector import VMAXArrayFactory
from arrays.xls_injector import XlsInjector
from arrays.vmax.vmax_inventory import VMAXInventoryCollector
from arrays.errors import *

__author__ = 'Julien B.'

logger = logging.getLogger('arrayxray')
stream = logging.StreamHandler()
logger.addHandler(stream)


def main(arguments):
    try:
        config = ConfigFileParser(file=arguments.config)
    except ConfigurationError as error:
        logger.critical('Error while parsing configuration: %s' % error)
        sys.exit(1)

    filename = arguments.file
    path = arguments.path if arguments.path else '.'
    try:
        formatter = XlsInjector(directory=path, filename=filename)
    except XlsFormatterError as error:
        logger.critical('Error while creation file: %s' % error)
        sys.exit(2)

    for array, address, user, password in config.get_arrays():
        logger.info('\nInventory of VMAX: %s' % array)
        try:
            vmax = VMAXArrayFactory(array, address, user, password)
        except VmaxInventoryFactoryError as error:
            logger.error('Can\'t generate a VMAX connector (%s)' % error)
            sys.exit(2)

        try:
            collector = VMAXInventoryCollector()
            collector.collect(formatter=formatter, array=vmax)

        except XlsFormatterError as error:
            logger.critical('Error while writing file: %s' % error)
            sys.exit(2)
        except VMAXConnectionError as error:
            logger.error('Problem : %s' % error)
            logger.warning('Skip this one and go ahead')
            continue
    del formatter


if __name__ == '__main__':
    msg = 'VMAX-XRay - Tool for Inventory a VMAX array'
    parser = argparse.ArgumentParser(description=msg)
    parser.add_argument('-c', '--config', type=str, help='config file', required=True)
    parser.add_argument('-p', '--path', type=str, help='path to store file', required=True)
    parser.add_argument('-f', '--file', type=str, help='name of the file', required=True)
    parser.add_argument('-d', '--debug', action='store_true', default=False,
                        help='enable debug mode')

    args = parser.parse_args()
    logger.setLevel(logging.DEBUG) if args.debug else logger.setLevel(logging.INFO)
    main(args)
