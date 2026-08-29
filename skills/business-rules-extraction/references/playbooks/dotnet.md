# .NET Playbook

Stack-specific extraction guidance for C#, VB.NET, and the .NET ecosystem.

## Detection Signals

- File extensions: `.cs`, `.vb`, `.csproj`, `.vbproj`, `.sln`, `.razor`, `.cshtml`
- Project files: `.csproj` with SDK-style format, `*.sln` solutions
- Namespace declarations: `namespace Company.Product.Domain`
- Standard directories: `Controllers/`, `Services/`, `Models/`, `Data/`

## Dependency Signals

- **Namespace/project references:** `using` directives and `<ProjectReference>` in `.csproj` reveal module boundaries and domain dependencies.
- **Solution structure:** `.sln` files organize projects; often each project represents a bounded context or layer.
- **Assembly dependencies:** `<PackageReference>` and inter-project references reveal the dependency graph.
- **Interface contracts:** `I*Service` interfaces in shared projects define domain boundaries.

## Mining Strategy

Prefer **hybrid** for .NET: trace from controllers/pages (top-down) to identify user-facing capabilities, and from Entity Framework models/FluentValidation (bottom-up) to find data rules, converging at service/handler classes.

### Entity/Model Layer

- EF Core configurations: `HasMaxLength()`, `IsRequired()`, `HasIndex().IsUnique()` in `OnModelCreating` or `IEntityTypeConfiguration` → data_integrity rules.
- Data annotations: `[Required]`, `[StringLength]`, `[Range]`, `[RegularExpression]` → validation rules.
- Navigation properties with cascade delete configuration → referential integrity rules.
- Value objects and owned types → business concept boundaries.
- VB.NET: Property definitions with validation in `Set` accessors.

### Service/Handler Layer

- MediatR handlers, service classes, or domain event handlers containing conditionals → business rules.
- Guard clauses and `ArgumentException`/`InvalidOperationException` throwing → constraint rules.
- Specification pattern implementations → named, composable business conditions.
- Domain events raised on state changes → action_enabler rules.
- State machine libraries (Stateless, etc.) → process_workflow rules with explicit transitions.

### Controller/Razor Layer

- `[Authorize]`, `[AllowAnonymous]`, policy-based auth → access_control rules.
- Model state validation, `[ApiController]` auto-validation → validation rules (merge/conflict check with entity layer).
- Razor Pages `OnPost` handlers with business conditions → entry-point-level rules.
- Blazor component logic with conditional rendering → UI-layer business visibility rules.

### Configuration and Background Services

- `appsettings.json` values injected via `IOptions<T>` and used in conditions → configurable threshold rules.
- `IHostedService`/`BackgroundService` implementations → batch/scheduled process rules.
- Hangfire/Quartz.NET job definitions → scheduled workflow rules.
- Feature management (`IFeatureManager`) → conditional capability rules (document current state).

### Definition-Use Tracing

For every threshold or constant used in enforcement logic, trace backward to its definition: `appsettings.json`, constants/enum class, or database configuration. Include the definition source as additional evidence when it supplies the concrete value. When the same business concept is enforced at multiple layers (e.g., FluentValidation and a DB constraint), compare thresholds — identical values merge; differing values are conflict-linked.

### FluentValidation

- `RuleFor()` chains → validation rules with clear field-level evidence.
- `Must()`/`Custom()` validators → complex cross-field business validation.
- `When()`/`Unless()` conditional validation → context-dependent rules.
- Each validator class often corresponds to one business operation's input rules.

### SignalR/Event Patterns

- Hub methods with authorization and business conditions → access_control + action_enabler.
- Domain event handlers triggering notifications → process_workflow rules.

## Evidence Layer Mapping

| Source Type | Layer |
|------------|-------|
| Service classes, domain handlers | `code` |
| Entity configurations, data annotations | `code` |
| SQL migrations (EF Core Migrations/) | `sql` |
| Database constraints in migration code | `db_constraint` |
| Background services, Hangfire jobs | `batch` |
| Domain events, message handlers | `workflow` |
| Controller validation, Razor page logic | `ui` |
| appsettings.json, configuration classes | `config` |
| Business rule engine definitions | `rules_engine` |
