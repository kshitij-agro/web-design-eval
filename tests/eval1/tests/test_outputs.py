"""
Use this file to define pytest tests that verify the outputs of the task.

This file will be copied to /tests/test_outputs.py and run by the /tests/test.sh file
from the working directory.
"""

from pathlib import Path

import numpy as np
import pytest
from PIL import Image
from skimage.metrics import structural_similarity

REFERENCE_PNG = Path("/app/reference.png")
SUBMISSION_PNG = Path("/app/output/submission.png")
SSIM_THRESHOLD = 0.90


def test_submission_matches_reference():
    """Submission screenshot must be structurally similar to the reference."""
    if not REFERENCE_PNG.is_file():
        pytest.fail(f"reference image missing: {REFERENCE_PNG}")
    if not SUBMISSION_PNG.is_file():
        pytest.fail(f"submission image missing: {SUBMISSION_PNG}")

    with Image.open(REFERENCE_PNG) as ref_img, Image.open(SUBMISSION_PNG) as sub_img:
        ref_gray = ref_img.convert("L")
        sub_gray = sub_img.convert("L")
        if sub_gray.size != ref_gray.size:
            sub_gray = sub_gray.resize(ref_gray.size, Image.LANCZOS)
        ref = np.asarray(ref_gray)
        sub = np.asarray(sub_gray)

    score = structural_similarity(ref, sub, data_range=255)
    assert score >= SSIM_THRESHOLD, (
        f"SSIM={score:.4f} below threshold {SSIM_THRESHOLD}"
    )
