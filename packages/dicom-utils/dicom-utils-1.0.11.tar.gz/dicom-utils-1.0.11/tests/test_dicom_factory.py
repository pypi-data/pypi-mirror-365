#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path

import numpy as np
import pydicom
import pytest
from pydicom import Dataset, Sequence
from pydicom.uid import ExplicitVRLittleEndian, ImplicitVRLittleEndian, RLELossless
from pydicom.valuerep import VR

from dicom_utils import DicomFactory
from dicom_utils.dicom import set_pixels
from dicom_utils.dicom_factory import FACTORY_REGISTRY, CompleteMammographyStudyFactory
from dicom_utils.tags import Tag
from dicom_utils.types import MammogramType


class TestDicomFactory:
    def test_init(self):
        DicomFactory()

    def test_constructor_overrides(self):
        factory = DicomFactory(Modality="MG")
        dcm = factory()
        assert dcm.Modality == "MG"

    def test_override_present_value(self):
        factory = DicomFactory()
        dcm = factory(Modality="MG")
        assert dcm.Modality == "MG"

    def test_set_new_value(self):
        factory = DicomFactory()
        dcm = factory(ViewPosition="MLO")
        assert dcm.ViewPosition == "MLO"

    def test_set_code_sequence(self):
        factory = DicomFactory()
        vcs = DicomFactory.code_sequence("view-code")
        vcms = DicomFactory.code_sequence("view-modifier-code")
        dcm = factory(ViewCodeSequence=vcs, ViewModifierCodeSequence=vcms)
        assert dcm.ViewCodeSequence == vcs
        assert dcm.ViewModifierCodeSequence == vcms

    def test_pixel_array_from_dicom(self):
        factory = DicomFactory()
        arr = DicomFactory.pixel_array_from_dicom(factory.dicom)
        assert isinstance(arr, np.ndarray)
        assert arr.shape == (128, 128)
        # Should be deterministic for a given seed
        assert arr.min() == 9
        assert arr.max() == 65523

    @pytest.mark.parametrize("meaning", ["foo", "bar"])
    def test_code_sequence(self, meaning):
        seq = DicomFactory.code_sequence(meaning)
        assert isinstance(seq, Sequence)
        assert len(seq) == 1
        assert seq[0].CodeMeaning == meaning

    @pytest.mark.parametrize(
        "tag,value,exp",
        [
            pytest.param(Tag.PatientAge, "18Y", VR("AS")),
            pytest.param(Tag.StudyDate, "00010101", VR("DA")),
            pytest.param(Tag.StudyTime, "010101", VR("TM")),
            pytest.param(Tag.StudyInstanceUID, "1.2.345", VR("UI")),
            pytest.param(Tag.PhotometricInterpretation, "MONOCHROME1", VR("CS")),
            pytest.param(Tag.ViewCodeSequence, [Dataset()], VR("SQ")),
        ],
    )
    def test_suggest_vr(self, tag, value, exp):
        vr = DicomFactory.suggest_vr(tag, value)
        assert vr == exp

    def test_ffdm_factory(self):
        factory = FACTORY_REGISTRY.get("ffdm")()
        dcm = factory()
        assert MammogramType.from_dicom(dcm) == MammogramType.FFDM
        assert dcm.pixel_array.any()

    def test_tomo_factory(self):
        factory = FACTORY_REGISTRY.get("tomo")()
        dcm = factory()
        assert MammogramType.from_dicom(dcm) == MammogramType.TOMO
        assert dcm.pixel_array.any()

    def test_synth_factory(self):
        factory = FACTORY_REGISTRY.get("synth")()
        dcm = factory()
        assert MammogramType.from_dicom(dcm) == MammogramType.SYNTH
        assert dcm.pixel_array.any()

    def test_ultrasound_factory(self):
        factory = FACTORY_REGISTRY.get("ultrasound")()
        dcm = factory()
        assert dcm.Modality == "US"
        assert dcm.pixel_array.any()

    def test_complete_mammography_case_factory(self):
        factory = FACTORY_REGISTRY.get("mammo-case")()
        dicoms = factory()
        assert len(dicoms) == 12
        for dcm in dicoms:
            assert dcm.pixel_array.any()

    @pytest.mark.parametrize("allow", [True, False])
    def test_nonproto_tag(self, allow):
        factory = DicomFactory(allow_nonproto_tags=allow)
        assert Tag.SeriesDescription not in factory.dicom
        dcm = factory(SeriesDescription="foo")

        if allow:
            assert dcm.SeriesDescription == "foo"
        else:
            assert Tag.SeriesDescription not in dcm

    def test_skip_pixels(self):
        factory = FACTORY_REGISTRY.get("ffdm")()
        dcm = factory(pixels=False)
        assert not hasattr(dcm, "PixelData")


class TestCompleteMammographyStudyFactory:

    @pytest.fixture
    def dicoms(self):
        H, W = 64, 32
        fact = CompleteMammographyStudyFactory(
            Rows=H,
            Columns=W,
            seed=42,
            BitsAllocated=16,
            WindowCenter=4096,
            WindowWidth=8192,
        )
        dicoms = fact()

        # Ensure we have a mix of inversions
        dicoms[0].PhotometricInterpretation = "MONOCHROME1"
        dicoms[1].PhotometricInterpretation = "MONOCHROME2"

        # Ensure we have a mix of TSUIDs
        tsuids = (ImplicitVRLittleEndian, ExplicitVRLittleEndian, RLELossless)
        for dcm, tsuid in zip(dicoms[: len(tsuids)], tsuids):
            set_pixels(dcm, dcm.pixel_array, tsuid)
            dcm.file_meta.TransferSyntaxUID = tsuid

        return dicoms

    def test_dicoms(self, dicoms):
        assert len(dicoms) == 12
        for dcm in dicoms:
            assert dcm.Rows == 64
            assert dcm.Columns == 32
            assert dcm.BitsAllocated == 16
            assert dcm.WindowCenter == 4096
            assert dcm.WindowWidth == 8192
            assert dcm.NumberOfFrames in (1, 3)
            assert dcm.pixel_array is not None

    def test_save_load_dicoms(self, tmp_path, dicoms):
        for dcm in dicoms:
            dcm: pydicom.FileDataset
            dest = Path(tmp_path, f"{dcm.SOPInstanceUID}.dcm")
            dcm.save_as(dest)

        loaded = list(Path(tmp_path).glob("*.dcm"))
        assert len(loaded) == 12
        for path in loaded:
            dcm = pydicom.dcmread(path)
            assert dcm.Rows == 64
            assert dcm.Columns == 32
            assert dcm.BitsAllocated == 16
            assert dcm.WindowCenter == 4096
            assert dcm.WindowWidth == 8192
            assert dcm.NumberOfFrames in (1, 3)
            assert dcm.pixel_array is not None
            if dcm.NumberOfFrames > 1:
                assert dcm.pixel_array.shape[0] == dcm.NumberOfFrames
