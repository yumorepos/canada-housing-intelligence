# Truth-First Repository Audit and Improvement Plan

_Date assessed: 2026-03-24 (UTC)_

## Method and evidence

This audit is based on direct inspection of the repository's code, configuration, docs, test suite, sample/processed datasets, and CI workflow. Findings below separate **verified facts** from **inference** where applicable.

---

## Executive verdict

**Verdict:** This is a credible **local prototype** with a clean analytical core and honest documentation, but it is **not yet a defensible intelligence product** in terms of data contracts, freshness, trust signaling depth, and production-grade engineering hygiene.

- **What it is now (verified):** a Streamlit app with Canada overview + three city drill-downs, reusable metric functions, manual ingestion CLI, fallback sample mode, and light tests. 
- **What it is not yet (verified):** a monitored data product with explicit schema contracts, strong CI gates, freshness SLAs, or statistically defensible confidence modeling.

---

## What is actually good already

1. **Architecture separation is cleaner than typical portfolio dashboards.**
   - Shared analytics are in `analysis/city_metrics.py`, while UI pages mostly compose those helpers. 
2. **Canada overview and city pages are genuinely implemented (not stub-only).**
   - Navigation and renderers are wired and include implemented-city/upcoming-city logic. 
3. **Provenance fields exist in transformed outputs and are surfaced in UI.**
   - Ingestion writes source metadata and `data_mode`; UI displays compact source/mode/period labels.
4. **Fallback behavior is implemented at loader layer, not ad hoc in UI.**
   - Missing source-backed file cleanly falls back to sample file.
5. **Tests exist for config, ingestion, and analytics logic; suite currently passes.**

---

## What is fragile, incomplete, misleading, or underpowered

1. **CI is effectively non-blocking and can pass with broken code/tests.**
   - Workflow uses `|| true` for install/compile/pytest; failures do not fail pipeline.
2. **Data contract is implicit in code constants, not explicit versioned contract files.**
   - Required columns are hard-coded in Python; no external schema registry/manifest exists.
3. **Freshness is not machine-checked despite provenance timestamps existing.**
   - `processed_at` is stored but no checks in app/tests/CI to enforce recency.
4. **Trust communication is compact but shallow.**
   - UI shows source/mode/period text, but does not expose coverage/confidence notes from provenance payload.
5. **“Source-backed” can still be single local generated artifact without integrity checks.**
   - No checksum/signature/source file lineage or run log for reproducibility.
6. **Robustness guardrails are static thresholds, not calibrated confidence methods.**
   - “Robust vs directional” is heuristic and unvalidated statistically.
7. **Potential mismatch between config subtitles and actual mode.**
   - City subtitles in config say insights are from local sample dataset even when source-backed file is loaded.
8. **App routing for city pages is manually mapped.**
   - Adding new cities needs both config and hard-coded renderer dict updates.
9. **Repo has peripheral artifacts with weak product value alignment.**
   - Standalone folium map script and generated HTML are not integrated into Streamlit flow.
10. **Dependency and tooling footprint is minimal to a fault.**
    - No linting/type checking/formatting/package lock; reproducibility and maintainability lag.

---

## Product risks

1. **Positioning risk:** Feels like “smart dashboard” more than “intelligence product” due to limited decision workflows and defensibility cues.
2. **Claim risk:** README honesty is good, but public viewers may still infer stronger data authority than warranted.
3. **Expansion risk:** Current architecture supports 3 cities well, but scaling to many cities is manual in routing/content strategy.

## Data risks

1. **Schema drift risk:** Raw CSV contract enforced only at runtime by ingestion function.
2. **Staleness risk:** No freshness monitor, no update cadence assertions, no stale-data UI warning threshold.
3. **Lineage risk:** No structured run manifest linking raw input hash -> transform params -> processed output hash.
4. **Statistical trust risk:** Neighborhood momentum outputs rely on simple first/last growth and std-dev volatility without uncertainty intervals.

## Engineering risks

1. **False-green CI risk:** `|| true` masks defects.
2. **Low quality gates:** No lint/type/doc/test coverage metrics.
3. **Hard-coded page renderer mapping:** Encourages drift between config and app behavior.
4. **No pinned lockfile:** Environment drift can break reproducibility over time.

## UX risks

1. **Provenance is visible but not inspectable:** users cannot drill into confidence/coverage rationale.
2. **No explicit “data recency” status badge with stale thresholds.**
3. **Static analysis narratives:** analyst notes are template-style and may feel generic.

## Portfolio/recruiter-presentation risks

1. **CI quality signal currently weak (easy to spot).**
2. **Manual ingestion + no schema contract can read as “toy workflow.”**
3. **No polished evidence of data trust discipline (lineage/freshness/contracts) in docs/screens.
4. **No explicit demo script with scenario-based storytelling for evaluators.**

---

## Truth gaps: claims vs implementation

### Verified aligned claims
- Local-first workflow and manual drop are accurately stated.
- Fallback mode behavior exists as documented.
- Limitations around automation/schema/freshness are explicitly acknowledged.

### Verified gaps or tensions
- CI badge suggests reliability, but workflow does not enforce failing checks.
- Provenance is said to include compact context in UI; true, but confidence/coverage notes are not surfaced in key views.
- Product language implies intelligence depth, but current statistical support is mostly heuristic guardrails.

---

## Dimension scoring (truth-first)

Scoring: 1 (weak) to 10 (strong), based on current codebase.

| Dimension | Score | Why |
|---|---:|---|
| Product clarity | 7 | Clear Canada→city flow and honest README, but weak actionability loop |
| Data credibility | 5 | Provenance fields + guardrails present, but no contracts/freshness checks/lineage integrity |
| Reproducibility | 4 | Manual steps + no lockfile + no run manifests |
| Maintainability | 6 | Good modularization; still lacks tooling gates and dynamic page registration |
| Test coverage quality | 6 | Useful unit tests, but CI non-blocking and no coverage threshold |
| Scalability | 4 | Manual city onboarding and local CSV workflow constrain growth |
| Trust/provenance | 5 | Metadata exists but trust UI and lineage are shallow |
| Visual polish | 6 | Functional Streamlit layout; not yet product-grade narrative polish |
| Recruiter/portfolio strength | 6 | Honest and coherent prototype; reliability/trust signals underdeveloped |
| Public demo readiness | 5 | Works locally; lacks freshness/status/defensibility cues needed for strong demo claims |

---

## Top 10 repository weaknesses (ranked)

1. **Non-failing CI pipeline (`|| true`)**
2. **No explicit schema contract/registry artifact**
3. **No freshness monitor or stale-data UX indicator**
4. **No reproducible lineage manifest (hashes/run metadata)**
5. **Heuristic robustness labels without uncertainty estimation**
6. **Config-app mismatch risk via hard-coded city renderer map**
7. **No quality-toolchain gates (lint/type/format/coverage)**
8. **No lockfile/environment pinning for deterministic setup**
9. **Provenance not fully surfaced (coverage/confidence notes hidden)**
10. **Loose portfolio packaging (map artifacts/demo narrative not integrated)**

---

## Highest-leverage improvements (priority order)

### Quick wins (high impact, low-medium effort)

1. **Make CI fail on real failures**
   - Why: Restores trust in badge and prevents silent regressions.
   - Files: `.github/workflows/ci.yml`.
   - User/product impact: Higher reliability.
   - Portfolio impact: Immediate credibility boost.
   - Difficulty: Low.
   - Dependency/risk: Low.

2. **Add explicit data contract file and ingestion validation against it**
   - Why: Converts implicit schema assumptions into auditable contract.
   - Files: `config/data_contract.yml` (new), `app/utils/ingestion.py`, `scripts/process_housing_raw.py`, tests.
   - User/product impact: Fewer bad-file failures; clearer contributor workflow.
   - Portfolio impact: Strong data-platform signal.
   - Difficulty: Low-Medium.
   - Dependency/risk: Low.

3. **Add freshness status check + stale warning in UI**
   - Why: Makes recency explicit and honest in demos.
   - Files: `app/utils/data_loader.py`, `app/main.py`, possibly `config/cities.yml` for freshness threshold.
   - User/product impact: Better trust and decision context.
   - Portfolio impact: Moves from dashboard to intelligence posture.
   - Difficulty: Low-Medium.
   - Dependency/risk: Low.

4. **Surface provenance confidence/coverage notes in UI**
   - Why: Existing metadata is wasted unless visible.
   - Files: `app/main.py`, `app/pages/canada_overview.py`, `app/pages/city_overview.py`.
   - User/product impact: Better interpretation guardrails.
   - Portfolio impact: Better responsible-analytics signaling.
   - Difficulty: Low.
   - Dependency/risk: Low.

5. **Create deterministic dev setup (lockfile + make/just commands)**
   - Why: Reduce setup drift and evaluation friction.
   - Files: `requirements.txt` (pin or constraints), new `Makefile`/`justfile`, README updates.
   - User/product impact: Easier onboarding.
   - Portfolio impact: Professional engineering hygiene.
   - Difficulty: Low.
   - Dependency/risk: Low.

### Medium-effort improvements

6. **Dynamic city page registration from config**
   - Why: Avoid dual-maintenance and scaling friction.
   - Files: `app/main.py`, `app/pages/*` wrappers or renderer registry.
   - Product impact: Faster city expansion.
   - Portfolio impact: Better architecture signal.
   - Difficulty: Medium.
   - Risk: Medium (page routing refactor).

7. **Lineage manifest per processing run**
   - Why: Strong reproducibility and trust (input hash/output hash/params/timestamp).
   - Files: `app/utils/ingestion.py`, `scripts/process_housing_raw.py`, `data/processed/manifests/*.json`.
   - Product impact: Auditability.
   - Portfolio impact: Data-engineering maturity.
   - Difficulty: Medium.
   - Risk: Medium.

8. **Add statistical uncertainty signals for growth rankings**
   - Why: Makes “momentum” claims more defensible.
   - Files: `analysis/city_metrics.py`, `app/pages/city_overview.py`, tests.
   - Product impact: Better confidence communication.
   - Portfolio impact: Strong analytical rigor signal.
   - Difficulty: Medium.
   - Risk: Medium (method decisions).

### Bigger structural improvements

9. **Introduce lightweight scheduled ingestion/check pipeline (local+CI)**
   - Why: Reduce manual drift and expose freshness automatically.
   - Files: new workflow/scripts/docs; ingestion + validation jobs.
   - Product impact: More trustworthy updates.
   - Portfolio impact: “real product operations” signal.
   - Difficulty: Medium-High.
   - Risk: Medium.

10. **Formalize source manifest and city coverage metadata model**
    - Why: Enables transparent per-city/per-metric confidence and update cadence.
    - Files: `config/sources.yml` (new), loaders/UI/docs/tests.
    - Product impact: Better informed decisions.
    - Portfolio impact: Significant trust uplift.
    - Difficulty: High.
    - Risk: Medium-High.

### Must-fix before claiming X

- **Before claiming “robust CI / production quality”**: fix non-blocking CI + add lint/type/test gates.
- **Before claiming “data trustworthiness”**: add explicit schema contract + freshness checks + visible confidence notes.
- **Before claiming “intelligence product”**: add uncertainty-aware ranking interpretation and clearer action-oriented outputs.

### Nice-to-have but low leverage

- Replace static folium artifact with integrated map experience (unless central to narrative).
- Add more styling polish before trust/freshness/CI issues are resolved.
- Add extra cities before scaling architecture + data governance basics are fixed.

---

## Explicit answers requested

### Top 5 fastest upgrades for substantial improvement

1. Fix CI to fail on test/compile errors.
2. Add `config/data_contract.yml` + enforce contract in ingestion.
3. Add stale-data detection and display recency badge in app header.
4. Display provenance confidence/coverage notes in Canada and city pages.
5. Add reproducible dev commands + pinned dependency strategy.

### Top 3 changes to improve recruiter impact

1. **CI credibility restoration** (real pass/fail, visible quality gates).
2. **Data contract + lineage manifest** (shows platform discipline).
3. **Trust-centric UX layer** (freshness + confidence surfaced clearly).

### Top 3 changes to improve data trustworthiness

1. Explicit schema contract with validation and clear error messages.
2. Freshness monitoring + stale warnings tied to declared cadence.
3. Run-level lineage artifacts (input/output hashes, parameters, timestamp).

### Phase 1/2/3 shipping guidance (summary)

- **Phase 1:** CI truth + schema contract + freshness and provenance surfacing.
- **Phase 2:** Confidence modeling, UX trust improvements, and demo/docs hardening.
- **Phase 3:** Structural durability (dynamic extensibility + scheduled checks + stronger reproducibility).

---

## Final implementation roadmap

### Phase 0: truth cleanup

- **Objective:** Align public claims with actual guarantees; remove misleading reliability signals.
- **Exact tasks:**
  1. Remove `|| true` in CI and fail fast.
  2. Update README/docs with explicit “current guarantees” and “non-guarantees”.
  3. Add architecture note section mapping each product claim to implementation evidence.
- **Files likely touched:** `.github/workflows/ci.yml`, `README.md`, `docs/architecture.md`.
- **Acceptance criteria:** CI fails when tests fail; docs reflect true reliability scope.
- **New honest claims unlocked:** “CI enforces tests”; “documented claims map to implemented checks.”

### Phase 1: high-leverage product/data fixes

- **Objective:** Make data trust and operational honesty visible in-product.
- **Exact tasks:**
  1. Add `config/data_contract.yml` and validate raw inputs against it.
  2. Add freshness threshold config and stale warning in app banner.
  3. Surface provenance confidence and coverage notes in Canada + city pages.
  4. Add tests for contract validation + stale-mode logic.
- **Files likely touched:** `config/data_contract.yml` (new), `app/utils/ingestion.py`, `app/utils/data_loader.py`, `app/main.py`, `app/pages/canada_overview.py`, `app/pages/city_overview.py`, tests.
- **Acceptance criteria:** Ingestion rejects contract-violating files; app shows recency status; confidence/coverage notes visible.
- **New honest claims unlocked:** “Schema-validated ingestion”; “freshness is monitored and surfaced”; “confidence caveats visible in UI.”

### Phase 2: trust + UX + documentation upgrades

- **Objective:** Increase defensibility and demo readiness.
- **Exact tasks:**
  1. Add uncertainty-aware neighborhood momentum statistics (e.g., dispersion/confidence bands or reliability labels beyond binary robust/directional).
  2. Improve analyst note generation to reference actual support metrics and recency.
  3. Add demo playbook with 3 decision scenarios and expected app walkthrough.
  4. Add screenshots/GIF in README tied to trust-aware UI states.
- **Files likely touched:** `analysis/city_metrics.py`, `app/pages/city_overview.py`, `README.md`, `docs/` demo guide, tests.
- **Acceptance criteria:** Momentum outputs include uncertainty context; demo docs reproducible.
- **New honest claims unlocked:** “Statistically better-supported momentum interpretation”; “structured demo narrative with trust states.”

#### Phase 2 execution note (2026-03-24)
- Screenshot/GIF capture is **blocked in this execution environment** because no browser screenshot tool is available in-session.
- Adjustment: keep this item open as a manual follow-up task; include explicit capture instructions in docs/README rather than fabricating images.

### Phase 3: structural improvements for durability

- **Objective:** Reduce manual fragility and improve scale/readiness.
- **Exact tasks:**
  1. Implement run manifest generation with hashes and parameters.
  2. Refactor city routing to config-driven renderer registration pattern.
  3. Add scheduled validation/freshness CI job and artifact publication.
  4. Add lint/type/coverage thresholds and deterministic dependency locking.
- **Files likely touched:** `app/main.py`, `app/utils/ingestion.py`, `scripts/process_housing_raw.py`, `.github/workflows/*.yml`, tooling config files, tests, docs.
- **Acceptance criteria:** Reproducible run artifacts produced; city addition path documented and mostly config-driven; CI enforces multiple quality gates.
- **New honest claims unlocked:** “Auditable lineage”; “scalable city onboarding path”; “durable engineering quality gates.”

#### Phase 3 execution note (2026-03-24)
- Coverage-threshold CI gating remains partially blocked in this execution environment because coverage tooling could not be installed from the restricted package index.
- Adjustment: implemented compile + lint + type + test CI gates now; left explicit coverage fail-under gating as an open follow-up item.

---

## Ranked improvement backlog

1. Fix CI to enforce failures.
2. Add explicit schema contract + ingestion enforcement.
3. Add freshness monitor logic + stale UX warnings.
4. Surface full provenance confidence/coverage notes in UI.
5. Add run lineage manifest (input/output hashes + params).
6. Add lint/type/coverage gates and dependency locking.
7. Refactor city routing to config-driven registration.
8. Upgrade momentum analytics with uncertainty-aware outputs.
9. Publish scenario-based demo guide and screenshots.
10. Integrate/deprecate orphan map artifacts based on product strategy.

## Single best first implementation step

**Fix CI to fail when tests/compile fail** (remove `|| true` and add minimal deterministic install + pytest gate).

## Exact files to inspect/edit first

1. `.github/workflows/ci.yml`
2. `README.md` (quality guarantees section)
3. `docs/architecture.md` (truth mapping)

## Suggested next Codex execution prompt (to begin Phase 0)

"Implement Phase 0 truth cleanup: (1) make CI fail on real failures in `.github/workflows/ci.yml`; (2) update README and `docs/architecture.md` with an explicit claims-vs-guarantees section; (3) add/adjust tests or checks as needed so CI is trustworthy; then summarize changes with citations."
