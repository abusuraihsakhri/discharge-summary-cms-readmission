import pytest

from lace_readmission.lace_score import calculate_lace


@pytest.mark.parametrize(
    "days, expected",
    [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (6, 4),
     (7, 5), (13, 5), (14, 7), (365, 7)],
)
def test_length_of_stay_points(days, expected):
    assert calculate_lace(days, False, 0, 0).length_of_stay == expected


@pytest.mark.parametrize("cci,points", [(0, 0), (1, 1), (2, 2), (3, 3), (4, 5), (12, 5)])
def test_comorbidity_points(cci, points):
    assert calculate_lace(0, False, cci, 0).comorbidity == points


@pytest.mark.parametrize("visits,points", [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (20, 4)])
def test_emergency_visits_points(visits, points):
    assert calculate_lace(0, False, 0, visits).emergency_visits == points


def test_components_sum_to_nineteen():
    breakdown = calculate_lace(14, True, 4, 4)
    assert breakdown.to_dict() == {
        "length_of_stay": 7,
        "acute_admission": 3,
        "comorbidity": 5,
        "emergency_visits": 4,
        "total": 19,
    }
    assert calculate_lace(0, False, 0, 0).total == 0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"length_of_stay_days": -1},
        {"length_of_stay_days": True},
        {"length_of_stay_days": 2.5},
        {"acute_admission": 1},
        {"charlson_score": -1},
        {"charlson_score": True},
        {"ed_visits_6_months": -1},
        {"ed_visits_6_months": 1.5},
    ],
)
def test_invalid_inputs_raise(kwargs):
    inputs = dict(length_of_stay_days=2, acute_admission=False,
                  charlson_score=0, ed_visits_6_months=0)
    inputs.update(kwargs)
    with pytest.raises(ValueError):
        calculate_lace(**inputs)
