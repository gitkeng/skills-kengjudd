# Vendor-neutral recommendations

## Rule

Describe products only when the repository verifiably uses them, in detection tables, as a direct successor in the same product line, or in a balanced option list. Never make one vendor the default migration target or recommended next action.

A recommendation names vendors only in a list of at least three viable examples spanning at least two providers, or combining hosted and self-hosted choices. Lead with the capability: runtime upgrade, containerization, managed relational storage, event messaging, function execution, identity, or telemetry.

Outdated-component migration paths may name the same product line's direct successor. Operations detection tables may name formats. Language terms that are homonyms are not vendor references.

## Modernization pathway format

For each pathway include: capability, suitability signals, constraints, portability trade-offs, reversible first step, and balanced examples when examples are useful. “Keep current deployment with remediation” is a valid baseline.

## Seed-list gate

The validator/build review scans these case-insensitive whole terms and adjudicates each hit:

`AWS`, `Amazon`, `Azure`, `GCP`, `Google Cloud`, `Lambda`, `ECS`, `EKS`, `S3`, `App Service`, `Cloud Run`, `Fargate`, `DynamoDB`, `Cosmos DB`, `BigQuery`.

Allowed dispositions are: observed repository usage in generated output; balanced list; direct successor; operations detection; language homonym; or this seed list. Record no single-vendor recommendation.
