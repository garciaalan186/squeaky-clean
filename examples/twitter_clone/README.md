# Example — Twitter Clone

Demonstrates Squeaky Clean's **richer ProblemSpec** schema (`domain_conventions` / `query_semantics` / `data_classification`) on a multi-context social-network problem.

## What's special about this spec

- `domain_conventions: ["timeline_includes_self", ...]` — these tags map to canonical INVARIANTs that the architect MUST surface verbatim. Without `timeline_includes_self`, an architect could legitimately produce a "tweets-by-followees only" timeline that excludes the user's own posts (real Twitter semantics include them).
- `query_semantics: [{"use_case": "GetTimelineUseCase", "shape": "self_plus_followees"}]` — declares the query shape so the architect picks a `find_by_authors([self_id, ...followee_ids])` repository method, not a `find_by_authors([followee_ids only])`.
- `data_classification: [{"field_ref": "User.password_hash", "sensitivity": "credential"}, ...]` — surfaces fields that must NOT be exposed via getters returning the raw value. The SecurityArchitect grounds its concerns in these declarations.

## Run

```bash
python -m src.interface.cli --problem-file examples/twitter_clone/twitter_problem.json --infra=auto
```

## What you'll see

- 6–9 modules across Auth / Posts / Timeline contexts.
- 22+ classes including User, Session, Tweet, FollowRelation, etc.
- Generated INVARIANTS mention "a user's timeline must include the user's own posts" verbatim (sourced from the `timeline_includes_self` convention).
- Cost: ~$0.40–$0.80 per run.

## Acceptance criteria covered

The spec includes the criterion `Given user 'alice' has not followed anyone, When get_timeline is called for alice, Then the result includes alice's own tweets` — this is the orchestrator-level UX policy that Squeaky Clean enforces via the `timeline_includes_self` convention rather than re-deriving from problem-domain inference.

## See also

- `examples/event_pipeline/` — for distributed multi-service architectures.
- `examples/todo_api/` — for the smallest end-to-end example.
- `docs/notation.md` — §Notation grammar reference (incl. `domain_conventions`, `query_semantics`).
