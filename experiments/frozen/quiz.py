"""Question validation and conservative, explainable grading."""

import json
import re
import unicodedata

KINDS = {"mcq", "multi", "order", "short"}


def clean_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    value = re.sub(r"[^\w%]+", " ", value, flags=re.UNICODE)
    return " ".join(value.split())


def phrase_present(answer: str, phrase: str) -> bool:
    target = clean_text(phrase)
    return bool(target) and f" {target} " in f" {clean_text(answer)} "


def validate_question(q: dict, source_text: str, passages: dict[str, str] | None = None):
    required = ["stage", "topic", "kind", "prompt", "options", "answer", "evidence", "locator"]
    if any(key not in q for key in required):
        raise ValueError("The question needs a stage, topic, type, prompt, options, answer, evidence and locator.")
    if q["stage"] not in {"main", "retry"} or q["kind"] not in KINDS:
        raise ValueError("Unsupported question stage or type.")
    for key in ("topic", "prompt", "evidence", "locator"):
        if not isinstance(q[key], str) or not q[key].strip() or len(q[key]) > 1000:
            raise ValueError(f"Invalid {key}.")
    if clean_text(q["evidence"]) not in clean_text(source_text):
        raise ValueError("The evidence must be an exact passage from the selected source. Pick a source quote before publishing.")
    if passages is not None and (q["locator"] not in passages or clean_text(q["evidence"]) not in clean_text(passages[q["locator"]])):
        raise ValueError("The evidence must appear in the selected source location.")
    options, answer = q["options"], q["answer"]
    if not isinstance(options, list) or len(options) > 8 or not all(isinstance(x, str) and x.strip() and len(x) <= 240 for x in options):
        raise ValueError("Options must be a list of up to eight short strings.")
    if q["kind"] == "mcq" and (len(options) < 2 or not isinstance(answer, int) or isinstance(answer, bool) or not 0 <= answer < len(options)):
        raise ValueError("A multiple-choice question needs two or more options and one answer index.")
    if q["kind"] == "multi" and (len(options) < 2 or not isinstance(answer, list) or not answer or any(not isinstance(x, int) or isinstance(x, bool) or x < 0 or x >= len(options) for x in answer) or len(set(answer)) != len(answer)):
        raise ValueError("Select-all questions need valid answer indices.")
    if q["kind"] == "order" and (len(options) < 2 or not isinstance(answer, list) or sorted(answer) != list(range(len(options)))):
        raise ValueError("Ordering questions need each block index exactly once.")
    if q["kind"] == "short":
        rubric = q.get("rubric", [])
        if options or not isinstance(answer, str) or not answer.strip() or not isinstance(rubric, list) or not rubric:
            raise ValueError("Short answers need a model answer and required concept groups.")
        if not all(isinstance(group, list) and group and all(isinstance(term, str) and term.strip() for term in group) for group in rubric):
            raise ValueError("Each rubric group must contain acceptable phrases.")


def grade(q: dict, answer):
    kind = q["kind"]
    correct = q["answer"]
    if kind == "mcq":
        if not isinstance(answer, int) or isinstance(answer, bool) or not 0 <= answer < len(q["options"]):
            raise ValueError("Choose one answer.")
        score = float(answer == correct)
    elif kind == "multi":
        if not isinstance(answer, list) or any(not isinstance(x, int) or isinstance(x, bool) or x < 0 or x >= len(q["options"]) for x in answer) or len(set(answer)) != len(answer):
            raise ValueError("Select one or more valid answers.")
        gold, given = set(correct), set(answer)
        score = len(gold & given) / len(gold | given) if gold | given else 0.0
    elif kind == "order":
        if not isinstance(answer, list) or sorted(answer) != list(range(len(q["options"]))):
            raise ValueError("Put every block in order.")
        score = sum(a == b for a, b in zip(answer, correct)) / len(correct)
    else:
        if not isinstance(answer, str) or not answer.strip() or len(answer) > 1500:
            raise ValueError("Write a short answer (up to 1500 characters).")
        # Rubric matching is a hint for the teacher, never an automatic pass.
        groups = q["rubric"]
        covered = sum(any(phrase_present(answer, item) for item in group) for group in groups)
        return round(covered / len(groups), 3), "needs_review"
    return round(score, 3), "correct" if score == 1 else "incorrect"


def unpack_question(row, include_key=True):
    q = dict(row)
    q["options"] = json.loads(q.pop("options_json"))
    q["answer"] = json.loads(q.pop("answer_json"))
    q["rubric"] = json.loads(q.pop("rubric_json"))
    if not include_key:
        for field in ("answer", "rubric", "explanation", "evidence"):
            q.pop(field, None)
    return q
