"""Constants used throughout the module."""

from django.conf import settings

SETTINGS = settings.MUSIC_PUBLISHER_SETTINGS

ENFORCE_SAAN = SETTINGS.get('enforce_saan')
ENFORCE_PUBLISHER_FEE = SETTINGS.get('enforce_publisher_fee')
ENFORCE_PR_SOCIETY = SETTINGS.get('enforce_pr_society')
ENFORCE_IPI_NAME = SETTINGS.get('enforce_ipi_name')

CONTROLLED_WRITER_REQUIRED_FIELDS = ['Last Name']
if ENFORCE_PR_SOCIETY:
    CONTROLLED_WRITER_REQUIRED_FIELDS.append('Performing Rights Society')
if ENFORCE_IPI_NAME:
    CONTROLLED_WRITER_REQUIRED_FIELDS.append('IPI Name #')

CAN_NOT_BE_CONTROLLED_MSG = (
    'Unsufficient data for a controlled writer, required fields are: {}.'
).format(', '.join(CONTROLLED_WRITER_REQUIRED_FIELDS))

# Default only has 18 societies from 12 countries. These are G7, without Japan,
# where we have no information about CWR use and all other societies covered
# by ICE Services
# If you need to add some, do it in the settings, not here.

try:
    SOCIETIES = settings.MUSIC_PUBLISHER_SOCIETIES
except AttributeError:
    SOCIETIES = [
        ('55', 'SABAM, Belgium'),

        ('101', 'SOCAN, Canada'),
        ('88', 'CMRRA, Canada'),

        ('40', 'KODA, Denmark'),

        ('89', 'TEOSTO, Finland'),

        ('58', 'SACEM, France'),

        ('35', 'GEMA, Germany'),

        ('74', 'SIAE, Italy'),

        ('23', 'BUMA, Netherlands'),
        ('78', 'STEMRA, Netherlands'),

        ('90', 'TONO, Norway'),

        ('79', 'STIM, Sweden'),

        ('52', 'PRS, United Kingdom'),
        ('44', 'MCPS, United Kingdom'),

        ('10', 'ASCAP, United States'),
        ('21', 'BMI, United States'),
        ('71', 'SESAC Inc., United States'),
        ('34', 'HFA, United States'),

        ('319', 'ICE Services, Administrative Agency'),
        ('707', 'Musicmark, Administrative Agency')]

SOCIETY_DICT = dict(SOCIETIES)

WORK_ID_PREFIX = SETTINGS.get('work_id_prefix', '')