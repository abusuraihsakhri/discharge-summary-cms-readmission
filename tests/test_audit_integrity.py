import pytest

from agents.base import AuditTrail, SecurityException
from agents.models import SystemTaskPayload
from agents.supervisor import SystemSupervisor


@pytest.mark.parametrize("field,replacement", [
    ("actor", "attacker"),
    ("event_type", "FORGED"),
    ("payload_hash", "0" * 64),
    ("current_hash", "f" * 64),
    ("timestamp", "2000-01-01T00:00:00Z"),
])
def test_modified_audit_fields_fail_verification(field, replacement):
    trail = AuditTrail(secret_key="unit-test-only-secret")
    trail.log("supervisor", "tier", "FIRST", {"status": "OK"})
    trail.log("supervisor", "tier", "SECOND", {"status": "OK"})
    assert trail.verify_integrity()
    trail.logs[0][field] = replacement
    assert not trail.verify_integrity()


def test_returned_trail_is_not_mutable_storage():
    trail = AuditTrail(secret_key="unit-test-only-secret")
    trail.log("supervisor", "tier", "EVALUATION", {})
    snapshot = trail.get_trail()
    snapshot[0]["actor"] = "attacker"
    snapshot.clear()
    assert trail.verify_integrity()
    assert len(trail.get_trail()) == 1


def test_phi_in_nested_attributes_is_rejected():
    payload = SystemTaskPayload(
        task_id="RESEARCH-1", target_identifier="CASE-1",
        primary_metric=10, attributes={"nested": {"email": "alice@example.org"}}
    )
    with pytest.raises(SecurityException):
        SystemSupervisor().process_task(payload)
