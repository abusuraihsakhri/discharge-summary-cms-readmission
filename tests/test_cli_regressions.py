import csv
import json

from cli import main as primary_cli
from lace_readmission.cli import main as secondary_cli


def test_lace_cli_output(capsys):
    assert primary_cli(["lace", "--length-of-stay", "14", "--acute",
                        "--charlson", "4", "--ed-visits", "4"]) == 0
    assert json.loads(capsys.readouterr().out)["total"] == 19
    assert primary_cli(["lace", "--length-of-stay", "-1",
                        "--charlson", "0", "--ed-visits", "0"]) == 1


def test_batch_false_is_not_true(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with open("input.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "task_id", "target_identifier", "primary_metric", "secondary_metric",
            "is_critical_flag", "status_descriptor"
        ])
        writer.writeheader()
        writer.writerow(dict(task_id="TEST", target_identifier="CASE",
                             primary_metric="0", secondary_metric="0",
                             is_critical_flag="False", status_descriptor="NOMINAL"))
    assert primary_cli(["batch", "-i", "input.csv", "-o", "results1.csv"]) == 0
    assert secondary_cli(["batch", "-i", "input.csv", "-o", "results2.csv"]) == 0
    with open("results1.csv", newline="") as f:
        row = next(csv.DictReader(f))
    assert row["overall_urgency"] == "ROUTINE"
    with open("results2.csv", newline="") as f:
        row = next(csv.DictReader(f))
    assert row["overall_status"] == "NOMINAL_OPTIMAL"


def test_batch_cannot_overwrite_input_or_escape(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with open("input.csv", "w") as f:
        f.write("task_id,target_identifier,primary_metric,secondary_metric,is_critical_flag,status_descriptor\n")
    assert primary_cli(["batch", "-i", "input.csv", "-o", "input.csv"]) == 1
    assert secondary_cli(["batch", "-i", "input.csv", "-o", "../bad.csv"]) == 1
