"""Create society tuple and dict.

    Attributes:
        SOCIETIES (tuple): (tis-n, Name (Country))
        SOCIETY_DICT: (dict): {tis-n, Name (Country)}
"""

import csv
import os
from collections import OrderedDict

dir_path = os.path.dirname(os.path.realpath(__file__))
path = os.path.join(dir_path, 'societies.csv')

with open(path, 'r') as f:
    reader = csv.reader(f)
    SOCIETIES = sorted(
        ((str(row[0]), '{} ({})'.format(row[1], row[2]))
         for row in reader),
        key=lambda row: row[1])

SOCIETY_DICT = OrderedDict(SOCIETIES)