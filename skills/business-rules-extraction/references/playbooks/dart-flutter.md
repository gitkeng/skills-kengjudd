# Dart / Flutter — Business-Rules Extraction Playbook

## Detection Signals

- `pubspec.yaml` declares packages, versions, and dependency overrides.
- `lib/` is the primary source root; `lib/src/` contains private implementation.
- Barrel files (re-export declarations in top-level `.dart`) define public API surface.
- `part` / `part of` directives merge files into a single library unit — follow both halves.
- Conditional imports (`if (dart.library.io)`) signal platform-specific forks — inspect each branch.

## Dependency Signals

- Package imports (`import 'package:...'`) and relative imports establish module boundaries.
- Architecture packages in `pubspec.yaml` signal patterns: `flutter_bloc`, `riverpod`, `get_it`, `injectable`, `drift`, `isar`.
- Federated plugin packages (`*_platform_interface`, `*_android`, `*_ios`, `*_web`) split platform implementations.

## Mining Strategy

Prefer **top-down** for UI-centric Flutter apps: start from route tables (`MaterialApp.routes`, `go_router`, `auto_route`) and trace through state management to domain logic. Supplement **bottom-up** from persistence schemas and repository contracts for data-heavy features.

## Evidence Layer Enum Mapping

| Dart/Flutter Source Type | Evidence `layer` Value |
|--------------------------|----------------------|
| Domain entities, value objects (`lib/domain/`, `lib/models/`) | `code` |
| Use case / interactor classes (`lib/usecases/`, `lib/application/`) | `code` |
| BLoC/Cubit/StateNotifier transition logic and guard conditions | `code` |
| Repository interface contracts and implementations | `code` |
| Service classes, utility functions with business logic | `code` |
| `TextFormField.validator` callbacks, `Form` validation closures | `ui` |
| Standalone validator functions used only in widget trees | `ui` |
| Visibility/Offstage/AbsorbPointer conditional rendering driven by domain state | `ui` |
| Route guards, `redirect` callbacks, `PopScope` exit-prevention | `ui` |
| Drift/Isar/sqflite schema definitions and migration SQL | `sql` |
| Database `CHECK` constraints, unique indexes in migrations | `db_constraint` |
| Isolate-based background work, `workmanager` scheduled tasks | `batch` |
| Stream pipelines orchestrating multi-step domain flows | `workflow` |
| Environment configs, feature flags, `RemoteConfig` values | `config` |
| Declarative rule tables (JSON/YAML-driven decision matrices) | `rules_engine` |

## Client-Only Enforcement — Explicit Absence

A pure Flutter app has **no server-side runtime**. All rules extracted from Dart source are client-enforced only. There is no service-layer backstop unless an external backend exists.

- Evidence from `TextFormField.validator`, `Form` closures, widget-tree conditionals, and route guards receives layer `ui`. These rules are bypassable by any client that skips the UI.
- When HTTP calls exist (`http`, `dio`, `graphql_flutter`, `amplify_flutter`), the server may independently enforce rules. State explicitly in `open_questions` when no server-side enforcement is confirmed for a client-side rule.
- Firebase Security Rules, Supabase RLS, or Amplify auth configs are **separate server-side rule sources** not present in Dart source — document their absence when no backend rule file is found.

## Platform Divergences — Bidirectional Conflicts

Platform-conditional branches (`Platform.isAndroid`, `Platform.isIOS`, `kIsWeb`, conditional imports) that enforce the **same business concept** with **different thresholds, conditions, or outcomes** produce **separate rules** with bidirectional `conflicting_rule_ids`.

Do NOT merge into a single rule with platform annotations. Per step 11 of the workflow: if any dimension (subject scope, condition, threshold, outcome) differs between platform branches, they are distinct conflicting rules.

- Each platform branch becomes its own rule with evidence citing the branch.
- Both rules cross-link via `conflicting_rule_ids`.
- Add an `open_questions` entry explaining the platform divergence rationale.
- If all four dimensions are identical (same logic, different import path only), merge into one rule with multiple evidence entries.

## Generated Code Exclusions

Exclude all generated files — never extract rules from them. Trace each to its generator:

| Pattern | Generator Source |
|---------|-----------------|
| `*.g.dart` | `build_runner` + `source_gen` (json_serializable, retrofit, injectable, etc.) |
| `*.freezed.dart` | `freezed` code generator |
| `*.gr.dart` | `auto_route` route generator |
| `*.config.dart` | `injectable` / `get_it` config generator |
| `*.mocks.dart` | `mockito` / `mocktail` build_runner output |
| `app_localizations.dart` in `l10n/` | `flutter gen-l10n` ARB localization |
| Files with header `// GENERATED CODE - DO NOT MODIFY BY HAND` | Any `source_gen`-based generator |

Also exclude: `.dart_tool/`, `.packages`, `build/`, `windows/flutter/generated_*`, `ios/Runner/GeneratedPluginRegistrant.*`.

When a generated file references a business-relevant annotation (e.g., `@JsonKey(defaultValue:)`), trace to the **hand-written source** bearing the annotation and cite that as evidence instead.

## Definition-Use Tracing

- Trace from public API (constructor params, public methods) into `_private` methods for full rule scope.
- Extension methods (`extension on Type`) may contain domain rules — follow all extensions on domain types.
- Mixin classes: follow `with` clauses to locate mixed-in rule logic.
- For every threshold, constant, or flag at an enforcement site, trace to its definition (enum, const, config file, `RemoteConfig` key) and include the definition as additional evidence.
- `typedef` and type aliases may obscure callback signatures carrying rule contracts.

## State Management — Rule Extraction Points

- **BLoC:** `Bloc<Event, State>` / `Cubit<State>` — transition logic in `on<Event>` handlers or `emit` calls.
- **Riverpod:** `StateNotifier`, `AsyncNotifier`, `Notifier` — business logic in notifier methods.
- **Provider (legacy):** `ChangeNotifier` subclasses with public mutators.
- **Redux:** `Reducer` functions and middleware — side-effect rules in middleware.
- Sealed class hierarchies for events/states — exhaustive `switch` contains branching logic.

## Offline Sync and Connectivity

- Connectivity listeners (`connectivity_plus`) gate sync triggers — extract retry, queue, and conflict-resolution rules.
- Local-first write + sync-queue patterns: the queue logic and reconciliation strategy are business rules.
- Platform channels (`MethodChannel`, `EventChannel`) bridge native code — inspect paired native implementations.

## UI Lifecycle / Rendering Plumbing — Exclude

- `initState`, `dispose`, `didChangeDependencies`, `didUpdateWidget` — exclude unless gating business behavior.
- `build()` rendering structure — exclude unless conditional branches are driven by domain state.
- `AnimationController`, `Tween`, `LayoutBuilder`, `MediaQuery`, `Sliver*`, `paint()`, `RenderObject` — exclude.
- `Key` assignments, `GlobalKey` for widget identity — infrastructure, not rules.
- `SchedulerBinding`, `WidgetsBinding` interactions — framework plumbing, exclude.

## Extraction Checklist

1. Parse `pubspec.yaml` for architecture packages (signals patterns in use).
2. Identify barrel exports to scope public API surface.
3. Map route table to screen widgets; trace each screen's state dependencies.
4. Collect all BLoC/Cubit/StateNotifier subclasses — extract event→state transition rules.
5. Collect `Form` validators and standalone validator functions — label evidence as `ui`.
6. Inspect repository interfaces for method-level contracts and return-type constraints.
7. For platform-conditional branches: extract each branch as a separate rule; link with `conflicting_rule_ids` when dimensions differ.
8. Exclude generated files (trace to generator source when annotations are business-relevant).
9. Cross-reference `ui`-layer rules against `code`-layer rules — flag duplicates and conflicts.
10. State explicitly when no server-side enforcement exists for a client-validated rule.
