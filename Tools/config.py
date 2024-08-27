class Config:
    """
    Configuration settings for processing text.

    Attributes:
        crumbs (bool): If True, includes intermediate outputs (crumbs) during processing.
        error_skip (bool): If True, skips over text with errors during processing.
        error_report (bool): If True, reports errors encountered during processing.
    """
    def __init__(self, crumbs: bool = False, error_skip: bool = False, error_report: bool = False):
        """
        Initializes the Config object with the specified options.

        Args:
            crumbs (bool, optional): Whether to include breadcrumbs during processing. Defaults to False.
            error_skip (bool, optional): Whether to skip over errors during processing. Defaults to False.
            error_report (bool, optional): Whether to report errors during processing. Defaults to False.
        """
        self.crumbs = crumbs
        self.error_skip = error_skip
        self.error_report = error_report
