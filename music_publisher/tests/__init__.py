"""
Tests for :mod:`music_publisher`.

The folder includes these files:

* CW200001DMP_000.V21 - CWR 2.1 registration file
* CW200002DMP_0000_V3-0-0.SUB - CWR 3.0 registration file
* CW200003DMP_0000_V3-0-0.ISR - CWR3.0 ISWC request file
* CW200001052_DMP.V21 - CWR 2.1 acknowledgement file
* dataimport.csv - used for data imports
* royaltystatement.csv - CSV royalty statement
* royaltystatement_200k_rows.csv - CSV royalty statement with 200.000 rows,
  used for load testing.

Actual tests are in :mod:`music_publisher.tests.tests`.
"""

from .tests import *
