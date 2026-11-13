# Analytics API

Use this reference when you need platform health metrics, run statistics, or exception resolution insights.

## Overview

Analytics endpoints provide aggregate views over runs and exceptions. Use them for dashboards, trend analysis, and operational health monitoring.

## Endpoints

### Run statistics (per-automation)

Total and completed run counts per automation in a workspace:

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}:automationRunAggregates"
```

Returns `automation_run_aggregates`, one entry per automation with `total_runs` and `completed_runs`.

### Run statistics (daily time series)

Daily run counts over an inclusive date range. Dates are passed as `google.type.Date` parts and `time_zone` (IANA) is required:

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}:dailyRunAggregates?start_date.year=2026&start_date.month=4&start_date.day=1&end_date.year=2026&end_date.month=4&end_date.day=11&time_zone=America/New_York"
```

Returns `daily_run_aggregates`, one entry per day: `{"date": "2026-04-01", "stats": {"total_runs": 12}}`.

To scope to automations, add `filter` on `automation_id` (`=`, combined with `OR`), URL-encoded:

```bash
...&filter=automation_id%20%3D%20%22${AUTO_ID}%22
```

### Organization insights

High-level metrics: cost/time savings, run counts, completion rates (auto-completed vs manually resolved), and runs awaiting guidance, per automation and per period.

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/dashboards:queryInsights?filter.time_window.start_time=2026-04-01T00:00:00Z&filter.time_window.end_time=2026-04-11T23:59:59Z&filter.time_window.time_zone=UTC"
```

Optional filters take bare ids and may repeat: `&filter.workspace_ids=${WS}` and `&filter.automation_ids=${AUTO_ID}`. Omit `filter.time_window` for all time.

The response has `value_insight` (`total_money_saved_usd`, `total_time_saved_secs`), `run_insight` (`total_runs_count`, `trend`), `completion_insight` (`total_percent_completions`, `completions_per_period` with `auto_completed_count` and `manually_resolved_count`) and `awaiting_guidance_insight` (`total_runs_awaiting_guidance`, `runs_per_period`). Each breaks down `insights_per_automation_per_workspace` or per period, keyed by workspace id. 64-bit counts are JSON strings.

### Exception insights

Mean time to resolution (MTTR) over a time window, for one workspace:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"time_window": {"start_time": "2026-04-01T00:00:00Z", "end_time": "2026-04-11T23:59:59Z", "time_zone": "UTC"}}' \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/exceptions:queryInsights"
```

Returns `{"mttr_seconds": 5400}`; `0` when no exception was resolved in the window.

## Use Cases

- **Operational dashboards**: combine daily run aggregates with exception insights for a health overview.
- **Automation ROI**: use organization insights to see cost/time savings and completion rates.
- **Triage prioritization**: pair MTTR with exception counts (from the [Exceptions API](exceptions-api.md)) to find automations that need attention.
