# QVF Deployment Guide

**Quantified Value Framework (QVF) - Enterprise Prioritization System**  
*Production Deployment and Usage Guide*

## Overview

The Quantified Value Framework (QVF) is an enterprise-grade prioritization system that combines mathematical rigor with optional AI enhancement to provide objective, measurable prioritization for Agile Release Trains and PI Planning.

### Key Features

- **Mathematical Foundation**: Built on AHP (Analytic Hierarchy Process) with 95%+ consistency rates
- **Performance**: <60 seconds for 10,000 work items with <2 second AI fallback
- **Azure DevOps Integration**: Seamless custom field deployment and work item updates
- **AI Enhancement**: Optional Ollama integration with mandatory mathematical fallback
- **Executive Dashboards**: Real-time prioritization insights for stakeholders

## Quick Start

### 1. Installation

```bash
# Install QVF with core features
pip install -e .

# Install with AI enhancement support
pip install -e ".[qvf]"

# Install full feature set
pip install -e ".[full]"

# Verify installation
qvf --version
```

### 2. Initial Configuration

```bash
# Create initial configuration
qvf configure init --output qvf_config.json --interactive

# Or use manual configuration
cat > qvf_config.json << EOF
{
  "ado": {
    "organization": "your-organization",
    "project": "your-project",
    "pat_token": "your-pat-token",
    "custom_fields": {
      "qvf_score": "QVF_Score",
      "qvf_rank": "QVF_Rank",
      "qvf_confidence": "QVF_Confidence",
      "qvf_category": "QVF_Category"
    }
  },
  "scoring": {
    "batch_size": 100,
    "timeout": 60,
    "consistency_threshold": 0.10,
    "enable_ai": true
  },
  "criteria": {
    "preset": "enterprise"
  }
}
EOF
```

### 3. Deploy to Azure DevOps

```bash
# Validate configuration and deploy
qvf deploy --config qvf_config.json --environment production

# Dry run for validation
qvf deploy --config qvf_config.json --dry-run

# Force deployment without validation
qvf deploy --config qvf_config.json --force
```

### 4. Score Work Items

```bash
# Score work items from CSV
qvf score work_items.csv -o scored_results.csv --preset enterprise

# Use different criteria presets
qvf score work_items.csv --preset agile
qvf score work_items.csv --preset startup
```

## CLI Command Reference

### Core Commands

#### `qvf score`
Score work items using QVF methodology.

```bash
qvf score <input_file> [OPTIONS]

Options:
  -o, --output FILE          Output CSV file for scored results
  -p, --preset PRESET        Criteria preset: enterprise|agile|startup
  --config FILE              Configuration file path
  --batch-size N             Batch size for processing (default: 100)

Examples:
  qvf score backlog.csv -o prioritized_backlog.csv
  qvf score features.csv --preset agile --batch-size 50
```

#### `qvf deploy`
Deploy QVF to Azure DevOps environment.

```bash
qvf deploy [OPTIONS]

Options:
  --config FILE              Required: Configuration file with ADO credentials
  --environment ENV          Target environment: development|staging|production
  --dry-run                  Preview deployment without making changes
  --force                    Skip pre-deployment validation

Examples:
  qvf deploy --config prod_config.json --environment production
  qvf deploy --config test_config.json --dry-run
```

#### `qvf configure`
Configure QVF criteria and settings.

```bash
qvf configure <action> [OPTIONS]

Actions:
  init                       Create initial configuration
  criteria                   Configure criteria weights
  stakeholders               Configure stakeholder settings
  weights                    Configure criteria weights

Options:
  --output FILE              Output configuration file
  --interactive              Interactive configuration mode

Examples:
  qvf configure init --output my_config.json --interactive
  qvf configure criteria --output enterprise_criteria.json
```

#### `qvf validate`
Validate QVF system health and configuration.

```bash
qvf validate [OPTIONS]

Options:
  --config FILE              Configuration file to validate
  --detailed                 Show detailed validation results
  --output FILE              Save validation results to file

Examples:
  qvf validate --config qvf_config.json --detailed
  qvf validate --config qvf_config.json --output validation_report.json
```

## Deployment Scripts

### Automated Deployment

Use the comprehensive deployment script for production deployments:

```bash
# Production deployment with full validation
python3 scripts/deploy_qvf.py --config config/qvf_production.json --environment prod

# Staging deployment with dry run
python3 scripts/deploy_qvf.py --config config/qvf_staging.json --dry-run

# Development deployment
python3 scripts/deploy_qvf.py --config config/qvf_dev.json --environment development
```

### Deployment Script Features

- **Environment Validation**: Checks Python version, dependencies, and system requirements
- **Azure DevOps Integration**: Tests connectivity and deploys custom fields
- **Health Monitoring**: Continuous monitoring during deployment
- **Rollback Capability**: Automatic rollback on failure with manual rollback support
- **Performance Testing**: Validates <60 second performance requirement

### Deployment Process

1. **Pre-deployment Validation**
   - Environment and dependency checks
   - Azure DevOps connectivity validation
   - Configuration validation
   - System performance baseline

2. **Deployment Execution**
   - Configuration backup creation
   - Custom field deployment to ADO
   - QVF scoring engine configuration
   - AI component deployment (optional)
   - Integration test execution

3. **Post-deployment Verification**
   - Health check validation
   - Performance requirement verification
   - Integration test execution
   - Deployment registry update

## Configuration Guide

### Azure DevOps Configuration

```json
{
  "ado": {
    "organization": "your-organization",
    "project": "your-project", 
    "pat_token": "your-personal-access-token",
    "custom_fields": {
      "qvf_score": "QVF_Score",
      "qvf_rank": "QVF_Rank",
      "qvf_confidence": "QVF_Confidence", 
      "qvf_category": "QVF_Category"
    },
    "work_item_types": ["Feature", "Epic", "User Story"],
    "batch_update_size": 100
  }
}
```

### Scoring Configuration

```json
{
  "scoring": {
    "batch_size": 100,
    "timeout": 60,
    "consistency_threshold": 0.10,
    "enable_ai": true,
    "ai_timeout": 30,
    "fallback_timeout": 2,
    "performance_target": 60
  }
}
```

### Criteria Configuration

```json
{
  "criteria": {
    "preset": "enterprise",
    "custom_weights": {
      "business_value": 0.25,
      "user_impact": 0.20,
      "strategic_alignment": 0.15,
      "time_criticality": 0.15,
      "risk_reduction": 0.10,
      "technical_feasibility": 0.10,
      "resource_availability": 0.05
    }
  }
}
```

### AI Enhancement Configuration

```json
{
  "ai": {
    "enabled": true,
    "ollama_host": "http://localhost:11434",
    "model": "llama3.1:8b",
    "timeout": 30,
    "max_concurrent": 5,
    "cache_enabled": true,
    "cache_ttl": 3600,
    "fallback_enabled": true,
    "fallback_timeout": 2
  }
}
```

## Data Format Requirements

### Input Work Items CSV

Required columns for QVF scoring:

```csv
id,title,description,work_item_type,business_value,user_impact,strategic_alignment,time_criticality,estimated_value,development_cost
WI-001,Customer Portal,New customer portal feature,Feature,8,7,9,6,50000,25000
WI-002,Mobile App,Mobile application development,Epic,9,8,7,8,100000,60000
```

### Column Specifications

- **id** (string): Unique work item identifier
- **title** (string): Work item title
- **description** (string): Detailed description
- **work_item_type** (string): Type (Feature, Epic, User Story, etc.)
- **business_value** (1-10): Business value rating
- **user_impact** (1-10): User impact rating  
- **strategic_alignment** (1-10): Strategic alignment rating
- **time_criticality** (1-10): Time criticality rating
- **estimated_value** (number): Estimated business value in currency
- **development_cost** (number): Development cost estimate
- **maintenance_cost** (number, optional): Ongoing maintenance cost
- **risk_cost** (number, optional): Risk mitigation cost

### Output Format

QVF scoring produces enriched work items with additional columns:

```csv
id,title,qvf_score,qvf_rank,criteria_score,financial_score,qvf_confidence,qvf_category
WI-002,Mobile App,87.5,1,82.3,92.1,0.85,Critical
WI-001,Customer Portal,76.2,2,78.9,73.8,0.82,High
```

## Testing

### Integration Test Suite

```bash
# Run comprehensive integration tests
python -m pytest tests/test_qvf_integration.py -v

# Run specific test categories
python -m pytest tests/test_qvf_integration.py::TestQVFEndToEnd -v
python -m pytest tests/test_qvf_integration.py::TestADOIntegration -v
python -m pytest tests/test_qvf_integration.py::TestAIIntegration -v

# Run with coverage
python -m pytest tests/test_qvf_integration.py --cov=src.datascience_platform.qvf
```

### Performance Testing

```bash
# Performance benchmarks
python3 tests/test_qvf_integration.py TestQVFCoreComponents.test_batch_scoring_performance
python3 tests/test_qvf_integration.py TestQVFEndToEnd.test_large_dataset_processing

# Performance requirements validation
python3 tests/test_qvf_integration.py TestQVFDeployment.test_performance_requirements
```

## Troubleshooting

### Common Issues

#### 1. Azure DevOps Connection Failures

```bash
# Validate ADO configuration
qvf validate --config qvf_config.json --detailed

# Test connection manually
curl -u ":YOUR_PAT_TOKEN" https://dev.azure.com/YOUR_ORG/_apis/projects
```

#### 2. Performance Issues

```bash
# Check system resources
qvf validate --config qvf_config.json --detailed

# Reduce batch size for memory-constrained environments
qvf score work_items.csv --batch-size 50

# Monitor scoring performance
time qvf score work_items.csv -o results.csv
```

#### 3. AI Enhancement Issues

```bash
# Check AI component status
qvf validate --config qvf_config.json --detailed

# Test Ollama connection
curl http://localhost:11434/api/version

# Disable AI if needed
# Set "enable_ai": false in configuration
```

#### 4. Scoring Consistency Issues

```bash
# Check criteria configuration
qvf configure criteria

# Validate consistency threshold
# Ensure consistency_threshold <= 0.10 in configuration

# Review criteria weights
# Ensure all weights sum to 1.0
```

### Log Analysis

QVF provides structured logging for troubleshooting:

```bash
# Enable detailed logging
export QVF_LOG_LEVEL=DEBUG

# Check deployment logs
tail -f deployments/deployment_12345/deployment.log

# Review scoring logs
grep "scoring_error" /var/log/qvf/qvf.log
```

## Performance Optimization

### System Requirements

**Minimum Requirements:**
- Python 3.8+
- 4GB RAM
- 2 CPU cores
- 1GB disk space

**Recommended for Production:**
- Python 3.9-3.11
- 8GB+ RAM
- 4+ CPU cores
- 5GB+ disk space
- GPU (optional, for AI enhancement)

### Performance Tuning

#### Batch Processing

```json
{
  "scoring": {
    "batch_size": 100,          // Reduce for memory constraints
    "max_concurrent": 5,        // Increase for more CPU cores
    "timeout": 60,              // Adjust based on dataset size
    "cache_enabled": true       // Enable for repeated scoring
  }
}
```

#### Memory Optimization

```json
{
  "system": {
    "max_memory_mb": 4096,      // Set memory limit
    "gc_enabled": true,         // Enable garbage collection
    "cache_size": 10000         // Adjust cache size
  }
}
```

#### AI Performance

```json
{
  "ai": {
    "model": "llama3.1:8b",     // Use smaller model for speed
    "max_concurrent": 3,        // Limit concurrent AI requests
    "timeout": 15,              // Reduce timeout for faster fallback
    "cache_ttl": 7200          // Longer cache for repeated queries
  }
}
```

## Security Considerations

### Credential Management

- Store PAT tokens securely (environment variables or key vaults)
- Rotate tokens regularly
- Use least-privilege access for ADO integration
- Enable audit logging for all QVF operations

### Data Protection

- Ensure work item data complies with organizational policies
- Consider data residency requirements for AI processing
- Implement encryption for sensitive configuration data
- Regular security audits of QVF deployments

## Monitoring and Observability

### Health Checks

```bash
# System health validation
qvf validate --config qvf_config.json --detailed --output health_report.json

# Continuous monitoring script
while true; do
  qvf validate --config qvf_config.json
  sleep 300  # Check every 5 minutes
done
```

### Performance Metrics

Key metrics to monitor:
- Scoring throughput (items/second)
- Average scoring time per item
- AI enhancement success rate
- ADO integration success rate
- Memory and CPU utilization

### Alerting

Configure alerts for:
- Scoring failures (>5% error rate)
- Performance degradation (>90 seconds for 1000 items)
- AI fallback activation (>10% fallback rate)
- ADO connection failures

## Production Checklist

### Pre-Deployment

- [ ] Configuration validated
- [ ] Azure DevOps connectivity tested
- [ ] Performance requirements verified
- [ ] Integration tests passing
- [ ] Security review completed
- [ ] Monitoring configured
- [ ] Rollback plan prepared

### Post-Deployment

- [ ] Health checks passing
- [ ] Performance metrics within targets
- [ ] User acceptance testing completed
- [ ] Documentation updated
- [ ] Team training completed
- [ ] Support procedures established

## Support and Maintenance

### Regular Maintenance

- **Weekly**: Health check validation and performance monitoring
- **Monthly**: Security audit and credential rotation
- **Quarterly**: Criteria weight review and optimization
- **Annually**: System architecture review and upgrade planning

### Version Updates

```bash
# Check for updates
pip list --outdated | grep datascience-platform

# Update QVF
pip install --upgrade datascience-platform[qvf]

# Validate after update
qvf validate --config qvf_config.json --detailed
```

## Contact and Support

For technical support or questions:
- **Documentation**: https://github.com/your-org/ds-package/wiki
- **Issues**: https://github.com/your-org/ds-package/issues
- **Discussions**: https://github.com/your-org/ds-package/discussions

---

*QVF Deployment Guide - Version 1.0.0*  
*Generated with Claude Code - August 2025*