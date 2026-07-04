You are writing a pytest acceptance-test suite for a Python project that
will be generated separately. The project's acceptance criteria are
listed below in Gherkin form. You do NOT know the project's class names,
module paths, or internal structure — that's intentional. The project
must expose a `tests/conftest.py` containing a `discover_implementation()`
function that returns a dict mapping behavior names to concrete callables
or fixture factories. Your test suite calls `discover_implementation()`
and uses the returned dict to assert each acceptance criterion holds.

ACCEPTANCE CRITERIA
{criteria_block}

OUTPUT FORMAT
  Emit two files:

  ### File: tests/test_acceptance.py
  ```python
  # The acceptance-test suite. Imports from conftest only via fixtures.
  ```

  ### File: tests/conftest_template.py
  ```python
  # The expected shape of conftest.py the project must provide.
  # Provide explicit comments documenting which behavior keys you
  # require in the discover_implementation() return dict, with a
  # one-line description per key. The project under test will provide
  # its own conftest.py matching this contract.
  ```

Conventions for the suite:

- One pytest function per acceptance criterion.
- Use the criterion's verb as the dict key when looking up the
  implementation (e.g. "create_event", "publish_event").
- Skip rather than fail if `discover_implementation()` doesn't return
  the expected key — that's a structural mismatch, not an assertion
  failure, and we want to count those separately.
- Prefer property-style assertions (output type / fields present /
  invariant holds) over exact-string equality, so two different
  implementations of the same behavior can both pass.
- If a criterion asserts an error is raised, use pytest.raises with the
  most general appropriate exception class.

Emit nothing outside the two fenced code blocks.
