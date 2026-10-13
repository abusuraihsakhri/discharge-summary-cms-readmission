# Discharge Summary CMS Readmission

A research-oriented LACE index calculator alongside two legacy, experimental audit pipelines. The offline browser calculator implements the published **LACE point rubric (0–19)**.

**Not a clinical decision support system.** LACE does not implement the CMS Hospital-Wide All-Cause Readmission (HWR) measure. Neither the browser tool nor the legacy threshold-based engines estimate an individualized readmission probability, interpret discharge summaries, or perform medication reconciliation. The software is not clinically validated and must not direct patient care.

## Browser calculator

Open [web/index.html](web/index.html) in a modern browser. Enter:

- Inpatient length of stay, in whole days (0 denotes less than one day)
- Whether the admission was acute/emergent
- Charlson comorbidity index score, calculated using the derivation study definition
- Number of emergency department visits in the preceding six months

The output reports four point components and their sum. All calculations run locally in JavaScript; the page loads no external libraries or APIs and sends no input data to a server. **Do not enter patient identifiers or protected health information.**

A [GitHub Pages publishing workflow](.github/workflows/pages.yml) is included. Availability of a hosted site depends on the repository's Pages configuration and successful workflow deployment; the hosted URL should not be used until verified.

### Point calculation

| Component | Input | Points |
|---|---|---|
| Length of stay | 0, 1, 2, 3, 4–6, 7–13, ≥14 days | 0, 1, 2, 3, 4, 5, 7 |
| Acuity | Acute/emergent admission | 3, otherwise 0 |
| Comorbidity | Charlson score 0, 1, 2, 3, ≥4 | 0, 1, 2, 3, 5 |
| ED visits | 0, 1, 2, 3, ≥4 over previous six months | 0, 1, 2, 3, 4 |

**Source:** van Walraven C, et al. *Derivation and validation of an index to predict early death or unplanned readmission after discharge from hospital to the community.* CMAJ. 2010. [Original paper and Table 3](https://pmc.ncbi.nlm.nih.gov/articles/PMC2845681/).

The original endpoint included death **or** unplanned readmission within 30 days. The LACE score alone is not a CMS quality measure and does not calculate an absolute risk without separate, validated calibration. Refer to the [CMS outcome-measure methodology](https://www.cms.gov/medicare/quality/initiatives/hospital-quality-initiative/measure-methodology) for HWR specifications.

## Python and CLI

Python 3.9+ is required. From the repository root:

```bash
python -m pip install -e ".[test]"
python -m pytest -q
node --check web/app.js
node --test tests/lace-browser.test.cjs
```

Node.js is used only for the optional browser-logic tests; it is not needed to run the browser app or Python services.

Calculate LACE points from the CLI:

```bash
python cli.py lace --length-of-stay 14 --acute --charlson 4 --ed-visits 4
# outputs the four components and a total of 19
```

The same command is available through `python lace_readmission_app.py lace ...` and the installed `discharge-summary-cms-readmission` executable.

Programmatic Python:

```python
from lace_readmission.lace_score import calculate_lace
breakdown = calculate_lace(14, True, 4, 4)
print(breakdown.to_dict())
```

## HTTP APIs and legacy demonstrations

```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

- `POST /api/lace`: strict, nonnegative integer inputs `length_of_stay_days`, `charlson_score`, `ed_visits_6_months`; boolean `acute_admission`. Returns the original LACE point components and total.
- `GET /health`: process health check.
- `POST /api/audit`, `POST /api/chat`, `GET /api/audit/logs`, `GET /metrics`: legacy experimental threshold/audit endpoints, **not** clinical risk-scoring or CMS compliance.
- `python cli.py audit`, `batch`, `chat`, `verify-audit`: preserved experimental CLI operations.
- `python lace_readmission_app.py serve`: an alternative legacy service that also exposes `POST /api/lace`.

The `agents/` and `lace_readmission/` audit subsystems evaluate generic demonstration thresholds (including primary metric >25); these numbers have no established interpretation as LACE scores or CMS HWR specifications. `enrichment.py` contains illustrative threshold modules rather than implemented clinical feature pipelines. No real external language-model provider integration is supplied.

## Security and deployment

The HTML app has no backend dependency and should be used with synthetic, aggregate data. The Python APIs have **no authentication or production PHI protections**; do not expose them publicly or send clinical records to them. The identifier filter detects a limited set of patterns and **does not guarantee HIPAA de-identification**.

Audit entries are HMAC-SHA256 chained and verified within one process. The log is in-memory, and an unset `AUDIT_SECRET_KEY` uses a random **ephemeral** development key; this is not a durable compliance audit store. To run Docker Compose, set a private `AUDIT_SECRET_KEY` environment variable (see [.env.example](.env.example)). Never commit the real key. Existing keys that were once embedded in repository configuration must be rotated if used.

```bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
docker compose up --build
```

The Docker example binds port 8000; deploy only within a secured, access-controlled environment.

## Technology and compatibility

Python, Pydantic, FastAPI, pytest; dependency-free HTML, CSS, and JavaScript. Browser calculator supports current Chromium, Firefox and Safari engines with JavaScript enabled. Python packaging and tests run in GitHub Actions for Python 3.10–3.12. The Pages workflow serves only the `web/` static assets.

## License

[MIT](LICENSE).
