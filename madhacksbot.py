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

COL_COMPANY_NAME = 0
COL_CONTACT_NAME = 1
COL_CONTACT_EMAIL = 3
COL_STATUS = 5
COL_LAST_CONTACTED = 7

class Sponsor():
    # Some of these are valid in emails, but we should be careful
    bad_characters = (';', '/', '\\', '"', "'", '(', ')')

    def __init__(self, name, contactName, email, tier=None):
        self.name = self.__validate(name)
        self.contactName = self.__validate(contactName)
        self.email = self.__validate(email)

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
        me = "team@madhacks.org"
        you = self.email
        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "University of Wisconsin - MadHacks Offer of Sponsorship"
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
    def __validate(cls, text):
        for char in cls.bad_characters:
            if char in text:
                raise ValueError("Bad character '%s' found in text." % char)
        return text.strip()

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
    def send_emails(self, args):
        sponsors = []
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
            if len(name) < 3:
                name = None

            contactName = row[COL_CONTACT_NAME]
            if len(contactName) < 3:
                contactName = None

            email = row[COL_CONTACT_EMAIL]
            if len(email) < 5 or not re.match("[^@()]+@[\w\-]+\.[\w]+", email):
                email = None

            sponsor = Sponsor(name, contactName, email)

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

    def send_email(self, sponsor):
        template = sponsor.buildemail()

        if sponsor.confirm_send(template):
            sponsor.sendemail(template)
            return True
        else:
            print('Chose not to send email to %s/%s' %
                  (sponsor.name, sponsor.get_first_name()))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--validate', action='store_true')
    parser.add_argument('file', type=argparse.FileType('r'))
    args = parser.parse_args()

    if args.validate:  # User passed the --validate option
        import libs.validate
        libs.validate.validate(args)
    else:
        main = Main()
        main.send_emails(args)
