from human_review_gate import evaluate


def test_human_review_requires_specific_exhausted_evidence() -> None:
    status = {
        "status": "unsolved",
        "machine_analysis_exhausted": True,
        "human_review_reason": "conflicting_ocr",
        "artifact": "output/decoded-frame.png",
        "specific_question": "Are positions 8 and 14 O/0 or S/5?",
        "candidate_values": ["FLAG{A0S}", "FLAG{AOS}"],
        "remaining_machine_options": [],
        "attempted_machine_methods": ["tesseract", "easyocr", "contrast and rotation sweep"],
    }
    assert evaluate(status)["human_review_recommended"] is True


def test_tool_failure_does_not_recommend_human_review() -> None:
    status = {
        "status": "unsolved",
        "machine_analysis_exhausted": False,
        "human_review_reason": "tool_missing",
        "artifact": "image.png",
        "specific_question": "Read it",
        "remaining_machine_options": ["install OCR"],
        "attempted_machine_methods": ["missing command"],
    }
    assert evaluate(status)["human_review_recommended"] is False
