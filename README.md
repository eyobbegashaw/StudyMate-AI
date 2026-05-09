# StudyAI - Offline AI-Powered Study Assistant

A desktop application that provides students with an AI-powered study companion. Features a split-panel interface where students can view study materials while interacting with an AI assistant. Works completely offline.

## Features

- **Document Processing**: Open .docx, .pptx, .txt, .pdf files
- **Automatic PDF Conversion**: All documents convert to PDF for viewing
- **RAG Pipeline**: Document content extraction, chunking, embeddings, and vector storage
- **Offline AI Chat**: Local AI model integration with context-aware responses
- **Settings**: Dark/Light mode, English/Amharic language, panel swap
- **Update System**: GitHub release checking with in-app notifications
- **About Page**: Developer info and version details

## Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd studyai

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Install Ollama for full AI features
# Visit https://ollama.ai and run: ollama pull llama2

# Run the application
python main.py
```

## Usage

1. **Open a Document**: Click "Open File" or drag & drop. Supported formats: .docx, .pptx, .txt, .pdf
2. **View Document**: PDF displays in the right panel (or left if swapped)
3. **Chat with AI**: Ask questions about the document in the chat panel
4. **Settings**: Access via ⚙️ button to change theme, language, or swap panels
5. **Updates**: Check for updates via About page or update badge

## Project Structure

```
studyai/
├── main.py                 # PyWebView entry point
├── backend/
│   ├── converter.py        # Document to PDF conversion
│   ├── rag_processor.py    # RAG pipeline
│   ├── model.py           # AI model integration
│   └── updater.py         # GitHub release checker
├── frontend/
│   ├── index.html         # Main UI
│   ├── styles/
│   │   ├── dark.css
│   │   └── light.css
│   └── scripts/
│       ├── app.js         # Main app logic
│       ├── pdf-viewer.js  # PDF.js integration
│       └── chat.js       # Chat functionality
├── locales/
│   ├── en.json           # English translations
│   └── am.json           # Amharic translations
├── requirements.txt
└── README.md
```

## Technical Details

### Document Conversion
- `.docx` → python-docx + reportlab
- `.pptx` → python-pptx + reportlab
- `.txt` → Direct to PDF
- `.pdf` → Pass-through

### RAG System
1. Document text extraction
2. Text chunking (500 words, 50-word overlap)
3. Embedding generation (all-MiniLM-L6-v2)
4. Vector storage (ChromaDB)
5. Similarity search for context retrieval

### AI Model
- Default: Ollama with llama2 model
- Fallback: Offline mode with basic responses
- Context-aware conversations using RAG

## Settings

| Setting | Options | Default |
|---------|---------|---------|
| Theme | Light/Dark | Light |
| Language | English/Amharic | English |
| Panel Layout | Left-Right/Right-Left | Viewer Right |

## Dependencies

- **PyWebView**: Desktop wrapper
- **python-docx**: Word document processing
- **python-pptx**: PowerPoint processing
- **reportlab**: PDF generation
- **PyPDF2**: PDF text extraction
- **pdfminer.six**: Alternative PDF text extraction
- **langchain**: RAG framework
- **chromadb**: Vector database
- **sentence-transformers**: Embedding models
- **requests**: HTTP requests for updates

## Known Limitations

- Ollama must be installed separately for full AI features
- Large documents may take time to process for RAG
- PDF conversion may not preserve complex formatting
- Requires local AI model for best experience

## Contributing

Contributions welcome! Please submit issues and pull requests on GitHub.

## License

MIT License

## Version

Current Version: 1.0.0

## Contact

Developer: [Your Name]
GitHub: [repository-url]
