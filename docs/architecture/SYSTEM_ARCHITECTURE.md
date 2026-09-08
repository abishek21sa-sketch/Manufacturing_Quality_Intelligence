# System Architecture

## Decision flow

1. **Acquire** process, inspection, measurement-system and contextual data.
2. **Validate** against canonical data contracts and quality rules.
3. **Statistically monitor** stable-process behavior using SPC and capability.
4. **Predict** part/lot quality risk using temporally validated models.
5. **Diagnose** influential process signals with model-level contributions and quality methods.
6. **Simulate** defect/cost exposure under uncertainty and scenario changes.
7. **Optimize** inspection intensity/resource allocation under capacity and cost constraints.
8. **Recommend** containment, sampling or continued-production actions with rationale.
9. **Serve** outputs through versioned REST APIs and an operator-facing frontend.

## Boundaries

The domain layer contains quality semantics and is independent of HTTP/UI concerns. AI models consume the canonical feature contract. Optimization consumes probabilities and business parameters rather than raw model internals. The decision layer is the only layer allowed to combine predictive, statistical, simulation and optimization evidence into an action.

## Production extension points

Plant connectors, feature store/model registry, authentication/RBAC, event bus, relational persistence, observability, drift monitoring and human approval workflows can be added behind existing boundaries without rewriting the analytical core.
