"""ManifestWriteError: raised when a manifest generator cannot write (R6.8)."""


class ManifestWriteError(RuntimeError):
    """A manifest generator failed to write its output file.

    Replaces the old return-None-on-OSError degrade: ``None`` from a
    generator now ONLY means "not applicable for this language/spec set",
    while write failures raise this error carrying the reason. Call sites
    (``ManifestEmitter``) catch ``(OSError, ManifestWriteError)`` and log
    the failure event, keeping manifest emission best-effort but loud.
    """
