# Django specific settings
import os
import xlsxwriter
from tqdm import tqdm
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
# Ensure settings are read
application = get_wsgi_application()

from game.models import FirmPosition, FirmPrice, FirmProfit, Room, Round, RoundComposition, RoundState


def main():

    save_path = "data/excel_data.xlsx"
    workbook = xlsxwriter.Workbook(save_path)

    data = get_formatted_data()

    write_table_to_workbook(workbook, data, "all_data")


def get_formatted_data():

    cols = (
        "room_id",
        "radius",
        "opponent_score_displayed",
        "round_id",
        "round",
        "firm0_id",
        "firm0_price",
        "firm0_position",
        "firm0_profit",
        "firm1_id",
        "firm1_price",
        "firm1_position",
        "firm1_profit",
        "t",
    )

    data = [cols, ]

    rooms = Room.objects.filter(state="end").order_by("id")

    for rm in tqdm(rooms):

        for rd in Round.objects.filter(room_id=rm.id):

            pvp = int(rd.pvp)

            firm_ids = [
                RoundComposition.objects.filter(round_id=rd.id, firm_id=0).first().user_id,
                RoundComposition.objects.filter(round_id=rd.id, firm_id=1).first().user_id
            ]

            active_player_t0 = RoundState.objects.filter(round_id=rd.id, t=0).first().firm_active

            if active_player_t0 == 1:
                cond = \
                    FirmPosition.objects.get(agent_id=0, t=0, round_id=rd.id).value == 0 and \
                    FirmPrice.objects.get(agent_id=0, t=0, round_id=rd.id).value == 5
            else:
                cond = \
                    FirmPosition.objects.get(agent_id=1, t=0, round_id=rd.id).value == 20 and \
                    FirmPrice.objects.get(agent_id=1, t=0, round_id=rd.id).value == 5

            if cond:
                for t in range(rm.ending_t):

                    row = [rm.id, rm.radius, int(rm.display_opponent_score), rd.id, pvp]

                    for firm_id in (0, 1):

                        user_id = firm_ids[firm_id]

                        row.append(user_id)

                        row.append(
                            FirmPrice.objects.get(agent_id=firm_id, round_id=rd.id, t=t).value
                        )

                        row.append(
                            FirmPosition.objects.get(agent_id=firm_id, round_id=rd.id, t=t).value
                        )

                        row.append(
                            FirmProfit.objects.get(t=t+1, round_id=rd.id, agent_id=firm_id).value -
                            FirmProfit.objects.get(t=t, round_id=rd.id, agent_id=firm_id).value
                        )

                    row.append(t)

                    data.append(row)

    return data


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


if __name__ == '__main__':
    main()
