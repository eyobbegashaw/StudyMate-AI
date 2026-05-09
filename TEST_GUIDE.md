# StudyAI - Test Guide

## Current Status ✅

### Backend (Python)
- ✅ `main.py` - PyWebView entry point
- ✅ `backend/converter.py` - LibreOffice conversion (max 5 file tabs)
- ✅ `backend/rag_processor.py` - RAG pipeline with ChromaDB
- ✅ `backend/model.py` - Meta-Llama-3-8B-Instruct-Q4_K_M.gguf (4096 context)
- ✅ `backend/updater.py` - GitHub release checker

### Frontend (HTML/CSS/JS)
- ✅ `frontend/index.html` - Main UI with file tabs
- ✅ `frontend/styles/light.css` - Light theme + file tabs CSS
- ✅ `frontend/styles/dark.css` - Dark theme + file tabs CSS
- ✅ `frontend/scripts/app.js` - File tabs (max 5), settings, about
- ✅ `frontend/scripts/pdf-viewer.js` - PDF.js viewer
- ✅ `frontend/scripts/chat.js` - Chat functionality

## How to Test

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install LibreOffice (for document conversion)
- Download: https://www.libreoffice.org/download/
- Install normally (Windows: `C:\Program Files\LibreOffice\`)

### 3. Download AI Model (Optional - for full AI features)
The app uses **Phi-3-mini-4k-instruct-q4.gguf** (smaller, faster, 4k context):
- Visit: https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf
- Download: `Phi-3-mini-4k-instruct-q4.gguf`
- Place in: `C:\Users\rabon\.studyai_models\`

Or run:
```bash
python download_model.py
```

### 4. Run the App
```bash
python main.py
```

## Features Implemented ✅

### File Tabs (Max 5)
- Open files → Creates tab at top
- Click tab → Switches to that file
- Close tab → × button on tab
- Max 5 tabs → Alert if exceeded

### Meta-Llama-3-8B Model
- Default model: `Meta-Llama-3-8B-Instruct-Q4_K_M.gguf`
- Context window: **4096 tokens** (no more overflow!)
- CPU mode (no CUDA/GPU required)
- Fallback mode if model not found

### Fixed Issues
- ✅ Buttons work (Settings/About/Open File)
- ✅ No deprecated `OPEN_DIALOG` warning
- ✅ File dialog uses `FileDialog.OPEN`
- ✅ 4096 context window (no token overflow)
- ✅ LibreOffice conversion (better than reportlab)

## Testing Checklist

1. **Open File** → Click "Open File" → Select .docx/.pptx/.txt/.pdf
2. **File Tabs** → Open multiple files (max 5) → Switch between tabs
3. **Chat** → Ask questions about opened document
4. **Settings** → Change theme, language, swap panels
5. **About** → View version info
6. **PDF Viewer** → Navigate pages with Previous/Next buttons

## Troubleshooting

### Model not found
```
WARNING:backend.model:Model not found at C:\Users\rabon\.studyai_models\Meta-Llama-3-8B-Instruct-Q4_K_M.gguf
```
**Solution**: Download model manually or app runs in fallback mode.

### LibreOffice not found
```
ERROR:backend.converter:LibreOffice not found
```
**Solution**: Install LibreOffice from https://www.libreoffice.org/

### pywebview not installed
```bash
pip install pywebview
```

## Next Steps

1. Test opening different file types (.docx, .pptx, .txt, .pdf)
2. Test file tabs (open 5 files, try to open 6th)
3. Test switching between tabs
4. Test closing tabs
5. Test chat with AI (if model installed)
6. Test settings (theme, language, panel swap)
7. Test update checker (set GitHub repo in `backend/updater.py`)

## Screenshots Needed
- [ ] Main interface with file tabs
- [ ] Settings modal
- [ ] About modal
- [ ] Chat in action
- [ ] PDF viewer with navigation
