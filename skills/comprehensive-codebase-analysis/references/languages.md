# Language detection router

Detect from extensions, manifests, build files, shebangs, imports, generated-code markers, and embedded-language regions. Report evidence and approximate share. Load every matching family playbook; mixed repositories use multiple.

| Signals | Load |
|---|---|
| `.java`, `.kt`, Maven or Gradle files | `language-jvm.md` |
| `.cs`, `.fs`, solution/project files | `language-dotnet.md` |
| `.py`, Python project/requirements files | `language-python.md` |
| `.js`, `.ts`, JSX/TSX, Node package files | `language-js-ts.md` |
| `.go`, `go.mod`; `.rs`, Cargo files | `language-go-rust.md` |
| `.php`, Composer files; `.rb`, Gem files | `language-php-ruby.md` |
| C/C++ headers/sources and native build files | `language-c-cpp.md` |
| SQL/schema/migration files; COBOL/PL-I sources or copybooks | `language-sql-legacy.md` |

Do not classify minified, generated, vendored, or lock-file content as first-party language share. Detect templating languages and embedded SQL separately. When a language has no dedicated row, apply the closest runtime/paradigm checks and document the limitation rather than ignoring it.
