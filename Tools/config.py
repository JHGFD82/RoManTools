class Config:
    """

    Config class represents a configuration object with three boolean attributes: crumbs, error_skip, and error_report.

    Attributes:
        crumbs (bool): Indicates whether to enable or disable the generation of crumbs.
        error_skip (bool): Indicates whether to skip errors or raise exceptions when encountered.
        error_report (bool): Indicates whether to generate error reports.

    Methods:
        __init__(crumbs: bool = False, error_skip: bool = False, error_report: bool = False)
            Initializes a new instance of the Config class with the specified attributes.

    Example usage:
        # Create a new Config object with default values
        config = Config()

        # Create a new Config object with specific attribute values
        config = Config(crumbs=True, error_skip=False, error_report=True)

    """
    def __init__(self, crumbs: bool = False, error_skip: bool = False, error_report: bool = False):
        self.crumbs = crumbs
        self.error_skip = error_skip
        self.error_report = error_report