# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# invenio-catalogue-marc21 is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.


"""Marc21 Catalogue demo."""

import random
from datetime import UTC, datetime, timedelta
from pathlib import Path
from random import randint

from faker import Faker
from faker_file.base import DynamicTemplate
from faker_file.contrib.pdf_file.reportlab_snippets import (
    add_h1_heading,
    add_h2_heading,
    add_page_break,
    add_paragraph,
    add_picture,
    add_table,
)
from faker_file.providers.pdf_file import PdfFileProvider
from faker_file.providers.pdf_file.generators import reportlab_generator


def resource_type_generator(*, chapter: bool = False) -> str:
    """Create fake record resource type."""
    if chapter:
        return "CHAPTER"
    return "CATALOGUE"


def create_fake_data(*, chapter: bool = False, files: bool = True) -> dict:
    """Create records for demo purposes."""
    fake = Faker()

    mmsid = randint(9000000000000, 9999999999999)  # noqa: S311
    ac_number = randint(13000000, 19999999)  # noqa: S311
    local_id = randint(70000, 99999)  # noqa: S311
    ac_id = f"AC{ac_number}"
    last_name = fake.last_name()
    first_name = fake.first_name()
    person_title = fake.suffix_nonbinary()
    create_date = fake.date_time_this_decade()
    country_code = fake.country_code()
    fake_resource_type = resource_type_generator(chapter=chapter)

    data_to_use = {
        "files": {
            "enabled": files,
        },
        "pids": {},
        "metadata": {
            "leader": "00000nam a2200000zca4501",
            "fields": {
                "001": f"{mmsid}",
                "005": "FAKE0826022415.0",
                "007": "cr#|||||||||||",
                "008": f"230501s{create_date.strftime('%Y')}    |||     om    ||| | eng c",
                "009": f"{ac_id}",
                "020": [
                    {
                        "ind1": "_",
                        "ind2": "_",
                        "subfields": {"a": [f"{fake.isbn13()}"]},
                    },
                ],
                "035": [
                    {
                        "ind1": "_",
                        "ind2": "_",
                        "subfields": {"a": [f"({country_code}-OBV){ac_id}"]},
                    },
                    {
                        "ind1": "_",
                        "ind2": "_",
                        "subfields": {"a": [f"({country_code}-599)OBV{ac_id}"]},
                    },
                ],
                "040": [
                    {
                        "ind1": "_",
                        "ind2": "_",
                        "subfields": {
                            "a": [f"{country_code}-UB"],
                            "b": ["eng"],
                            "d": [f"{country_code}-UB"],
                            "e": ["rda"],
                        },
                    },
                ],
                "041": [{"ind1": "_", "ind2": "_", "subfields": {"a": ["eng"]}}],
                "044": [{"ind1": "_", "ind2": "_", "subfields": {"a": [country_code]}}],
                "100": [
                    {
                        "ind1": "1",
                        "ind2": "_",
                        "subfields": {
                            "4": [country_code],
                            "a": [f"{first_name}, {last_name}"],
                        },
                    },
                ],
                "245": [
                    {
                        "ind1": "1",
                        "ind2": "0",
                        "subfields": {
                            "a": [f"{fake.text(max_nb_chars=20)}"],
                            "b": [f"{fake.company()}"],
                            "c": [f"{person_title} {first_name}, {last_name}"],
                        },
                    },
                ],
                "246": [
                    {
                        "ind1": "1",
                        "ind2": "_",
                        "subfields": {
                            "a": [f"{fake.catch_phrase()}"],
                            "i": [country_code],
                        },
                    },
                ],
                "264": [
                    {
                        "ind1": "_",
                        "ind2": "1",
                        "subfields": {
                            "a": ["Duckburg"],
                            "b": [f"{fake.company()}"],
                            "c": [f"{create_date.strftime('%Y')}"],
                        },
                    },
                ],
                "300": [
                    {
                        "ind1": "_",
                        "ind2": "_",
                        "subfields": {
                            "a": ["1 Online-Ressource (VII, XXX Pages)"],
                        },
                    },
                ],
                "336": [{"ind1": "_", "ind2": "_", "subfields": {"b": ["txt"]}}],
                "337": [{"ind1": "_", "ind2": "_", "subfields": {"b": ["c"]}}],
                "338": [{"ind1": "_", "ind2": "_", "subfields": {"b": ["cr"]}}],
                "347": [
                    {
                        "ind1": "_",
                        "ind2": "_",
                        "subfields": {"a": ["Textdatei"]},
                    },
                ],
                "502": [
                    {
                        "ind1": "_",
                        "ind2": "_",
                        "subfields": {
                            "c": [fake.company()],
                            "d": [f"{create_date.strftime('%Y')}"],
                        },
                    },
                ],
                "655": [
                    {
                        "ind1": "_",
                        "ind2": "7",
                        "subfields": {
                            "0": [f"({country_code}-552){fake.ssn()}"],
                            "2": ["gnd-content"],
                            "a": ["Hochschulschrift"],
                        },
                    },
                ],
                "700": [
                    {
                        "ind1": "1",
                        "ind2": "_",
                        "subfields": {
                            "4": [country_code],
                            "a": [f"{fake.first_name()}, {fake.last_name()}"],
                        },
                    },
                    {
                        "ind1": "1",
                        "ind2": "_",
                        "subfields": {
                            "4": [country_code],
                            "a": [f"{fake.first_name()}, {fake.last_name()}"],
                        },
                    },
                ],
                "710": [
                    {
                        "ind1": "2",
                        "ind2": "_",
                        "subfields": {
                            "a": [f"TU Graz {fake.company()}"],
                        },
                    },
                    {
                        "ind1": "1",
                        "ind2": "_",
                        "subfields": {
                            "a": [f"TU Graz {fake.company()}"],
                        },
                    },
                ],
                "751": [
                    {
                        "ind1": "_",
                        "ind2": "_",
                        "subfields": {
                            "a": [f"{fake.city()}"],
                        },
                    },
                    {
                        "ind1": "_",
                        "ind2": "_",
                        "subfields": {
                            "a": [f"{fake.city()}"],
                        },
                    },
                ],
                "970": [
                    {
                        "ind1": "2",
                        "ind2": "_",
                        "subfields": {"d": [f"{fake_resource_type}"]},
                    },
                ],
                "995": [
                    {
                        "ind1": "_",
                        "ind2": "_",
                        "subfields": {
                            "9": ["local"],
                            "a": [f"{local_id}"],
                            "i": ["FAKEInstitution"],
                        },
                    },
                ],
            },
        },
    }

    return data_to_use


def create_fake_file() -> Path:
    """Create a fake PDF file."""
    faker = Faker()
    faker.add_provider(PdfFileProvider)

    content = faker.pdf_file(
        pdf_generator_cls=reportlab_generator.ReportlabPdfGenerator,
        content=DynamicTemplate(
            [
                (add_h1_heading, {}),  # Add h1 heading
                (add_paragraph, {}),  # Add paragraph
                (add_paragraph, {}),  # Add paragraph
                (add_page_break, {}),  # Add page break
                (add_h2_heading, {}),  # Add h2 heading
                (add_paragraph, {}),  # Add paragraph
                (add_picture, {}),  # Add picture
                (add_page_break, {}),  # Add page break
                (add_h1_heading, {}),  # Add h1 heading
                (add_table, {}),  # Add table
                (add_paragraph, {}),  # Add paragraph
                (add_page_break, {}),  # Add page break
            ]
            * 3,
        ),
        raw=True,
    )

    # Define the path to save the PDF file
    output_file_path = Path("/tmp/output.pdf")  # noqa: S108

    # Save the PDF content to a file
    with output_file_path.open("wb") as fp:
        fp.write(content)

    return output_file_path


def fake_feature_date(days: int = 365) -> str:
    """Generate a fake feature_date."""
    start_date = datetime.now(UTC).replace(tzinfo=None)
    random_number_of_days = random.randrange(1, days)  # noqa: S311
    _date = start_date + timedelta(days=random_number_of_days)
    return _date.strftime("%Y-%m-%d")


def create_fake_catalogue_record(n_chapters: int) -> tuple:
    """Create records for demo purposes in backend."""
    data = create_fake_data()
    data_access = {"files": "public", "record": "public"}
    data["access"] = data_access
    data_chapters = [create_fake_data(chapter=True) for _ in range(n_chapters)]

    return data, data_chapters, data_access
