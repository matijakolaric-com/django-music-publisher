import os

SECRET_KEY = os.getenv('SECRET_KEY', '')

MUSIC_PUBLISHER_SETTINGS = {
    'token': os.getenv('TOKEN', ''),
    'validator_url':
        'https://matijakolaric.com/api/v1/cwr/original/field/multi/',

    'publisher_id': 'XXX',
    'publisher_name': 'THE SEXY PUBLISHER',
    'publisher_ipi_name': '199',
    'publisher_ipi_base': 'I0000000393',
    'publisher_pr_society': '052',
    'publisher_mr_society': '044',
    'publisher_sr_society': None,

    'library': 'THE FOO LIBRARY',
    'label': 'FOO BAR MUSIC',
}
