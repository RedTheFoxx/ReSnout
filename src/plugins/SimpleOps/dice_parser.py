import re
import random
from typing import List, Tuple


class DiceParser:
    """Parse dice notation strings and roll dice"""

    DICE_PATTERN = re.compile(r"(\d*)d(\d+)")
    NUMBER_PATTERN = re.compile(r"[+-]?\d+")

    @classmethod
    def parse(cls, dice_str: str) -> Tuple[List[Tuple[int, int]], List[int]]:
        """Parse dice notation string into dice groups and modifiers"""
        dice_groups = []
        modifiers = []

        # Find all dice groups
        for dice_match in cls.DICE_PATTERN.finditer(dice_str):
            count = int(dice_match.group(1)) if dice_match.group(1) else 1
            faces = int(dice_match.group(2))
            dice_groups.append((count, faces))

        # Find all modifiers
        # Create a set of positions that are part of dice notation
        dice_positions = set()
        for dice_match in cls.DICE_PATTERN.finditer(dice_str):
            dice_positions.update(range(dice_match.start(), dice_match.end()))

        # Find all numbers and only add them as modifiers if they're not in dice positions
        for mod_match in cls.NUMBER_PATTERN.finditer(dice_str):
            if not any(
                pos in dice_positions
                for pos in range(mod_match.start(), mod_match.end())
            ):
                modifiers.append(int(mod_match.group()))

        return dice_groups, modifiers

    @classmethod
    def roll(cls, dice_groups: List[Tuple[int, int]]) -> List[List[int]]:
        """Roll dice for each dice group"""
        results = []
        for count, faces in dice_groups:
            rolls = [random.randint(1, faces) for _ in range(count)]
            results.append(rolls)
        return results

    @classmethod
    def calculate_total(
        cls, dice_results: List[List[int]], modifiers: List[int]
    ) -> int:
        """Calculate total from dice rolls and modifiers"""
        total = sum(sum(group) for group in dice_results)
        total += sum(modifiers)
        return total
