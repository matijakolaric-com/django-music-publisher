import os

try:
    from .settings import *
except ImportError:
    pass

MUSIC_PUBLISHER_SETTINGS = {
    'admin_show_publisher': False,
    'admin_show_saan': True,

    'enforce_saan': False,
    'enforce_publisher_fee': False,
    'enforce_pr_society': True,
    'enforce_ipi_name': True,

    'token': os.getenv('TOKEN', None),
    'validator_url': os.getenv(
        'VALIDATOR_URL',
        'https://matijakolaric.com/api/v1/cwr/original/field/multi/'),
    'generator_url': os.getenv(
        'GENERATOR_URL',
        'https://matijakolaric.com/api/v1/cwr/original/creator/'),
    'highlighter_url': os.getenv(
        'HIGHLIGHTER_URL',
        'https://matijakolaric.com/api/v1/cwr/highlighter/'),

    'work_id_prefix': os.getenv('WORK_ID_PREFIX', 'XXX'),

    'publisher_id': 'XXX',
    'publisher_name': 'DMP DEMO SESAC PUBLISHER',
    'publisher_ipi_name': '00000000199',
    'publisher_pr_society': '071',
    'publisher_mr_society': '034',
    'publisher_sr_society': None,

    'us_publisher_override': {
        'ASCAP': {
            'publisher_id': 'XXXA',
            'publisher_name': 'DMP DEMO ASCAP PUBLISHER',
            'publisher_ipi_name': '00000000493',
            'publisher_pr_society': '010',
            'publisher_mr_society': '034',
            'publisher_sr_society': None,
        },
        'BMI': {
            'publisher_id': 'XXXB',
            'publisher_name': 'DMP DEMO BMI PUBLISHER',
            'publisher_ipi_name': '00000000395',
            'publisher_pr_society': '021',
            'publisher_mr_society': '034',
            'publisher_sr_society': None,
        },
        'SESAC': None,
    },

    'library': 'DMP DEMO LIBRARY',
    'label': 'DMP DEMO LABEL',
}
