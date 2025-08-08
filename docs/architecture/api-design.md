# QVF Platform API Design Specification

**Version**: 1.0  
**Date**: 2025-01-08  
**Status**: Design Phase  

## Overview

This document specifies the REST API design for the QVF Platform, including endpoints, request/response formats, authentication, and integration patterns.

## Base API Structure

```
Base URL: https://qvf-platform.com/api/v1/
Authentication: Bearer JWT tokens
Content-Type: application/json
```

## Authentication & Authorization

### JWT Token Structure
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user-uuid",
    "email": "user@company.com",
    "role": "admin|user|viewer",
    "ado_user_id": "optional-ado-id",
    "exp": 1672531200,
    "iat": 1672444800
  }
}
```

### Authentication Flow
1. **Login**: `POST /auth/login` - Returns access + refresh tokens
2. **Refresh**: `POST /auth/refresh` - Returns new access token
3. **Logout**: `POST /auth/logout` - Invalidates tokens
4. **Profile**: `GET /auth/me` - Current user information

## Core API Endpoints

### Administrative Operations (`/admin/`)

#### System Status
```http
GET /api/v1/admin/system/status
Authorization: Bearer <token>

Response 200:
{
  "status": "healthy|degraded|error",
  "version": "1.0.0",
  "uptime": "72h 15m 30s",
  "components": {
    "database": {
      "status": "healthy",
      "response_time_ms": 15,
      "connection_pool": "8/20"
    },
    "redis": {
      "status": "healthy", 
      "memory_usage": "45%",
      "hit_rate": "92.3%"
    },
    "qvf_engine": {
      "status": "healthy",
      "last_calculation": "2025-01-08T12:00:00Z",
      "ai_enhancement": "available|unavailable"
    },
    "ado_integration": {
      "status": "healthy",
      "last_sync": "2025-01-08T11:45:00Z",
      "sync_lag_minutes": 5
    }
  },
  "metrics": {
    "api_requests_per_minute": 45,
    "average_response_time_ms": 120,
    "error_rate_percent": 0.5,
    "active_users": 23
  }
}
```

#### Configuration Management
```http
GET /api/v1/admin/config
Authorization: Bearer <token>

Response 200:
{
  "qvf_configuration": {
    "name": "Enterprise Configuration",
    "version": "2.1.0",
    "criteria": [
      {
        "id": "business_value",
        "name": "Business Value",
        "weight": 0.25,
        "enabled": true,
        "description": "Expected business impact"
      }
    ],
    "weights": {
      "business_value": 0.25,
      "strategic_alignment": 0.25,
      "customer_value": 0.20,
      "implementation_complexity": 0.15,
      "risk_assessment": 0.15
    }
  },
  "system_settings": {
    "ai_enhancement_enabled": true,
    "max_work_items_per_calculation": 1000,
    "calculation_timeout_seconds": 300,
    "cache_ttl_hours": 24
  }
}

PUT /api/v1/admin/config
Content-Type: application/json
Authorization: Bearer <token>

Request Body:
{
  "qvf_configuration": { /* updated config */ },
  "system_settings": { /* updated settings */ }
}

Response 200:
{
  "success": true,
  "message": "Configuration updated successfully",
  "validation_results": {
    "weights_sum": 1.0,
    "criteria_count": 9,
    "validation_passed": true
  },
  "applied_at": "2025-01-08T12:15:00Z"
}
```

### QVF Scoring Operations (`/scoring/`)

#### Calculate QVF Scores
```http
POST /api/v1/scoring/calculate
Content-Type: application/json
Authorization: Bearer <token>

Request Body:
{
  "session_name": "Sprint Planning - Q1 2025",
  "work_items": [
    {
      "id": "12345",
      "title": "User Authentication System",
      "description": "Implement secure user authentication with OAuth2",
      "type": "Epic",
      "state": "New",
      "assigned_to": "dev-team-1",
      "custom_fields": {
        "business_value": 4,
        "strategic_alignment": 5,
        "customer_value": 4,
        "implementation_complexity": 3,
        "risk_assessment": 2
      },
      "metadata": {
        "story_points": 21,
        "priority": "High",
        "area_path": "Platform\\Security"
      }
    }
  ],
  "configuration": {
    "use_ai_enhancement": true,
    "include_personal_metrics": true,
    "calculation_timeout": 300
  }
}

Response 200:
{
  "calculation_id": "calc-uuid-12345",
  "session_id": "session-uuid-67890",
  "results": [
    {
      "work_item_id": "12345",
      "qvf_score": 0.847,
      "normalized_score": 84.7,
      "rank": 1,
      "criteria_breakdown": {
        "business_value": {
          "raw_score": 4,
          "weighted_score": 1.0,
          "weight": 0.25,
          "contribution_percent": 29.5
        },
        "strategic_alignment": {
          "raw_score": 5,
          "weighted_score": 1.25,
          "weight": 0.25,
          "contribution_percent": 29.5
        }
      },
      "confidence": {
        "overall": 0.92,
        "data_completeness": 0.95,
        "ai_enhancement": 0.88,
        "consistency": 0.94
      },
      "evidence": [
        "High strategic alignment with Q1 security objectives",
        "Strong business value due to compliance requirements",
        "Moderate implementation complexity manageable by current team"
      ],
      "recommendations": [
        "Consider breaking into smaller epics for better predictability",
        "Ensure security expertise available before sprint commitment"
      ]
    }
  ],
  "summary": {
    "total_items": 25,
    "processing_time_ms": 2340,
    "ai_enhancement_used": true,
    "personal_metrics_applied": 3,
    "calculation_timestamp": "2025-01-08T12:30:00Z"
  },
  "warnings": [
    "2 work items missing complete criteria data",
    "AI enhancement timeout occurred for 1 item (fallback used)"
  ]
}
```

#### Retrieve Calculation Results
```http
GET /api/v1/scoring/results/{calculation_id}
Authorization: Bearer <token>

Response 200:
{
  "calculation_id": "calc-uuid-12345",
  "status": "completed|processing|failed",
  "results": { /* Same structure as calculate response */ },
  "created_at": "2025-01-08T12:30:00Z",
  "completed_at": "2025-01-08T12:30:02Z"
}
```

### Personal Metrics (`/personal-metrics/`)

#### List User Metrics
```http
GET /api/v1/personal-metrics/
Authorization: Bearer <token>

Query Parameters:
- category?: string (performance|quality|velocity|satisfaction)
- include_scores?: boolean (default: false)
- limit?: number (default: 50)
- offset?: number (default: 0)

Response 200:
{
  "metrics": [
    {
      "id": "metric-uuid-123",
      "name": "Team Velocity",
      "description": "Story points completed per sprint",
      "category": "performance", 
      "data_type": "numeric",
      "frequency": "sprint",
      "target_value": 50.0,
      "unit": "points",
      "is_higher_better": true,
      "tags": ["team", "productivity"],
      "current_value": 47.5,
      "trend": "stable", // "increasing|decreasing|stable"
      "trend_percentage": 2.3,
      "last_updated": "2025-01-08T10:00:00Z",
      "scores_count": 12,
      "created_at": "2024-12-01T09:00:00Z"
    }
  ],
  "total": 15,
  "has_more": false
}
```

#### Create Personal Metric
```http
POST /api/v1/personal-metrics/
Content-Type: application/json
Authorization: Bearer <token>

Request Body:
{
  "name": "Code Review Turnaround Time",
  "description": "Average time from PR creation to approval",
  "category": "quality",
  "data_type": "numeric", 
  "frequency": "weekly",
  "target_value": 2.0,
  "unit": "days",
  "is_higher_better": false,
  "tags": ["code-review", "quality", "team-process"]
}

Response 201:
{
  "id": "metric-uuid-456",
  "name": "Code Review Turnaround Time",
  "category": "quality",
  "data_type": "numeric",
  "created_at": "2025-01-08T12:45:00Z",
  "message": "Personal metric created successfully"
}
```

#### Add Metric Score
```http
POST /api/v1/personal-metrics/{metric_id}/scores
Content-Type: application/json
Authorization: Bearer <token>

Request Body:
{
  "value": 1.8,
  "period_start": "2025-01-01",
  "period_end": "2025-01-07", 
  "notes": "Improved process with automated notifications",
  "confidence_level": 4,
  "context": {
    "sprint": "Sprint 15",
    "team_size": 6,
    "prs_reviewed": 24
  }
}

Response 201:
{
  "id": "score-uuid-789",
  "metric_id": "metric-uuid-456",
  "value": 1.8,
  "created_at": "2025-01-08T12:50:00Z",
  "message": "Score recorded successfully"
}
```

### Analytics & Dashboards (`/analytics/`)

#### Executive Dashboard Data
```http
GET /api/v1/analytics/dashboard/executive
Authorization: Bearer <token>

Query Parameters:
- time_period?: string (current_quarter|last_quarter|ytd)
- include_trends?: boolean (default: true)

Response 200:
{
  "dashboard_data": {
    "strategic_investment_distribution": {
      "by_theme": {
        "Digital Transformation": {
          "investment": 2500000,
          "percentage": 35.7,
          "strategic_alignment": 0.89,
          "project_count": 8
        },
        "Customer Experience": {
          "investment": 1800000,
          "percentage": 25.7,
          "strategic_alignment": 0.92,
          "project_count": 12
        }
      },
      "total_investment": 7000000,
      "strategic_percentage": 78.4,
      "tactical_percentage": 21.6
    },
    "top_initiatives": [
      {
        "id": "epic-123",
        "title": "Customer Portal Redesign",
        "qvf_score": 0.94,
        "investment": 450000,
        "strategic_alignment": 0.96,
        "expected_completion": "2025-06-30",
        "status": "In Progress"
      }
    ],
    "portfolio_health": {
      "total_projects": 45,
      "on_track": 32,
      "at_risk": 8,
      "blocked": 5,
      "health_score": 0.78
    },
    "generated_at": "2025-01-08T13:00:00Z"
  }
}
```

#### Product Owner Dashboard
```http
GET /api/v1/analytics/dashboard/product-owner
Authorization: Bearer <token>

Query Parameters:
- sprint_id?: string
- include_gantt?: boolean (default: true)

Response 200:
{
  "dashboard_data": {
    "sprint_context": {
      "sprint_id": "sprint-15",
      "name": "Sprint 15 - Q1 2025",
      "start_date": "2025-01-06",
      "end_date": "2025-01-19",
      "status": "active"
    },
    "epic_breakdown": [
      {
        "epic_id": "epic-456",
        "title": "User Management System",
        "qvf_score": 0.82,
        "completion_percentage": 65,
        "story_count": 12,
        "story_points_total": 55,
        "story_points_completed": 36,
        "projected_completion": "2025-02-15"
      }
    ],
    "gantt_chart_data": {
      "timeline_start": "2025-01-01",
      "timeline_end": "2025-06-30",
      "quarters": [
        {"name": "Q1 2025", "start": "2025-01-01", "end": "2025-03-31"}
      ],
      "items": [
        {
          "id": "epic-456",
          "name": "User Management System",
          "start_date": "2025-01-06",
          "end_date": "2025-02-15", 
          "progress": 65,
          "qvf_score": 0.82,
          "dependencies": ["epic-123"],
          "status": "in_progress"
        }
      ]
    }
  }
}
```

## Error Response Format

All API errors follow a consistent format:

```json
{
  "error": {
    "code": "QVF_VALIDATION_ERROR",
    "message": "Criteria weights must sum to 1.0",
    "details": {
      "current_sum": 0.95,
      "missing": 0.05,
      "affected_criteria": ["risk_assessment"]
    },
    "request_id": "req-uuid-789",
    "timestamp": "2025-01-08T13:15:00Z"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_REQUEST` | 400 | Request body validation failed |
| `UNAUTHORIZED` | 401 | Missing or invalid authentication |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `QVF_VALIDATION_ERROR` | 422 | QVF configuration validation failed |
| `QVF_CALCULATION_ERROR` | 422 | QVF calculation failed |
| `QVF_TIMEOUT_ERROR` | 408 | Calculation timed out |
| `INTERNAL_ERROR` | 500 | Server error |
| `SERVICE_UNAVAILABLE` | 503 | AI enhancement or external service unavailable |

## Rate Limiting

API requests are rate-limited to ensure system stability:

```
Rate Limits:
- 100 requests per minute per user (general API)
- 10 calculation requests per minute per user 
- 1000 requests per hour per user
- Burst limit: 20 requests per 10 seconds

Headers:
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1672531260
```

## WebSocket Support (Future Enhancement)

For real-time updates during long-running calculations:

```javascript
// WebSocket connection for calculation updates
const ws = new WebSocket('wss://qvf-platform.com/ws/calculations/{session_id}');

// Message types:
{
  "type": "calculation_progress",
  "data": {
    "session_id": "session-uuid",
    "progress": 45,
    "items_processed": 11,
    "items_total": 25,
    "current_item": "Processing Epic: User Authentication System"
  }
}

{
  "type": "calculation_complete",
  "data": {
    "session_id": "session-uuid",
    "calculation_id": "calc-uuid-123",
    "results_url": "/api/v1/scoring/results/calc-uuid-123"
  }
}
```

## Integration with External Systems

### Azure DevOps Integration
- **Sync Endpoint**: `POST /api/v1/ado/sync`
- **Webhook Support**: ADO webhooks trigger QVF recalculation
- **Custom Fields**: Automatic creation and updates of QVF custom fields

### Authentication Integration
- **SSO Support**: SAML/OAuth2 integration planned
- **ADO Authentication**: Optional integration with ADO identity

## API Versioning Strategy

- **Current Version**: v1
- **Versioning Scheme**: URL path versioning (`/api/v1/`, `/api/v2/`)
- **Backward Compatibility**: Maintained for at least 2 major versions
- **Deprecation Policy**: 6-month notice before version retirement

## OpenAPI/Swagger Documentation

The API will provide comprehensive OpenAPI 3.0 specification:
- **Interactive Docs**: Available at `/api/docs` 
- **Schema Export**: Available at `/openapi.json`
- **TypeScript Generation**: Automated client generation for frontend

---

This API design provides a comprehensive, RESTful interface to all QVF platform capabilities while maintaining consistency, security, and scalability standards expected in enterprise environments.