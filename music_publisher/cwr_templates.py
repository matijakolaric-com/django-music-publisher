"""Django templates for CWR generation.

Attributes:
    TEMPLATES_21 (dict): Record templates for CWR 2.1
    TEMPLATES_22 (dict): Record templates for CWR 2.2, based on 2.1
    TEMPLATES_30 (dict): Record templates for CWR 3.0
    TEMPLATES_31 (dict): Record templates for CWR 3.1, based on 3.0
"""

from django.template import Template

TEMPLATES_21 = {
    "HDR": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        'HDRPB{{ ipi_name_number|rjust:11|slice:"2:" }}'
        '{{ name|ljust:45 }}01.10{{ creation_date|date:"Ymd" }}'
        '{{ creation_date|date:"His" }}{{ creation_date|date:"Ymd" }}'
        "               \r\n{% endautoescape %}"
    ),
    # CWR 2.1 revision 8 "hack" - no sender type field, 11 digit IPI name
    "HDR_8": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "HDR{{ ipi_name_number|rjust:11 }}"
        "{{ name|ljust:45 }}01.10{{ "
        'creation_date|date:"Ymd" }}'
        '{{ creation_date|date:"His" }}{{ '
        'creation_date|date:"Ymd" }}'
        "               \r\n{% endautoescape %}"
    ),
    "GRH": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "GRH{{ transaction_type|ljust:3 }}0000102.10"
        "0000000000  \r\n{% endautoescape %}"
    ),
    "WRK": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "{{ record_type }}"
        "{{ transaction_sequence|rjust:8 }}00000000"
        "{{ work_title|ljust:60 }}  {{ code|ljust:14 }}"
        "{{ iswc|ljust:11 }}00000000            UNC"
        '{{ duration|date:"His"|default:"000000" }}{{ recorded_indicator }}'
        "      {{ version_type }}  "
        + " " * 40
        + "N00000000000"
        + " " * 51
        + "N"
        "\r\n{% endautoescape %}"
    ),
    "SPU": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "SPU{{ transaction_sequence|rjust:8 }}"
        "{{ record_sequence|rjust:8 }}{{ chain_sequence|rjust:2 }}"
        "{{ code|ljust:9 }}"
        "{{ name|ljust:45 }}"
        ' {{ role|default:"E "|ljust:2}}'
        "000000000{{ ipi_name_number|rjust:11 }}              "
        "{{ pr_society|soc }}{{ pr_share|default:0|cwrshare }}"
        "{{ mr_society|soc }}{{ mr_share|default:0|cwrshare }}"
        "{{ sr_society|soc }}{{ sr_share|default:0|cwrshare }}"
        " N {{ ipi_base_number|ljust:13 }}"
        "              {{ saan|ljust:14 }}  "
        "{{usa_license|ljust:1}}"
        "\r\n{% endautoescape %}"
    ),
    "SPT": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "SPT{{ transaction_sequence|rjust:8 }}"
        "{{ record_sequence|rjust:8 }}{{ code|ljust:9 }}"
        "      {{ pr_share|default:0|cwrshare }}"
        "{{ mr_share|default:0|cwrshare }}"
        "{{ sr_share|default:0|cwrshare }}"
        "I2136N001\r\n{% endautoescape %}"
    ),
    "SWR": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "SWR{{ transaction_sequence|rjust:8 }}"
        "{{ record_sequence|rjust:8 }}{{ code|ljust:9 }}"
        "{{ last_name|ljust:45 }}{{ first_name|ljust:30 }} "
        "{{ writer_role|ljust:2 }}000000000{{ ipi_name_number|rjust:11 }}"
        "{{ pr_society|soc }}{{ pr_share|default:0|cwrshare }}"
        "{{ mr_society|soc }}{{ mr_share|default:0|cwrshare }}"
        "{{ sr_society|soc }}{{ sr_share|default:0|cwrshare }}"
        " N  {{ ipi_base_number|ljust:13 }}             \r\n"
        "{% endautoescape %}"
    ),
    "SWT": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "SWT{{ transaction_sequence|rjust:8 }}"
        "{{ record_sequence|rjust:8 }}{{ code|ljust:9 }}"
        "{{ pr_share|default:0|cwrshare }}"
        "{{ mr_share|default:0|cwrshare }}"
        "{{ sr_share|default:0|cwrshare }}I2136N001\r\n{% endautoescape %}"
    ),
    "PWR": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "PWR{{ transaction_sequence|rjust:8 }}"
        "{{ record_sequence|rjust:8 }}{{ publisher_code|ljust:9 }}"
        "{{ publisher_name|ljust:45 }}              "
        "{{ saan|ljust:14 }}"
        "{{ code|ljust:9 }}\r\n{% endautoescape %}"
    ),
    "OPU": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "OPU{{ transaction_sequence|rjust:8 }}"
        "{{ record_sequence|rjust:8 }}{{ sequence|rjust:2 }}"
        + " " * 54
        + "YE 00000000000000000000              "
        "   {{ pr_share|default:0|cwrshare }}"
        "   {{ mr_share|default:0|cwrshare }}"
        "   {{ sr_share|default:0|cwrshare }}"
        " N                                             "
        "\r\n{% endautoescape %}"
    ),
    "OWR": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "OWR{{ transaction_sequence|rjust:8 }}"
        "{{ record_sequence|rjust:8 }}{{ code|ljust:9 }}"
        "{{ last_name|ljust:45 }}{{ first_name|ljust:30 }}"
        '{{ writer_unknown_indicator|default:" "}}'
        "{{ writer_role|ljust:2 }}000000000{{ ipi_name_number|rjust:11 }}"
        "{{ pr_society|soc }}{{ pr_share|default:0|cwrshare }}"
        "{{ mr_society|soc }}{{ mr_share|default:0|cwrshare }}"
        "{{ sr_society|soc }}{{ sr_share|default:0|cwrshare }}    "
        "{{ ipi_base_number|ljust:13 }}             \r\n{% endautoescape %}"
    ),
    "ALT": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "ALT{{ transaction_sequence|rjust:8 }}"
        "{{ record_sequence|rjust:8 }}{{ alternate_title|ljust:60 }}{{ title_type|ljust:2 }}  "
        "\r\n{% endautoescape %}"
    ),
    "OWK": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "VER{{ transaction_sequence|rjust:8 }}"
        "{{ record_sequence|rjust:8 }}{{ work_title|ljust:60 }}"
        + " " * (11 + 2 + 45 + 30 + 60 + 11 + 13 + 45 + 30 + 11 + 13 + 14)
        + "\r\n{% endautoescape %}"
    ),
    "PER": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "PER{{ transaction_sequence|rjust:8 }}"
        "{{ record_sequence|rjust:8 }}{{ last_name|ljust:45 }}"
        "{{ first_name|ljust:30 }}                        \r\n"
        "{% endautoescape %}"
    ),
    "REC": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "REC{{ transaction_sequence|rjust:8 }}"
        "{{ record_sequence|rjust:8 }}"
        '{{ release_date|default:"00000000" }}'
        + " " * 60
        + '{{ duration|rjust:6|default:"000000" }}     '
        + " " * 151
        + "{{ isrc|ljust:12 }}     \r\n{% endautoescape %}"
    ),
    "ORN": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "ORN{{ transaction_sequence|rjust:8 }}"
        "{{ record_sequence|rjust:8 }}LIB"
        + " " * 60
        + "{{ cd_identifier|ljust:15 }}0000{{ library|ljust:60 }}"
        + " " * (26 + 12 + 60 + 20)
        + "0000                  \r\n"
        "{% endautoescape %}"
    ),
    "GRT": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "GRT00001{{ transaction_count|rjust:8 }}"
        "{{ record_count|rjust:8 }}   0000000000\r\n{% endautoescape %}"
    ),
    "TRL": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "TRL00001{{ transaction_count|rjust:8 }}"
        "{{ record_count|rjust:8 }}{% endautoescape %}"
    ),
    "OPT": Template(""),
    "OWT": Template(""),
    "XRF": Template(""),
    "MAN": Template(""),
}

TEMPLATES_22 = TEMPLATES_21.copy()
TEMPLATES_22.update(
    {
        "HDR": Template(
            "{% load cwr_generators %}{% autoescape off %}"
            'HDRPB{{ ipi_name_number|rjust:11|slice:"2:" }}'
            '{{ name|ljust:45 }}01.10{{ creation_date|date:"Ymd" }}'
            '{{ creation_date|date:"His" }}{{ creation_date|date:"Ymd" }}'
            "               2.2002{{ settings.SOFTWARE|ljust:30 }}"
            "{{ settings.SOFTWARE_VERSION|ljust:30 }}\r\n{% endautoescape %}"
        ),
        "HDR_8": Template(
            "{% load cwr_generators %}{% autoescape off %}"
            "HDR{{ ipi_name_number|rjust:11 }}"
            "{{ name|ljust:45 }}01.10{{ "
            'creation_date|date:"Ymd" }}'
            '{{ creation_date|date:"His" }}{{ '
            'creation_date|date:"Ymd" }}'
            "               2.2002{{ settings.SOFTWARE|ljust:30 }}"
            "{{ settings.SOFTWARE_VERSION|ljust:30 }}\r\n{% endautoescape %}"
        ),
        "GRH": Template(
            "{% load cwr_generators %}{% autoescape off %}"
            "GRH{{ transaction_type|ljust:3 }}0000102.20"
            "0000000000  \r\n{% endautoescape %}"
        ),
        "PWR": Template(
            "{% load cwr_generators %}{% autoescape off %}"
            "PWR{{ transaction_sequence|rjust:8 }}"
            "{{ record_sequence|rjust:8 }}{{ publisher_code|ljust:9 }}"
            "{{ publisher_name|ljust:45 }}              "
            "{{ saan|ljust:14 }}"
            "{{ code|ljust:9 }}01\r\n{% endautoescape %}"
        ),
        "ORN": Template(
            "{% load cwr_generators %}{% autoescape off %}"
            "ORN{{ transaction_sequence|rjust:8 }}"
            "{{ record_sequence|rjust:8 }}LIB"
            + " " * 60
            + "{{ cd_identifier|ljust:15 }}0000{{ library|ljust:60 }}"
            + " " * (26 + 12 + 60 + 20)
            + "0000"
            + " " * (18 + 26 + 42)
            + "\r\n"
            "{% endautoescape %}"
        ),
        "REC": Template(
            "{% load cwr_generators %}{% autoescape off %}"
            "REC{{ transaction_sequence|rjust:8 }}"
            "{{ record_sequence|rjust:8 }}"
            '{{ release_date|default:"00000000" }}'
            + " " * 60
            + '{{ duration|rjust:6|default:"000000" }}     '
            + " " * 151
            + "{{ isrc|ljust:12 }}     "
            "{{ recording_title|ljust:60 }}{{ version_title|ljust:60 }}"
            "{{ display_artist|ljust:60 }}{{ record_label.name|ljust:60 }}"
            "{{ isrc_validity|ljust:20 }}{{ code|ljust:14 }}"
            "\r\n{% endautoescape %}"
        ),
        "XRF": Template(
            "{% load cwr_generators %}{% autoescape off %}"
            "XRF{{ transaction_sequence|rjust:8 }}"
            "{{ record_sequence|rjust:8 }}{{ organization.code|soc }}"
            "{{ identifier|ljust:14 }}WY\r\n{% endautoescape %}"
        ),
    }
)

TEMPLATES_30 = {
    "HDR": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "HDRPB{{ code|ljust:4 }}"
        "{{ name|ljust:45 }}" + " " * 11 + '{{ creation_date|date:"Ymd" }}'
        '{{ creation_date|date:"His" }}{{ creation_date|date:"Ymd" }}'
        + " " * 15
        + "3.0000{{ settings.SOFTWARE|ljust:30 }}"
        "{{ settings.SOFTWARE_VERSION|ljust:30 }}"
        "{{ filename|ljust:27 }}\r\n{% endautoescape %}"
    ),
    "GRH": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "GRH{{ transaction_type|ljust:3 }}0000103.000000000000"
        "\r\n{% endautoescape %}"
    ),
    "WRK": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "WRK{{ transaction_sequence|rjust:8 }}00000000"
        "{{ work_title|ljust:60 }}  {{ code|ljust:14 }}"
        "{{ iswc|ljust:11 }}00000000            UNC"
        '{{ duration|date:"His"|default:"000000" }}{{ recorded_indicator }}'
        "      {{ version_type }}N00000000000"
        + " " * 51
        + "N\r\n{% endautoescape %}"
    ),
    "SPU": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "SPU{{ transaction_sequence|rjust:8 }}"
        "{{ record_sequence|rjust:8 }}01"
        "{{ code|ljust:9 }}"
        '{{ name|ljust:45 }}N{{ role|default:"E "|ljust:2}}'
        "000000000{{ ipi_name_number|rjust:11 }}"
        "{{ ipi_base_number|ljust:13 }} \r\n{% endautoescape %}"
    ),
    "SPT": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "SPT{{ transaction_sequence|rjust:8 }}"
        "{{ record_sequence|rjust:8 }}001{{ code|ljust:9 }}"
        "{{ pr_share|default:0|cwrshare }}"
        "{{ mr_share|default:0|cwrshare }}"
        "{{ sr_share|default:0|cwrshare }}I2136"
        "{{ pr_society|ljust:4 }}"
        "{{ mr_society|ljust:4 }}"
        "{{ sr_society|ljust:4 }}" + " " * 32 + "0000\r\n{% endautoescape %}"
    ),
    "SWR": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "SWR{{ transaction_sequence|rjust:8 }}"
        "{{ record_sequence|rjust:8 }}{{ code|ljust:9 }}"
        "{{ last_name|ljust:45 }}{{ first_name|ljust:30 }}N"
        "{{ writer_role|ljust:2 }}{{ ipi_name_number|rjust:11 }}"
        "{{ ipi_base_number|ljust:13 }} N  \r\n"
        "{% endautoescape %}"
    ),
    "SWT": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "SWT{{ transaction_sequence|rjust:8 }}"
        "{{ record_sequence|rjust:8 }}001{{ code|ljust:9 }}"
        "{{ pr_share|default:0|cwrshare }}"
        "{{ mr_share|default:0|cwrshare }}"
        "{{ sr_share|default:0|cwrshare }}I2136{{ pr_society|ljust:4 }}"
        "{{ mr_society|ljust:4 }}{{ sr_society|ljust:4 }}"
        + " " * 32
        + "0000\r\n{% endautoescape %}"
    ),
    "OWT": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "OWT{{ transaction_sequence|rjust:8 }}"
        "{{ record_sequence|rjust:8 }}001{{ code|ljust:9 }}"
        "{{ pr_share|default:0|cwrshare }}"
        "{{ mr_share|default:0|cwrshare }}"
        "{{ pr_share|default:0|cwrshare }}"
        "I2136{{ pr_society|ljust:4 }}"
        "{{ mr_society|ljust:4 }}{{ sr_society|ljust:4 }}"
        + " " * 32
        + "0000\r\n{% endautoescape %}"
    ),
    "PWR": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "PWR{{ transaction_sequence|rjust:8 }}"
        "{{ record_sequence|rjust:8 }}"
        "{{ publisher_sequence|rjust:2 }}{{ publisher_code|ljust:9 }}"
        "{{ code|ljust:9 }}" + " " * 14 + "{{ publisher_pr_society|ljust:4 }}"
        "{{ saan|ljust:14 }}"
        "{{ original_publishers.0.agreement.agreement_type.code|ljust:2 }}"
        "\r\n{% endautoescape %}"
    ),
    "OPU": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "OPU{{ transaction_sequence|rjust:8 }}"
        "{{ record_sequence|rjust:8 }}{{ sequence|rjust:2 }}"
        + " " * 54
        + "YE 00000000000000000000              \r\n{% endautoescape %}"
    ),
    "OPT": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "OPT{{ transaction_sequence|rjust:8 }}"
        "{{ record_sequence|rjust:8 }}001         "
        "{{ pr_share|default:0|cwrshare }}"
        "{{ mr_share|default:0|cwrshare }}"
        "{{ sr_share|default:0|cwrshare }}I2136" + " " * 44 + "0000\r\n"
        "{% endautoescape %}"
    ),
    "OWR": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "OWR{{ transaction_sequence|rjust:8 }}"
        "{{ record_sequence|rjust:8 }}{{ code|ljust:9 }}"
        "{{ last_name|ljust:45 }}{{ first_name|ljust:30 }}"
        '{{ writer_unknown_indicator|default:"N"}}'
        "{{ writer_role|ljust:2 }}000000000{{ ipi_name_number|rjust:11 }}"
        "{{ ipi_base_number|ljust:13 }} N  \r\n"
        "{% endautoescape %}"
    ),
    "ALT": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "ALT{{ transaction_sequence|rjust:8 }}"
        "{{ record_sequence|rjust:8 }}{{ alternate_title|ljust:60 }}{{ title_type|ljust:2 }}  "
        "\r\n{% endautoescape %}"
    ),
    "OWK": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "OWK{{ transaction_sequence|rjust:8 }}"
        "{{ record_sequence|rjust:8 }}{{ work_title|ljust:60 }}"
        + " " * (11 + 14 + 50 + 8 + 45 + 30 + 11 + 13 + 45 + 30 + 11 + 13)
        + "\r\n{% endautoescape %}"
    ),
    "PER": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "PER{{ transaction_sequence|rjust:8 }}"
        "{{ record_sequence|rjust:8 }}{{ last_name|ljust:45 }}"
        "{{ first_name|ljust:30 }}"
        + " " * 11
        + "{{ isni|ljust:16 }}     \r\n{% endautoescape %}"
    ),
    "REC": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "REC{{ transaction_sequence|rjust:8 }}"
        "{{ record_sequence|rjust:8 }}"
        '{{ release_date|default:"00000000" }}'
        '{{ duration|rjust:6|default:"000000" }}'
        "{{ isrc|ljust:12 }}{{ recording_title|ljust:60 }}"
        "{{ version_title|ljust:60 }}{{ display_artist|ljust:60 }}"
        + " " * 11
        + "{{ recording_artist.isni|ljust:16 }}{{ record_label.name|ljust:60 }}"
        "{{ isrc_validity|ljust:20 }}{{ code|ljust:14 }}\r\n"
        "{% endautoescape %}"
    ),
    "ORN": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "ORN{{ transaction_sequence|rjust:8 }}"
        "{{ record_sequence|rjust:8 }}LIB"
        "{{ cd_identifier|ljust:15 }}0000"
        "{{ library|ljust:60 }}"
        + " " * (60 + 60 + 1 + 12 + 60 + 20)
        + "0000"
        + " " * (19 + 26 + 21 + 40)
        + "\r\n{% endautoescape %}"
    ),
    "XRF": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "XRF{{ transaction_sequence|rjust:8 }}"
        "{{ record_sequence|rjust:8 }}{{ organization.code|ljust:4 }}"
        "{{ identifier|ljust:14 }}WY\r\n{% endautoescape %}"
    ),
    "ISR": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "ISR{{ transaction_sequence|rjust:8 }}00000000"
        "{{ work_title|ljust:60 }}  {{ work_id|ljust:14 }}"
        "{{ iswc|ljust:11 }}{{ indicator|ljust:1 }}\r\n{% endautoescape %}"
    ),
    "WRI": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "WRI{{ transaction_sequence|rjust:8 }}"
        "{{ record_sequence|rjust:8 }}{{ code|ljust:9 }}"
        "{{ ipi_name_number|rjust:11 }}{{ last_name|ljust:45 }}"
        "{{ first_name|ljust:30 }}{{ capacity|ljust:2 }}\r\n"
        "{% endautoescape %}"
    ),
    "GRT": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "GRT00001{{ transaction_count|rjust:8 }}"
        "{{ record_count|rjust:8 }}\r\n{% endautoescape %}"
    ),
    "TRL": Template(
        "{% load cwr_generators %}{% autoescape off %}"
        "TRL00001{{ transaction_count|rjust:8 }}"
        "{{ record_count|rjust:8 }}{% endautoescape %}"
    ),
    "MAN": Template(""),
}

TEMPLATES_31 = TEMPLATES_30.copy()
TEMPLATES_31.update(
    {
        "HDR": Template(
            "{% load cwr_generators %}{% autoescape off %}"
            "HDRPB{{ code|ljust:4 }}"
            "{{ name|ljust:45 }}" + " " * 11 + '{{ creation_date|date:"Ymd" }}'
            '{{ creation_date|date:"His" }}{{ creation_date|date:"Ymd" }}'
            + " " * 15
            + "3.1000{{ settings.SOFTWARE|ljust:30 }}"
            "{{ settings.SOFTWARE_VERSION|ljust:30 }}"
            "{{ filename|ljust:27 }}\r\n{% endautoescape %}"
        ),
        "GRH": Template(
            "{% load cwr_generators %}{% autoescape off %}"
            "GRHWRK0000103.100000000000"
            "\r\n{% endautoescape %}"
        ),
        "MAN": Template(
            "{% load cwr_generators %}{% autoescape off %}"
            "MAN{{ transaction_sequence|rjust:8 }}"
            "{{ record_sequence|rjust:8 }}{{ code|ljust:9 }}"
            "{{ share|cwrshare }}{{ share|cwrshare }}"
            "{{ share|cwrshare }}\r\n{% endautoescape %}"
        ),
    }
)
