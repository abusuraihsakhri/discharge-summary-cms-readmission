"""LACE index point calculator (van Walraven et al., CMAJ 2010).

This is NOT the CMS Hospital-Wide All-Cause Readmission (HWR) measure.
The score describes risk stratification and is not an individualized probability.
Reference: https://pmc.ncbi.nlm.nih.gov/articles/PMC2845681/ (Table 3).
"""
from dataclasses import dataclass
from typing import Dict


def _nonnegative_integer(value: int, name: str) -> int:
    # bool is a subclass of int; reject it to avoid silently accepting True as 1.
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer")
    return value


@dataclass(frozen=True)
class LACEBreakdown:
    length_of_stay: int
    acute_admission: int
    comorbidity: int
    emergency_visits: int

    @property
    def total(self) -> int:
        return sum((self.length_of_stay, self.acute_admission, self.comorbidity, self.emergency_visits))

    def to_dict(self) -> Dict[str, int]:
        return {
            "length_of_stay": self.length_of_stay,
            "acute_admission": self.acute_admission,
            "comorbidity": self.comorbidity,
            "emergency_visits": self.emergency_visits,
            "total": self.total,
        }


def calculate_lace(
    length_of_stay_days: int,
    acute_admission: bool,
    charlson_score: int,
    ed_visits_6_months: int,
) -> LACEBreakdown:
    """Return the original LACE index components and total (range 0–19).

    The Charlson score must be computed using the index specification
    employed by the derivation study. No probability or CMS HWR estimate is made.
    """
    days = _nonnegative_integer(length_of_stay_days, "length_of_stay_days")
    if not isinstance(acute_admission, bool):
        raise ValueError("acute_admission must be a boolean")
    cci = _nonnegative_integer(charlson_score, "charlson_score")
    visits = _nonnegative_integer(ed_visits_6_months, "ed_visits_6_months")

    if days == 0:
        length_points = 0
    elif days <= 3:
        length_points = days
    elif days <= 6:
        length_points = 4
    elif days <= 13:
        length_points = 5
    else:
        length_points = 7

    return LACEBreakdown(
        length_of_stay=length_points,
        acute_admission=3 if acute_admission else 0,
        comorbidity=cci if cci <= 3 else 5,
        emergency_visits=min(visits, 4),
    )
