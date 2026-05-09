let pdfDoc = null;
let currentPage = 1;
let totalPages = 0;
let scale = 1.5;

// Configure PDF.js worker
if (typeof pdfjsLib !== 'undefined') {
    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
}

function loadPDF(pdfPath) {
    if (!pdfPath || typeof pdfjsLib === 'undefined') return;
    
    // Convert Windows path to file URL
    let url = pdfPath;
    if (pdfPath.match(/^[A-Za-z]:\\/)) {
        // Windows absolute path
        url = 'file:///' + pdfPath.replace(/\\/g, '/');
    } else if (!pdfPath.startsWith('file://') && !pdfPath.startsWith('http')) {
        url = 'file://' + pdfPath;
    }
    
    console.log('Loading PDF from:', url);
    
    // Load PDF from URL
    pdfjsLib.getDocument(url).promise.then(function(pdf) {
        pdfDoc = pdf;
        totalPages = pdf.numPages;
        currentPage = 1;
        updatePageInfo();
        renderPage(currentPage);
    }).catch(function(error) {
        console.error('Error loading PDF:', error);
        // Try loading via fetch as fallback
        fetch(url).then(function(response) {
            return response.arrayBuffer();
        }).then(function(data) {
            return pdfjsLib.getDocument({data: data}).promise;
        }).then(function(pdf) {
            pdfDoc = pdf;
            totalPages = pdf.numPages;
            currentPage = 1;
            updatePageInfo();
            renderPage(currentPage);
        }).catch(function(err) {
            console.error('Fallback also failed:', err);
            alert('Error loading PDF. Please try again.');
        });
    });
}

function renderPage(pageNum) {
    if (!pdfDoc) return;
    
    pdfDoc.getPage(pageNum).then(function(page) {
        const canvas = document.getElementById('pdf-canvas');
        if (!canvas) return;
        
        const context = canvas.getContext('2d');
        const viewport = page.getViewport({scale: scale});
        
        canvas.height = viewport.height;
        canvas.width = viewport.width;
        
        const renderContext = {
            canvasContext: context,
            viewport: viewport
        };
        
        page.render(renderContext).promise.then(function() {
            console.log('Page rendered');
        }).catch(function(err) {
            console.error('Render error:', err);
        });
    }).catch(function(err) {
        console.error('Error getting page:', err);
    });
}

function nextPage() {
    if (!pdfDoc || currentPage >= totalPages) return;
    currentPage++;
    updatePageInfo();
    renderPage(currentPage);
}

function prevPage() {
    if (!pdfDoc || currentPage <= 1) return;
    currentPage--;
    updatePageInfo();
    renderPage(currentPage);
}

function updatePageInfo() {
    const pageInfo = document.getElementById('page-info');
    if (pageInfo) {
        pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
    }
    
    const prevBtn = document.getElementById('btn-prev-page');
    const nextBtn = document.getElementById('btn-next-page');
    
    if (prevBtn) prevBtn.disabled = currentPage <= 1;
    if (nextBtn) nextBtn.disabled = currentPage >= totalPages || !pdfDoc;
}

function zoomIn() {
    scale += 0.25;
    renderPage(currentPage);
}

function zoomOut() {
    if (scale > 0.5) {
        scale -= 0.25;
        renderPage(currentPage);
    }
}
