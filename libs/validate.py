import csv
from madhacksbot import Sponsor

COL_COMPANY_NAME = 0
COL_CONTACT_NAME = 1
COL_CONTACT_EMAIL = 3
COL_STATUS = 5  # TODO: check row status before sending
COL_LAST_CONTACTED = 7


def validate(args):
    reader = csv.reader(args.file)
    for row in reader:
        # Basic validation (copied from madhacksbot.py)
        if len(row) < 3 or row[COL_COMPANY_NAME] == 'Company Name':
            continue
        elif row[COL_STATUS] != 'Not Contacted':
            print('Skipping row due to status field')
            continue
        elif row[COL_LAST_CONTACTED]:
            print('Skipping row due to last contact date.')
            continue

        try:
            Sponsor(row[COL_COMPANY_NAME], row[COL_CONTACT_NAME],
                    row[COL_CONTACT_EMAIL], None)
        except ValueError as err:
            print(err)
            print(row)
            print('')
        except IndexError as err:
            print(err)
            print(row)
            print('')
