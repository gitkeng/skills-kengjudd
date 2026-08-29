# Reference playbook

## Program structure

Create an annotated source tree and namespace/module hierarchy. Mark entry points, generated/vendor/test areas, and component ownership. Use paths as evidence.

## Interfaces

Inventory public and cross-component interfaces with full signatures: name, visibility, parameters/types/defaults, return/error/async contract, implementation/callers, and evidence. Add implicit configuration contracts for required setting keys, environment variables, named connections, flags, ports, and expected files; do not reveal secret values.

## Data models

Inventory entities, value objects, storage mapping, fields/types/nullability, primary keys, foreign keys, cardinality, constraints, validation, and owning component. Include Mermaid v11 `erDiagram` with PK/FK annotations. Label inferred database constraints and distinguish application validation from enforced schema.

## API reference

For each HTTP, RPC, GraphQL, CLI, event, or other operation record method/topic/command, route/name, operation identifier, handler evidence, request parameters/body with an example payload, response/status/error with example payload, authentication, authorization, request-forgery protection where applicable, and side effects. Redact secrets and personal data.

## Modules

Describe module purpose, exports, dependencies, dependents, shared state, cycles, cohesion, and coupling notes. Cross-link `CMP-NNN` and architecture documents.
