'''
Handle merging updated CSV subsets with CSV supersets.
'''
import csv

COL_COMPANY_NAME = 0
COL_CONTACT_NAME = 1
COL_CONTACT_EMAIL = 3
COL_STATUS = 5  # TODO: check row status before sending
COL_LAST_CONTACTED = 7


class Merger():
    def __init__(self, args):
        self.file1 = args.file
        self.file2 = args.mergefile
        self.outfile = args.mergeout

        self.f1reader = csv.reader(self.file1)
        self.f2reader = csv.reader(self.file2)
        self.outwriter = csv.writer(self.outfile)

        self.sponsor_index = {}
        self.__build_index()

    def __build_index(self):
        # Populate index with original rows from file1
        for row in self.f1reader:
            index_key = (row[COL_COMPANY_NAME] + row[COL_CONTACT_NAME] +
                         row[COL_CONTACT_EMAIL])
            if index_key in self.sponsor_index:
                print(index_key)
                raise ValueError('Multiple sponsors with same index key')
            self.sponsor_index[index_key] = row

        self.file1.close()

        # Use file2 to overwrite rows from file1 or create new rows
        for row in self.f2reader:
            index_key = (row[COL_COMPANY_NAME] + row[COL_CONTACT_NAME] +
                         row[COL_CONTACT_EMAIL])
            self.sponsor_index[index_key] = row

        self.file2.close()
        print(self.sponsor_index)

    def save_file(self):
        for index in self.sponsor_index:
            self.outwriter.writerow(self.sponsor_index[index])
