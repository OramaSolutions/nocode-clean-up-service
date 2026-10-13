"""Training state of a version as seen on disk."""

from pathlib import Path

# Where a finished training leaves its model inside a version folder. Weights
# only reach the server after the RunPod job finishes and its results are
# downloaded, so finding them proves the training really completed.
WEIGHT_PATTERNS = (
    "detect/train*/weights/*.pt",
    "segment/train*/weights/*.pt",
    "classify/train*/weights/*.pt",
    "model/model.pt",  # defect detection
)
# Train step status meaning "finished", as stored in the project's stepData.
COMPLETED = "completed"


def has_trained_model(version: Path) -> bool:
    return any(next(version.glob(pattern), None) is not None for pattern in WEIGHT_PATTERNS)
