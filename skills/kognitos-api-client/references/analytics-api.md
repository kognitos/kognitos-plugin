# Analytics API

Use this reference when you need platform health metrics, run statistics, or exception resolution insights.

## Overview

Analytics endpoints provide aggregate views over runs and exceptions. Use them for dashboards, trend analysis, and operational health monitoring.

## Endpoints

### Run statistics (per-automation)

Aggregate run counts per automation in a workspace:

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/analytics/run_stats"
```

### Run statistics (daily time series)

Daily run counts over a date range. Optionally filter to a single automation:

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/analytics/run_stats?daily=true&start_date=2026-04-01T00:00:00Z&end_date=2026-04-11T23:59:59Z&time_zone=America/New_York"
```

Add `&automation_id=${AUTO_ID}` to scope to a single automation.

### Organization insights

High-level metrics: cost/time savings, completion rates, run trends, and straight-through processing rate.

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/analytics/insights?start_date=2026-04-01T00:00:00Z&end_date=2026-04-11T23:59:59Z"
```

Add `&workspace_id=${WS}` to filter by workspace.

### Exception insights

Exception resolution metrics including mean time to resolution (MTTR) over a time window.

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/analytics/exception_insights?start_date=2026-04-01T00:00:00Z&end_date=2026-04-11T23:59:59Z&time_zone=UTC"
```

## Use Cases

- **Operational dashboards**: combine `run_stats` (daily) with `exception_insights` for a health overview.
- **Automation ROI**: use `insights` to see cost/time savings and straight-through processing rates.
- **Triage prioritization**: pair `exception_insights` MTTR with exception counts (from the [Exceptions API](exceptions-api.md)) to find automations that need attention.
