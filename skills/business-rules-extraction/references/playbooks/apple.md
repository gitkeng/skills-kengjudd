# Apple Platforms Playbook — Swift & Objective-C Business-Rules Extraction

## 1 Package / Project / Module Signals

| Signal | Where Found | Rule Relevance |
|--------|-------------|----------------|
| `Package.swift` dependencies & targets | repo root or package dir | Boundaries between modules; public API surface defines contract rules |
| `.xcodeproj` / `.xcworkspace` targets | project root | Build phases, linked frameworks, and capability entitlements encode deployment constraints |
| `@_exported import`, `@testable import` | source files | Visibility leaks across module boundaries; test-only relaxations |
| `Info.plist` keys | bundle resources | Platform-enforced capability rules |
| CocoaPods `Podfile` / Carthage `Cartfile` | repo root | Pinned dependency versions encode compatibility rules |
| Swift Package Manager platform constraints (`.iOS(.v15)`) | `Package.swift` | Minimum deployment target rules |

## 2 Protocols / Extensions / Categories / Delegates / Selectors / Runtime Dispatch

### Swift Protocols & Extensions
- `protocol` declarations define behavioral contracts; conformance (`struct X: P`) binds rules to types.
- Protocol extensions with `where` clauses impose conditional rules.
- `@objc optional` protocol methods indicate optional behavioral hooks.

### Objective-C Categories & Protocols
- Categories (`@interface NSString (Validation)`) attach rules to existing types without subclassing.
- Formal protocols with `@required` / `@optional` delineate mandatory vs advisory rules.
- Class extensions (anonymous categories in `.m`) hide private rule logic from the header contract.

### Delegates & Selectors
- Delegate patterns (`weak var delegate: FooDelegate?`) route decisions to external rule owners.
- `#selector` / `@selector` bind runtime dispatch to named rule methods.
- `responds(to:)` guards optional rule paths at runtime.

### Runtime Dispatch
- `@objc dynamic` enables KVO and method swizzling — rules may be intercepted at runtime.
- Message forwarding (`forwardingTarget(for:)`) redirects rule evaluation to alternate objects.

## 3 Swift Guards / Patterns / Property Wrappers / Errors

### Guards & Patterns
- `guard` statements encode preconditions; the `else` branch defines violation handling.
- `if case let`, `switch` exhaustiveness, and `where` clauses encode classification rules.
- `@unknown default` signals forward-compatible enumeration handling rules.

### Property Wrappers
- `@propertyWrapper` types encapsulate validation/transformation rules.
- `wrappedValue` setter is the enforcement point; `projectedValue` may expose rule metadata.

### Errors & Results
- `enum` conforming to `Error` enumerates domain failure rules.
- `throws` / `rethrows` propagate rule violations up the call stack.
- `Result<Success, Failure>` encodes success/failure paths as first-class values.

## 4 Objective-C Headers / Properties / Macros

### Headers
- `.h` files are the public contract; rules exposed here are module-boundary commitments.
- `NS_ASSUME_NONNULL_BEGIN` / `_Nullable` annotations encode nullability rules at the API boundary.
- `NS_SWIFT_NAME` customizes Swift import naming — rule method identity may differ across languages.

### Properties
- `@property` attributes: `readonly` (immutable rule), `copy` (value-semantics rule), `nonatomic` (thread-safety decision).
- Custom getters/setters embed validation rules.

### Macros
- `NS_ENUM` / `NS_OPTIONS` define closed/open rule domains.
- `NS_UNAVAILABLE` / `NS_DESIGNATED_INITIALIZER` encode construction rules.
- Preprocessor `#if TARGET_OS_IOS` gates platform-specific rules.

## 5 UI Validation / Navigation / Visibility

| Mechanism | Rule Type |
|-----------|-----------|
| `UITextField` delegate `shouldChangeCharactersIn` | Input-format validation |
| SwiftUI `.disabled(condition)` / `.opacity(0)` | Conditional visibility/access rules |
| `NavigationLink` / `sheet(isPresented:)` with binding guards | Navigation-eligibility rules |
| `@ViewBuilder` conditional branches | UI-state-driven composition rules |
| `UIAlertController` presentation gating | User-confirmation rules |
| Form `.validation` modifiers / custom `ViewModifier` | Field-level constraint rules |

## 6 Persistence / Configuration

- Core Data `NSManagedObjectModel` constraints (validation predicates, delete rules, optionality).
- `@FetchRequest` predicates and sort descriptors encode query-time filtering rules.
- `UserDefaults` / `@AppStorage` keys carry lightweight config rules; missing keys imply defaults.
- Keychain access groups and `kSecAttrAccessible` constants encode security-tier rules.
- CloudKit `CKRecord` field types and `CKReference` actions encode relational integrity rules.

## 7 Definition-Use Tracing

- Follow `let` / `var` binding from declaration through all mutation/read sites.
- Computed properties inline rule logic at access points.
- `didSet` / `willSet` observers trigger side-effect rules on mutation.
- Closure captures (`[weak self]`) carry ownership rules into deferred execution.
- Key paths (`\Type.property`) enable type-safe indirection; trace usage in KVO and SwiftUI bindings.

## 8 Client-Only Absence Signals

- No server endpoint calls (`URLSession`, `Alamofire`, `Moya`) → rules are purely local.
- Validation logic without corresponding server-side schema → client-only enforcement.
- Offline-first patterns (`Reachability` checks gating network calls) → local rule fallback paths.
- On-device ML (`CoreML`, `Vision`) inference without server round-trip → local decision rules.

## 9 Generated / Derived Artifacts

| Artifact | Generator | Treatment |
|----------|-----------|-----------|
| `.pbxproj` internal UUIDs | Xcode | Ignore; not rule-bearing |
| `*.generated.swift` (Sourcery, SwiftGen) | Code-generation tools | Trace rules to templates, not output |
| Core Data `+CoreDataProperties.swift` | Xcode model editor | Rules live in `.xcdatamodeld`, not generated code |
| Protocol Buffers `.pb.swift` | `protoc` | Rules live in `.proto` definitions |
| Interface Builder `*.storyboard` XML | Xcode IB | Segue identifiers and constraint constants carry UI rules |

## 10 Lifecycle / Memory / Rendering Plumbing (Exclude)

- `viewDidLoad`, `viewWillAppear`, `sceneDidBecomeActive` — framework timing hooks.
- `applicationDidFinishLaunching`, `applicationWillTerminate` — app lifecycle.
- SwiftUI `onAppear`, `onDisappear`, `task` — view lifecycle modifiers.
- `deinit`, `autoreleasepool`, ARC retain/release — ownership plumbing.
- `draw(_ rect:)`, `layoutSubviews`, Auto Layout activation — rendering plumbing.

## 11 Merge / Conflict Policy

Compare every Swift, Objective-C, UI, persistence, and configuration copy using subject scope, condition, threshold, and outcome:

- All four dimensions identical: merge into one rule and retain every location as evidence.
- Any dimension differs: keep separate rules, set bidirectional `conflicting_rule_ids`, set `review.status` to `needs_review`, and state the discrepancy in `open_questions`.
- Never prefer a language, UI technology, or newer-looking file without repository evidence that scopes applicability.
- Source-control markers or structurally ambiguous generated/project files are coverage findings. Do not choose a branch or extract a rule from an unresolved region.

## 12 Evidence Layer Mapping

| Artifact | `layer` value |
|---|---|
| Swift/Objective-C guards, calculations, protocols, delegates, model logic | `code` |
| Embedded queries or repository query text | `sql` |
| Persistent-model validation, uniqueness, delete, or relationship constraints | `db_constraint` |
| Background task registration with stakeholder-visible timing | `batch` |
| Navigation/state-transition declarations and event flow | `workflow` |
| Form validation, enabled/visible decisions, screen guards | `ui` |
| Build/runtime flags or settings that parameterize policy | `config` |
| Repository-local decision tables or declarative rule definitions | `rules_engine` |

## 13 Extraction Checklist

1. Identify module boundaries and both language families from repository evidence.
2. Catalogue protocol conformances, categories, extensions, delegates, and runtime-dispatch uncertainty.
3. Trace guards, pattern matches, property observers, wrappers, and error cases to observable outcomes.
4. Review persistent-model constraints, queries, UI gates, configuration, and scheduled work.
5. Exclude lifecycle, memory, rendering, generated, and project-file plumbing unless it changes policy.
6. Mark client-only enforcement and explicitly record absent service/data enforcement.
7. Apply the four-dimension merge/conflict comparison across all copies.
8. Assign every evidence entry one canonical `layer` value and retain exact file/line/snippet evidence.
