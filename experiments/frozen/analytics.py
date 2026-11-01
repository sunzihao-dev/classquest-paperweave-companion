"""Formative teacher reporting. Missing and unreviewed work never count as wrong."""

from collections import Counter, defaultdict
import json


def _answer_label(q, value):
    if q["kind"] == "mcq" and isinstance(value, int) and 0 <= value < len(q["options"]):
        return q["options"][value]
    if q["kind"] == "multi" and isinstance(value, list):
        return ", ".join(q["options"][i] for i in value if isinstance(i, int) and 0 <= i < len(q["options"]))
    if q["kind"] == "order" and isinstance(value, list):
        return " → ".join(q["options"][i] for i in value if isinstance(i, int) and 0 <= i < len(q["options"]))
    return "Short answer"


def build_report(quiz, questions, participants, responses, room=None):
    n = len(participants)
    by_question = defaultdict(list)
    for row in responses:
        by_question[row["question_id"]].append(row)
    q_reports = []
    topic_map = defaultdict(lambda: {"main": [], "retry": []})
    review_queue = []
    for q in questions:
        rows = by_question[q["id"]]
        scored = [r for r in rows if r["outcome"] in ("correct", "incorrect")]
        correct = sum(r["outcome"] == "correct" for r in scored)
        wrong = [r for r in scored if r["outcome"] == "incorrect"]
        choices = Counter(_answer_label(q, json.loads(r["answer_json"])) for r in wrong)
        item = {
            "id": q["id"], "prompt": q["prompt"], "topic": q["topic"], "stage": q["stage"],
            "kind": q["kind"], "locator": q["locator"], "evidence": q["evidence"],
            "participants": n, "answered": len(rows), "missing": max(0, n - len(rows)),
            "correct": correct, "incorrect": len(wrong),
            "needs_review": len(rows) - len(scored),
            "accuracy": round(correct / len(scored) * 100) if scored else None,
            "sure_and_wrong": sum(r["confidence"] == "sure" for r in wrong),
            "unsure_and_correct": sum(r["confidence"] == "unsure" and r["outcome"] == "correct" for r in scored),
            "common_wrong": choices.most_common(1)[0][0] if choices else None,
        }
        q_reports.append(item)
        topic_map[q["topic"]][q["stage"]].append(item)
        for r in rows:
            if r["outcome"] == "needs_review":
                review_queue.append({"response_id": r["id"], "question": q["prompt"],
                                     "nickname": r["nickname"], "answer": json.loads(r["answer_json"]),
                                     "rubric_hint": round((r["score"] or 0) * 100),
                                     "locator": q["locator"]})
    topics = []
    for topic, grouped in topic_map.items():
        main, retry = grouped["main"], grouped["retry"]
        def rate(items):
            total = sum(item["correct"] + item["incorrect"] for item in items)
            return round(100 * sum(item["correct"] for item in items) / total) if total else None
        main_rate, retry_rate = rate(main), rate(retry)
        scored_count = sum(item["correct"] + item["incorrect"] for item in main)
        if main_rate is None:
            action = "Collect responses or review open answers"
        elif scored_count < 3:
            action = "Early signal; gather more answers"
        elif main_rate < 55:
            action = "Reteach with a concrete example"
        elif main_rate < 80:
            action = "Give a brief recap and another example"
        else:
            action = "Move on; offer an optional challenge"
        topics.append({"topic": topic, "first_rate": main_rate, "retry_rate": retry_rate,
                       "change": retry_rate - main_rate if main_rate is not None and retry_rate is not None else None,
                       "action": action, "questions": len(main),
                       "unreviewed": sum(item["needs_review"] for item in main),
                       "missing": sum(item["missing"] for item in main)})
    topics.sort(key=lambda x: (x["first_rate"] is None, x["first_rate"] if x["first_rate"] is not None else 101))
    main_items = [item for item in q_reports if item["stage"] == "main"]
    total_scored = sum(item["correct"] + item["incorrect"] for item in main_items)
    overall = round(100 * sum(item["correct"] for item in main_items) / total_scored) if total_scored else None
    return {"quiz": quiz["title"], "room": room, "participants": n,
            "overall_first_rate": overall, "questions": q_reports, "topics": topics,
            "review_queue": review_queue, "first_submissions": sum(item["answered"] for item in main_items),
            "first_missing": sum(item["missing"] for item in main_items),
            "interpretation": "Classroom planning signal, not a high-stakes grade. Short answers await educator review."}
