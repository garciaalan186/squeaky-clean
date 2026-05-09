# Example — Todo API

The smallest end-to-end Squeaky Clean example. Generates a Flask-based Todo REST API with port/adapter discipline preserved across Domain → Application → Infrastructure → Interface layers.

## Run

```bash
export ANTHROPIC_API_KEY="<your-key>"  # secret-scan: allow
squeaky generate --problem-file examples/todo_api/todo_problem.json --infra=auto
```

Or via the module entry point if you haven't installed the CLI:

```bash
python -m src.interface.cli --problem-file examples/todo_api/todo_problem.json --infra=auto
```

## What you'll see

- **Architecture**: 3 bounded contexts (Tasks / TaskRepository / TaskHandlers) span 3-4 modules across the four Clean Architecture layers.
- **Generated**: ~10 classes, including a `Todo` Entity, a `Title` ValueObject, a `TaskRepository` Port + concrete `LocalDiskTaskRepository` Adapter, and a `FlaskTaskHandler`.
- **Composition root**: `src/main.py` wires everything and starts the Flask app on `127.0.0.1:8000`.
- **Cost**: ~$0.05–$0.10 per run.

## Acceptance criteria covered

The generated tests cover:

- creating a Todo with a non-empty title
- rejecting an empty title via VO invariant
- toggling `is_complete` via `mark_complete`
- retrieving a Todo by id (and erroring on unknown ids)
- listing all Todos

## Verifying the output

After generation:

```bash
cd <run_output_dir>
pip install -r requirements.txt --target .test-deps/
PYTHONPATH=.:.test-deps python -m pytest tests/ -q
```
