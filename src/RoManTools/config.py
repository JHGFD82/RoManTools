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
