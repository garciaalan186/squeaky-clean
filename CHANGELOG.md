# Changelog

All notable changes to Squeaky Clean will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Complete pattern ICP catalog** — all 34 GoF + DDD/Clean patterns now have a dedicated agent spec in every supported language (Python, TypeScript, JavaScript, Java, Go, Rust): 5 creational, 7 structural, 11 behavioral, 11 ddd_clean. 177 new specs under `squeaky_clean/interface/agent_specs/icps/<lang>/<category>/`. Each is language-idiomatic — Go specs are written around interfaces, structs, structural typing and `error` returns rather than inheritance and exceptions.
- **Pattern-rich benchmark problems P6–P9** — four Python problems in the built-in registry (`squeaky_clean/interface/cli/problem_resolver.py`), selectable by id via `--problem` / `--problems`: `P6 stock_monitor` (Observer — subscribers are notified on price update, unsubscribed investors are not), `P7 order_lifecycle` (State — Pending → Paid → Shipped → Delivered, each state permitting only its one valid forward transition), `P8 text_editor` (Command + Memento — insert/delete commands snapshot the buffer for single-level undo), `P9 drawing_canvas` (Composite + Visitor — nested shape groups traversed by an area visitor). Specs at `eval/problems/p6_stock_monitor.py`, `p7_order_lifecycle.py`, `p8_text_editor.py`, `p9_drawing_canvas.py`. Each demands a structurally distinct pattern the P0–P5 suite never exercises, measuring whether the architect *chooses* the right pattern end-to-end.
- **Golden-Squib routing fixtures** — `eval/squib_fixtures/` holds 28 hand-authored minimal `.squib` files plus `manifest.json`, one per catalog pattern that no benchmark `ProblemSpec` already requires. `tests/eval/test_golden_squib_routing.py` parses each fixture through the real `ParseArchitectureNotation` → `AssignPatterns` path used by the pipeline, across all six languages, and asserts the focal class routes to that pattern's dedicated ICP and that the routed spec file exists on disk. Deterministic — no LLM calls.
- `tests/application/use_cases/test_pattern_icp_resolution.py` — guardrail asserting on disk that every pattern × language pair resolves to an ICP spec file that exists, and that no catalog pattern degrades to the SimpleClass escape hatch.
- **`ProblemSpec` decomposed into two cohesive views** — `.behavior` returns a `BehaviorSpec` (`acceptance_criteria`, `produces_contracts`, `consumes_contracts`, `data_classification`, `expected_outcomes`), the irreducible acceptance oracle the Squib IR cannot carry and the input the OracleCompiler compiles tests from; `.structural_hints` returns a `StructuralHints` (`required_patterns`, `required_bounded_contexts`, `expected_module_count`, `expected_class_count`), the half a Squib already encodes. The flat fields remain the construction surface, so authoring a `ProblemSpec` is unchanged. New DTOs at `squeaky_clean/application/dtos/behavior_spec.py` and `structural_hints.py`.
- **`derive_structural_hints_from_squib(architecture)`** (`squeaky_clean/application/use_cases/derive_structural_hints.py`) — deterministic projection of an `ArchitectureSpec` onto `StructuralHints`, no LLM call. Generalizes the recovery path's `ProblemSpecSynthesizer`: on the squib-first and architecture-recovery paths the structural half is derived from the IR rather than authored, leaving only the behavioral half to supply.
- **Architectural Complexity Score (ACS)** — composite metric across Structural / Codegen / Constraint dimensions. Per-run `EvalMetrics.acs_*` fields + SUMMARY.md section. See `BENCHMARK_METHODOLOGY.md`.
- Examples directory: `todo_api/`, `event_pipeline/`, `twitter_clone/`.
- Public-facing docs: `overview.md`, `architecture.md`, `notation.md`, `writing_a_problem_spec.md`, `extending.md`, `roadmap.md`.
- `LICENSE` (Apache 2.0), `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`.

### Changed

- **Agents renamed for the transformation they perform** — the pipeline reads as a compiler: front-ends compile a requirement into the Squib IR, verifier passes check it, a backend lowers it to code. `PrincipalArchitect` → **`RequirementCompiler`** (`Requirement ⟶ Squib`; wired in `design_architecture.py`), `TestArchitect` → **`OracleCompiler`** (all seven spec variants — shared plus Python, TypeScript, JavaScript, Java, Go, Rust — compiling a `BehaviorSpec` + Squib signatures into executable test files; wired in `generate_test_architecture.py`), `SecurityArchitect` → **`ThreatAnalyzer`** (wired in `review_security.py`), `DomainArchitect` / `ApplicationArchitect` / `InfrastructureArchitect` / `InterfaceArchitect` → **`<Layer>Verifier`**, `EngineeringManager` → **`ModuleLowerer`**. Spec files now at `squeaky_clean/interface/agent_specs/architects/{RequirementCompiler,ThreatAnalyzer,<Layer>Verifier}.md`, `architects/{_shared,<lang>}/OracleCompiler.md` and `managers/ModuleLowerer.md`; the per-agent eval scorers label their scores `RequirementCompiler` / `OracleCompiler`. Unchanged: the `ModelTier` members (Architect / Manager / ICP / Fixer — a separate routing axis), `InfrastructureChoiceArchitect`, the ICP agent family, and the deterministic `AssignPatterns` / `IntegrateModule` / `ValidateArchitecture` stages.
- `MapPatternToICP` now resolves every recognized `PatternName` to `<lang>/<category>/<Pattern>ICP`. `Facade` → `structural/FacadeICP`, `Observer` → `behavioral/ObserverICP` and `AbstractFactory` → `creational/AbstractFactoryICP` (all three were `ddd_clean/SimpleClassICP`); `Repository` → `ddd_clean/RepositoryICP` in the domain layer and under `--infra=manual` (was `SimpleClassICP`); `Gateway` → `ddd_clean/GatewayICP` in Go, Rust and JavaScript as well as Python/TypeScript/Java. `SimpleClassICP` is now strictly the escape hatch for an unrecognized pattern name, never a stand-in for a catalog pattern. Unchanged: under `--infra=auto`, Infrastructure/Interface-layer `Repository`/`Gateway`/`Adapter` classes still route first to the concrete Tier C adapter ICPs.
- Agent spec library version `0.1.0` → `0.2.0` (`squeaky_clean/interface/agent_specs/VERSION`).
- All hardcoded `/home/alan/git/clean-agents/...` paths in `src/` replaced with checkout-relative anchors (`Path(__file__).resolve().parents[N]`). Framework now runs from any clone location.
- `CLAUDE.md` content moved to `AGENTS.md` in the parent directory; framework no longer references the AI-assistant-specific filename.

## [0.1.0] — Pre-launch (Milestone K complete)

### Added

- 60 Tier C ICPs across 15 infrastructure categories × 4 languages (Python, Java, Go, Rust). JS/TS Tier C parity landed in K8.
- Polymorphic `ImplementedClassParser` (Python / Java / Go / Rust / JS-TS).
- Polymorphic `LanguageDependencyInstaller` (pip / mvn / cargo / go mod / npm).
- `validate_http_conventions` validator with retry-on-violation.
- Per-module criterion filtering for TestArchitect.
- Java/Go/Rust security ICPs (5 categories × 3 languages, replacing Python-syntax stubs).
- Registry-driven `LanguageAdapterSelector` with unit-tested coverage gate.
- 12-run cross-language e2e verification at $3.32 total spend.

### Fixed

- `ImplementedClassParseError: code body does not declare class X` for Go / Rust.
- `Could not find metadata java.nio.file/maven-metadata.xml` (stdlib TechSpecs no longer emitted as Maven coordinates).
- `ModuleNotFoundError: confluent_kafka` in generated Python tests (dependency installer runs before TestRunner).
- TestArchitect emitting wrong dotted import paths (now uses `ClassPaths:` block).

### Status

Framework is **launch-ready** per the Milestone K exit criterion: 1508 tests passing, mypy strict clean across 661 source files, all 6 supported languages reach integration phase end-to-end without crashes, build verification (`mvn compile` / `pytest`) green for at least Python.
