import subprocess
import os
import platform
from pathlib import Path

def convert_with_libreoffice(input_file, output_folder):
    """Convert documents to PDF using LibreOffice."""
    # Find LibreOffice path based on OS
    if platform.system() == "Windows":
        possible_paths = [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        ]
        soffice_path = None
        for path in possible_paths:
            if os.path.exists(path):
                soffice_path = path
                break
        if not soffice_path:
            raise FileNotFoundError("LibreOffice not found. Please install from https://www.libreoffice.org/")
    elif platform.system() == "Darwin":  # macOS
        soffice_path = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
    else:  # Linux
        soffice_path = "soffice"
    
    cmd = [
        soffice_path,
        '--headless',
        '--convert-to', 'pdf',
        '--outdir', output_folder,
        input_file
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=120)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error converting: {e.stderr}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


class DocumentConverter:
    def __init__(self):
        self.supported_formats = ['.docx', '.pptx', '.txt', '.pdf']
    
    def convert_to_pdf(self, input_path, output_path=None):
        """Convert document to PDF using LibreOffice."""
        try:
            input_path = Path(input_path)
            ext = input_path.suffix.lower()
            
            if ext not in self.supported_formats:
                raise ValueError(f"Unsupported format: {ext}")
            
            if ext == '.pdf':
                return str(input_path)
            
            if output_path is None:
                output_path = str(input_path.parent)
            
            success = convert_with_libreoffice(str(input_path), output_path)
            
            if success:
                pdf_path = Path(output_path) / (input_path.stem + ".pdf")
                if pdf_path.exists():
                    return str(pdf_path)
            
            raise Exception("PDF conversion failed")
            
        except Exception as e:
            print(f"Error converting {input_path}: {e}")
            raise
    
    def extract_text(self, pdf_path):
        """Extract text from PDF for RAG processing."""
        try:
            from pdfminer.high_level import extract_text
            return extract_text(pdf_path)
        except Exception as e:
            print(f"Error extracting text: {e}")
            try:
                import PyPDF2
                with open(pdf_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() or ""
                    return text
            except Exception as e2:
                print(f"Fallback extraction failed: {e2}")
                return ""
