#!/usr/bin/env python3
# coding: utf-8

"""
Abstract class Injector.
Define the behavior of all injectors.
"""

import logging
from abc import ABCMeta, abstractmethod


class Injector(object, metaclass=ABCMeta):
    """
    Abstract class Formatter
    Purpose of that class : define the behavior of a formatter object
    """

    def __init__(self):
        self._logger = logging.getLogger('arrayxray')

    @abstractmethod
    def save(self, *args, **kwargs):
        raise NotImplementedError
