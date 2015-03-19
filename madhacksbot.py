#! /usr/bin/python
__author__ = 'riccardo mutschlechner'

import argparse
import smtplib  # SMTP email
import csv  # CSV parsing
import re  # regex
from email.mime.multipart import MIMEMultipart  # moar SMTP email
from email.mime.text import MIMEText  # even moar SMTP email
from keys import getkey, getlogin  # login/pass for email acct, needs to be created locally
import time

from libs.constants import *


class Sponsor():
    # Some of these are valid in emails, but we should be careful
    bad_characters = (';', '/', '\\', '"', '(', ')', ',')

    def __init__(self, name, contactName, email, tier=None):
        self.name = self.__validate(name)
        self.contactName = self.__validate(contactName)
        self.email = self.__validate(email, extrachars=[' '])

        if tier:  # TODO: when tier is used, remove the if statement
            self.tier = self.__validate(tier)

    def get_first_name(self):
        return self.contactName.split(' ', 1)[0]

    def __str__(self):
        return ('%s: %s, %s, %s' % (self.name, self.contactName. self.email,
                self.tier))

    def sendemail(self, content):
        print("Sending email to: ", self.name)
        # me == my email address
        # you == recipient's email address
        me = "MadHacks Team <team@madhacks.org>"
        you = self.email
        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "MadHacks + %s" % self.name
        msg['From'] = me
        msg['To'] = you

        # Create the body of the message
        text = content

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, 'plain')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)

        user = getlogin()  # this function needs to be replaced locally (or defined) with the email login.
        passwd = getkey()  # this function needs to be replaced locally (or defined) with the email password.
        print("Sending...")

        # Send the message via local SMTP server.
        s = smtplib.SMTP_SSL('smtp.gmail.com')
        s.login(user, passwd)

        # sendmail function takes 3 arguments: sender's address, recipient's address
        # and message to send - here it is sent as one string.
        s.sendmail(me, you, msg.as_string())
        s.quit()

        print("Sent!")

    @classmethod
    def __validate(cls, text, extrachars=[]):
        text = text.strip()
        for char in cls.bad_characters:
            if char in text:
                raise ValueError("Bad character '%s' found in text." % char)
        for char in extrachars:
            if char in text:
                raise ValueError("Bad character '%s' found in text." % char)
        return text

    def buildemail(self):
        print('Building email for Sponsor: "%s", "%s", "%s"' %
              (self.name, self.contactName, self.email))
        filename = (self.name + ".txt").replace(" ", "_")
        filename = filename.replace("/", "")  # strip bad stuff for files
        filename = "./emails/" + filename

        template = ""

        with open("template.txt") as t:
            template = ''.join(t.readlines())


            # add sponsor contact name with first name of recruiter
            template = template.replace("[RECRUITER NAME]", self.get_first_name())

            # add company name
            template = template.replace("[COMPANY NAME]", self.name)

        with open(filename, "w") as f:
            f.write(template)

        return template

    def confirm_send(self, template):
        print("ARE YOU SURE YOU WOULD LIKE THE BOT TO SEND THE EMAIL TO: %s %s" %
              (self.name, self.contactName))
        try:
            confirm = raw_input('[y/N]: ')
        except NameError as err:
            confirm = input('[y/N]: ')
        if 'y' in confirm.lower():
            return True
        else:
            return False


class Main():
    email_regex = re.compile("[^@: ]+@[\w\-]+\.[\w]+")

    def __init__(self):
        self.stat_sent = 0
        self.stat_manual_skip = 0

    def display_stats(self):
        print('')
        print('Sent %i e-mails' % self.stat_sent)
        print('Manually skipped %i e-mails' % self.stat_manual_skip)

    def send_emails(self, args):
        reader = csv.reader(args.file, delimiter=',')
        outfile = open('data/sponsors-run-%i.csv' % time.time(), 'w')
        writer = csv.writer(outfile)

        for row in reader:
            # Check conditions where we shouldn't send
            if len(row) < 3 or row[COL_COMPANY_NAME] == 'Company Name':
                writer.writerow(row)
                continue
            elif row[COL_STATUS] != 'Not Contacted':
                print('Skipping row due to status field')
                writer.writerow(row)
                continue
            elif row[COL_LAST_CONTACTED]:
                print('Skipping row due to last contact date.')
                writer.writerow(row)
                continue

            # Load other columns
            name = row[COL_COMPANY_NAME]
            if len(name) < 2:
                print('Skipping due to invalid company name')
                writer.writerow(row)
                continue

            contactName = row[COL_CONTACT_NAME]
            if len(contactName) < 3:
                print('Skipping due to invalid contact name')
                writer.writerow(row)
                continue

            email = row[COL_CONTACT_EMAIL]
            if len(email) < 5 or not re.match("[^@: ]+@[\w\-]+\.[\w]+", email):
                print('Skipping due to invalid email')
                writer.writerow(row)
                continue

            try:
                sponsor = Sponsor(name, contactName, email)
            except ValueError:
                print('Skipping %s/%s due to validation error' % (name, email))

            # Final check, and then ask to send
            if sponsor.name and sponsor.contactName and sponsor.email:
                email_sent = self.send_email(sponsor)

                if email_sent:
                    now = time.gmtime()
                    date = '%i/%i/%i' % (now.tm_mon, now.tm_mday, now.tm_year)
                    row[COL_STATUS] = 'Waiting Response'
                    row[COL_LAST_CONTACTED] = date
            else:
                print('Cannot build email; field data is missing/invalid')

            writer.writerow(row)

        outfile.close()

        self.display_stats()

    def send_email(self, sponsor):
        template = sponsor.buildemail()

        if sponsor.confirm_send(template):
            sponsor.sendemail(template)
            self.stat_sent += 1
            return True
        else:
            self.stat_manual_skip += 1
            print('Chose not to send email to %s/%s' %
                  (sponsor.name, sponsor.get_first_name()))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--merge', action='store_true')
    parser.add_argument('--validate', action='store_true')
    parser.add_argument('--stats', action='store_true')
    parser.add_argument('file', type=argparse.FileType('r'))
    parser.add_argument('--mergefile', type=argparse.FileType('r'),
                        help='Used only as the second merge source')
    parser.add_argument('--mergeout', type=argparse.FileType('w'),
                        help='Used as the merge output CSV file')
    args = parser.parse_args()

    if args.merge:  # User passed the --merge option
        import libs.merge
        merger = libs.merge.Merger(args)
        merger.save_file()
    elif args.validate:  # User passed the --validate option
        import libs.validate
        libs.validate.validate(args)
    elif args.stats:  # User passed the --stats option
        import libs.stats
        libs.stats.compute_data_entry_stats(args)
    else:  # No mode option passed; use the default mail-sending mode
        main = Main()
        main.send_emails(args)
