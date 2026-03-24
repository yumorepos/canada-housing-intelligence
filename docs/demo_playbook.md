# Demo Playbook: Canada Housing Intelligence

## Purpose
Provide a repeatable, truth-first demo flow for recruiters and reviewers that highlights:
- what is implemented,
- what confidence limits exist,
- and how provenance/freshness should be interpreted.

## Preconditions
1. Install dependencies and run tests:
   - `pip install -r requirements.txt`
   - `pytest -q`
2. Ensure at least one processed dataset exists at `data/processed/housing_source_processed.csv`.
3. Start app:
   - `streamlit run app/main.py`

## Scenario 1: Canada-level tradeoff scan (2 minutes)
1. Open **Canada Overview**.
2. Read the data-mode banner and freshness line first.
3. In **Decision Snapshot**, compare:
   - lower-rent city,
   - lower-price city,
   - higher-pressure city,
   - strongest coverage city.
4. Use **City Comparison Table** to validate directional differences.
5. End with analyst notes, explicitly calling out provenance and confidence caveats.

**Truth callout:** city-level comparisons are directional intelligence, not official benchmark-grade rankings.

## Scenario 2: City momentum + reliability (3 minutes)
1. Select a live city page (Montreal/Toronto/Vancouver).
2. Review **Executive Snapshot** and coverage info.
3. In **Neighborhood Momentum & Stability**, compare rent/price leaders.
4. Highlight **support score** and **reliability labels** before discussing any neighborhood momentum conclusion.
5. Use analyst notes to mention support score and recency timestamp.

**Truth callout:** robust/directional plus support score should be treated as confidence context, not causal proof.

## Scenario 3: Trust posture under stale or sample data (2 minutes)
1. Run app with only fallback sample data (temporarily move source-backed processed CSV).
2. Confirm banner switches to sample mode and freshness behavior is visible.
3. Explain what still works (local analytics flow) and what remains limited (freshness automation, external lineage).

**Truth callout:** fallback mode protects usability, not external data authority.

## Demo do/don't script
### Do
- Open with provenance and freshness.
- Use directional language ("signal", "indication", "support level").
- Mention limitations before claiming conclusions.

### Don't
- Claim official benchmark quality.
- Claim automated pipelines or freshness monitoring not implemented.
- Present neighborhood momentum as causal.
