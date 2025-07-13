"""
Base romanization strategy abstract class.

This module defines the abstract base class that all romanization strategies must implement.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..syllable import SyllableProcessor, Syllable


class RomanizationStrategy(ABC):
    """
    Abstract base class for romanization-specific syllable processing strategies.
    """
    
    def __init__(self, processor: "SyllableProcessor"):
        """
        Initialize the strategy with a processor reference.
        
        Args:
            processor: The SyllableProcessor instance containing shared data and methods.
        """
        self.processor = processor
    
    @abstractmethod
    def find_final(self, text: str, initial: str, syllable: "Syllable") -> str:
        """
        Find the final part of a syllable for this romanization method.
        
        Args:
            text: The text from which to extract the final.
            initial: The initial part of the syllable.
            syllable: The Syllable instance for accessing helper methods.
            
        Returns:
            The final part of the syllable.
        """
        pass
    
    @abstractmethod
    def find_initial(self, text: str, syllable: "Syllable") -> str:
        """
        Find the initial part of a syllable for this romanization method.
        
        Args:
            text: The text from which to extract the initial.
            syllable: The Syllable instance for accessing helper methods.
            
        Returns:
            The initial part of the syllable, or 'ø' if no initial exists.
        """
        pass
    
    @abstractmethod
    def validate_syllable(self, initial: str, final: str, syllable: "Syllable") -> bool:
        """
        Validate a complete syllable for this romanization method.
        
        Args:
            initial: The initial part of the syllable.
            final: The final part of the syllable.
            syllable: The Syllable instance for accessing helper methods.
            
        Returns:
            True if the syllable is valid, False otherwise.
        """
        pass
    
    def handle_apostrophe_in_initial(self, text: str, index: int) -> str:
        """
        Handle apostrophes found within initial detection for this romanization method.
        Default implementation returns the text up to the apostrophe.
        
        Args:
            text: The text being processed.
            index: The index where the apostrophe was found.
            
        Returns:
            The initial part including apostrophe handling.
        """
        return text[:index]

    
    def handle_dash_in_initial(self, text: str, index: int) -> str:
        """
        Handle dashes found within initial detection for this romanization method.
        Default implementation returns the text up to the dash.
        
        Args:
            text: The text being processed.
            index: The index where the dash was found.
            
        Returns:
            The initial part including dash handling.
        """
        return text[:index]
