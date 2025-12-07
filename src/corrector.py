from transformers import pipeline

class TextCorrector:
    # Grammar correction using a T5 model via HuggingFace Transformers
    def __init__(self):
        self.corrector = pipeline(
            "text2text-generation",
            model="vennify/t5-base-grammar-correction", 
            max_length=512
        )
        # Using a conservative character limit well below the 512 token limit
        self.max_char_chunk = 450 

    def _chunk_text(self, text):
        """Splits a long string into chunks of max_char_chunk size."""
        chunks = []
        i = 0
        while i < len(text):
            # Take a chunk of size up to max_char_chunk
            chunk = text[i:i + self.max_char_chunk]
            
            # Simple boundary check: If not the last chunk, try to end at a space
            if i + self.max_char_chunk < len(text):
                last_space = chunk.rfind(' ')
                if last_space > 0 and (len(chunk) - last_space) < 50:
                    # Cut off at the last space to avoid cutting a word in half
                    chunks.append(chunk[:last_space].strip())
                    i += last_space + 1
                else:
                    # If no good space found near the end, just take the fixed chunk
                    chunks.append(chunk.strip())
                    i += self.max_char_chunk
            else:
                # Last chunk
                chunks.append(chunk.strip())
                i += self.max_char_chunk
        return [c for c in chunks if c] # Filter out empty chunks

    def _run_model(self, text_chunk):
        """Helper to run the actual prediction"""
        try:
            input_text = "grammar: " + text_chunk
            res = self.corrector(input_text)
            return res[0]['generated_text']
        except Exception as e:
            # Fallback if model fails
            return text_chunk

    def correct_text(self, text):
        """
        Splits text into lines (paragraphs) and then further chunks them 
        by character length before correcting.
        """
        # 1. Split text by existing paragraphs/lines from OCR
        lines = text.split('\n')
        corrected_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                corrected_lines.append("")
                continue

            # 2. Chunk the line if it's too long
            if len(line) > self.max_char_chunk:
                chunks = self._chunk_text(line)
                corrected_chunks = []
                for chunk in chunks:
                    corrected_chunk = self._run_model(chunk)
                    if len(corrected_chunk) <= len(chunk) + 5:
                        corrected_chunks.append(corrected_chunk)
                    else:
                        corrected_chunks.append(chunk)
                
                # Join the corrected chunks back together (using a space)
                corrected_lines.append(" ".join(corrected_chunks))
            else:
                # Process shorter lines directly
                corrected_line = self._run_model(line)
                if len(corrected_line) <= len(line) + 5:
                    corrected_lines.append(corrected_line)
                else:
                    corrected_lines.append(line)
                
        return "\n".join(corrected_lines)