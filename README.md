# Discharge Summary CMS Readmission

> **Domain:** Clinical Decision Support & Biomedical Computing
> **Standard:** CMS Hospital-Wide All-Cause Readmission (HWR)

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

Discharge Summary CMS Readmission is a clinical decision support system that evaluates patient discharge data against CMS Hospital-Wide All-Cause Readmission (HWR) specifications. It provides multi-agent evaluation with HMAC-SHA256 tamper-evident audit trails and zero-PHI outbound guarding.

The system contains two integrated subsystems:
- **`agents/`** - Enterprise supervisor with PHI guard, audit trail, and specialized workers
- **`lace_readmission/`** - LACE index (Length of stay, Acuity, Comorbidities, ED visits) calculator with medication reconciliation gap detection

---

## ⚙️ Key Capabilities & Algorithmic Modules

- **Deterministic Calculation Engine**: Strict compliance with CMS HWR formulations and thresholds.
- **Risk & Urgency Classification**: Multi-tier categorization (ROUTINE, ELEVATED_RISK, CRITICAL_STAT_PANIC).
- **Validation & Guardrails**: Rigorous input bounds checking and anomaly detection.
- **Zero-PHI Outbound Interceptor**: Active regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
- **HMAC-SHA256 Audit Trail**: Chained, cryptographically signed logs for every evaluation.
- **FastAPI REST API**: Exposes OpenAPI endpoints and operational Prometheus metrics.

---

## 💻 Installation

```bash
pip install -e ".[test]"
```

Or with dependencies only:
```bash
pip install -e .
```

---

## 💻 CLI Quickstart & Usage

### 1. Run Audit (Single Task Evaluation)
```bash
# Top-level CLI (agents subsystem)
python cli.py audit --task-id TASK-001 --target TARGET-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT

# LACE Readmission CLI
python lace_readmission_app.py audit --task-id TASK-001 --target TARGET-01 --primary 29.4 --secondary 15.1 --critical --status DISCORDANT
```

### 2. Interactive Chat Query
```bash
python cli.py chat "What is the system status?"
python lace_readmission_app.py chat "What standard is applied?"
```

### 3. Batch Process CSV
```bash
python cli.py batch -i sample.csv -o results.csv
python lace_readmission_app.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch FastAPI Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
python lace_readmission_app.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
- `--task-id`: Unique task / case identifier
- `--target`: Entity or target identifier
- `--primary`: Primary domain measurement or score (float)
- `--secondary`: Secondary kinetic or confidence score (float)
- `--critical`: Emergency escalation flag
- `--status`: Status code or phenotype descriptor

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `task_id` | Parameter / observation metric | Required |
| `target_identifier` | Parameter / observation metric | Required |
| `primary_metric` | Parameter / observation metric | Required |
| `secondary_metric` | Parameter / observation metric | Required |
| `is_critical_flag` | Emergency escalation flag | Required |
| `status_descriptor` | Status code or phenotype | Required |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Path Traversal Protection:** Batch commands validate input paths remain within the working directory.
* **Secure Key Handling:** Audit secret key sourced from `AUDIT_SECRET_KEY` environment variable with development fallback warning.

---

## 🧪 Testing & Verification

Run the full automated test suite:

```bash
pytest -v
```

Run specific test modules:

```bash
pytest tests/test_discharge_summary_cms_readmission.py -v
pytest tests/test_lace_readmission.py -v
pytest tests/test_enrichment.py -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## 🐳 Container Deployment

```bash
docker build -t discharge-summary-cms-readmission .
docker run -p 8000:8000 discharge-summary-cms-readmission
```

With docker-compose:

```bash
docker-compose up
```

---

## 📁 Project Structure

```
discharge-summary-cms-readmission/
├── agents/                    # Enterprise agent subsystem
│   ├── api.py                 # FastAPI REST server
│   ├── base.py                # PHI guard, HMAC audit trail, security
│   ├── llm_factory.py         # LLM provider abstraction
│   ├── models.py              # Pydantic data models
│   ├── supervisor.py          # Multi-agent orchestrator
│   ├── workers.py             # Specialized evaluation workers
│   ├── learning.py            # Bayesian calibration engine
│   ├── metrics.py             # Prometheus metrics exporter
│   └── streamer.py            # WebSocket telemetry broadcaster
├── lace_readmission/          # LACE Readmission subsystem
│   ├── agents.py              # LACE coordinator and sub-agents
│   ├── engine.py              # Domain calculation engine
│   ├── models.py              # Data models and status enums
│   ├── cli.py                 # CLI entry point
│   └── server.py              # FastAPI server factory
├── tests/                     # Test suite
├── web/                       # Static web interface
├── cli.py                     # Top-level CLI entry point
├── lace_readmission_app.py    # LACE CLI entry point
├── enrichment.py              # Feature enrichment engines
├── simulator.py               # Stress testing simulator
├── sample.csv                 # Sample batch input
├── sample_payload.json        # Sample API payload
├── benchmark_dataset.json     # Golden benchmark test cases
├── Dockerfile                 # Container build
├── docker-compose.yml         # Multi-container orchestration
└── pyproject.toml             # Project metadata and dependencies
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
