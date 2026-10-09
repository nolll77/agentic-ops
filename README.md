# AgenticOps Core Engine

**AgenticOps** (formerly known as TrustGuard ML or Agentic Control Plane) is a standalone, AI-native MLOps Policy Engine and runtime. It provides autonomous validation, monitoring, and chaos engineering capabilities for machine learning systems in production.

## Features

- **Policy Engine**: Enforces MLOps governance policies.
- **Risk Register**: 435 Failure Modes structured across 10 system dimensions (infrastructure, data, feature engineering, training, serving, observability, security, governance, exploitation, organization).
- **Extensible Adapters**: Pluggable interfaces (`BaseSignalAdapter`, `BaseExecutionAdapter`) to integrate with any stack (MLflow, Kubernetes, Airflow, Datadog).

## Integration

This core engine is meant to be consumed as a library. In your ML project, you can install it and implement your own clients in `src/agentic_client/`.
