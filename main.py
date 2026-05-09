import os
import sys
import json
import logging
import threading
from pathlib import Path
import webview

# Suppress pywebview accessibility and other noisy logs
logging.getLogger('pywebview').setLevel(logging.CRITICAL)
logging.getLogger('pywebview.window').setLevel(logging.CRITICAL)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import backend modules
try:
    from backend.converter import DocumentConverter
    from backend.rag_processor import RAGProcessor
    from backend.model import AIModel
    from backend.updater import UpdateChecker
except ImportError as e:
    logger.error(f"Import error: {e}")
    sys.exit(1)


class StudyAI:
    def __init__(self):
        self.converter = DocumentConverter()
        self.rag = RAGProcessor()
        self.model = AIModel()
        self.updater = UpdateChecker()
        self.current_pdf_path = None
        self.current_doc_id = None
        self.chat_history = []
        self.open_files = []
        self.settings = {
            "theme": "light",
            "language": "en",
            "panel_swap": False
        }
        self.window = None
        self.load_settings()
    
    def echo(self, message):
        """Test method."""
        return {"status": "success", "message": message}
    
    def get_settings(self):
        return self.settings
    
    def update_settings(self, new_settings):
        self.settings.update(new_settings)
        self.save_settings()
        return {"status": "success", "settings": self.settings}
    
    def save_settings(self):
        try:
            settings_path = Path.home() / ".studyai_settings.json"
            with open(settings_path, 'w') as f:
                json.dump(self.settings, f)
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
    
    def load_settings(self):
        try:
            settings_path = Path.home() / ".studyai_settings.json"
            if settings_path.exists():
                with open(settings_path, 'r') as f:
                    self.settings.update(json.load(f))
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
    
    def open_file_dialog(self):
        """Open native file dialog - runs on main thread."""
        try:
            if hasattr(self, 'window') and self.window:
                files = self.window.create_file_dialog(
                    webview.FileDialog.OPEN,
                    allow_multiple=False,
                    file_types=("Document Files (*.docx;*.pptx;*.txt;*.pdf)", "All Files (*.*)")
                )
                if files and len(files) > 0:
                    return {"status": "success", "file_path": files[0]}
                return {"status": "cancelled"}
            return {"status": "error", "message": "Window not available"}
        except Exception as e:
            logger.error(f"Error in file dialog: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_open_files(self):
        return {"files": self.open_files}
    
    def close_file_tab(self, index):
        try:
            if 0 <= index < len(self.open_files):
                file_info = self.open_files.pop(index)
                if file_info.get('doc_id'):
                    self.rag.clear_document(file_info['doc_id'])
                return {"status": "success"}
            return {"status": "error", "message": "Invalid tab index"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def open_file(self, file_path):
        try:
            if not os.path.exists(file_path):
                return {"status": "error", "message": "File not found"}
            
            ext = Path(file_path).suffix.lower()
            if ext not in self.converter.supported_formats:
                return {"status": "error", "message": f"Unsupported format: {ext}"}
            
            if len(self.open_files) >= 5:
                return {"status": "error", "message": "Maximum 5 files can be open at once."}
            
            pdf_path = self.converter.convert_to_pdf(file_path)
            doc_id = Path(file_path).stem
            
            text = self.converter.extract_text(pdf_path)
            if text:
                self.rag.process_document(text, doc_id)
            
            file_info = {
                "path": file_path,
                "name": Path(file_path).name,
                "pdf_path": pdf_path,
                "doc_id": doc_id
            }
            
            existing = next((f for f in self.open_files if f["path"] == file_path), None)
            if not existing:
                self.open_files.append(file_info)
            
            self.current_pdf_path = pdf_path
            self.current_doc_id = doc_id
            
            return {
                "status": "success",
                "pdf_path": pdf_path,
                "message": "Document opened successfully"
            }
        except Exception as e:
            logger.error(f"Error opening file: {e}")
            return {"status": "error", "message": str(e)}
    
    def ask_question(self, question):
        """Generate AI response - runs in separate thread to avoid blocking."""
        result = {"status": "error", "message": "No document loaded"}
        
        if self.current_doc_id:
            try:
                # Get context from RAG
                rag_result = self.rag.query(question)
                context = rag_result.get("context", "") if rag_result["status"] == "success" else ""
                
                # Generate response
                result = self.model.generate_response(question, context, self.chat_history[-10:])
                
                # Update chat history
                if result["status"] in ["success", "fallback"]:
                    self.chat_history.append({"role": "user", "content": question})
                    self.chat_history.append({"role": "assistant", "content": result["response"]})
                    
                    # Keep only last 20 messages
                    if len(self.chat_history) > 20:
                        self.chat_history = self.chat_history[-20:]
            except Exception as e:
                logger.error(f"Error in ask_question: {e}")
                result = {"status": "error", "message": str(e)}
        else:
            result = {"status": "error", "message": "Please open a document first."}
        
        return result
    
    def get_chat_history(self):
        return self.chat_history
    
    def clear_chat(self):
        self.chat_history = []
        return {"status": "success"}
    
    def close_document(self):
        if self.current_doc_id:
            self.rag.clear_document(self.current_doc_id)
            self.current_doc_id = None
            self.current_pdf_path = None
        return {"status": "success"}
    
    def check_updates(self):
        return self.updater.check_for_updates()


if __name__ == '__main__':
    api = StudyAI()
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_path = os.path.join(current_dir, 'frontend', 'index.html')
    
    if os.name == 'nt':  # Windows
        frontend_url = 'file:///' + frontend_path.replace('\\', '/')
    else:
        frontend_url = 'file://' + frontend_path
    
    # Use mswebview2 on Windows to avoid accessibility issues
    # This prevents the "window.native.AccessibilityObject.Bounds.Empty" errors
    gui_engine = 'mswebview2' if os.name == 'nt' else None
    
    window = webview.create_window(
        'StudyAI - Offline Study Assistant',
        frontend_url,
        js_api=api,
        width=1400,
        height=900,
        min_size=(1000, 700)
    )
    
    api.window = window
    
    # Start with mswebview2 on Windows to avoid accessibility recursion
    webview.start(debug=False, gui=gui_engine)
