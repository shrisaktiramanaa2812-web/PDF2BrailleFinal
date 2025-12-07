class BrailleTranslator:
    def __init__(self):
        self.number_sign = '⠼'
        self.cap_sign = '⠠'
        
        # Standard Grade 1 Mapping
        self.map = {
            'a': '⠁', 'b': '⠃', 'c': '⠉', 'd': '⠙', 'e': '⠑',
            'f': '⠋', 'g': '⠛', 'h': '⠓', 'i': '⠊', 'j': '⠚',
            'k': '⠅', 'l': '⠇', 'm': '⠍', 'n': '⠝', 'o': '⠕',
            'p': '⠏', 'q': '⠟', 'r': '⠗', 's': '⠎', 't': '⠞',
            'u': '⠥', 'v': '⠧', 'w': '⠺', 'x': '⠭', 'y': '⠽', 'z': '⠵',
            ' ': ' ', '\n': '\n', ',': '⠂', ';': '⠆', ':': '⠒',
            '.': '⠲', '!': '⠖', '(': '⠶', ')': '⠶', '?': '⠦',
            '"': '⠶', "'": '⠄', '-': '⠤'
        }
        
        # Numbers mapping (1-9, 0) -> (a-j)
        self.num_map = {
            '1': '⠁', '2': '⠃', '3': '⠉', '4': '⠙', '5': '⠑',
            '6': '⠋', '7': '⠛', '8': '⠓', '9': '⠊', '0': '⠚'
        }

    def translate(self, text):
        braille_output = []
        is_number_mode = False

        for char in text:
            # Handle Numbers
            if char.isdigit():
                if not is_number_mode:
                    braille_output.append(self.number_sign)
                    is_number_mode = True
                braille_output.append(self.num_map.get(char, ''))
                continue
            else:
                is_number_mode = False

            # Handle Capital Letters
            if char.isupper():
                braille_output.append(self.cap_sign)
                char = char.lower()

            # Handle Standard Mapping
            if char in self.map:
                braille_output.append(self.map[char])
            else:
                # Fallback for unknown characters to avoid '?' if possible
                # We simply ignore or print a placeholder space
                braille_output.append(' ') 
                
        return "".join(braille_output)