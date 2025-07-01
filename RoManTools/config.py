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

import logging


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
        self.logger = logging.getLogger(__name__)
        if not logging.getLogger().hasHandlers():
            logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    def print_crumb(self, level: int = 0, stage: str = '', message: str = '', footer: bool = False):
        """
        Prints a crumb message based on the configuration settings using logging.

        Args:
            level (int): The number of '#' symbols to prefix the crumb (0 for none).
            stage (str): The stage or action of processing (e.g., 'Segmentation', 'Converted text').
            message (str): The main message or detail to display after the stage.
            footer (bool): If True, adds a '---' line as a crumb footer.

        Example:
            >>> config = Config(crumbs=True)
            >>> config.print_crumb(1, 'Segmentation', 'Processing text')
            # Segmentation: Processing text
            >>> config.print_crumb(2, 'Cached', '"foo" -> "bar"')
            ## Cached: "foo" -> "bar"
            >>> config.print_crumb(footer=True)
            ---
        """
        if self.crumbs:
            if message:
                prefix = '#' * level + ' ' if level > 0 else ''
                stage_str = f'{stage}: ' if stage else ''
                self.logger.info(f'{prefix}{stage_str}{message}')
            if footer:
                self.logger.info('---')
