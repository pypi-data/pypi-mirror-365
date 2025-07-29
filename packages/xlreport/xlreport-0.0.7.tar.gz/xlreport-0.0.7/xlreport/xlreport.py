#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import subprocess
import sys
from itertools import zip_longest
from math import log

import xlsxwriter as xls

# Platform-specific font selection for optimal compatibility
if sys.platform.startswith('win'):
    HEADER_FONT_NAME = "Times New Roman"
    GEN_FONT_NAME = "Arial"
elif sys.platform == 'darwin':
    HEADER_FONT_NAME = "Times New Roman"
    GEN_FONT_NAME = "Helvetica"
elif sys.platform.startswith('lin'):
    HEADER_FONT_NAME = "Liberation Serif"
    GEN_FONT_NAME = "Liberation Sans"
else:
    # Fallback for other systems
    HEADER_FONT_NAME = "DejaVu Serif"
    GEN_FONT_NAME = "DejaVu Sans"

FONT_SIZE = 9
WRAP_FONT_SIZE = 7
TITLE_RANGE = "B1:E1"
HEADER_BG_COLOR = "#D4D0C8"
HEADER_FONT_COLOR = "#003366"
NUM_FORMAT = "0.00;[RED]-0.00"
TITLE_BG = "#F1F1F1"
DEFAULT_COLUMN_WIDTH = 10
MAX_COLUMN_WIDTH = 50
MAX_CELL_CONTENT_LENGTH = 200


def ensure_unicode(input_value):
    """Convert input to unicode string if needed."""
    if isinstance(input_value, bytes):
        return input_value.decode("utf-8", errors="replace")
    return str(input_value)


def open_file(filename):
    """Open file with default application based on OS."""
    try:
        if sys.platform == "win32":
            os.startfile(filename)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.run([opener, filename], check=True)
    except Exception:
        pass


def is_nested(iterable):
    """Check if input is a nested iterable."""
    if not hasattr(iterable, "__iter__") or isinstance(iterable, (str, bytes)):
        return False
    try:
        first = next(iter(iterable))
        return hasattr(first, "__iter__") and not isinstance(first, (str, bytes))
    except (StopIteration, TypeError):
        return False


class Exfile:
    """Class for creating Excel files with formatted worksheets."""

    def __init__(self, filename):
        """Initialize with output filename."""
        if not filename.lower().endswith(".xlsx"):
            raise ValueError("Filename must end with .xlsx")
        self.filename = os.path.abspath(filename)
        self.workbook = xls.Workbook(self.filename)
        self._formats = {}
        self.worksheet_names = []

    def _get_format(self, format_properties):
        """Get cached format or create new one."""
        key = frozenset(format_properties.items())
        if key not in self._formats:
            self._formats[key] = self.workbook.add_format(format_properties)
        return self._formats[key]

    @staticmethod
    def calculate_column_width(text_length):
        """Calculate column width based on content length."""
        if text_length <= 3:
            return 3
        if text_length > 100:
            return MAX_COLUMN_WIDTH
        width = (51.16 * log(text_length) - 38.395) * 0.85 / 10 + (log(text_length) * 2)
        extra = text_length / 10 if text_length > 20 else 0
        return min(max(width + extra, 3), MAX_COLUMN_WIDTH)

    def write(self, data_list, title, worksheet_name=None, wrap=False):
        """Write data to worksheet with formatting."""
        datatype = repr(type(data_list)).lower()

        assert re.search("list|dict_values|dataframe|array|tuple|set|series", datatype)
        if hasattr(data_list, "to_records"):
            data_list = [list(data_list.columns)] + list(data_list.to_records(index=False))
        elif not is_nested(data_list):
            data_list = list(zip_longest(data_list, fillvalue=""))

        if worksheet_name is None:
            worksheet = self.workbook.add_worksheet()
        else:
            wname = ensure_unicode(worksheet_name)
            try:
                worksheet = self.workbook.add_worksheet(wname)
            except xls.exceptions.DuplicateWorksheetName:
                worksheet = self.workbook.add_worksheet(f"{wname}-2")

        start_row, start_col = 4, 1

        # Write title
        worksheet.merge_range(
            TITLE_RANGE, ensure_unicode(title),
            self._get_format({
                "bold": 1,
                "border": 1,
                "align": "center",
                "fg_color": TITLE_BG,
                "text_wrap": True,
                "font_name": HEADER_FONT_NAME,
                "font_size": 12
            }))

        # Write headers
        headers = data_list[0]
        for col_idx, header in enumerate(headers):
            worksheet.set_column(start_col + col_idx, start_col + col_idx,
                                 self.calculate_column_width(len(repr(header))))
            worksheet.write(
                start_row - 1, start_col + col_idx,
                ensure_unicode(header).strip(),
                self._get_format({
                    "bold": 1,
                    "font_color": HEADER_FONT_COLOR,
                    "font_size": FONT_SIZE,
                    "bg_color": HEADER_BG_COLOR,
                    "indent": 1
                }))

        worksheet.freeze_panes(start_row, 0)

        # Write data
        for row_idx, row_data in enumerate(data_list[1:]):
            for col_idx, cell_value in enumerate(row_data):
                if cell_value is None:
                    continue
                try:
                    if isinstance(cell_value, str):
                        fmt = self._get_format({
                            "text_wrap": wrap,
                            "font_size": WRAP_FONT_SIZE if wrap else FONT_SIZE,
                            "align": "vcenter" if wrap else "left",
                            "font_name": GEN_FONT_NAME
                        })
                        worksheet.write(start_row + row_idx, start_col + col_idx,
                                        ensure_unicode(cell_value), fmt)
                    else:
                        fmt = self._get_format({
                            "num_format":
                                NUM_FORMAT if isinstance(cell_value, float) and
                                not cell_value.is_integer() else "#,##0;[Red]-#,##0",
                            "font_size":
                                FONT_SIZE,
                            "font_name":
                                GEN_FONT_NAME
                        })
                        worksheet.write(start_row + row_idx, start_col + col_idx, cell_value, fmt)
                except (TypeError, ValueError):
                    worksheet.write(
                        start_row + row_idx, start_col + col_idx,
                        str(cell_value)[:MAX_CELL_CONTENT_LENGTH],
                        self._get_format({
                            "font_size": FONT_SIZE,
                            "font_name": GEN_FONT_NAME
                        }))

        return worksheet

    def add_links(self):
        """Add navigation links between worksheets."""
        worksheets = self.workbook.worksheets()
        for source_sheet in worksheets:
            for link_idx, target_sheet in enumerate(worksheets):
                source_sheet.write_url(
                    0, 6 + link_idx, f"internal:'{target_sheet.name}'!A1",
                    self._get_format({
                        "font_color": "gray" if target_sheet.name == source_sheet.name else "blue",
                        "bold": 0,
                        "underline": 1
                    }) if target_sheet.name == source_sheet.name else None, target_sheet.name)

    def save(self, start=True):
        """Save workbook and optionally open file."""
        try:
            self.workbook.close()
            if start:
                open_file(self.filename)
        except PermissionError:
            print("! Cannot write file - permission error")
            raise
        except Exception:
            print("! Error saving file")
            raise


def to_file(xls_name, inlist, header_list=None, title="Title", shname="sheet1", wrap=False):
    """Convenience function to create Excel file from data."""
    exfile = Exfile(xls_name)
    if header_list:
        if hasattr(inlist, "to_records"):
            inlist = list(inlist.to_records())
        if hasattr(inlist, "tolist"):
            inlist = inlist.tolist()
        inlist.insert(0, header_list)
    exfile.write(inlist, title, shname, wrap=wrap)
    try:
        exfile.save()
    except PermissionError:
        print("!-File probably opened")
        sys.exit(1)


def generate_random_data(num_rows=10):
    import random
    import string
    from datetime import datetime, timedelta

    unicode_ranges = [
        (0x0020, 0x007E),  # Basic Latin (printable ASCII)
        (0x00A0, 0x00FF),  # Latin-1 Supplement (e.g., accented characters)
        (0x0100, 0x017F),  # Latin Extended-A (more European characters)
        # (0x0370, 0x03FF),  # Greek and Coptic
    ]

    def gen_datetime(min_year=1900, max_year=datetime.now().year):
        # generate a datetime in format yyyy-mm-dd hh:mm:ss.000000
        start = datetime(min_year, 1, 1, 00, 00, 00)
        years = max_year - min_year + 1
        end = start + timedelta(days=365 * years)
        return start + (end - start) * random.random()

    def get_random_unicode_char():
        """Get a random Unicode character from various language ranges."""
        range_start, range_end = random.choice(unicode_ranges)
        code_point = random.randint(range_start, range_end)
        try:
            return chr(code_point)
        except ValueError:
            return chr(random.randint(0x00C0, 0x00FF))

    header = ["col1", "col2", "col3", "col4", "col5", "col6"]

    result = [header]
    for _ in range(num_rows):
        row = [
            random.choice(string.ascii_letters),
            random.randint(100, 100000),
            random.uniform(-1, 1),
            get_random_unicode_char(),
            random.choice([True, False]),
            str(gen_datetime()),
        ]
        result.append(row)

    return result


def test_numpy():
    from numpy.random import default_rng
    arr = default_rng(42).random((100, 4))
    header = ["col1", "col2", "col3", "col4"]
    to_file("test.xlsx", arr, header, title="Test numpy")


def test_df():
    import numpy as np
    import pandas as pd

    df = pd.DataFrame({
        "col1": ["A", "A", False, np.nan, "D", "C"],
        "col2": [2, 1, 9, -8, 7, -4],
        "col3": [-0.8, 1, 9, 4, 2, 3],
        "col4": ["a", "B", "c", "D", True, "F"],
    })
    # df = list(range(100))
    to_file("testdf.xlsx", df, title="Test dataframe")


def test_1d():
    r = list(range(100))
    to_file("simplelist.xlsx", r, title="Simple list")


if __name__ == "__main__":
    test_df()
