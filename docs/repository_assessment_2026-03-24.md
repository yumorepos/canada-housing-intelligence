# Repository Assessment and Truth-First Improvement Plan

_Date assessed: 2026-03-24 (UTC)_

## 1. Executive verdict
Canada Housing Intelligence is a strong **truth-aware local prototype** with real product shape (Canada overview + city drill-downs), source-backed ingestion support, and working quality checks, but it is still short of a fully trustworthy analytics product because freshness/provenance signals are lightweight, the data workflow is still manual, and deployment/demo polish is uneven.

## 2. Current-state audit

### Product clarity and UX
- The Streamlit app launches into a Canada-first flow and then city drill-downs, with dynamic city renderer resolution based on module naming.
- The Canada page includes decision snapshot metrics, table, trend charts, and analyst notes.
- The city page includes KPI cards, trajectory plots, neighborhood momentum, support scoring, and analyst notes.

Assessment:
- **Working:** product flow and narrative are coherent for a recruiter demo.
- **Partial:** several labels/subtitles still imply sample-only context even though source-backed mode exists.
- **Fragile:** city additions still depend on file/module naming convention and the existence of page wrappers.

### Architecture and code quality
- Shared analysis logic is centralized in `analysis/city_metrics.py`, and UI pages are mostly composition wrappers.
- Config loading and profile merging are handled by `app/utils/config.py`.
- Data loading is centralized in `app/utils/data_loader.py`, including fallback and freshness status extraction.

Assessment:
- **Working:** decent modular separation for a portfolio app.
- **Partial:** duplicated path bootstrap snippets (`sys.path` manipulation) appear across modules.
- **Fragile:** dynamic imports by string are convenient but can silently fail when wrappers are missing.

### Data pipeline credibility and trust/provenance
- Manual raw CSV -> processed CSV path is implemented through `scripts/process_housing_raw.py` and `app/utils/ingestion.py`.
- Ingestion validates against a YAML data contract and writes provenance columns.
- Loader adds freshness status from `processed_at` and supports sample fallback.
- Weekly data-health workflow runs contract/freshness checks and uploads report artifacts.

Assessment:
- **Working:** local-first ingestion with schema checks is real.
- **Partial:** provenance is mostly row-level metadata; no committed manifest artifacts are present in the repo.
- **Fragile:** freshness checks depend on a single timestamp field and local discipline for updates.

### Testing depth and CI/CD maturity
- Tests cover metrics logic, config validation, ingestion validation, and dynamic renderer resolution.
- CI runs install, compileall, ruff, mypy, and pytest.
- Data-health has a scheduled workflow.

Assessment:
- **Working:** meaningful baseline test coverage across core logic.
- **Partial:** no explicit coverage threshold gate.
- **Fragile:** only two workflows; no deployment validation pipeline for Streamlit runtime.

### Documentation, demo readiness, recruiter appeal
- README is unusually honest about limits and architecture.
- `docs/demo_playbook.md` provides a recruiter-facing narrative.
- `docs/architecture.md` contains claim-to-implementation mapping.

Assessment:
- **Working:** truth-first tone is a real differentiator.
- **Partial:** legacy/non-core artifacts (`visualization.py`, static `map.html`) can dilute credibility if not explained.
- **Fragile:** screenshots are still called out as manual follow-up, reducing polished demo readiness.

### Scalability path
- Config-driven city profiles exist.
- Core analysis supports multi-city comparisons.

Assessment:
- **Working:** enough structure for 3-10 city growth with discipline.
- **Partial:** onboarding new cities still requires new wrapper modules to satisfy dynamic import conventions.
- **Fragile:** manual ingestion and static CSV artifacts do not scale to frequent updates.

## 3. Top strengths
1. **Truth-first documentation posture** (README + architecture + demo playbook) is stronger than typical portfolio dashboards.
2. **Real national + city product flow** is implemented and coherent.
3. **Schema-aware ingestion + fallback loading** is in place and test-backed.
4. **Shared analytics module** keeps business logic largely out of page wrappers.
5. **CI + scheduled data-health checks** exist (not just claimed).

## 4. Top weaknesses
1. **Manual data operations remain the core bottleneck** (no automated ingestion from external sources).
2. **Trust signaling is present but still thin** (metadata-based, not deeply auditable UX).
3. **City expansion ergonomics are only semi-config-driven** because wrappers are still required.
4. **Demo polish is mixed** due to disconnected legacy map artifacts and missing visual proof assets.
5. **No hard coverage gate** weakens quality narrative for recruiter scrutiny.

## 5. Prioritized improvement plan

### P0 = must-fix credibility/product issues

1) **Align city subtitles with actual data mode semantics**
- Why: prevents sample-only messaging when source-backed data is loaded.
- Impact: immediate trust clarity in demos.
- Difficulty: low.
- Risk: low.
- Value: truthfulness + recruiter value.

2) **Add explicit stale-data UX state in overview pages (not only banner)**
- Why: users can miss top-level captions; stale context should be unavoidable.
- Impact: stronger decision safety and trust.
- Difficulty: low-medium.
- Risk: low.
- Value: product value + truthfulness.

3) **Ship committed example lineage manifests + docs on interpretation**
- Why: code writes manifests, but repo currently provides no concrete examples.
- Impact: auditable data credibility signal.
- Difficulty: low.
- Risk: low.
- Value: recruiter value + data trust.

4) **Define and enforce a minimum test coverage threshold in CI**
- Why: baseline tests exist, but no explicit coverage floor weakens guardrails.
- Impact: stronger engineering credibility.
- Difficulty: low-medium.
- Risk: low-medium (can fail initially).
- Value: recruiter value + code quality.

### P1 = high-leverage upgrades

5) **Refactor city page registration to be fully config-driven**
- Why: reduce manual wrapper expansion cost and drift.
- Impact: cleaner scalability path.
- Difficulty: medium.
- Risk: medium.
- Value: technical credibility + product scalability.

6) **Introduce source manifest (`config/sources.yml`) and cadence checks in data-health**
- Why: makes source expectations explicit and machine-checkable.
- Impact: stronger freshness/provenance governance.
- Difficulty: medium.
- Risk: medium.
- Value: truthfulness + data trust.

7) **Add uncertainty framing to neighborhood momentum outputs**
- Why: current robust/directional labels are useful but still heuristic.
- Impact: more defensible analytics storytelling.
- Difficulty: medium.
- Risk: medium.
- Value: product value + technical credibility.

8) **Integrate or retire `visualization.py`/`map.html` path**
- Why: orphan artifacts can look like unfinished experimentation.
- Impact: tighter portfolio narrative.
- Difficulty: low-medium.
- Risk: low.
- Value: recruiter appeal.

### P2 = nice-to-have expansions

9) **Add one additional implemented city (e.g., Calgary) after routing refactor**
- Why: shows scalability and broader relevance.
- Impact: better market coverage for demos.
- Difficulty: medium.
- Risk: medium.
- Value: recruiter/product value.

10) **Improve visual storytelling (annotated charts + guided insights)**
- Why: current charts are clear but mostly generic Streamlit defaults.
- Impact: higher demo memorability.
- Difficulty: medium.
- Risk: low.
- Value: recruiter appeal.

11) **Publish a one-command demo launcher and scripted walkthrough checks**
- Why: lowers friction for reviewers.
- Impact: better demo reliability and handoff.
- Difficulty: low-medium.
- Risk: low.
- Value: recruiter value.

## 6. Best next implementation phase

### Recommended first phase: "Trust Surface Hardening"

#### Exact scope
1. Update city subtitle language in config to be mode-agnostic and truth-safe.
2. Promote freshness status to high-visibility status components on Canada and city pages.
3. Commit at least one real processing manifest example under `data/processed/manifests/` and document fields.
4. Add CI coverage gate with a realistic initial threshold.

#### Files likely affected
- `config/cities.yml`
- `app/main.py`
- `app/pages/canada_overview.py`
- `app/pages/city_overview.py`
- `.github/workflows/ci.yml`
- `README.md`
- `docs/architecture.md`
- `data/processed/manifests/*.json` (new)

#### Acceptance criteria
- City subtitles never misstate sample/source-backed context.
- Freshness status (fresh/stale/unknown) is visible on each major page above analytical conclusions.
- Repo includes at least one valid lineage manifest artifact matching current schema.
- CI fails if coverage drops below threshold.

#### How success should be verified
- Run `pytest -q` with coverage output and verify threshold enforcement.
- Run Streamlit app in both source-backed and fallback modes and confirm visible freshness states.
- Validate lineage example file against documented required keys.
- Smoke-check recruiter walkthrough from `docs/demo_playbook.md`.

## 7. Truth map

### What can honestly be claimed today
- It is a Streamlit-based local-first analytics app with a Canada overview plus Montreal/Toronto/Vancouver drill-downs.
- It supports source-backed processed data with fallback to local sample data.
- It has manual raw CSV ingestion with contract validation and provenance columns.
- It has passing unit tests and CI checks for compile/lint/type/test, plus scheduled data-health checks.

### What should NOT be claimed yet
- Fully automated production data pipeline.
- Benchmark-grade or causal housing intelligence.
- Enterprise-grade provenance/lineage governance.
- Cloud-native scalable backend architecture.

### What must be built to support stronger claims
- Automated source ingestion with declared cadence expectations.
- Deeper provenance artifacts + visible trust UX linked to those artifacts.
- Coverage-thresholded CI and broader test depth (integration/UI smoke).
- Scalable city extension path without manual wrapper coupling.

## 8. Final recommendation
Execute **Trust Surface Hardening** first. It has the best ratio of effort to credibility gain: it tightens truthfulness in the UI, materially strengthens recruiter confidence, and lays the foundation for more ambitious product upgrades without pretending the pipeline is production-grade.
