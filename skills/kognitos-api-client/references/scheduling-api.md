# Scheduling API

Use this reference when you need to create, inspect, or manage automation schedules.

## Overview

Each automation can have at most one schedule (a singleton sub-resource). Schedules define when and how often an automation runs automatically. You can enable or disable a schedule without deleting it.

## Endpoints

### Get schedule

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}/schedule"
```

Returns the schedule's `config` (start, repeat interval, patterns, end, active window), `enabled`, a readable `summary`, the upcoming `next_run_times` and, for a schedule that ends after N runs, `remaining_occurrences`. An automation without a schedule returns `404`.

### Create schedule

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "start": {
        "start_date": {"year": 2026, "month": 4, "day": 14},
        "time": {"hours": 9, "minutes": 0},
        "time_zone": "America/New_York"
      },
      "repeat_interval": {
        "unit": "FREQUENCY_UNIT_DAY",
        "interval": 1
      }
    }
  }' \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}/schedule"
```

A scheduled run gets no inputs, so every input of the automation needs a default value or an optional type; otherwise creating the schedule fails with `FAILED_PRECONDITION`.

### Update schedule

```bash
curl -sS -X PATCH \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "start": {
        "start_date": {"year": 2026, "month": 4, "day": 14},
        "time": {"hours": 14, "minutes": 30},
        "time_zone": "America/New_York"
      },
      "repeat_interval": {
        "unit": "FREQUENCY_UNIT_WEEK",
        "interval": 1
      },
      "weekly_pattern": {
        "days": ["DAY_OF_WEEK_MONDAY", "DAY_OF_WEEK_WEDNESDAY", "DAY_OF_WEEK_FRIDAY"]
      }
    }
  }' \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}/schedule"
```

### Delete schedule

```bash
curl -sS -X DELETE \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}/schedule"
```

### Enable schedule

Resume triggering runs without recreating the schedule.

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{}' \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}:enableAutomationSchedule"
```

### Disable schedule

Pause scheduled runs without deleting the schedule.

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{}' \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}:disableAutomationSchedule"
```

## Schedule Configuration

### Repeat intervals

| Unit | Value |
|------|-------|
| Minute | `FREQUENCY_UNIT_MINUTE` |
| Hour | `FREQUENCY_UNIT_HOUR` |
| Day | `FREQUENCY_UNIT_DAY` |
| Week | `FREQUENCY_UNIT_WEEK` |
| Month | `FREQUENCY_UNIT_MONTH` |
| Year | `FREQUENCY_UNIT_YEAR` |

Set `interval` to N for "every N units" (e.g. `interval: 2` with `FREQUENCY_UNIT_WEEK` = every 2 weeks).

### Weekly pattern

Specify which days of the week to run:

```json
{
  "weekly_pattern": {
    "days": ["DAY_OF_WEEK_MONDAY", "DAY_OF_WEEK_FRIDAY"]
  }
}
```

### Monthly pattern

Fixed day of month:

```json
{"monthly_pattern": {"day_number": 15}}
```

Ordinal day (e.g. "second Tuesday"):

```json
{"monthly_pattern": {"ordinal_day": {"ordinal": "ORDINAL_SECOND", "day": "DAY_OF_WEEK_TUESDAY"}}}
```

### Yearly pattern

```json
{
  "yearly_pattern": {
    "month": "MONTH_JANUARY",
    "day_pattern": {"day_number": 1}
  }
}
```

### End conditions

| Type | Description |
|------|-------------|
| `SCHEDULE_END_TYPE_NEVER` | Run indefinitely |
| `SCHEDULE_END_TYPE_ON_DATE` | Stop on a specific date (requires `end_date`) |
| `SCHEDULE_END_TYPE_AFTER_OCCURRENCES` | Stop after N runs (requires `max_occurrences`) |

```json
{"end": {"end_type": "SCHEDULE_END_TYPE_AFTER_OCCURRENCES", "max_occurrences": 10}}
```

```json
{"end": {"end_type": "SCHEDULE_END_TYPE_ON_DATE", "end_date": {"year": 2026, "month": 12, "day": 31}}}
```

### Active window

Restrict execution to a daily time window:

```json
{
  "active_window": {
    "window_start": {"hours": 9, "minutes": 0},
    "window_end": {"hours": 17, "minutes": 0},
    "time_zone": "America/New_York"
  }
}
```
