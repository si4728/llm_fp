from __future__ import annotations

from typing import Any


class Oracle:
    """Deterministic post-hoc evaluation for function delegation experiments."""

    def evaluate_case(self, case_id: str, payload: dict[str, Any]):
        if case_id == "C01":
            return int(payload["a"]) + int(payload["b"])
        if case_id == "C02":
            return float(payload["a"]) / float(payload["b"])
        if case_id == "C03":
            if float(payload["b"]) == 0:
                return "DIVISION_BY_ZERO"
            return float(payload["a"]) / float(payload["b"])
        if case_id == "C04":
            return len(str(payload["text"]).split())
        if case_id == "C05":
            return len(str(payload["text"]))
        if case_id == "C06":
            text = str(payload["text"])
            return len(text.replace(" ", ""))
        if case_id == "C07":
            score = float(payload["score"])
            if score >= 90:
                return "A"
            if score >= 80:
                return "B"
            if score >= 70:
                return "C"
            return "D"
        if case_id == "C08":
            return int(payload["a"]) - int(payload["b"])
        if case_id == "C09":
            return (int(payload["a"]) + int(payload["b"])) * int(payload["c"])
        if case_id == "C10":
            return len(str(payload["text"]).split())
        if case_id == "C11":
            return "ASK_FOR_CLARIFICATION"
        if case_id == "C12":
            value = int(payload["value"])
            if value > 0:
                return "POSITIVE"
            if value < 0:
                return "NEGATIVE"
            return "ZERO"
        if case_id == "C13":
            score = float(payload["score"])
            if score >= 70:
                return "PASS"
            return "FAIL"
        if case_id == "C14":
            return len(str(payload["text"]))
        if case_id == "C15":
            return len(str(payload["text"]))
        if case_id == "C16":
            return round(float(payload["value"]), 2)
        if case_id == "C17":
            return bool(payload["a"]) and bool(payload["b"]) or bool(payload["c"])
        if case_id == "C18":
            year = int(payload["year"])
            if year % 400 == 0:
                return True
            if year % 100 == 0:
                return False
            return year % 4 == 0
        if case_id == "C19":
            values = list(payload["values"])
            return sorted(set(values))
        if case_id == "C20":
            return int(payload["x"]) + int(payload["y"])
        raise ValueError(f"Unsupported case_id: {case_id}")
