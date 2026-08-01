"""TechSpecResolution: explicit outcome union for TechSpec resolution (R6.8).

Replaces the swallow-and-degrade ``TechSpec | None`` house style inside the
resolver chain. The success variant is ``TechSpec`` itself — a ``Resolved``
wrapper would add a module and an unwrap step without carrying any extra
information (``isinstance(x, TechSpec)`` already narrows the union).

``None`` remains legal ONLY where it means "source not applicable / clean
cache miss", never "an error happened" — errors travel as ``FetchFailed`` /
``Poisoned`` with a reason.
"""

from squeaky_clean.domain.value_objects.tech_spec import TechSpec
from squeaky_clean.domain.value_objects.tech_spec_fetch_failed import TechSpecFetchFailed
from squeaky_clean.domain.value_objects.tech_spec_poisoned import TechSpecPoisoned

TechSpecResolution = TechSpec | TechSpecFetchFailed | TechSpecPoisoned
