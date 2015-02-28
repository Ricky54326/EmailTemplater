import unittest
import madhacksbot

DEFAULT_COMPANY = 'MadHacks'
DEFAULT_CONTACT = 'Bob Smith'
DEFAULT_EMAIL = 'bobsmith@madhacks.org'
DEFAULT_TIER = None


class TestSponsor(unittest.TestCase):
    '''
    Test the Sponsor class.
    '''

    first_names = {
        'George Orwell': 'George',
        'Mad Hacks Bot': 'Mad'
    }

    def test_init_stripping(self):
        '''
        Test that the __init__ method removes leading and trailing spaces.
        '''
        s = madhacksbot.Sponsor('MadHacks ', 'Bob Smith ',
                               'bobsmith@madhacks.org ', DEFAULT_TIER)
        self.assertEqual(s.name, 'MadHacks')
        self.assertEqual(s.contactName, 'Bob Smith')
        self.assertEqual(s.email, 'bobsmith@madhacks.org')

        s = madhacksbot.Sponsor('\t MadHacks\t\n', '\t Bob Smith\t\n',
                       '\t bobsmith@madhacks.org \t\n', DEFAULT_TIER)
        self.assertEqual(s.name, 'MadHacks')
        self.assertEqual(s.contactName, 'Bob Smith')
        self.assertEqual(s.email, 'bobsmith@madhacks.org')


    def test_init_filtering(self):
        '''
        Test the character filtering of __init__'s parameters.

        This does not test all filtered characters, but rather that some
        filtering is done on every input.
        '''
        madhacksbot.Sponsor('Madhacks', 'Bob Smith', 'bob@madhacks.org', None)
        self.assertRaises(ValueError, madhacksbot.Sponsor, 'MadHacks (MH)',
                          DEFAULT_CONTACT, DEFAULT_EMAIL, DEFAULT_TIER)
        self.assertRaises(ValueError, madhacksbot.Sponsor, DEFAULT_COMPANY,
                          'Bob Smith/George Orwell', DEFAULT_EMAIL,
                          DEFAULT_TIER)
        self.assertRaises(ValueError, madhacksbot.Sponsor, DEFAULT_COMPANY,
                          DEFAULT_CONTACT, 'bob@example.com (get work email)',
                          DEFAULT_TIER)

    def test_get_first_name(self):
        '''
        Test that the Sponsor class's get_first_name method correctly
        splits the name of the contact.
        '''
        for fullname in self.first_names:
            s = madhacksbot.Sponsor(DEFAULT_COMPANY, fullname, DEFAULT_EMAIL,
                                    DEFAULT_TIER)
            self.assertEqual(s.get_first_name(), self.first_names[fullname],
                             'Returned first name does not match test.')

    def test_validate_extrachars(self):
        '''
        Emails have an extra list of invalid characters, such as spaces.
        Check that an error is thrown for these.
        '''
        self.assertRaises(ValueError, madhacksbot.Sponsor, DEFAULT_COMPANY,
                          DEFAULT_CONTACT, 'email @example.com', DEFAULT_TIER)
