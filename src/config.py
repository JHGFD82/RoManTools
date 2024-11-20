class Config:
    """
    Configuration settings for processing text.

    Attributes:
        crumbs (bool): If True, includes intermediate outputs (crumbs) during processing.
        error_skip (bool): If True, skips over text with errors during processing.
        error_report (bool): If True, reports errors encountered during processing.
    """
    def __init__(self, crumbs: bool = False, error_skip: bool = False, error_report: bool = False):
        self.crumbs = crumbs
        self.error_skip = error_skip
        self.error_report = error_report
