"""
Pinyin romanization strategy implementation.

This module contains the strategy for processing Pinyin syllables.
"""

from typing import TYPE_CHECKING
from .base import RomanizationStrategy
from ..constants import vowels

if TYPE_CHECKING:
    from ..syllable import Syllable


class PinyinStrategy(RomanizationStrategy):
    """
    Strategy for processing Pinyin syllables.
    
    Pinyin characteristics:
    - Standard vowel/consonant case handling
    - No apostrophes in initials
    - Clear syllable boundaries
    """
    
    def find_final(self, text: str, initial: str, syllable: "Syllable") -> str:
        """
        Handles the final part extraction for Pinyin method.
        
        Args:
            text: The text from which to extract the final.
            initial: The initial part of the syllable.
            syllable: The Syllable instance for accessing helper methods.
            
        Returns:
            The final part of the syllable.
        """
        for i, c in enumerate(text):
            # Handle cases where the final starts with a vowel or consonant
            if c in vowels:
                final = syllable.handle_vowel_case(text, i, initial)
                if final is not None:
                    return final
            else:
                return syllable.handle_consonant_case(text, i, initial)
        return text
    
    def find_initial(self, text: str, syllable: "Syllable") -> str:
        """
        Handles the initial part extraction for Pinyin method.
        
        Args:
            text: The text from which to extract the initial.
            syllable: The Syllable instance for accessing helper methods.
            
        Returns:
            The initial part of the syllable, or 'ø' if no initial exists.
        """
        # Use the standard initial detection logic from syllable
        # This delegates to the existing _find_initial logic but through strategy
        from ..constants import vowels, apostrophes, dashes
        
        for i, c in enumerate(text):
            if c in vowels:
                if i == 0:  # If a vowel is found at the beginning of the syllable, return 'ø' to indicate no initial
                    return 'ø'
                # Otherwise, all text up to this point is the initial
                if (initial := text[:i]) not in self.processor.init_list:  # Check if the initial is valid
                    syllable.errors.append(f"invalid initial: '{initial}'")
                    return text[:i]  # Return text up to this point if not valid
                return initial
            if c in apostrophes:  # Handle apostrophes using strategy
                return self.handle_apostrophe_in_initial(text, i)
            if c in dashes:  # Handle dashes using strategy  
                return self.handle_dash_in_initial(text, i)

        return text
    
    def validate_syllable(self, initial: str, final: str, syllable: "Syllable") -> bool:
        """
        Validate a complete syllable for Pinyin method.
        
        Args:
            initial: The initial part of the syllable.
            final: The final part of the syllable.
            syllable: The Syllable instance for accessing helper methods.
            
        Returns:
            True if the syllable is valid, False otherwise.
        """
        # Use the processor's validation method
        if initial == '':
            return self.processor.validate_final_using_array('ø', final)
        return self.processor.validate_final_using_array(initial, final)
