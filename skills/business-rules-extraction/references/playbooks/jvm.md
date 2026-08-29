# JVM Playbook

Stack-specific extraction guidance for Java, Kotlin, and JVM-based frameworks.

## Detection Signals

- File extensions: `.java`, `.kt`, `.kts`, `.groovy`, `.scala`
- Build files: `pom.xml`, `build.gradle`, `build.gradle.kts`, `settings.gradle`
- Package declarations: `package com.example.domain`
- Standard directories: `src/main/java/`, `src/main/kotlin/`, `src/main/resources/`

## Dependency Signals

- **Import/package graphs:** `import` statements and package structure reveal domain boundaries. Cross-package imports signal domain dependencies.
- **Build module structure:** Multi-module Maven/Gradle projects often align with domain boundaries.
- **Annotation scanning:** `@Autowired`, `@Inject`, constructor parameters reveal component wiring.
- **Interface implementations:** Service interfaces and their implementations reveal domain contracts.

## Mining Strategy

Prefer **hybrid** for JVM: start top-down from controllers/endpoints to identify business capabilities, then bottom-up from entity/repository layer to find data integrity rules, meeting in the service layer where most business logic lives.

### Entity Layer (persistence)

- `@Entity`/`@Table` classes define persistent entities and their field constraints.
- Field annotations: `@NotNull`, `@Size`, `@Min`, `@Max`, `@Pattern`, `@Column(nullable, length, unique)` → validation and data_integrity rules.
- Relationship annotations: `@OneToMany`, `@ManyToOne` with cascade/fetch → entity ownership and lifecycle rules.
- `@Version` → optimistic locking policy. `@Where`/`@Filter` → soft-delete or tenant isolation rules.
- Kotlin data classes with `init` blocks → validation at construction time.

### Service Layer (business logic)

- Methods with conditional returns, exception throwing, or state changes based on business conditions → constraints and action_enablers.
- Private methods called only for specific conditions → decision rules.
- Calculations using business-named variables → computation rules.
- `@Transactional` boundaries hint at atomic business operations.
- State machine implementations (enum-based, library-based) → process_workflow rules.
- Event publication (`@EventListener`, message publishing) → action_enablers triggering downstream processes.

### Controller/Endpoint Layer (entry points and UI validation)

- `@Valid`/`@Validated` on request bodies → validation rules (often duplicating entity constraints — apply merge/conflict policy).
- Custom validators (`implements ConstraintValidator`) → complex validation rules.
- Authorization annotations: `@PreAuthorize`, `@Secured`, `@RolesAllowed` → access_control rules.
- Response code selection logic → business outcome branching.

### Configuration and Rules Engines

- `application.yml`/`application.properties` values used in conditionals → configurable thresholds (document the current value and that it is configurable).
- Drools `.drl` files, Easy Rules definitions, or similar → rules_engine layer evidence. Decision tables in spreadsheet format → DMN export candidates.
- Scheduled tasks (`@Scheduled`, Quartz jobs) → batch layer; the schedule and trigger conditions are process_workflow rules.
- Feature flags/toggles → document current state and flag as potentially transient.

### Definition-Use Tracing

For every threshold, constant, or flag referenced in enforcement code, trace backward to its definition: constants class, enum, `application.yml`/`application.properties` entry, or database lookup. Include the definition site as additional evidence when it supplies the concrete value or business meaning. If two modules enforce the same business concept with values sourced from different definitions, this indicates a potential conflict — cite both definition sources.

### Spring/Framework Specifics

- `@ControllerAdvice`/`@ExceptionHandler` → error-handling business policies.
- Spring Security configuration → access_control rules (URL patterns, method security, CORS/CSRF policies with business justification).
- Spring Batch job/step/tasklet structure → batch workflow with conditional flow.
- Interceptors/filters with business conditions (not pure plumbing like logging) → cross-cutting rules.

### Kotlin Specifics

- `require()`/`check()` preconditions → constraint rules with clear evidence.
- Sealed classes/interfaces for state → exhaustive state enumeration.
- Extension functions on domain types → domain-specific computations.
- `when` expressions with exhaustive matching → decision rules.

## Evidence Layer Mapping

| Source Type | Layer |
|------------|-------|
| Service/domain classes | `code` |
| Entity annotations and constraints | `code` |
| SQL migrations, schema files | `sql` |
| Database constraints defined in DDL | `db_constraint` |
| Scheduled jobs, batch processors | `batch` |
| Event handlers, message listeners | `workflow` |
| Controller validation, request DTOs | `ui` |
| application.yml, properties files | `config` |
| Drools/rules engine definitions | `rules_engine` |
