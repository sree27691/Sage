document.addEventListener('DOMContentLoaded', () => {
    // --- Elements ---
    const tabs = document.querySelectorAll('.tab-btn');
    const views = document.querySelectorAll('.view');
    const tabIndicator = document.querySelector('.tab-indicator');
    const analyzeBtn = document.getElementById('analyze-btn');
    const initialState = document.getElementById('initial-state');
    const pipelineView = document.getElementById('pipeline-view');
    const resultView = document.getElementById('result-view');
    const tcsScoreEl = document.getElementById('tcs-score');
    const tcsBandEl = document.getElementById('tcs-band');
    const gaugeFill = document.querySelector('.gauge-fill');
    const conflictBanner = document.getElementById('conflict-banner');
    const pillars = document.querySelectorAll('.pillar .bar');
    const aspectsList = document.getElementById('aspects-list');
    const quickReplies = document.getElementById('quick-replies');
    const chatInput = document.getElementById('chat-input');
    const chatSendBtn = document.getElementById('chat-send-btn');
    const chatHistory = document.getElementById('chat-history');
    const errorMsg = document.getElementById('error-msg');

    // --- State ---
    let currentProductContext = null;
    const targetScore = 72; // Default, will be updated

    // --- Tab Switching ---
    tabs.forEach((tab, index) => {
        tab.addEventListener('click', () => {
            // Update Tab UI
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Move Indicator
            if (index === 0) {
                tabIndicator.style.transform = 'translateX(0)';
            } else {
                tabIndicator.style.transform = 'translateX(100%)';
            }

            // Switch View
            views.forEach(v => v.classList.remove('active'));
            if (tab.dataset.tab === 'trust-card') {
                document.getElementById('trust-card-view').classList.add('active');
            } else {
                document.getElementById('sage-chat-view').classList.add('active');
            }
        });
    });

    // --- Analysis Flow ---
    analyzeBtn.addEventListener('click', async () => {
        console.log('[SAGE] Analyze button clicked');
        initialState.classList.add('hidden');
        pipelineView.classList.remove('hidden');
        errorMsg.classList.add('hidden');

        // Start visual steps
        const stepsInterval = runPipelineVisuals();

        try {
            // 1. Get Active Tab
            console.log('[SAGE] Step 1: Getting active tab...');
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            if (!tab.id) throw new Error("No active tab found");
            console.log('[SAGE] Active tab:', tab.url);

            // 2. Execute Script to get Data
            console.log('[SAGE] Step 2: Injecting content script...');
            const results = await chrome.scripting.executeScript({
                target: { tabId: tab.id },
                files: ['content.js']
            });
            console.log('[SAGE] Content script injected:', results);

            // Send message to content script to get data
            console.log('[SAGE] Step 3: Requesting page data...');
            const response = await chrome.tabs.sendMessage(tab.id, { action: "getPageData" });
            console.log('[SAGE] Page data received:', {
                url: response?.url,
                domSize: response?.dom_html?.length,
                imagesCount: response?.images?.length,
                hasStructuredContent: !!response?.structured_content
            });

            if (!response) throw new Error("Failed to extract page data");

            // 3. Call Backend Ingest
            console.log('[SAGE] Step 4: Calling backend /ingest/extension...');
            const ingestRes = await fetch('http://localhost:8001/ingest/extension', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(response)
            });

            console.log('[SAGE] Ingest response status:', ingestRes.status);
            if (!ingestRes.ok) {
                const errorText = await ingestRes.text();
                console.error('[SAGE] Ingest failed:', errorText);
                throw new Error(`Ingestion failed: ${errorText}`);
            }

            const ingestData = await ingestRes.json();
            console.log('[SAGE] Ingest successful');
            currentProductContext = ingestData.product_context; // Store context for chat

            // 4. Call Backend Process
            console.log('[SAGE] Step 5: Calling backend /process...');
            const processRes = await fetch('http://localhost:8001/process', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ product_context: ingestData.product_context })
            });

            if (!processRes.ok) throw new Error("Processing failed");
            const result = await processRes.json();
            console.log('[SAGE] Processing complete:', result);

            // Stop visuals and show results
            clearInterval(stepsInterval);
            finishPipelineVisuals();

            setTimeout(() => {
                pipelineView.classList.add('hidden');
                resultView.classList.remove('hidden');
                renderResults(result);
            }, 500);

        } catch (err) {
            console.error('[SAGE] ERROR:', err);
            console.error('[SAGE] Error stack:', err.stack);
            clearInterval(stepsInterval);
            pipelineView.classList.add('hidden');
            initialState.classList.remove('hidden');
            errorMsg.textContent = err.message || "An error occurred";
            errorMsg.classList.remove('hidden');
        }
    });

    function runPipelineVisuals() {
        const steps = ['retrieving', 'analyzing', 'verifying'];
        let currentStep = 0;

        // Initial state
        document.getElementById(`step-${steps[0]}`).classList.add('active');

        return setInterval(() => {
            if (currentStep < steps.length - 1) {
                // Mark current as completed
                document.getElementById(`step-${steps[currentStep]}`).classList.remove('active');
                document.getElementById(`step-${steps[currentStep]}`).classList.add('completed');

                currentStep++;

                // Activate next
                document.getElementById(`step-${steps[currentStep]}`).classList.add('active');
            }
        }, 2000); // Advance every 2s just for visuals if API is slow
    }

    function finishPipelineVisuals() {
        const steps = ['retrieving', 'analyzing', 'verifying'];
        steps.forEach(s => {
            const el = document.getElementById(`step-${s}`);
            el.classList.remove('active');
            el.classList.add('completed');
        });
    }

    function renderResults(data) {
        console.log('[RENDER] Full data received:', data);
        console.log('[RENDER] Trust summary:', data.trust_summary);
        console.log('[RENDER] Aspects:', data.trust_summary?.aspects);

        const { tcs_score, tcs_band, tcs_components, trust_summary } = data;

        // 1. Score Reveal
        animateScore(tcs_score * 100);

        // 2. Conflict Banner
        if (trust_summary.conflicts && trust_summary.conflicts.length > 0) {
            setTimeout(() => {
                conflictBanner.classList.remove('hidden');
                conflictBanner.classList.add('slide-in');

                // Populate conflict details
                const conflictDetails = document.getElementById('conflict-details');
                conflictDetails.innerHTML = trust_summary.conflicts.map(conflict =>
                    `<div class="conflict-item">• ${conflict}</div>`
                ).join('');

                // Add expand/collapse functionality
                document.getElementById('conflict-expand').addEventListener('click', function () {
                    conflictDetails.classList.toggle('hidden');
                    this.textContent = conflictDetails.classList.contains('hidden') ? '▼' : '▲';
                });
            }, 500);
        }

        // 3. Trust Pillars
        const metrics = [
            tcs_components.groundedness,
            tcs_components.accuracy,
            tcs_components.coverage,
            tcs_components.conflict_detection,
            tcs_components.uncertainty
        ];

        pillars.forEach((bar, index) => {
            setTimeout(() => {
                bar.style.height = `${metrics[index] * 100}%`;
            }, 800 + (index * 200));
        });

        // 4. Inject Aspects
        console.log('[RENDER] Calling injectAspects with:', trust_summary.aspects);
        injectAspects(trust_summary.aspects);

        // 5. Show Quick Replies in Chat
        quickReplies.classList.remove('hidden');

        // Add initial bot message
        if (chatHistory.children.length === 0) {
            addMessage("Hello! I've analyzed this product. Ask me anything about its specs, reviews, or hidden details.", 'bot');
        }
    }

    function animateScore(target) {
        let start = 0;
        const duration = 1500;
        const startTime = performance.now();

        // Handle 0 score explicitly
        if (target === 0) {
            tcsScoreEl.textContent = "0";
            gaugeFill.style.strokeDashoffset = 2 * Math.PI * 45; // Empty
            tcsBandEl.textContent = "CAUTION";
            tcsBandEl.classList.remove('hidden');
            return;
        }

        function updateScore(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const ease = 1 - Math.pow(1 - progress, 3);

            const current = Math.floor(ease * target);
            tcsScoreEl.textContent = current;

            // Update Gauge
            const circumference = 2 * Math.PI * 45;
            const offset = circumference - (ease * (target / 100) * circumference);
            gaugeFill.style.strokeDashoffset = offset;

            if (progress < 1) {
                requestAnimationFrame(updateScore);
            } else {
                tcsBandEl.textContent = getBand(target);
                tcsBandEl.classList.remove('hidden');
            }
        }
        requestAnimationFrame(updateScore);
    }

    function getBand(score) {
        if (score >= 80) return "TRUSTED";
        if (score >= 60) return "PILOT";
        return "CAUTION";
    }

    function injectAspects(aspects) {
        aspectsList.innerHTML = '';
        aspects.forEach(aspect => {
            const item = document.createElement('div');
            item.className = 'aspect-item';
            item.innerHTML = `
        <div class="aspect-header">
          <span>${aspect.name}</span>
          <span class="aspect-score ${getScoreClass(aspect.score_0_10)}">${aspect.score_0_10}/10</span>
        </div>
        <div class="aspect-content hidden">
          <p><strong>Pros:</strong> ${aspect.pros.join(', ')}</p>
          <p><strong>Cons:</strong> ${aspect.cons.join(', ')}</p>
        </div>
      `;

            item.querySelector('.aspect-header').addEventListener('click', () => {
                const content = item.querySelector('.aspect-content');
                content.classList.toggle('hidden');
            });

            aspectsList.appendChild(item);
        });
    }

    function getScoreClass(score) {
        if (score >= 8) return 'high';
        if (score >= 5) return 'medium';
        return 'low';
    }

    // --- Chat Logic ---
    chatSendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    async function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        if (!currentProductContext) {
            addMessage("Please analyze a product first so I have context!", 'bot');
            return;
        }

        // User Message
        addMessage(message, 'user');
        chatInput.value = '';

        // Loading
        const loadingId = addMessage("Thinking...", 'bot');

        try {
            const res = await fetch('http://localhost:8001/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    product_context: currentProductContext,
                    message: message
                })
            });

            if (!res.ok) throw new Error("Chat request failed");
            const data = await res.json();

            // Remove loading
            const loadingEl = document.querySelector(`[data-msg-id="${loadingId}"]`);
            if (loadingEl) loadingEl.remove();

            addMessage(data.response, 'bot');

        } catch (err) {
            console.error(err);
            const loadingEl = document.querySelector(`[data-msg-id="${loadingId}"]`);
            if (loadingEl) loadingEl.textContent = "Error: Failed to get response.";
        }
    }

    function addMessage(text, sender) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `chat-message ${sender}`;
        msgDiv.textContent = text;
        const id = Date.now();
        msgDiv.setAttribute('data-msg-id', id);
        chatHistory.appendChild(msgDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
        return id;
    }

    // Quick Replies
    quickReplies.querySelectorAll('button').forEach(btn => {
        btn.addEventListener('click', (e) => {
            chatInput.value = e.target.textContent;
            sendMessage();
        });
    });

});
