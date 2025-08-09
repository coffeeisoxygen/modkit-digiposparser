import re

import pytest

EXCLUDE_PRODUCTNAME = ["GIGAMAX", "NONTON"]
test_names = [
    "Nonton Hemat 5000 30 Hari",
    "GIGAMAX FIT 30 Hari",
    "OMG! Nonton 23GB 30 Hari + FITA 30 Hari",
]


@pytest.mark.quick
@pytest.mark.parametrize(
    "name,expected",
    [
        ("Nonton Hemat 5000 30 Hari", True),
        ("GIGAMAX FIT 30 Hari", True),
        ("OMG! Nonton 23GB 30 Hari + FITA 30 Hari", False),
    ],
)
def test_should_exclude(name, expected):
    should_exclude = any(
        re.match(rf"^{re.escape(f)}", name, re.IGNORECASE)
        for f in EXCLUDE_PRODUCTNAME
        if f.strip()
    )
    assert should_exclude == expected


@pytest.mark.quick
@pytest.mark.parametrize(
    "name,pattern,should_match",
    [
        ("Nonton Hemat 5000 30 Hari", "GIGAMAX", False),
        ("Nonton Hemat 5000 30 Hari", "NONTON", True),
        ("GIGAMAX FIT 30 Hari", "GIGAMAX", True),
        ("GIGAMAX FIT 30 Hari", "NONTON", False),
        ("OMG! Nonton 23GB 30 Hari + FITA 30 Hari", "GIGAMAX", False),
        ("OMG! Nonton 23GB 30 Hari + FITA 30 Hari", "NONTON", False),
    ],
)
def test_individual_pattern(name, pattern, should_match):
    regex = rf"^{re.escape(pattern)}"
    match = re.match(regex, name, re.IGNORECASE)
    assert (match is not None) == should_match
