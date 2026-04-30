# Changelog

All notable changes to Squeaky Clean will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Architectural Complexity Score (ACS)** — composite metric across Structural / Codegen / Constraint dimensions. Per-run `EvalMetrics.acs_*` fields + SUMMARY.md section. See `BENCHMARK_METHODOLOGY.md`.
- Examples directory: `todo_api/`, `event_pipeline/`, `twitter_clone/`.
- Public-facing docs: `overview.md`, `architecture.md`, `notation.md`, `writing_a_problem_spec.md`, `extending.md`, `roadmap.md`.
- `LICENSE` (Apache 2.0), `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`.

### Changed

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
