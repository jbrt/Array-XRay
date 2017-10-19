#!/usr/bin/env python3
# coding: utf-8

"""
This module contain classes for saving data under XLS format.
"""

import os
import logging
import xlsxwriter
from arrays.injector import Injector
from arrays.errors import XlsFormatterError
from datetime import datetime

__author__ = 'Julien B.'


class XlsInjector(Injector):
    """ Format the data under an XLS file """

    def __init__(self, directory: str, filename: str):
        """Constructor
        :param directory: Where create the inventory file
        :param filename: Filename of that Excel workbook
        """
        super().__init__()

        if not os.path.isdir(directory):
            self._logger.error('Path incorrect (%s)' % directory)
            raise XlsFormatterError

        if not os.access(directory, os.W_OK):
            self._logger.error('Insufficient rights on %s' % directory)
            raise XlsFormatterError

        # If the file is already open, add a timestamp to the filename
        try:
            file = os.path.join(directory, filename)
            if os.path.isfile(file):
                open(file, 'rb+')
        except (PermissionError, OSError):
            msg = '%s already open. Add a time to the filename' % filename
            self._logger.warning(msg)
            timestamp = datetime.now().strftime('_%Y-%m-%d_%Hh%Mm%Ss.')
            filename = timestamp.join(filename.split('.'))

        self._sheets = {}
        self._logger.info('Initializing a Excel workbook (%s)' % filename)
        self._book = xlsxwriter.Workbook(os.path.join(directory, filename))
        self._book.set_properties({'title':    'Array-XRay Inventory',
                                   'subject':  'Make an inventory of storage arrays',
                                   'author':   'Julien B.',
                                   'category': 'SAN Storage',
                                   'keywords': 'SAN, Symmetrix, VMAX, SVC, VPLEX',
                                   'comments': "It's better when it's not a "
                                               "manual task :-)"})

    def __del__(self):
        self._logger.debug('Now closing the workbook')
        self._book.close()

    def save(self, *args, **kwargs):
        name = kwargs['name']
        data = kwargs['data']
        if name not in self._sheets:
            self._sheets[name] = XlsSheet(self._book, name)
        self._sheets[name].add_row(data)


class XlsSheet(object):
    """ Abstract class that define the behavior of a Excel sheet """

    def __init__(self, workbook, sheet_name):
        """ Constructor

        :param workbook: Workbook Excel
        :param sheet_name: name for the sheet
        """
        self._column_width = {}  # To memorize the width of each cell
        self._header_exists = False  # Switch for creating the header the fist time
        self._current_row = 1

        self._logger = logging.getLogger('arrayxray')
        self._book = workbook
        self._sheet = workbook.add_worksheet(sheet_name)

    def _initialize_header(self, data):
        """ Define the sheet header format """

        column_format = self._book.add_format({'bold': True,
                                               'align': 'center',
                                               'bg_color': 'C5D9F1',
                                               'top': 1,
                                               'left': 1,
                                               'right': 1,
                                               'bottom': 1})

        for index, label in enumerate(data):
            self._sheet.write(0, index, label, column_format)
            self._memorize_width(index, len(label))

        self._sheet.autofilter(0, 0, 0, len(data)-1)
        self._sheet.freeze_panes('A2')
        self._header_exists = True

    def _memorize_width(self, column, number_of_char):
        """ Memorize the width of each cells """
        if column not in self._column_width:
            self._column_width[column] = [number_of_char]
        else:
            self._column_width[column].append(number_of_char)

    def add_row(self, data):
        """
        Adding a new line to the sheet
        :param data: data for the new line (dict)
        """
        if not self._header_exists:
            self._initialize_header(data)

        cell_format = self._book.add_format({'align': 'left',
                                             'top': 1,
                                             'left': 1,
                                             'right': 1,
                                             'bottom': 1})
        for column, key in enumerate(data):
            value = data[key] if not isinstance(data[key], list) else ', '.join(data[key])
            self._sheet.write(self._current_row, column, value, cell_format)
            self._memorize_width(column, len(str(value)))

        # Set the width of the column to the right size
        # Take the highest value as column size (with a little padding)
        for col, key in enumerate(data):
            self._sheet.set_column(col, col, max(self._column_width[col])+5)

        self._current_row += 1
