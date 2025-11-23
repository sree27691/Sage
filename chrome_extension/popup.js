document.addEventListener('DOMContentLoaded', () => {
    const analyzeBtn = document.getElementById('analyze-btn');
    const mainView = document.getElementById('main-view');
    const loadingView = document.getElementById('loading-view');
    const resultView = document.getElementById('result-view');
    const errorMsg = document.getElementById('error-msg');

    let currentProductContext = null;

    analyzeBtn.addEventListener('click', async () => {
        // UI State: Loading
        mainView.classList.add('hidden');
        loadingView.classList.remove('hidden');
        errorMsg.classList.add('hidden');

        try {
            // 1. Get Active Tab
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

            if (!tab.id) throw new Error("No active tab found");

            // 2. Execute Script to get Data
            const results = await chrome.scripting.executeScript({
                target: { tabId: tab.id },
                files: ['content.js']
            });

            // Send message to content script to get data (cleaner than return from executeScript sometimes)
            const response = await chrome.tabs.sendMessage(tab.id, { action: "getPageData" });

            if (!response) throw new Error("Failed to extract page data");

            // 3. Call Backend Ingest
            const ingestRes = await fetch('http://localhost:8000/ingest/extension', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(response)
            });

            if (!ingestRes.ok) throw new Error("Ingestion failed");
            const ingestData = await ingestRes.json();
            currentProductContext = ingestData.product_context; // Store context for chat

            // 4. Call Backend Process
            const processRes = await fetch('http://localhost:8000/process', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ product_context: ingestData.product_context })
            });

            if (!processRes.ok) throw new Error("Processing failed");
            const result = await processRes.json();

            // 5. Render Results
            renderResults(result);
            loadingView.classList.add('hidden');
            resultView.classList.remove('hidden');

        } catch (err) {
            console.error(err);
            loadingView.classList.add('hidden');
            mainView.classList.remove('hidden');
            errorMsg.textContent = err.message || "An error occurred";
            errorMsg.classList.remove('hidden');
        }
    });

    // Chat Logic
    const chatInput = document.getElementById('chat-input');
    const chatSendBtn = document.getElementById('chat-send-btn');
    const chatHistory = document.getElementById('chat-history');

    chatSendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    async function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        if (!currentProductContext) {
            appendMessage("Error: No product context available. Please analyze a page first.", 'bot');
            return;
        }

        // Add user message
        appendMessage(message, 'user');
        chatInput.value = '';

        // Show loading state (optional, could add a typing indicator)
        const loadingId = appendMessage("Thinking...", 'bot');

        try {
            const res = await fetch('http://localhost:8000/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    product_context: currentProductContext,
                    message: message
                })
            });

            if (!res.ok) throw new Error("Chat request failed");
            const data = await res.json();

            // Remove loading message and add response
            const loadingEl = document.querySelector(`[data-msg-id="${loadingId}"]`);
            if (loadingEl) loadingEl.remove();

            appendMessage(data.response, 'bot');

        } catch (err) {
            console.error(err);
            const loadingEl = document.querySelector(`[data-msg-id="${loadingId}"]`);
            if (loadingEl) loadingEl.textContent = "Error: Failed to get response.";
        }
    }

    function appendMessage(text, sender) {
        const div = document.createElement('div');
        div.className = `chat-message ${sender}`;
        div.textContent = text;
        const id = Date.now();
        div.setAttribute('data-msg-id', id);
        chatHistory.appendChild(div);
        chatHistory.scrollTop = chatHistory.scrollHeight;
        return id;
    }

    function renderResults(data) {
        const { tcs_score, tcs_band, tcs_components, trust_summary } = data;

        // Score
        const scoreEl = document.getElementById('tcs-score');
        scoreEl.textContent = Math.round(tcs_score * 100);
        scoreEl.style.borderColor = getColor(tcs_score);
        scoreEl.style.color = getColor(tcs_score);

        // Band
        const bandEl = document.getElementById('tcs-band');
        bandEl.textContent = tcs_band;

        // Verdict
        document.getElementById('verdict-text').textContent = trust_summary.overall_verdict;

        // Metrics
        document.getElementById('metric-groundedness').textContent = Math.round(tcs_components.groundedness * 100) + '%';
        document.getElementById('metric-accuracy').textContent = Math.round(tcs_components.accuracy * 100) + '%';
        document.getElementById('metric-coverage').textContent = Math.round(tcs_components.coverage * 100) + '%';

        // Aspects
        const list = document.getElementById('aspects-list');
        list.innerHTML = '';
        trust_summary.aspects.forEach(aspect => {
            const div = document.createElement('div');
            div.className = 'aspect-item';
            div.innerHTML = `
        <div class="aspect-header">
          <span>${aspect.name}</span>
          <span style="color: ${getColor(aspect.score_0_10 / 10)}">${aspect.score_0_10}/10</span>
        </div>
        <div class="aspect-pros">
          ${aspect.pros.slice(0, 2).map(p => `• ${p}`).join('<br>')}
        </div>
      `;
            list.appendChild(div);
        });
    }

    function getColor(score) {
        if (score >= 0.8) return '#4ade80'; // Green
        if (score >= 0.5) return '#facc15'; // Yellow
        return '#f87171'; // Red
    }
});
