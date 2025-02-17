import random

class Dice:
    """A class representing a six-sided die with rolling functionality and ASCII representation."""
    
    # ASCII representation of dice faces
    ASCII_FACES = {
        1: [
            "+-------+",
            "|       |",
            "|   •   |",
            "|       |",
            "+-------+"
        ],
        2: [
            "+-------+",
            "| •     |",
            "|       |",
            "|     • |",
            "+-------+"
        ],
        3: [
            "+-------+",
            "| •     |",
            "|   •   |",
            "|     • |",
            "+-------+"
        ],
        4: [
            "+-------+",
            "| •   • |",
            "|       |",
            "| •   • |",
            "+-------+"
        ],
        5: [
            "+-------+",
            "| •   • |",
            "|   •   |",
            "| •   • |",
            "+-------+"
        ],
        6: [
            "+-------+",
            "| •   • |",
            "| •   • |",
            "| •   • |",
            "+-------+"
        ]
    }
    
    def __init__(self):
        """Initialize the die with a default value of 1."""
        self.value = 1
    
    def roll(self):
        """Roll the die and return the result.
        
        Returns:
            int: A random number between 1 and 6.
        """
        self.value = random.randint(1, 6)
        return self.value
    
    def show(self):
        """Return the ASCII representation of the current die face.
        
        Returns:
            str: Multi-line ASCII art representation of the die.
        """
        return '\n'.join(self.ASCII_FACES[self.value])
    
    def __str__(self):
        """String representation of the die.
        
        Returns:
            str: The current value of the die.
        """
        return str(self.value)