from __future__ import annotations

from pathlib import Path

import pytest

from src.models import inference


class FakeModel:
    """Small deterministic model used only for testing."""

    def __init__(self, classes: set[str]):
        self.classes_ = sorted(classes)
        self.prediction_calls = 0
        self.probability_calls = 0

    def predict(self, texts):
        self.prediction_calls += 1
        return [self.classes_[0] for _ in texts]

    def predict_proba(self, texts):
        self.probability_calls += 1
        probability = 1.0 / len(self.classes_)
        return [[probability for _ in self.classes_] for _ in texts]


@pytest.fixture
def classifier(monkeypatch, tmp_path):
    """Build a classifier without loading real model artifacts."""

    fake_models = {}

    for task in inference.TASKS:
        (tmp_path / f"{task}.joblib").touch()
        fake_models[task] = FakeModel(inference.EXPECTED_CLASSES[task])

    def fake_load(path):
        task = Path(path).stem
        return fake_models[task]

    monkeypatch.setattr(inference.joblib, "load", fake_load)

    instance = inference.CommentClassifier(model_dir=tmp_path)
    return instance, fake_models


def test_all_tasks_are_loaded(classifier):
    instance, models = classifier

    assert set(instance.models) == set(inference.TASKS)
    assert set(models) == set(inference.TASKS)


def test_single_prediction_structure(classifier):
    instance, _ = classifier

    result = instance.predict("Harika bir video olmuş!")

    assert result["text"] == "Harika bir video olmuş!"
    assert result["model_family"] == "tuned_baseline"
    assert set(result["predictions"]) == set(inference.TASKS)

    for task in inference.TASKS:
        prediction = result["predictions"][task]

        assert prediction["label"] in inference.EXPECTED_CLASSES[task]
        assert set(prediction["probabilities"]) == (inference.EXPECTED_CLASSES[task])
        assert sum(prediction["probabilities"].values()) == pytest.approx(
            1.0,
            abs=0.00001,
        )


def test_batch_prediction_preserves_order(classifier):
    instance, _ = classifier

    texts = [
        "Birinci yorum",
        "İkinci yorum",
        "Üçüncü yorum",
    ]

    results = instance.predict_batch(texts)

    assert [result["text"] for result in results] == texts
    assert len(results) == 3


def test_batch_calls_each_model_once(classifier):
    instance, models = classifier

    instance.predict_batch(["Birinci yorum", "İkinci yorum"])

    for model in models.values():
        assert model.prediction_calls == 1
        assert model.probability_calls == 1


def test_empty_batch_returns_empty_list(classifier):
    instance, models = classifier

    assert instance.predict_batch([]) == []

    for model in models.values():
        assert model.prediction_calls == 0
        assert model.probability_calls == 0


@pytest.mark.parametrize("text", ["", " ", "\n\t"])
def test_empty_comment_is_rejected(classifier, text):
    instance, _ = classifier

    with pytest.raises(ValueError, match="cannot be empty"):
        instance.predict(text)


@pytest.mark.parametrize("text", [None, 123, 3.14, ["yorum"]])
def test_non_string_comment_is_rejected(classifier, text):
    instance, _ = classifier

    with pytest.raises(TypeError, match="must be a string"):
        instance.predict(text)


@pytest.mark.parametrize("texts", ["yorum", b"yorum", None, 123])
def test_invalid_batch_container_is_rejected(classifier, texts):
    instance, _ = classifier

    with pytest.raises(TypeError, match="sequence of strings"):
        instance.predict_batch(texts)


def test_invalid_comment_inside_batch_is_rejected(classifier):
    instance, models = classifier

    with pytest.raises(ValueError, match="cannot be empty"):
        instance.predict_batch(["Geçerli yorum", "  "])

    for model in models.values():
        assert model.prediction_calls == 0


def test_comment_whitespace_is_trimmed(classifier):
    instance, _ = classifier

    result = instance.predict("  Harika bir video!  ")

    assert result["text"] == "Harika bir video!"


def test_missing_model_file_raises_error(tmp_path):
    with pytest.raises(FileNotFoundError, match="Missing model"):
        inference.CommentClassifier(model_dir=tmp_path)


def test_unexpected_model_classes_are_rejected(monkeypatch, tmp_path):
    for task in inference.TASKS:
        (tmp_path / f"{task}.joblib").touch()

    class InvalidModel(FakeModel):
        def __init__(self):
            super().__init__({"UNKNOWN"})

    monkeypatch.setattr(
        inference.joblib,
        "load",
        lambda path: InvalidModel(),
    )

    with pytest.raises(ValueError, match="Unexpected classes"):
        inference.CommentClassifier(model_dir=tmp_path)


def test_model_without_predict_is_rejected(monkeypatch, tmp_path):
    for task in inference.TASKS:
        (tmp_path / f"{task}.joblib").touch()

    class InvalidModel:
        classes_ = ["UNKNOWN"]

        def predict_proba(self, texts):
            return []

    monkeypatch.setattr(
        inference.joblib,
        "load",
        lambda path: InvalidModel(),
    )

    with pytest.raises(TypeError, match=r"predict\(\)"):
        inference.CommentClassifier(model_dir=tmp_path)
