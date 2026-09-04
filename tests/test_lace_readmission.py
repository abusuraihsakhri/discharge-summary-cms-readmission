import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from lace_readmission.models import FrontierPayload, ExecutionStatus
from lace_readmission.engine import FrontierDomainEngine
from lace_readmission.agents import LACEIndexCalculatorAgent, MedReconciliationGapAgent, PostDischargePlanAuditorAgent, LACEReadmissionCoordinator
from lace_readmission.cli import main


def test_sub_agents():
    a1 = LACEIndexCalculatorAgent()
    p1 = FrontierPayload("T1", "KEY-01", primary_metric=35.0, secondary_metric=4.0, status_descriptor="NOMINAL")
    alerts1 = a1.audit(p1)
    assert len(alerts1) == 1
    assert alerts1[0].status == ExecutionStatus.ELEVATED_RISK

    a2 = MedReconciliationGapAgent()
    p2 = FrontierPayload("T2", "KEY-02", primary_metric=10.0, secondary_metric=15.0, status_descriptor="NOMINAL", is_critical_flag=True)
    alerts2 = a2.audit(p2)
    assert len(alerts2) == 1
    assert alerts2[0].status == ExecutionStatus.CRITICAL_INTERVENTION

    a3 = PostDischargePlanAuditorAgent()
    p3 = FrontierPayload("T3", "KEY-03", primary_metric=10.0, secondary_metric=4.0, status_descriptor="DISCORDANT_ANOMALY")
    alerts3 = a3.audit(p3)
    assert len(alerts3) == 1


def test_coordinator():
    coord = LACEReadmissionCoordinator()
    p_nominal = FrontierPayload("T4", "KEY-04", primary_metric=12.0, secondary_metric=4.0, status_descriptor="NOMINAL")
    dossier = coord.process(p_nominal)
    assert dossier["overall_status"] == ExecutionStatus.NOMINAL.value
    assert dossier["total_alerts"] == 0

    ans = coord.query_supervisory_chat("What standard is applied?")
    assert "CMS Hospital-Wide All-Cause Readmission (HWR)" in ans or "specifications" in ans


def test_coordinator_critical():
    coord = LACEReadmissionCoordinator()
    p_critical = FrontierPayload("T5", "KEY-05", primary_metric=45.0, secondary_metric=20.0, status_descriptor="VIOLATION", is_critical_flag=True)
    dossier = coord.process(p_critical)
    assert dossier["overall_status"] == ExecutionStatus.CRITICAL_INTERVENTION.value
    assert dossier["total_alerts"] >= 2
    assert dossier["critical_count"] >= 1


def test_cli():
    assert main(["audit", "--task-id", "CLI-01"]) == 0
    assert main(["chat", "What", "is", "the", "system", "status?"]) == 0


def test_batch_path_traversal_blocked(tmp_path):
    """Batch command must reject paths outside the working directory."""
    outside = tmp_path / "outside.csv"
    outside.write_text("task_id,target_identifier,primary_metric,secondary_metric,is_critical_flag,status_descriptor\nT1,K1,10.0,5.0,False,NOMINAL\n")
    assert main(["batch", "-i", str(outside)]) == 1


def test_batch_missing_file():
    """Batch command must return error when file does not exist."""
    assert main(["batch", "-i", "nonexistent_file_12345.csv"]) == 1


def test_batch_valid_input(tmp_path, monkeypatch):
    """Batch command processes valid CSV within working directory."""
    monkeypatch.chdir(tmp_path)
    csv_path = tmp_path / "input.csv"
    csv_path.write_text("task_id,target_identifier,primary_metric,secondary_metric,is_critical_flag,status_descriptor\nT1,K1,10.0,5.0,False,NOMINAL\n")
    assert main(["batch", "-i", "input.csv", "-o", "output.csv"]) == 0
    assert (tmp_path / "output.csv").exists()


def test_engine_boundaries():
    """Verify engine threshold boundaries are correct."""
    assert FrontierDomainEngine.PRIMARY_BOUND == 25.0
    assert FrontierDomainEngine.SECONDARY_BOUND == 10.0

    # At boundary - should not trigger
    assert FrontierDomainEngine.evaluate_primary_parameter(25.0) is None
    assert FrontierDomainEngine.evaluate_secondary_kinetics(10.0, False) is None

    # Just above boundary - should trigger
    assert FrontierDomainEngine.evaluate_primary_parameter(25.01) is not None
    assert FrontierDomainEngine.evaluate_secondary_kinetics(10.01, False) is not None
