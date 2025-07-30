import copy
from pathlib import Path
from typing import Any, List

import pytest

from dicom_utils.anonymize import *
from dicom_utils.private import MEDCOG_ADDR, MEDCOG_NAME, PRIVATE_ELEMENTS_DESCRIPTION


CRITICAL_PHI_TAGS: Final[List[Tag]] = [
    Tag.InstitutionAddress,
    Tag.OperatorsName,
    Tag.PatientAddress,
    Tag.PatientBirthDate,
    Tag.PatientName,
    Tag.PatientTelephoneNumbers,
    Tag.ReferringPhysicianName,
    Tag.ReferringPhysicianAddress,
    Tag.StudyDate,
]

POSSIBLE_ANON_VALS: Final[List[str]] = ["", "ANONYMIZED"]


@pytest.mark.parametrize(
    "test_data",
    [
        ("1", 1),
        ("078Y", 78),
        ("090Y", 90),
        ("abcdefgh120ijklmnopqrts", 120),
    ],
)
def test_str_to_first_int(test_data) -> None:
    input_string, expected_int = test_data
    assert expected_int == str_to_first_int(input_string)


@pytest.mark.parametrize(
    "test_data",
    [
        ("1", "001Y"),
        ("000078Y", "078Y"),
        ("90Y", "90Y+"),
        ("abcdefgh120ijklmnopqrts", "90Y+"),
    ],
)
def test_anonymize_age(test_data) -> None:
    input_string, expected_output = test_data
    assert expected_output == anonymize_age(input_string)


@pytest.mark.parametrize(
    "actual_age, expected_age",
    [
        ("12", "012Y"),
        ("000052Y", "052Y"),
        ("90Y", "90Y+"),
        ("5642", "90Y+"),
    ],
)
def test_age_anon(test_dicom: pydicom.Dataset, actual_age: str, expected_age: str) -> None:
    ds = copy.deepcopy(test_dicom)
    ds.PatientAge = actual_age

    anonymize(ds)

    assert ds.PatientAge == expected_age


def test_private_tags(test_dicom) -> None:
    medcog_elements = get_medcog_elements(test_dicom)

    ds = copy.deepcopy(test_dicom)
    anonymize(ds)

    block = get_medcog_block(ds)
    assert block[0].value == PRIVATE_ELEMENTS_DESCRIPTION
    for i, element in enumerate(medcog_elements):
        assert block[i + 1].VR == element.VR
        assert block[i + 1].value == element.value


def test_anonymize(test_dicom) -> None:
    # Additional testing is present in the `dicom-anonymizer` repo
    # This test is more of a sanity check
    ds = copy.deepcopy(test_dicom)

    for tag in CRITICAL_PHI_TAGS:
        s = "19000101" if "date" in repr(tag).lower() else "filler string"
        ds.add_new(tag.tag_tuple, "LO", s)

    for tag in CRITICAL_PHI_TAGS:
        assert hasattr(ds, tag.name)
        assert ds[tag] != ""

    anonymize(ds)

    assert ds.PatientID[: len(PATIENT_ID_PREFIX)] == PATIENT_ID_PREFIX

    for tag in CRITICAL_PHI_TAGS:
        assert not hasattr(ds, tag.name) or (ds[tag].value in POSSIBLE_ANON_VALS)


def test_patient_id_anon(test_dicom) -> None:
    datasets = [copy.deepcopy(test_dicom) for _ in range(3)]

    for i in [0, 2]:
        datasets[i].PatientID = "one patient"
    datasets[1].PatientID = "another patient"

    for d in datasets:
        anonymize(d)

    for d in datasets:
        assert d.PatientID[: len(PATIENT_ID_PREFIX)] == PATIENT_ID_PREFIX

    assert datasets[0].PatientID == datasets[2].PatientID
    assert datasets[0].PatientID != datasets[1].PatientID


@pytest.mark.parametrize(
    "actual_descr, expected_descr",
    [
        ("test12345", "test12345"),
    ],
)
def test_deriv_descr_anon(test_dicom: pydicom.Dataset, actual_descr: str, expected_descr: str) -> None:
    ds = copy.deepcopy(test_dicom)
    ds.DerivationDescription = actual_descr

    anonymize(ds)

    assert ds.DerivationDescription == expected_descr, f"{ds.DerivationDescription} != {expected_descr}"


@pytest.mark.parametrize(
    "tag_a, tag_b, filler_str",
    [
        (Tag.PatientName, Tag.InstitutionName, "test123"),
        (Tag.InstitutionName, Tag.PatientName, "test123"),
        (Tag.InstitutionAddress, Tag.PatientName, "1234 Street, City"),
        (Tag.PatientName, Tag.InstitutionAddress, "1234 Street, City"),
        (Tag.PatientAddress, Tag.PatientName, "_"),
        (Tag.PatientName, Tag.PatientAddress, "_"),
    ],
)
def test_override_anon_rules(test_dicom: pydicom.Dataset, tag_a: Tag, tag_b: Tag, filler_str: str) -> None:
    ds = copy.deepcopy(test_dicom)
    for t in [tag_a, tag_b]:
        ds.add_new(t.tag_tuple, "LO", filler_str)
    anonymize(ds, {tag_a: preserve_value})
    assert tag_a in ds and ds[tag_a].value == filler_str
    assert not hasattr(ds, tag_b.name) or (ds[tag_b].value in POSSIBLE_ANON_VALS)


def test_is_anonymized(test_dicom: pydicom.Dataset) -> None:
    not_medcog_name = MEDCOG_NAME + " "
    test_dicom.private_block(MEDCOG_ADDR, not_medcog_name, create=True)
    test_dicom.private_block(MEDCOG_ADDR, not_medcog_name, create=False)  # Check block exists (i.e. no exception)

    # The non-Medcognetics block we just created should not make us think that the case is anonymized
    assert not is_anonymized(test_dicom)
    anonymize(test_dicom)
    assert is_anonymized(test_dicom)

    with pytest.raises(Exception):
        not_medcog_name = MEDCOG_NAME + "  "
        # This should not return the MedCognetics block but should raise an exception that the block doesn't exist
        test_dicom.private_block(MEDCOG_ADDR, not_medcog_name, create=False)


def test_double_anonymization(test_dicom: pydicom.Dataset) -> None:
    anonymize(test_dicom)
    with pytest.raises(AssertionError, match="DICOM file is already anonymized"):
        anonymize(test_dicom)


@pytest.mark.parametrize(
    "num_frames, irrad_event_uid, type_str",
    [
        (None, None, "IS"),
        (None, None, "SQ"),
        (1, 1, "IS"),
    ],
)
def test_fix_bad_fields(
    test_dicom: pydicom.Dataset, num_frames: Any, irrad_event_uid: Any, type_str: str, tmp_path: Path
) -> None:
    ds = copy.deepcopy(test_dicom)

    ds.add_new(Tag.NumberOfFrames.tag_tuple, type_str, num_frames)
    ds.add_new(Tag.IrradiationEventUID.tag_tuple, type_str, irrad_event_uid)

    ds.save_as(tmp_dicom_file := tmp_path / "tmp.dcm")

    ds = pydicom.dcmread(tmp_dicom_file)

    # We are only checking that no exceptions are thrown when these tags are accessed
    ds[Tag.NumberOfFrames]
    ds[Tag.IrradiationEventUID]
