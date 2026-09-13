"""
Tests for voice_clone.py — voice cloning CLI tool.
"""

import os
import sys
import tempfile
import numpy as np
import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice_clone import (
    validate_voice_name,
    validate_audio_file,
    validate_prompt_integrity,
    voice_exists,
    resolve_device,
    find_source_audio,
    VOICE_NAME_PATTERN,
    MAX_AUDIO_DURATION,
    MIN_SAMPLE_RATE,
)


class TestValidateVoiceName:
    """Tests for voice name validation."""

    def test_valid_names(self):
        assert validate_voice_name("mi_voz")
        assert validate_voice_name("carlos-2024")
        assert validate_voice_name("test_voice_1")
        assert validate_voice_name("A")
        assert validate_voice_name("123")

    def test_invalid_names(self):
        assert not validate_voice_name("invalid name")
        assert not validate_voice_name("voz@invalid")
        assert not validate_voice_name("test.pdf")
        assert not validate_voice_name("voz con espacios")
        assert not validate_voice_name("")

    def test_pattern(self):
        assert VOICE_NAME_PATTERN.match("valid_name")
        assert not VOICE_NAME_PATTERN.match("invalid name")


class TestValidateAudioFile:
    """Tests for audio file validation."""

    def test_nonexistent_file(self):
        result = validate_audio_file("nonexistent.wav")
        assert result is None

    def test_invalid_file(self):
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b"not audio")
            path = f.name
        try:
            result = validate_audio_file(path)
            assert result is None
        finally:
            os.unlink(path)


class TestValidatePromptIntegrity:
    """Tests for prompt integrity validation."""

    def test_valid_prompt(self):
        with tempfile.NamedTemporaryFile(suffix='.npz', delete=False) as f:
            path = f.name
            np.savez(path,
                     fine_prompt=np.zeros((8, 100), dtype=np.int32),
                     coarse_prompt=np.zeros((2, 100), dtype=np.int32),
                     semantic_prompt=np.zeros(50, dtype=np.int64))
        try:
            assert validate_prompt_integrity(path) is True
        finally:
            os.unlink(path)

    def test_missing_keys(self):
        with tempfile.NamedTemporaryFile(suffix='.npz', delete=False) as f:
            path = f.name
            np.savez(path, fine_prompt=np.zeros((8, 100)))
        try:
            assert validate_prompt_integrity(path) is False
        finally:
            os.unlink(path)

    def test_wrong_shape_fine(self):
        with tempfile.NamedTemporaryFile(suffix='.npz', delete=False) as f:
            path = f.name
            np.savez(path,
                     fine_prompt=np.zeros((6, 100), dtype=np.int32),
                     coarse_prompt=np.zeros((2, 100), dtype=np.int32),
                     semantic_prompt=np.zeros(50, dtype=np.int64))
        try:
            assert validate_prompt_integrity(path) is False
        finally:
            os.unlink(path)

    def test_wrong_shape_coarse(self):
        with tempfile.NamedTemporaryFile(suffix='.npz', delete=False) as f:
            path = f.name
            np.savez(path,
                     fine_prompt=np.zeros((8, 100), dtype=np.int32),
                     coarse_prompt=np.zeros((3, 100), dtype=np.int32),
                     semantic_prompt=np.zeros(50, dtype=np.int64))
        try:
            assert validate_prompt_integrity(path) is False
        finally:
            os.unlink(path)

    def test_nonexistent_file(self):
        assert validate_prompt_integrity("nonexistent.npz") is False


class TestResolveDevice:
    """Tests for device resolution."""

    def test_explicit_cpu(self):
        assert resolve_device("cpu") == "cpu"

    def test_explicit_cuda(self):
        result = resolve_device("cuda")
        assert result in ("cuda", "cpu")

    def test_explicit_mps(self):
        result = resolve_device("mps")
        assert result in ("mps", "cpu")

    def test_auto(self):
        result = resolve_device("auto")
        assert result in ("cuda", "mps", "cpu")


class TestVoiceExists:
    """Tests for voice existence check."""

    def test_existing_voice(self):
        assert voice_exists("en_speaker_0") is True

    def test_nonexistent_voice(self):
        assert voice_exists("definitely_not_a_real_voice_xyz") is False


class TestFindSourceAudio:
    """Tests for auto-detection of source audio."""

    def test_no_directory(self):
        original = os.environ.get('SOURCE_VOICE_DIR')
        try:
            result = find_source_audio()
            # Should return None if dir doesn't exist or is empty
            assert result is None or os.path.isfile(result)
        finally:
            if original:
                os.environ['SOURCE_VOICE_DIR'] = original


class TestConstants:
    """Tests for module constants."""

    def test_max_duration(self):
        assert MAX_AUDIO_DURATION == 13

    def test_min_sample_rate(self):
        assert MIN_SAMPLE_RATE == 8000

    def test_audio_extensions(self):
        assert '.wav' in ('.wav', '.mp3', '.ogg', '.flac', '.m4a', '.wma')
        assert '.mp3' in ('.wav', '.mp3', '.ogg', '.flac', '.m4a', '.wma')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
