# app.py
import streamlit as st
import re
from src.ocr_engine import OCREngine
from src.corrector import TextCorrector
from src.braille_mapper import BrailleTranslator
# from src.evaluator import Evaluator 
from docx import Document 
import io

# --------------------------------------------------------------------------
# Define utility functions
# --------------------------------------------------------------------------
def clean_final_text(text):
    """
    FIXED: Removes common repetitive OCR artifacts, including tokens with punctuation,
    and repeated headers/phrases that span multiple lines.
    """
    # Replace :. with .
    text = re.sub(r'\:\.', '.', text)
    # Replace ;. with .
    text = re.sub(r'\;\.', '.', text)
    # Remove excessive blank lines
    text = re.sub(r'(\n\s*){3,}', '\n\n', text)
    
    return text

def create_word_document(text):
    # Creates a Word document in memory from the provided text using python-docx
    document = Document()
    
    paragraphs = text.split('\n\n')
    for p_text in paragraphs:
        p_text = p_text.replace('\n', ' ') 
        
        if "-- Page Break --" in p_text:
            document.add_section() 
        else:
            document.add_paragraph(p_text)
            
    doc_buffer = io.BytesIO()
    document.save(doc_buffer)
    doc_buffer.seek(0)
    return doc_buffer
# --------------------------------------------------------------------------


# Page Config
st.set_page_config(page_title="AI Braille Converter", layout="wide")

st.title("⠠⠁⠃⠇⠑ AI Braille Converter")
st.markdown("""
**Upload a PDF document to convert it into Grade 1 Braille.** *Now saves output as a Microsoft Word document (.docx).*
""")

use_correction = True

# --- INPUT FILES ---
uploaded_file = st.file_uploader("Choose the PDF file to process", type="pdf", key="pdf_uploader")
uploaded_ground_truth = st.file_uploader("Optional: Upload Ground Truth Text File (.txt) for Evaluation", type="txt", key="gt_uploader")
# --------------------

# --- INITIALIZATION AND CACHING ---
if 'processed_braille' not in st.session_state: st.session_state['processed_braille'] = None # Braille result cache
if 'processed_english' not in st.session_state: st.session_state['processed_english'] = None # English result cache
if 'uploaded_file_name' not in st.session_state: st.session_state['uploaded_file_name'] = None # Uploaded file name cache
if 'uploaded_file_bytes' not in st.session_state: st.session_state['uploaded_file_bytes'] = None # Uploaded file bytes cache
if 'raw_ocr_combined' not in st.session_state: st.session_state['raw_ocr_combined'] = None # Raw OCR combined text cache
if 'evaluation_report' not in st.session_state: st.session_state['evaluation_report'] = None # Evaluation report cache
if 'last_gt_key' not in st.session_state: st.session_state['last_gt_key'] = None # Added for robust GT caching

# ----------------------------------
# --- Load Engines with Caching ---
from src.evaluator import Evaluator 
@st.cache_resource
def load_engines():
    return OCREngine(), TextCorrector(), BrailleTranslator()
def load_evaluation_engines():
    return Evaluator()
# ----------------------------------

# --------------------------------------------------------------------------
# --- MAIN PROCESSING LOGIC ---
if uploaded_file is not None:
    # Read file content immediately to compare against the cached bytes
    uploaded_file.seek(0)
    current_file_bytes = uploaded_file.read()

    is_new_file = (
        st.session_state['uploaded_file_name'] != uploaded_file.name or 
        st.session_state['uploaded_file_bytes'] != current_file_bytes
    )
    
    should_process = is_new_file or st.session_state['processed_braille'] is None

    if should_process:
        
        # Store the current file details
        st.session_state['uploaded_file_name'] = uploaded_file.name
        st.session_state['uploaded_file_bytes'] = current_file_bytes
        
        st.info("File Uploaded. Processing entire document... (This may take a moment)")
        
        # ocr_engine, corrector, translator, evaluator = load_engines()
        ocr_engine, corrector, translator = load_engines()
        evaluator = load_evaluation_engines()
        # --- Step 1: OCR ---
        with st.spinner("Extracting text (preserving layout)..."):
            uploaded_file.seek(0) 
            page_texts_raw = ocr_engine.process_pdf(uploaded_file)
            num_pages = len(page_texts_raw)
        
        # --- Step 2 & 3: Process all pages ---
        full_corrected_text = []
        full_raw_ocr_text = []
        progress_bar = st.progress(0, text="Processing Pages...")
        
        for i, raw_text in enumerate(page_texts_raw):
            corrected_page_text = raw_text
            
            full_raw_ocr_text.append(raw_text)
            
            if use_correction:
                with st.spinner(f"Refining Page {i + 1} with Transformer AI..."):
                    corrected_page_text = corrector.correct_text(raw_text)
            
            # create_word_document(corrected_page_text)  # Pre-cache DOCX for each page if needed
            # print(corrected_page_text)
            full_corrected_text.append(corrected_page_text)
            progress_bar.progress((i + 1) / num_pages, text=f"Processing Page {i + 1} of {num_pages}...")
        
        progress_bar.empty()
        
        # --- Final Compilation and Global Cleanup ---
        final_corrected_text = "\n\n-- Page Break --\n\n".join(full_corrected_text)
        final_corrected_text = clean_final_text(final_corrected_text)

        final_raw_ocr_text = "\n\n-- Page Break --\n\n".join(full_raw_ocr_text)

        # --- Final Braille Translation ---
        # braille_text_joined = translator.translate(final_raw_ocr_text)
        braille_text_joined = translator.translate(final_corrected_text)
        
        # --- STORE RESULTS IN SESSION STATE ---
        # st.session_state['processed_english'] = final_raw_ocr_text
        st.session_state['processed_english'] = final_corrected_text
        st.session_state['processed_braille'] = braille_text_joined
        st.session_state['raw_ocr_combined'] = final_raw_ocr_text
        st.session_state['evaluation_report'] = None
        
        st.success("Conversion Complete! Results cached.")
    
    # --- Evaluation Logic (Runs every time after processing is done) ---
    if uploaded_ground_truth is not None and st.session_state['processed_english'] is not None:
        
        uploaded_ground_truth.seek(0)
        gt_key = uploaded_ground_truth.read()
        
        if st.session_state['last_gt_key'] != gt_key or st.session_state['evaluation_report'] is None:
            
            ocr_engine, corrector, translator = load_engines()
            evaluator = load_evaluation_engines()
            
            uploaded_ground_truth.seek(0)
            ground_truth_text = uploaded_ground_truth.read().decode("utf-8")
            
            # raw_ocr_text = st.session_state['raw_ocr_combined']
            corrected_text = st.session_state['processed_english']

            if corrected_text:
                with st.spinner("Calculating Accuracy Metrics..."):
                    report = evaluator.get_accuracy_report(corrected_text, ground_truth_text)
                    st.session_state['evaluation_report'] = report
                    st.session_state['last_gt_key'] = gt_key
                    st.balloons() 

    # --- RETRIEVE CACHED RESULTS FOR DISPLAY/DOWNLOAD ---
    final_text_joined = st.session_state['processed_english']
    braille_text_joined = st.session_state['processed_braille']
    final_raw_ocr_joined = st.session_state['raw_ocr_combined']
    report = st.session_state['evaluation_report']
    
    # --- Generate DOCX in memory (done only when needed for download) ---
    raw_ocr_docx_buffer = create_word_document(final_raw_ocr_joined)
    english_docx_buffer = create_word_document(final_text_joined)
    braille_docx_buffer = create_word_document(braille_text_joined)

    # --------------------------------------------------------------------------
    # --- DISPLAY METRICS ---
    # --------------------------------------------------------------------------
    if report is not None:
        st.header("✨ Evaluation Results")
        st.markdown(f"**Ground Truth Size:** {report['raw_length']} characters")
        
        col_corrected = st.columns(2)

        with col_corrected[0]:
            st.metric(
                label="Corrected CER",
                value=f"{report['corrected_cer']:.2f}%",
            )
        with col_corrected[1]:
            st.metric(
                label="Character Accuracy",
                value=f"{report['character_accuracy']:.2f}%",
            )
        st.divider()

    # --------------------------------------------------------------------------
    # --- DISPLAY DOWNLOADS ---
    # --------------------------------------------------------------------------

    st.header("Output Files")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Extracted English Text")
        
        preview_text = final_text_joined.replace("\n\n-- Page Break --\n\n", "\n\n--- Page Break ---\n\n")
        preview_text = preview_text[:1000] + ("..." if len(preview_text) > 1000 else "")
        st.text_area("English Preview", value=preview_text, height=400)
        
        st.download_button(
            label="Download Full English (.docx)",
            data=english_docx_buffer,
            file_name="extracted_english_full.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
    with col2:
        st.subheader("Braille Output")
        
        preview_braille = braille_text_joined.replace("\n⠐⠧⠐\n", "\n--- PAGE BREAK ---\n")
        preview_braille = preview_braille[:1000] + ("..." if len(braille_text_joined) > 1000 else "")
        st.text_area("Braille Preview", value=preview_braille, height=400)

        st.download_button(
            label="Download Full Braille (.docx)",
            data=braille_docx_buffer,
            file_name="braille_output_full.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
