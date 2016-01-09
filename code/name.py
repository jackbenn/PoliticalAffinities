import string
import re

class Name(object):
    '''
    Various functions to deal with names
    '''

    @staticmethod
    def denickname(name):
        nicknames = {
                'andy': 'andrew',
                'anna': 'ann',
                'bill': 'william',
                'brad': 'bradley',
                'bob': 'robert',
                'cathy': 'catherine',
                'chris': 'christopher',
                'dan': 'daniel',
                'dave': 'david',
                'debbie': 'debra',
                'don': 'donald',
                'doug': 'douglas',
                'drew': 'andrew',
                'ed': 'edmund',  # warning: edward to come
                'gerry': 'gerald',
                'greg': 'gregory',
                'hank': 'henry',
                'hugh': 'hugo',
                'jake': 'jacob',
                'jan': 'janice',
                'jeff': 'jeffrey',
                'jim': 'james',
                'joe': 'joseph',
                'joyanne': 'joy',
                'judy': 'judith',
                'larry': 'lawrence',
                'kathy': 'kathryn',
                'mathew': 'matthew',
                'matt': 'matthew',  # not good
                'mike': 'michael',
                'nick': 'nicholas',
                'norm': 'norman',
                'pat': 'patrick',  # warning: patricia
                'phil': 'philip',
                'randy': 'randolph',
                'rich': 'richard',
                'sam': 'samuel',
                'sandy': 'sandra',
                'stephan': 'steven',
                'stephen': 'steven',
                'steve': 'steven', # not good
                'tim': 'timothy',
                'timo': 'timothy',
                'tom': 'thomas',
                'will': 'william',
                'zack': 'zachary',
                'ziggy': 'steven'

        }
        # issues with van
        if name in nicknames:
            return nicknames[name]
        else:
            return name

    def __init__(self, name, source):
        name = name.lower().strip()

        # despace multi-word last names
        name = re.sub('\bvan de ', 'van_de_', name)
        name = re.sub('\bvan ', 'van_', name)

        if source == 'election':
            if " " in name:
                rest, self.last = name.rsplit(" ", 1)
                if " " in rest:
                    self.first, _ = rest.split(" ", 1)
                else:
                    self.first = rest
            else:
                self.last = name
                self.first = ""
        elif source == 'contribution':
            if " " in name:
                self.last, rest = name.split(" ", 1)
                if " " in rest:
                    self.first, _ = rest.split(" ", 1)
                else:
                    self.first = rest
            else:
                self.last = name
                self.first = ""
        self.first = self.denickname(self.first)

    def __eq__(self, other):
        return self.first == other.first and self.last == other.last

    def __gt__(self, other):
        if self.last != other.last:
            return self.last > other.last
        else:
            return self.first > other.first

    def __lt__(self, other):
        if self.last != other.last:
            return self.last < other.last
        else:
            return self.first < other.first

    def __str__(self):
        return self.last + ", " + self.first

    def __len__(self):
        return len(str(self))

    @staticmethod
    def pair_name_lists(list1, list2):
        width1 = max([len(x) for x in list1])
        formatstr = "{0:" + str(width1) + "} {1}"
        sorted1 = sorted(list1)
        sorted2 = sorted(list2)
        i1 = i2 = 0
        while i1 < len(sorted1) and i2 < len(sorted2):
            if sorted1[i1] == sorted2[i2]:
                print formatstr.format(sorted1[i1], sorted2[i2])
                i1 += 1
                i2 += 1
            elif sorted1[i1] < sorted2[i2]:
                print formatstr.format(sorted1[i1], "")
                i1 += 1
            else:
                print formatstr.format("", sorted2[i2])
                i2 += 1
