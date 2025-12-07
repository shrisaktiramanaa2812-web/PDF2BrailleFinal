# src/evaluator.py
import numpy as np
import Levenshtein
import nltk
from nltk.metrics.distance import edit_distance
import re 

# --------------------------------------------------------------------------
# FIX: Robust download logic to handle environmental path issues
# --------------------------------------------------------------------------
try:
    # 1. Check if the resource is already available in this environment's path
    nltk.data.find('corpora/wordnet')
except LookupError:
    print("NLTK resource 'wordnet' not found in the Streamlit environment's paths.")
    print("Attempting to download 'wordnet' now...")
    try:
        # 2. Attempt to download directly into the environment path
        # Using quiet=True to suppress standard output during the run
        nltk.download('wordnet', quiet=True) 
        print("'wordnet' successfully downloaded for this environment.")
    except Exception as e:
        # 3. Catch any failure (network, permission, or AttributeError)
        print(f"FATAL NLTK DOWNLOAD ERROR: {e}")
        print("The automatic NLTK download failed. Please ensure your network is connected and that you have run 'python -c \"import nltk; nltk.download(\\'wordnet\\')\"' in your terminal.")
        # Re-raise the LookupError so the app does not run with a broken component
        raise
# --------------------------------------------------------------------------


class Evaluator:

    def calculate_char_accuracy(self, ground_truth : str, corrected_text : str) -> float:
        """
        Calculates Character Accuracy between ground truth and corrected text.
        """
        # 1. Normalize the strings (important for fair comparison)
        # Removing extra whitespace ensures accuracy isn't penalized for layout differences.
        gt_clean = " ".join(ground_truth.split()).lower()
        ocr_clean = " ".join(corrected_text.split()).lower()

        # If the ground truth is empty, handle the edge case
        if not gt_clean:
            return 0.0 if ocr_clean else 100.0
        
        # 2. Calculate Levenshtein Distance (Number of Edits)
        # The distance is the minimum number of insertions, deletions, or substitutions.
        edit_distance = Levenshtein.distance(gt_clean, ocr_clean)
        
        # 3. Calculate CER
        # CER = (Edits / Total Characters in Ground Truth)
        cer = edit_distance / len(gt_clean)
        
        # 4. Convert CER to Accuracy Percentage
        # Accuracy = (1 - CER) * 100
        accuracy_rate = (1.0 - cer) * 100
        
        return accuracy_rate

    def calculate_cer(self, predicted_text: str, ground_truth_text: str) -> float:
        """
        Calculates the Character Error Rate (CER).
        """
        
        # 1. Clean and normalize the text (Crucial step for fair comparison)
        def normalize_text(text):
            # Convert to lower case
            text = text.lower()
            # Remove all non-alphanumeric characters, and keep spaces temporarily
            text = re.sub(r'[^\w\s]', '', text) 
            # Remove all remaining whitespace (tabs, newlines, spaces) 
            text = ''.join(text.split())
            return text

        normalized_predicted = normalize_text(predicted_text)
        normalized_ground_truth = normalize_text(ground_truth_text)

        if not normalized_ground_truth:
            return 0.0

        # 2. Calculate Levenshtein Distance (Edit Distance)
        edits = edit_distance(normalized_predicted, normalized_ground_truth)
        
        # 3. Calculate CER
        cer = edits / len(normalized_ground_truth)
        
        return cer

    def get_accuracy_report(self, corrected_text, ground_truth_text) -> dict:
        """Generates a full evaluation report."""
        corrected_cer = self.calculate_cer(corrected_text, ground_truth_text)
        
        character_accuracy = self.calculate_char_accuracy(ground_truth_text, corrected_text)
            
        return {
            "corrected_cer": corrected_cer * 100,
            "character_accuracy": character_accuracy,
            # "improvement_percent": improvement,
            "raw_length": len(''.join(ground_truth_text.split()))
        }