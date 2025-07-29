"""
Pokemon name normalization and fuzzing utilities.

This module handles the normalization of Pokemon names to match the expected
data format, including handling special cases, forms, and variations.
"""

from typing import Optional


class PokemonNameNormalizer:
    """
    Handles normalization of Pokemon names for data lookup.
    
    This class contains logic to handle various Pokemon name variations,
    special forms, and edge cases to ensure proper data retrieval.
    """
    
    @staticmethod
    def normalize_name(name: str) -> str:
        """
        Normalize a Pokemon name for data lookup.
        
        Args:
            name: The input Pokemon name
            
        Returns:
            Normalized name that should match the data format
        """
        # Handle spaces and hyphens
        if ' ' in name:
            name = name.replace(' ', '-')

        

        # Handle special cases
        name = PokemonNameNormalizer._handle_special_cases(name)
        
        # Convert to lowercase at the end
        return name.lower()
    
    @staticmethod
    def _handle_special_cases(name: str) -> str:
        """
        Handle special Pokemon name cases and forms.
        
        Args:
            name: The name to process
            
        Returns:
            Processed name
        """
        name_lower = name.lower()
        if 'urshifu' in name_lower:
            if 'single' in name_lower:
                return 'urshifu-single-strike'
            elif 'rapid' in name_lower:
                return 'urshifu-rapid-strike'
            else:
                return 'urshifu-single-strike'
        
        if 'zacian' in name_lower:
            if 'crowned' in name_lower:
                return 'zacian-crowned'
            else:
                return 'zacian'
        if 'cramorant' in name_lower:
            if 'gulping' in name_lower:
                return 'cramorant-gulping'
            elif 'gorging' in name_lower:
                return 'cramorant-gorging'
            else:
                return 'cramorant'

        if 'zamazenta' in name_lower:
            if 'crowned' in name_lower:
                return 'zamazenta-crowned'
            else:
                return 'zamazenta'
        
        if 'necrozma' in name_lower:
            if 'dawn' in name_lower:
                return 'necrozma-dawn'
            elif 'dusk' in name_lower:
                return 'necrozma-dusk'
            elif 'ultra' in name_lower:
                return 'necrozma-ultra'
            else:
                return 'necrozma'
        if 'sawsbuck' in name_lower:
            return 'sawsbuck'
        if 'vivillon' in name_lower:
            return 'vivillon'
        #Oricorio forms
        if 'oricorio' in name_lower:
            if 'baile' in name_lower:
                return 'oricorio-baile'
            elif 'pa' in name_lower:
                return 'oricorio-pau'
            elif 'sensu' in name_lower:
                return 'oricorio-sensu'
            elif 'pom' in name_lower:
                return 'oricorio-pom-pom'
            else:
                return 'oricorio-baile'
        
        if 'porygon-z' in name_lower:
            return 'porygon-z'
        
        if 'porygon-z' in name_lower:
            return 'porygon-z'
        # Florges forms
        if 'florges' in name_lower:
            return 'florges'
        
        # Maushold forms
        if 'maushold' in name_lower:
            return 'maushold'
        
        # Pikachu forms
        if 'pikachu' in name_lower:
            return 'pikachu'
        
        if 'alcremie' in name_lower:
            if 'gmax' in name_lower:
                return 'alcremie-gmax'
            else:
                return 'alcremie'
        if 'polteageist' in name_lower:
            return 'polteageist'

        if 'poltchageist' in name_lower:
            return 'poltchageist'
        
        if 'sinistcha' in name_lower:
            return 'sinistcha'  
        if 'meowstic' in name_lower:
            if 'f' in name_lower:
                return 'meowstic-female'
            else:
                return 'meowstic-male'

        if 'meloetta' in name_lower:
            if 'aria' in name_lower:
                return 'meloetta-aria'
            elif 'pirouette' in name_lower:
                return 'meloetta-pirouette'
            else:
                return 'meloetta-aria'
        
        if 'sinistea' in name_lower:
            return 'sinistea'
        
        if 'oinkologne' in name_lower:
            if 'f' in name_lower:
                return 'oinkologne-female'
            elif 'm' in name_lower:
                return 'oinkologne-male'
            else:
                return 'oinkologne-female'
        
        # Ogerpon forms
        if 'ogerpon' in name_lower:
            if 'cornerstone' in name_lower:
                return 'ogerpon-cornerstone-mask'
            elif 'wellspring' in name_lower:
                return 'ogerpon-wellspring-mask'
            elif 'hearthflame' in name_lower:
                return 'ogerpon-hearthflame-mask'
            else:
                return 'ogerpon'
        
        # Squawkabilly forms
        if 'squawkabilly' in name_lower:
            if 'blue' in name_lower:
                return 'squawkabilly-blue-plumage'
            elif 'red' in name_lower:
                return 'squawkabilly-red-plumage'
            elif 'white' in name_lower:
                return 'squawkabilly-white-plumage'
            else:
                return 'squawkabilly-white-plumage'
        if 'basculegion' in name_lower:
            if 'f' in name_lower:
                return 'basculegion-female'
            elif 'm' in name_lower:
                return 'basculegion-male'
            else:
                return 'basculegion-female'
        if 'gastrodon' in name_lower:
            return 'gastrodon'
        # Tauros Paldea forms
        if 'tauros' in name_lower and 'paldea' in name_lower:
            if 'blaze' in name_lower:
                return 'tauros-paldea-blaze-breed'
            elif 'aqua' in name_lower:
                return 'tauros-paldea-aqua-breed'
            elif 'combat' in name_lower:
                return 'tauros-paldea-combat-breed'
            else:
                return 'tauros-paldea-blaze-breed'
        
        # Arceus forms
        if 'arceus' in name_lower:
            return 'arceus'
        
        # Indeedee forms
        if 'indeedee' in name_lower:
            if 'f' in name_lower:
                return 'indeedee-female'
            elif 'm' in name_lower:
                return 'indeedee-male'
            else:
                return 'indeedee-female'
        
        return name 