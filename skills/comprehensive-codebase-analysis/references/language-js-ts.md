# JavaScript and TypeScript playbook

Inspect package and lock files, workspace configuration, runtime/module type, compiler/bundler settings, scripts, framework routes, server/client boundaries, workers, and tests. Separate first-party source from generated bundles and vendored assets.

Record exported function/class/type signatures, overloads, generics, async contracts, event names, message shapes, module side effects, and environment/configuration keys. Identify runtime validation gaps where static types do not constrain external input.

Trace HTTP, RPC, GraphQL, CLI, browser, and message-consumer entry points. Check authentication/authorization middleware order, request-forgery defenses, DOM/output encoding, dynamic code execution, prototype/property injection, command/query construction, dependency scripts, secret exposure, and rejected-promise handling.

Count decisions from branches, loops, catches, conditional expressions, optional branch-like constructs, and short-circuit conditions using a documented convention. Treat transpiled/minified code as excluded unless it is the only source, then label confidence and coverage limits.
