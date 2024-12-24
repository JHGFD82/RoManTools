"""
Configuration settings for romanized Mandarin text processing.

This module provides the `Config` class, which is used to manage various configuration options for text processing,
including:
- Including intermediate outputs (crumbs) during processing.
- Skipping error reporting on invalid characters.
- Reporting errors encountered during processing.

Classes:
    Config: Manages configuration settings for text processing.
"""


class Config:
    """
    Configuration settings for processing text. Options are ancillary to the main processing functions except
    error_skip which is essential for methods where non-romanized Mandarin characters are maintained in output.
    """

    def __init__(self, crumbs: bool = False, error_skip: bool = False, error_report: bool = False):
        """
        Initializes instances of the Config class.

        Args:
            crumbs (bool): If True, includes intermediate outputs (crumbs) during processing.
            error_skip (bool): If True, skips error reporting on invalid characters.
            error_report (bool): If True, reports errors encountered during processing.
        """

        self.crumbs = crumbs
        self.error_skip = error_skip
        self.error_report = error_report
