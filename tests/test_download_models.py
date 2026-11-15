from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from scripts import download_models as downloader


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@pytest.fixture
def model_setup(monkeypatch, tmp_path):
    source_dir = tmp_path / "source"
    destination_dir = tmp_path / "models"

    source_dir.mkdir()

    contents = {
        "sentiment.joblib": b"trusted-sentiment-model",
        "toxicity.joblib": b"trusted-toxicity-model",
    }

    expected_hashes = {
        filename: sha256(content) for filename, content in contents.items()
    }

    for filename, content in contents.items():
        (source_dir / filename).write_bytes(content)

    monkeypatch.setattr(
        downloader,
        "EXPECTED_HASHES",
        expected_hashes,
    )

    return source_dir, destination_dir, contents


def test_calculate_sha256(tmp_path):
    path = tmp_path / "sample.bin"
    path.write_bytes(b"hello world")

    assert downloader.calculate_sha256(path) == sha256(b"hello world")


def test_verify_file(tmp_path):
    path = tmp_path / "model.joblib"
    path.write_bytes(b"valid-model")

    assert downloader.verify_file(path, sha256(b"valid-model"))
    assert not downloader.verify_file(path, sha256(b"other-model"))
    assert not downloader.verify_file(
        tmp_path / "missing.joblib",
        sha256(b"valid-model"),
    )


def test_successful_download_and_verification(
    monkeypatch,
    model_setup,
):
    source_dir, destination_dir, contents = model_setup
    calls = []

    def fake_download(**kwargs):
        calls.append(kwargs)
        return str(source_dir / kwargs["filename"])

    monkeypatch.setattr(
        downloader,
        "hf_hub_download",
        fake_download,
    )

    downloader.download_models(
        revision="test-revision",
        model_dir=destination_dir,
    )

    for filename, content in contents.items():
        assert (destination_dir / filename).read_bytes() == content

    assert len(calls) == len(contents)

    for call in calls:
        assert call["repo_id"] == downloader.REPO_ID
        assert call["revision"] == "test-revision"
        assert call["repo_type"] == "model"

    assert not list(destination_dir.glob("*.tmp"))


def test_existing_verified_models_are_not_downloaded(
    monkeypatch,
    model_setup,
):
    _, destination_dir, contents = model_setup
    destination_dir.mkdir()

    for filename, content in contents.items():
        (destination_dir / filename).write_bytes(content)

    def unexpected_download(**kwargs):
        pytest.fail("A verified model must not be downloaded again.")

    monkeypatch.setattr(
        downloader,
        "hf_hub_download",
        unexpected_download,
    )

    downloader.download_models(model_dir=destination_dir)

    for filename, content in contents.items():
        assert (destination_dir / filename).read_bytes() == content


def test_hash_mismatch_rejects_download(
    monkeypatch,
    model_setup,
):
    source_dir, destination_dir, _ = model_setup

    def fake_download(**kwargs):
        return str(source_dir / kwargs["filename"])

    monkeypatch.setattr(
        downloader,
        "hf_hub_download",
        fake_download,
    )

    monkeypatch.setattr(
        downloader,
        "EXPECTED_HASHES",
        {"sentiment.joblib": sha256(b"different-model")},
    )

    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        downloader.download_models(model_dir=destination_dir)

    assert not (destination_dir / "sentiment.joblib").exists()
    assert not list(destination_dir.glob("*.tmp"))


def test_download_failure_preserves_existing_file(
    monkeypatch,
    model_setup,
):
    _, destination_dir, _ = model_setup
    destination_dir.mkdir()

    existing_file = destination_dir / "sentiment.joblib"
    existing_file.write_bytes(b"existing-file")

    monkeypatch.setattr(
        downloader,
        "EXPECTED_HASHES",
        {"sentiment.joblib": sha256(b"approved-model")},
    )

    def failing_download(**kwargs):
        raise ConnectionError("Simulated network failure")

    monkeypatch.setattr(
        downloader,
        "hf_hub_download",
        failing_download,
    )

    with pytest.raises(ConnectionError, match="network failure"):
        downloader.download_models(model_dir=destination_dir)

    assert existing_file.read_bytes() == b"existing-file"
    assert not list(destination_dir.glob("*.tmp"))


def test_download_to_custom_directory(
    monkeypatch,
    model_setup,
):
    source_dir, _, contents = model_setup
    custom_dir = source_dir.parent / "custom-model-location"

    def fake_download(**kwargs):
        return Path(source_dir / kwargs["filename"])

    monkeypatch.setattr(
        downloader,
        "hf_hub_download",
        fake_download,
    )

    downloader.download_models(model_dir=custom_dir)

    assert custom_dir.is_dir()

    for filename, content in contents.items():
        assert (custom_dir / filename).read_bytes() == content
