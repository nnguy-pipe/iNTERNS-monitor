# AHMS Report API Contract

This document defines the backend hook surface for report generation and retrieval.

## Base Path

- API prefix: /api
- Content-Type: application/json

## Endpoint: Generate Health Report

- Method: POST
- Path: /api/reports/generate

### Request Body

```json
{
  "system_name": "service-name",
  "environment": "ci",
  "lookback_minutes": 60
}
```

### Response (200)

```json
{
  "id": "uuid",
  "system_name": "service-name",
  "environment": "ci",
  "status": "healthy",
  "health_score": 0.92,
  "primary_issue": "No primary issue",
  "reasoning": {
    "reasoning_chain": ["Analyzed 10 events"],
    "evidence_count": 10,
    "recommendation": "Monitor closely if score < 0.5"
  },
  "confidence": 0.84,
  "suggestions": [
    {
      "action": "Monitor system more closely for trends",
      "severity": "medium",
      "confidence": 0.75
    }
  ],
  "cascading_failures": [],
  "event_clusters": 2,
  "anomalies": [],
  "created_at": "2026-06-12T10:20:30.123456"
}
```

## Endpoint: Latest Health Report

- Method: GET
- Path: /api/reports/latest
- Query:
  - system_name (required)
  - environment (required)

### Response (200)

```json
{
  "id": "uuid",
  "system_name": "service-name",
  "environment": "ci",
  "status": "warning",
  "health_score": 0.61,
  "primary_issue": "Error detected: timeout",
  "suggestions": ["Investigate recent issues and review logs"],
  "created_at": "2026-06-12T10:20:30.123456"
}
```

## Endpoint: User Report Rendering Hook

- Method: GET
- Path: /api/reports/user
- Query:
  - system_name (required)
  - environment (required)
  - format (optional, default: json)
    - json
    - markdown

### Response (200, format=json)

```json
{
  "id": "uuid",
  "system_name": "service-name",
  "environment": "ci",
  "status": "warning",
  "health_score": 0.61,
  "confidence": 0.78,
  "primary_issue": "Error detected: timeout",
  "suggestions": ["Investigate recent issues and review logs"],
  "reasoning": {
    "reasoning_chain": ["Found 2 error logs"],
    "evidence_count": 8,
    "recommendation": "Monitor closely if score < 0.5"
  },
  "anomalies": [],
  "correlated_events": ["event-1", "event-2"],
  "created_at": "2026-06-12T10:20:30.123456"
}
```

### Response (200, format=markdown)

```json
{
  "id": "uuid",
  "system_name": "service-name",
  "environment": "ci",
  "status": "warning",
  "health_score": 0.61,
  "confidence": 0.78,
  "primary_issue": "Error detected: timeout",
  "suggestions": ["Investigate recent issues and review logs"],
  "reasoning": {
    "reasoning_chain": ["Found 2 error logs"],
    "evidence_count": 8,
    "recommendation": "Monitor closely if score < 0.5"
  },
  "anomalies": [],
  "correlated_events": ["event-1", "event-2"],
  "created_at": "2026-06-12T10:20:30.123456",
  "format": "markdown",
  "report_markdown": "# AHMS Health Report: service-name\n..."
}
```

## Endpoint: One-Shot User Report Generation

- Method: POST
- Path: /api/reports/user/generate

### Request Body

```json
{
  "system_name": "service-name",
  "environment": "ci",
  "lookback_minutes": 60,
  "format": "markdown"
}
```

### Response (200)

Returns the same generated payload as /api/reports/generate plus:

- format: markdown
- report_markdown: readable report body

## Endpoint: CI Verdict

- Method: POST
- Path: /api/ci/evaluate

### Request Body

```json
{
  "system_name": "service-name",
  "environment": "ci",
  "deployment_context": {
    "sha": "abc123"
  }
}
```

### Response (200)

```json
{
  "system_name": "service-name",
  "environment": "ci",
  "verdict": "pass",
  "rationale": {
    "summary": "Health assessment complete",
    "reason_code": "HEALTHY_SCORE",
    "health_score": 0.92,
    "primary_issue": null,
    "report_id": "uuid"
  },
  "timestamp": "2026-06-12T10:25:00.000000"
}
```

## Error Responses

- 400 Bad Request: Missing required fields or invalid format
- 404 Not Found: No report found for the requested system/environment
- 503 Service Unavailable: Simulator unavailable for simulator endpoints
