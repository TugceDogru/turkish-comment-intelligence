from __future__ import annotations

import argparse
import hashlib
import os
import tempfile
from pathlib import Path

from huggingface_hub import hf_hub_download

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_DIR = PROJECT_ROOT / "models" / "baseline_tuned"

REPO_ID = "TugceDogru/turkish-comment-intelligence-baselines"
PINNED_REVISION = "de3bace638060b19fe41e448e1931df6f73948fc"

EXPECTED_HASHES = {
    "actionability.joblib": (
        "ba028bd869f9ba0b05e54c503fd721a22ba43363067b55bdd9b91270999c919a"
    ),
    "question_type.joblib": (
        "27f36a67ea383cfbd81075cf179a270237d3b78388eec06535a2cc782dca8bbc"
    ),
    "sentiment.joblib": (
        "32b9438b8277f13656d9d027630748713d0146b4190db557fedda7fe21e1541e"
    ),
    "toxicity.joblib": (
        "1048cd36f371b027938db97ce0b6d561a80720aea3e4c0fcc9c5c36103daa1a0"
    ),
}


def calculate_sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def verify_file(path: Path, expected_hash: str) -> bool:
    return path.is_file() and calculate_sha256(path) == expected_hash


def download_models(
    revision: str = PINNED_REVISION,
    model_dir: Path | str = DEFAULT_MODEL_DIR,
) -> None:
    destination_dir = Path(model_dir)
    destination_dir.mkdir(parents=True, exist_ok=True)

    for filename, expected_hash in EXPECTED_HASHES.items():
        destination = destination_dir / filename

        if verify_file(destination, expected_hash):
            print(f"[OK] Already verified: {filename}")
            continue

        print(f"[DOWNLOAD] {filename}")

        # Only download from the approved repository and revision.
        # Never deserialize an artifact during download.
        downloaded_path = Path(
            hf_hub_download(
                repo_id=REPO_ID,
                filename=filename,
                repo_type="model",
                revision=revision,
            )
        )

        if not verify_file(downloaded_path, expected_hash):
            raise ValueError(
                f"SHA-256 mismatch for {filename}. "
                "The downloaded artifact does not match the approved file."
            )

        temporary_path = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                dir=destination_dir,
                prefix=f".{filename}.",
                suffix=".tmp",
                delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)

                with downloaded_path.open("rb") as source:
                    for chunk in iter(
                        lambda: source.read(1024 * 1024),
                        b"",
                    ):
                        temporary_file.write(chunk)

            if not verify_file(temporary_path, expected_hash):
                raise ValueError(f"SHA-256 mismatch while copying {filename}.")

            os.replace(temporary_path, destination)
            print(f"[OK] Verified: {filename}")

        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

    print("\nAll four model artifacts are verified.")
    print(f"Model directory: {destination_dir.resolve()}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download and verify approved baseline models."
    )
    parser.add_argument(
        "--revision",
        default=PINNED_REVISION,
        help="Hugging Face commit SHA (defaults to the verified revision).",
    )
    parser.add_argument(
        "--model-dir",
        type=Path,
        default=DEFAULT_MODEL_DIR,
        help="Destination directory for verified model artifacts.",
    )

    args = parser.parse_args()
    download_models(revision=args.revision, model_dir=args.model_dir)


if __name__ == "__main__":
    main()
