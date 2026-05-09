"""Tests for ParseTestArchitecture."""

import pytest

from squeaky_clean.application.dtos.test_architecture_parse_error import (
    TestArchitectureParseError,
)
from squeaky_clean.application.use_cases.parse_test_architecture import ParseTestArchitecture

_SAMPLE = """GHERKIN
---
Feature: Calculator
  Scenario: Addition
    Given operands 2 and 3
    When add is called
    Then result is 5
  Scenario: Subtraction
    Given operands 5 and 2
    When subtract is called
    Then result is 3
---

TEST_SKELETONS
---
FILE tests/test_calculator.py
CLASS Calculator
```python
import pytest


def test_add() -> None:
    pytest.fail("not implemented")


def test_subtract() -> None:
    pytest.fail("not implemented")
```

FILE tests/test_operand.py
CLASS Operand
```python
import pytest


def test_value() -> None:
    pytest.fail("not implemented")
```
---
"""


def test_parse_extracts_scenarios_and_skeletons() -> None:
    ta = ParseTestArchitecture().parse(_SAMPLE)
    assert len(ta.gherkin_scenarios) == 2
    assert ta.gherkin_scenarios[0].startswith("Feature: Calculator")
    assert "Scenario: Addition" in ta.gherkin_scenarios[0]
    assert "Scenario: Subtraction" in ta.gherkin_scenarios[1]
    assert len(ta.test_skeletons) == 2
    by_name = {s.class_name: s for s in ta.test_skeletons}
    assert by_name["Calculator"].file_path == "tests/test_calculator.py"
    assert "def test_add" in by_name["Calculator"].code
    assert "def test_subtract" in by_name["Calculator"].code
    assert by_name["Operand"].file_path == "tests/test_operand.py"
    assert "def test_value" in by_name["Operand"].code


def test_parse_tolerant_of_extra_whitespace() -> None:
    raw = "\n\n  " + _SAMPLE + "\n\n"
    ta = ParseTestArchitecture().parse(raw)
    assert len(ta.test_skeletons) == 2


def test_parse_malformed_raises() -> None:
    with pytest.raises(TestArchitectureParseError):
        ParseTestArchitecture().parse("not a valid response at all")


_JS_SAMPLE = """GHERKIN
---
Feature: Calculator
  Scenario: Addition
    Given operands 2 and 3
    When add is called
    Then result is 5
---

TEST_SKELETONS
---
FILE tests/calculator.test.js
CLASS Calculator
```javascript
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { Calculator } from '../src/calculator.js';

test('add two operands', () => {
  const calculator = new Calculator();
  const result = calculator.add(2, 3);
  assert.strictEqual(result, 5);
});
```
---
"""


def test_parse_javascript_skeletons() -> None:
    ta = ParseTestArchitecture().parse(_JS_SAMPLE)
    assert len(ta.test_skeletons) == 1
    sk = ta.test_skeletons[0]
    assert sk.class_name == "Calculator"
    assert sk.file_path == "tests/calculator.test.js"
    assert "node:test" in sk.code
    assert "../src/calculator.js" in sk.code
