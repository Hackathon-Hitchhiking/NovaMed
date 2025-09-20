from __future__ import annotations

from typing import List, Optional, Tuple


from schemas.anamnesis import AnamnesisIn
from schemas.prediction import DiagnosisSuggestionOut


class MLClient:
    """
    Stub ML client. Replace with real model integration.

    predict(anamnesis, exam_path) -> (diagnosis_suggestions, referral_specialties)
    - diagnosis_suggestions: List[Tuple[str, float, Optional[str]]]
        (disease_name, probability, rationale)
    - referral_specialties: List[str]
    """

    async def predict(
        self,
        anamnesis: AnamnesisIn,
        exam_path: Optional[str] = None,
    ) -> Tuple[List[DiagnosisSuggestionOut], List[str]]:
        # Simple heuristics for a stub implementation
        diagnosis: List[Tuple[str, float, Optional[str]]] = []
        referrals: List[str] = []

        general = anamnesis.general or type("X", (), {"age": None, "sex": None})()
        lifestyle = anamnesis.lifestyle or type("Y", (), {"diet": None})()
        complaints = set(anamnesis.complaints or [])

        if "жажда" in complaints or lifestyle.get("diet") == ["fatty"]:
            diagnosis.append(
                DiagnosisSuggestionOut(
                    disease_name="Сахарный диабет",
                    probability=0.65,
                    rationale="жалоба на жажду / диета",
                )
            )
            referrals.append("эндокринология")

        if general.get("sex") == "male" and general.get("age", 0) > 50:
            diagnosis.append(
                DiagnosisSuggestionOut(
                    disease_name="Артериальная гипертензия",
                    probability=0.55,
                    rationale="возраст/пол",
                )
            )
            referrals.append("кардиология")

        # if an exam image is provided, slightly boost the confidence
        if exam_path:
            boosted: List[DiagnosisSuggestionOut] = []
            for item in diagnosis:
                boosted.append(
                    DiagnosisSuggestionOut(
                        disease_name=item.disease_name,
                        probability=min(item.probability + 0.1, 0.98),
                        rationale=((item.rationale or "") + " + exam") or None,
                    )
                )
            diagnosis = boosted

        # Provide default when no obvious pattern found
        if not diagnosis:
            diagnosis.append(
                DiagnosisSuggestionOut(
                    disease_name="Неспецифическое состояние", probability=0.2
                )
            )

        # Deduplicate referrals
        referrals = list(dict.fromkeys(referrals))
        return diagnosis, referrals

    async def record_outcome(
        self,
        visit_id: int,
        disease_name: str,
        is_correct: bool,
    ) -> None:
        # Stub: place to send feedback to ML system
        return None
