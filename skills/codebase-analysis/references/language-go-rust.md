# Go and Rust playbook

## Go

Inspect modules, workspaces, build tags, generated markers, packages, `main` functions, handlers, goroutines, channels, interfaces, tests, and embedded assets. Record exported signatures, error contracts, context propagation, interface satisfaction, and configuration access. Check unchecked errors, nil/interface traps, races, unbounded goroutines, channel closure, path/query construction, authorization middleware, and request limits.

## Rust

Inspect Cargo workspace/manifests/locks, features, targets, build scripts, modules, traits, macros, unsafe blocks, async runtimes, handlers, and tests. Record public signatures, lifetimes where contract-relevant, trait bounds, error enums, feature gates, and environment/configuration access. Check unsafe invariants, panic paths, unchecked indexing, blocking in async tasks, authorization layers, deserialization limits, secret handling, and process/file operations.

For both, estimate complexity from explicit branches, loops, match/select arms beyond the first, catches-equivalents, and boolean decisions; document conventions. Treat generated code and macro expansion as separate coverage concerns. Map goroutine/channel or task/channel communication as async dependencies.
