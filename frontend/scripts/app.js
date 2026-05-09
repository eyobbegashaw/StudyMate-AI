// Global variables
let settings = {theme: 'light', language: 'en', panel_swap: false};
let pywebviewReady = false;
let openFiles = []; // Array to store open file info (max 5)
const MAX_TABS = 5;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, waiting for pywebview...');
    waitForPyWebView();
});

function waitForPyWebView() {
    if (window.pywebview && window.pywebview.api) {
        console.log('pywebview ready!');
        pywebviewReady = true;
        initApp();
    } else {
        setTimeout(waitForPyWebView, 100);
    }
}

async function initApp() {
    try {
        // Load settings
        settings = await window.pywebview.api.get_settings();
        console.log('Settings loaded:', settings);
        
        // Apply settings to UI
        document.getElementById('theme-select').value = settings.theme || 'light';
        document.getElementById('lang-select').value = settings.language || 'en';
        document.getElementById('swap-panels').checked = settings.panel_swap || false;
        
        // Apply theme
        document.getElementById('theme-stylesheet').href = `styles/${settings.theme || 'light'}.css`;
        
        // Apply panel swap
        if (settings.panel_swap) {
            document.getElementById('main-panels').classList.add('swapped');
        }
        
        // Check for updates
        checkForUpdates();
        
        console.log('StudyAI initialized successfully');
    } catch (e) {
        console.error('Error initializing app:', e);
    }
}

// File Tabs Management
function addFileTab(filePath, fileName) {
    // Check if file already open
    const existingIndex = openFiles.findIndex(f => f.path === filePath);
    if (existingIndex >= 0) {
        // File already open, just switch to it
        switchToFileTab(existingIndex);
        return;
    }
    
    // Check max tabs (5)
    if (openFiles.length >= MAX_TABS) {
        alert(`Maximum ${MAX_TABS} files can be open at once. Close a tab first.`);
        return;
    }
    
    // Add to open files
    openFiles.push({
        path: filePath,
        name: fileName,
        pdfPath: null
    });
    
    renderFileTabs();
    
    // Switch to new tab
    switchToFileTab(openFiles.length - 1);
}

function renderFileTabs() {
    const tabsContainer = document.getElementById('file-tabs');
    if (!tabsContainer) return;
    
    tabsContainer.innerHTML = '';
    
    openFiles.forEach((file, index) => {
        const tab = document.createElement('div');
        tab.className = 'file-tab';
        tab.dataset.index = index;
        
        const nameSpan = document.createElement('span');
        nameSpan.className = 'tab-name';
        nameSpan.textContent = file.name;
        nameSpan.onclick = () => switchToFileTab(index);
        
        const closeBtn = document.createElement('span');
        closeBtn.className = 'tab-close';
        closeBtn.textContent = '×';
        closeBtn.onclick = (e) => {
            e.stopPropagation();
            closeFileTab(index);
        };
        
        tab.appendChild(nameSpan);
        tab.appendChild(closeBtn);
        tabsContainer.appendChild(tab);
    });
}

function switchToFileTab(index) {
    if (index < 0 || index >= openFiles.length) return;
    
    // Update active tab
    const tabs = document.querySelectorAll('.file-tab');
    tabs.forEach((tab, i) => {
        tab.classList.toggle('active', i === index);
    });
    
    // Load the file
    const file = openFiles[index];
    if (file.pdfPath) {
        document.getElementById('doc-name').textContent = file.name;
        document.getElementById('empty-viewer').classList.add('hidden');
        document.getElementById('pdf-canvas').classList.remove('hidden');
        document.getElementById('pdf-controls').classList.remove('hidden');
        loadPDF(file.pdfPath);
    }
}

function closeFileTab(index) {
    if (index < 0 || index >= openFiles.length) return;
    
    const wasActive = document.querySelectorAll('.file-tab')[index]?.classList.contains('active');
    
    // Remove file
    openFiles.splice(index, 1);
    renderFileTabs();
    
    // If we closed the active tab, switch to first tab or clear
    if (wasActive) {
        if (openFiles.length > 0) {
            switchToFileTab(0);
        } else {
            clearViewer();
        }
    } else if (openFiles.length > 0) {
        // Update active tab index
        const activeIndex = openFiles.findIndex(f => f.pdfPath);
        if (activeIndex >= 0) switchToFileTab(activeIndex);
    }
}

function clearViewer() {
    document.getElementById('doc-name').textContent = '';
    document.getElementById('empty-viewer').classList.remove('hidden');
    document.getElementById('pdf-canvas').classList.add('hidden');
    document.getElementById('pdf-controls').classList.add('hidden');
}

// File handling
async function openFile() {
    console.log('Open File clicked');
    try {
        // Try native file dialog first
        const result = await window.pywebview.api.open_file_dialog();
        console.log('File dialog result:', result);
        
        if (result.status === 'success' && result.file_path) {
            await processFile(result.file_path);
        } else if (result.status === 'cancelled') {
            console.log('File dialog cancelled');
        } else {
            // Fallback to HTML file input
            console.log('Falling back to HTML file input');
            document.getElementById('file-input').click();
        }
    } catch (e) {
        console.error('Error opening file dialog:', e);
        // Fallback to HTML file input
        document.getElementById('file-input').click();
    }
}

async function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    console.log('File selected:', file.name);
    await processFile(file.path || file.name, file.name);
    
    // Reset file input
    event.target.value = '';
}

async function processFile(filePath, fileName) {
    console.log('Processing file:', filePath);
    showLoading('Processing document...');
    
    try {
        const result = await window.pywebview.api.open_file(filePath);
        console.log('Open file result:', result);
        
        if (result.status === 'success') {
            // Add tab
            const name = fileName || filePath.split('\\').pop().split('/').pop();
            addFileTab(filePath, name);
            
            // Update tab with PDF path
            const tabIndex = openFiles.findIndex(f => f.path === filePath);
            if (tabIndex >= 0) {
                openFiles[tabIndex].pdfPath = result.pdf_path;
            }
            
            loadPDF(result.pdf_path);
            addMessage('system', `Document "${name}" loaded successfully. You can now ask questions about it.`);
        } else {
            alert('Error: ' + result.message);
        }
    } catch (e) {
        console.error('Error opening file:', e);
        alert('Error opening file: ' + e.message);
    } finally {
        hideLoading();
    }
}

// Modal functions
function showSettings() {
    console.log('Showing settings modal');
    document.getElementById('settings-modal').classList.remove('hidden');
}

function closeSettings() {
    console.log('Closing settings');
    document.getElementById('settings-modal').classList.add('hidden');
}

function showAbout() {
    console.log('Showing about modal');
    document.getElementById('about-modal').classList.remove('hidden');
}

function closeAbout() {
    console.log('Closing about');
    document.getElementById('about-modal').classList.add('hidden');
}

// Settings functions
function changeTheme() {
    const theme = document.getElementById('theme-select').value;
    document.getElementById('theme-stylesheet').href = `styles/${theme}.css`;
    settings.theme = theme;
    saveSettings();
}

function changeLanguage() {
    const lang = document.getElementById('lang-select').value;
    settings.language = lang;
    saveSettings();
}

function togglePanels() {
    const isChecked = document.getElementById('swap-panels').checked;
    const mainPanels = document.getElementById('main-panels');
    
    if (isChecked) {
        mainPanels.classList.add('swapped');
    } else {
        mainPanels.classList.remove('swapped');
    }
    
    settings.panel_swap = isChecked;
    saveSettings();
}

function saveSettings() {
    if (pywebviewReady) {
        window.pywebview.api.update_settings(settings);
    }
}

// Update functions
async function checkForUpdates() {
    try {
        const result = await window.pywebview.api.check_updates();
        if (result.update_available) {
            document.getElementById('update-badge').classList.remove('hidden');
        }
    } catch (e) {
        console.log('Update check failed:', e);
    }
}

async function showUpdate() {
    try {
        const result = await window.pywebview.api.check_updates();
        if (result.update_available) {
            alert(`New version available: ${result.latest_version}\nCurrent version: ${result.current_version}\n\nVisit: ${result.html_url}`);
        } else {
            alert('You have the latest version!');
        }
    } catch (e) {
        console.error('Update check failed:', e);
    }
}

async function checkUpdatesFromAbout() {
    await showUpdate();
}

// Chat functions
async function clearChat() {
    if (confirm('Clear chat history?')) {
        await window.pywebview.api.clear_chat();
        document.getElementById('chat-messages').innerHTML = '';
        addMessage('system', 'Chat cleared. Open a document to start asking questions.');
    }
}

function handleInputKeydown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Utility functions
function showLoading(text) {
    document.getElementById('loading-overlay').classList.remove('hidden');
    document.getElementById('loading-text').textContent = text || 'Processing...';
}

function hideLoading() {
    document.getElementById('loading-overlay').classList.add('hidden');
}

function addMessage(type, text) {
    const container = document.getElementById('chat-messages');
    if (!container) return;
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${type}-message`;
    
    if (type === 'assistant') {
        // Add copy/share buttons for AI responses
        const textDiv = document.createElement('div');
        textDiv.textContent = text;
        msgDiv.appendChild(textDiv);
        
        const btnContainer = document.createElement('div');
        btnContainer.className = 'message-buttons';
        
        const copyBtn = document.createElement('button');
        copyBtn.className = 'btn-small';
        copyBtn.textContent = 'Copy';
        copyBtn.onclick = () => {
            navigator.clipboard.writeText(text).then(() => {
                copyBtn.textContent = 'Copied!';
                setTimeout(() => copyBtn.textContent = 'Copy', 2000);
            }).catch(err => console.error('Copy failed:', err));
        };
        
        const shareBtn = document.createElement('button');
        shareBtn.className = 'btn-small';
        shareBtn.textContent = 'Share';
        shareBtn.onclick = () => {
            if (navigator.share) {
                navigator.share({
                    title: 'StudyAI Response',
                    text: text
                }).catch(err => console.log('Share cancelled'));
            } else {
                alert('Share not supported. Use Copy instead.');
            }
        };
        
        btnContainer.appendChild(copyBtn);
        btnContainer.appendChild(shareBtn);
        msgDiv.appendChild(btnContainer);
    } else {
        msgDiv.textContent = text;
    }
    
    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
}
