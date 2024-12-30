"""Module related to the word management of the Cemantix game plugin. Handles the word list and the word2vec model."""

from gensim.models import KeyedVectors
from pathlib import Path
import random

class GameManager:
    def __init__(self):
        self.model = None
        self.dictionary = set()
        self.mystery_words = []
        self.current_mystery_word = None
        
        try:
            # Load word vectors
            model_path = Path(__file__).parent / "data/frWac_non_lem_no_postag_no_phrase_500_skip_cut100.bin"
            if not model_path.exists():
                raise FileNotFoundError(f"Model file not found at {model_path}")
                
            self.model = KeyedVectors.load_word2vec_format(model_path, binary=True)
            
            # Load dictionary words
            dict_path = Path(__file__).parent / "data/dictionnary.txt"
            if not dict_path.exists():
                raise FileNotFoundError(f"Dictionary file not found at {dict_path}")
                
            with open(dict_path, "r", encoding="utf-8") as f:
                self.dictionary = set(line.strip() for line in f)
                
            # Load mystery words
            mystery_path = Path(__file__).parent / "data/mystery.txt"
            if not mystery_path.exists():
                raise FileNotFoundError(f"Mystery words file not found at {mystery_path}")
                
            with open(mystery_path, "r", encoding="utf-8") as f:
                self.mystery_words = [line.strip() for line in f]
                
        except Exception as e:
            raise
        
    def start_new_game(self):
        """Select a new mystery word for the game"""
        self.current_mystery_word = random.choice(self.mystery_words)
        print(self.current_mystery_word)
        return self.current_mystery_word
        
    def is_word_valid(self, word):
        """Check if a word is in the dictionary"""
        return word in self.dictionary
        
    def calculate_similarity(self, word):
        """
        Calculate semantic similarity between input word and mystery word
        Returns similarity in per mille (0-1000)
        """
        try:
            similarity = self.model.similarity(word, self.current_mystery_word)
            return int(similarity * 1000)
        except KeyError:
            return None
