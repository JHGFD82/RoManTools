"""
Strategy factory for creating appropriate romanization strategies.

This module contains the factory class responsible for creating the correct
strategy instance based on the romanization method identifier.
"""

from typing import TYPE_CHECKING, Dict, Type
from .base import RomanizationStrategy
from .pinyin import PinyinStrategy
from .wade_giles import WadeGilesStrategy
from ..constants import method_shorthand_to_full

if TYPE_CHECKING:
    from ..syllable import SyllableProcessor


class RomanizationStrategyFactory:
    """
    Factory for creating appropriate romanization strategies.
    
    This factory encapsulates the logic for strategy selection and instantiation,
    making it easy to add new romanization methods without modifying existing code.
    """
    
    @staticmethod
    def create_strategy(method: str, processor: "SyllableProcessor") -> RomanizationStrategy:
        """
        Create the appropriate strategy for the given romanization method.
        
        Args:
            method: The romanization method identifier ('py', 'wg', etc.).
            processor: The SyllableProcessor instance.
            
        Returns:
            The appropriate strategy instance.
            
        Raises:
            ValueError: If the method is not supported.
        """
        strategies: Dict[str, Type[RomanizationStrategy]] = {
            'py': PinyinStrategy,
            'wg': WadeGilesStrategy,
        }
        
        strategy_class = strategies.get(method)
        if strategy_class is None:
            available_methods = ', '.join(method_shorthand_to_full.keys())
            raise ValueError(f"Unsupported romanization method: '{method}'. Available methods: {available_methods}")
            
        return strategy_class(processor)
    
    @staticmethod
    def get_available_methods() -> list[str]:
        """
        Get a list of all available romanization methods.
        
        Returns:
            List of available method identifiers.
        """
        return list(method_shorthand_to_full.keys())
    
    @staticmethod
    def register_strategy(method: str, strategy_class: Type[RomanizationStrategy]) -> None:
        """
        Register a new strategy class for a romanization method.
        
        This method allows for dynamic registration of new strategies without
        modifying the factory code directly.
        
        Args:
            method: The romanization method identifier.
            strategy_class: The strategy class to register.
            
        Raises:
            ValueError: If the method is already registered.
        """
        # This would require refactoring to use instance variables instead of 
        # a static dictionary, but provides a blueprint for future extensibility
        raise NotImplementedError("Dynamic strategy registration not yet implemented")
