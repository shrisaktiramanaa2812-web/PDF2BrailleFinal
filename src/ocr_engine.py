import easyocr
import numpy as np
from pdf2image import convert_from_bytes
import os



POPPLER_PATH = r".\poppler_binaries\poppler-25.11.0\Library\bin"

class OCREngine:
    
    def __init__(self):
        # Initialize Reader (loads model into memory)
        # 'gpu=True' recommended if you have CUDA, else False
        self.reader = easyocr.Reader(['en'], gpu=True) 

    def process_pdf(self, pdf_file):

        print("Processing PDF...")
        
        # --- CONFIGURATION START ---
        # 1. Get the current working directory as base path
        base_path = os.getcwd()
        
        # 2. Define the path to the poppler 'bin' folder relative to your project
        # UPDATE THIS PATH to match exactly where you extracted the bin folder
        # Example: if you put it in a folder named 'poppler' inside your project:
        poppler_path = os.path.join(base_path, "poppler_binaries", "poppler-25.11.0", "Library", "bin")
        
        # 3. Validation to help you debug if the path is wrong
        if not os.path.exists(poppler_path):
            # Fallback: Try to find standard structure if the user just unzipped it
            # Adjust this logic if your folder structure is different
            poppler_path = POPPLER_PATH

        if not os.path.exists(os.path.join(poppler_path, 'pdfinfo.exe')):
            raise FileNotFoundError(f"Could not find pdfinfo.exe at: {poppler_path}. Please check the folder structure.")
        # --- CONFIGURATION END ---

        # Convert PDF to List of PIL Images
        images = convert_from_bytes(pdf_file.read(),poppler_path=poppler_path)

        page_texts = []
        
        
        for i, img in enumerate(images):
            # EasyOCR expects numpy array
            img_np = np.array(img)
            
            # Detail=0 gives simple text list
            results = self.reader.readtext(img_np, detail=0, paragraph = True) 
            
            page_text = "\n\n".join(results)
            page_texts.append(page_text)
            
        return page_texts