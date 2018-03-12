# Django specific settings
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
# Ensure settings are read
application = get_wsgi_application()

from game.models import FirmPosition, FirmPrice, FirmProfit, Room, Round

import xlsxwriter
import sqlite3


def main():

    workbook = xlsxwriter.Workbook(self.save_path)

    data = get_formatted_data()


# def


def write_table_to_workbook(workbook, table, worksheet_name):

    """
    Write table data to excel workbook (add a worksheet)
    :param table: the content of the table
    :param workbook: the workbook (excel file)
    :param worksheet_name: the worksheet name
    :return: the workbook with worksheet added
    """

    worksheet = workbook.add_worksheet(worksheet_name)

    # prepare column title format
    title = workbook.add_format({'bold': True})
    title.set_bottom()

    # prepare data format (alignment)
    align = workbook.add_format()
    align.set_align("left")

    rows = table
    cols = range(len(table[0]))

    # fit column size to content
    for col_number in cols:

        max_width = \
            max(len(str(rows[j][col_number])) for j in range(len(rows)))

        worksheet.set_column(col_number, col_number, max_width)

    # Iterate over the data and write it out row by row
    # Format column title if row == 0
    for row_number, row in enumerate(rows):
        for col_number in cols:

            if row_number == 0:
                worksheet.write(row_number, col_number, row[col_number], title)
            else:
                worksheet.write(row_number, col_number, row[col_number], align)

    return workbook


if __name__ == '__main__':
