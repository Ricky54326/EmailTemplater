import csv
from libs.constants import *


def compute_data_entry_stats(args):
    total_rows = 0.0  # Need float for Python 2 division
    need_contact_name = 0
    need_email = 0

    reader = csv.reader(args.file)
    for row in reader:
        if row[COL_COMPANY_NAME] and row[COL_COMPANY_NAME] != 'Company Name':
            total_rows += 1
            if not row[COL_CONTACT_NAME]:
                need_contact_name += 1
            if not row[COL_CONTACT_EMAIL]:
                need_email += 1

    print('Statistics:')
    print(' %i sponsors total' % total_rows)
    print(' %i sponsors need email addresses: that\'s %i%%' %
          (need_email, need_email / total_rows * 100))
    print(' %i sponsors need names; that\'s %i%%' %
          (need_contact_name, need_contact_name / total_rows * 100))
