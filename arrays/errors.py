#!/usr/bin/env python3
# coding: utf-8


class ConfigurationError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class SVCConnectorError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class VmaxInventoryFactoryError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class VMAXConnectionError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class VPLEXConnectionError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class XlsFormatterError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)
