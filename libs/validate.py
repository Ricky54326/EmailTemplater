import csv
from madhacksbot import Sponsor

COL_COMPANY_NAME = 0
COL_CONTACT_NAME = 1
COL_CONTACT_EMAIL = 3
COL_STATUS = 5  # TODO: check row status before sending


def validate(args):
    reader = csv.reader(args.file)
    for row in reader:
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
