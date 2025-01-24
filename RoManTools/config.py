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

    def print_crumb(self, level: int = 0, stage: str = '', message: str = ''):
        """
        Prints a crumb message based on the configuration settings.

        Args:
            level (int): The level of the crumb message.
            stage (str): The stage of processing.
            message (str): The message to display.

        Example:
            >>> config = Config(crumbs=True)
            >>> config.print_crumb(1, 'Segmentation', 'Processing text')
            # Segmentation: Processing text
        """
        if self.crumbs:
            prefix = '#' * level + ' ' if level > 0 else ''
            stage = f'{stage}: ' if stage else ''
            print(f'{prefix}{stage}{message}')
