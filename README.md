# 🌟 PDF2BrailleFinal: OCR, Evaluation, and Translation Pipeline

This repository contains the code for a custom pipeline that processes PDF documents, extracts text using OCR, compares the output against Ground Truth, and is structured for future translation features.

## Prerequisites

To execute this project, you need the following installed on your machine:

1.  **Python 3.8+**
2.  **Git** (for cloning the repository)
3.  **Poppler Utility:** This is required by `pdf2image` to convert PDF files into images.

| Operating System | Installation Command |
| :--- | :--- |
| **Linux (Debian/Ubuntu)** | `sudo apt-get install poppler-utils` |
| **macOS (using Homebrew)** | `brew install poppler` |
| **Windows** | Download the latest release binary for Poppler and add the `bin/` folder to your system's PATH variable. |

## ⚙️ Setup and Execution

Follow these steps to set up the environment and run the application.

### Step 1: Clone the Repository

Open your terminal or command prompt and clone the project files:

```bash
git clone https://github.com/shrisaktiramanaa2812-web/PDF2BrailleFinal
cd PDF2BrailleFinal



# Create the environment
python3 -m venv venv

# Activate the environment (macOS/Linux)
source venv/bin/activate

# Activate the environment (Windows PowerShell)
.\venv\Scripts\Activate

#Install Required Libraries
pip install -r requirements.txt

#sample digital and scanned PDFS directory
assets/PDFs

#sample Ground Truth text files directory
assets/Ground_truth

#Run application using this line
streamlit run app.py