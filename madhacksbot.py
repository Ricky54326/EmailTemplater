#! /usr/bin/python
__author__ = 'riccardo mutschlechner'

import smtplib # SMTP email
import csv # CSV parsing
import re # regex
from email.mime.multipart import MIMEMultipart # moar SMTP email
from email.mime.text import MIMEText # even moar SMTP email
from keys import getkey, getlogin # login/pass for email acct, needs to be created locally

COL_COMPANY_NAME = 0
COL_CONTACT_NAME = 1
COL_CONTACT_EMAIL = 3
COL_STATUS = 5  # TODO: check row status before sending

class Sponsor:
    # Some of these are valid in emails, but we should be careful
    bad_characters = (';', '/', '\\', '"', "'")

    def __init__(self, name, contactName, email, tier):
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


    @classmethod
    def __validate(cls, text):
        for char in cls.bad_characters:
            if char in text:
                raise ValueError("Bad character '%s' found in text." % char)
        return text.strip()


def sendEmail(sponsor, content):
    print("Sending email to: ", sponsor.name)
    # me == my email address
    # you == recipient's email address
    me = "team@madhacks.org"
    you = sponsor.email

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

    user = getlogin() # this function needs to be replaced locally (or defined) with the email login.
    passwd = getkey() # this function needs to be replaced locally (or defined) with the email password.
    print("Sending...")

    # Send the message via local SMTP server.
    s = smtplib.SMTP_SSL('smtp.gmail.com')
    s.login(user,passwd)

    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    s.sendmail(me, you, msg.as_string())
    s.quit()

    print("Sent!")


def buildemail(sponsor):
    print('Building email for Sponsor: "%s", "%s", "%s"' %
          (sponsor.name, sponsor.contactName, sponsor.email))
    filename = (sponsor.name + ".txt").replace(" ", "_")
    filename = filename.replace("/", "") # strip bad stuff for files
    filename = "./emails/" + filename

    template = ""

    with open("template.txt") as t:
        template = ''.join(t.readlines())

    # add sponsor contact name with first name of recruiter
    template = template.replace("[RECRUITER NAME]", sponsor.get_first_name())

    # add company name
    template = template.replace("[COMPANY NAME]", sponsor.name)

    with open(filename, "w") as f:
        f.write(template)

    return template


def confirmSend(sponsor, template):
    print("ARE YOU SURE YOU WOULD LIKE THE BOT TO SEND THE EMAIL TO: %s %s" %
          (sponsor.name, sponsor.contactName))
    try:
        confirm = raw_input('[y/N]: ')
    except NameError as err:
        confirm = input('[y/N]: ')
    if 'y' in confirm.lower():
        return True
    else:
        return False


def main():
    Sponsors = []
    with open('data/sponsors_test.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            # Check for malformated rows
            if len(row) < 3 or row[COL_COMPANY_NAME] == 'Company Name':
                continue

            # when we add a tier field, if we do, please change [[TIER]] to the appropriate field
            name = row[COL_COMPANY_NAME]
            if len(name) < 3:
                name = None

            contactName = row[COL_CONTACT_NAME]
            if len(contactName) < 3:
                contactName = None

            email = row[COL_CONTACT_EMAIL]
            # make sure email is valid, and also a valid length
            if len(email) < 5 or not re.match("[^@()]+@[\w\-]+\.[\w]+", email):
                email = None


            tier = ""
            if len(tier) < 3:
                tier = None

            Sponsors.append(Sponsor(name, contactName, email, tier))

        for sponsor in Sponsors:
            # print(sponsor)

            # if we have all of the correct fields... build the emails!
            if sponsor.name and sponsor.contactName and sponsor.email:
                template = buildemail(sponsor)
                # Confirm sending with user
                if confirmSend(sponsor, template):
                    sendEmail(sponsor, template)
                else:
                    print("Chose not to send email to " + sponsor.name)
            else:
                print("Cannot build email for sponsor because of missing or invalid fields")


if __name__ == "__main__":
    main()
