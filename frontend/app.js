document.addEventListener('DOMContentLoaded', () => {
    // ─── BACKEND URL CONFIG ───────────────────────────────────────────────────
    // Auto-detects local vs Vercel production.
    // On localhost:  requests go to the same local FastAPI server (port 8001).
    // On Vercel:     requests go to Hugging Face Spaces backend (no 10s timeout).
    //
    // ► After deploying to HF Spaces, replace the URL below:
    //   Format:  https://{your-hf-username}-sentinel-zero.hf.space
    const BACKEND_URL = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
        ? ''
        : 'https://REPLACE_WITH_YOUR_HF_SPACE_URL';
    // ─────────────────────────────────────────────────────────────────────────

    // State management
    let alerts = [];
    let activeAlertId = null;
    let eventSource = null;
    let currentMode = 'splunk'; // 'splunk' or 'sift'
    let scrollPercent = 0;

    // DOM Elements
    const splunkAlertsContainer = document.getElementById('splunk-alerts-container');
    const modeBadge = document.getElementById('mode-badge');
    const btnTriageAll = document.getElementById('btn-triage-all');
    const btnRunForensics = document.getElementById('btn-run-forensics');
    const statusText = document.getElementById('status-text');
    const statusDot = document.querySelector('.status-dot');
    
    // Scrollytelling Sections
    const sections = {
        intro: document.getElementById('sec-intro'),
        splunk: document.getElementById('sec-splunk'),
        sift: document.getElementById('sec-sift'),
        runbook: document.getElementById('sec-runbook')
    };

    // Diagnostics / Outputs
    const confidenceBadge = document.getElementById('confidence-badge');
    const hallucinationReason = document.getElementById('hallucination-reason');
    const correctedFindings = document.getElementById('corrected-findings');
    const runbookPanel = document.getElementById('sec-runbook');
    const runbookContent = document.getElementById('runbook-content');
    const btnCopyRunbook = document.getElementById('btn-copy-runbook');
    const forensicTask = document.getElementById('forensic-task');

    // Canvas Background Particle Grid & Frame Scrubber
    const canvas = document.getElementById('bg-canvas');
    const ctx = canvas.getContext('2d');
    let particles = [];
    const numParticles = 200;
    const perspective = 400;
    let width = window.innerWidth;
    let height = window.innerHeight;

    // Frame Sequence Preloading
    const totalFrames = 300;
    const frames = [];
    let loadedFramesCount = 0;
    let framesLoaded = false;

    function preloadFrames() {
        for (let i = 1; i <= totalFrames; i++) {
            const img = new Image();
            const frameNum = String(i).padStart(3, '0');
            img.src = `/frames/frame_${frameNum}.jpg`;
            img.onload = () => {
                loadedFramesCount++;
                if (loadedFramesCount === totalFrames) {
                    framesLoaded = true;
                    console.log("All 300 frames preloaded successfully.");
                }
            };
            img.onerror = () => {
                // Fallback will naturally occur if frames fail to load
            };
            frames.push(img);
        }
    }
    preloadFrames();

    // Video Background Auto-Detector & Scrubber (Fallback)
    const video = document.getElementById('bg-video');
    let useVideo = false;

    video.addEventListener('loadedmetadata', () => {
        if (!framesLoaded) {
            useVideo = true;
            canvas.style.display = 'none';
            video.style.display = 'block';
            video.style.position = 'fixed';
            video.style.top = '0';
            video.style.left = '0';
            video.style.width = '100vw';
            video.style.height = '100vh';
            video.style.objectFit = 'cover';
            video.style.zIndex = '-2';
            console.log("Sentinel Background Video (bg_scroll.mp4) detected. Canvas fallback disabled.");
        }
    });

    let lastFrameIndex = -1;
    let windowResized = true;

    // Resize Canvas
    function resizeCanvas() {
        width = window.innerWidth;
        height = window.innerHeight;
        canvas.width = width;
        canvas.height = height;
        windowResized = true;
    }
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    // Particle system removed to prevent visual clutter and lag

    // Draw frame as background-size: cover
    function drawCoverImage(img) {
        if (!img || img.naturalWidth === 0) return false;
        const imgRatio = img.naturalWidth / img.naturalHeight;
        const canvasRatio = canvas.width / canvas.height;
        let drawWidth, drawHeight, x, y;

        if (canvasRatio > imgRatio) {
            drawWidth = canvas.width;
            drawHeight = canvas.width / imgRatio;
            x = 0;
            y = (canvas.height - drawHeight) / 2;
        } else {
            drawWidth = canvas.height * imgRatio;
            drawHeight = canvas.height;
            x = (canvas.width - drawWidth) / 2;
            y = 0;
        }

        ctx.drawImage(img, x, y, drawWidth, drawHeight);
        return true;
    }

    // Render 3D Scrollytelling Canvas
    function drawCanvas() {
        let frameDrawn = false;
        if (loadedFramesCount > 0) {
            const frameIndex = Math.min(totalFrames - 1, Math.floor(scrollPercent * totalFrames));
            if (frameIndex !== lastFrameIndex || windowResized) {
                const frameImg = frames[frameIndex];
                if (frameImg && frameImg.complete) {
                    ctx.clearRect(0, 0, width, height);
                    frameDrawn = drawCoverImage(frameImg);
                    if (frameDrawn) {
                        lastFrameIndex = frameIndex;
                        windowResized = false;
                    }
                }
            } else {
                frameDrawn = true; // We already have the correct frame painted
            }
        }

        // Fallback removed. Just wait for frames to load.
        if (!frameDrawn && totalFrames > 0 && loadedFramesCount < 10) {
            ctx.fillStyle = '#07090e';
            ctx.fillRect(0, 0, width, height);
            ctx.fillStyle = '#06b6d4';
            ctx.font = '20px monospace';
            ctx.textAlign = 'center';
            ctx.fillText('INITIALIZING SYSTEM...', width / 2, height / 2);
        }
        requestAnimationFrame(drawCanvas);
    }
    requestAnimationFrame(drawCanvas);

    // Scrollytelling Section Triggers on Scroll
    window.addEventListener('scroll', () => {
        const scrollTop = window.scrollY;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        scrollPercent = docHeight > 0 ? scrollTop / docHeight : 0;

        // Scrub video if active
        if (useVideo && video.duration) {
            video.currentTime = scrollPercent * video.duration;
        }

        // Toggle sections based on scroll percent
        if (scrollPercent < 0.20) {
            revealSection('intro');
            updateHeaderMode('SPLUNK MODE', 'splunk');
        } else if (scrollPercent >= 0.20 && scrollPercent < 0.50) {
            revealSection('splunk');
            updateHeaderMode('SPLUNK MODE', 'splunk');
            currentMode = 'splunk';
        } else if (scrollPercent >= 0.50 && scrollPercent < 0.80) {
            revealSection('sift');
            updateHeaderMode('SIFT FORENSICS MODE', 'sift');
            currentMode = 'sift';
        } else {
            revealSection('runbook');
            updateHeaderMode('CONTAINMENT VAULT', 'sift');
        }
    });

    function revealSection(activeKey) {
        Object.keys(sections).forEach(key => {
            if (key === activeKey) {
                sections[key].classList.add('visible');
            } else {
                sections[key].classList.remove('visible');
            }
        });
    }

    function updateHeaderMode(text, className) {
        modeBadge.innerText = text;
        modeBadge.className = `system-mode-badge ${className}`;
    }

    // Fetch alerts initially
    fetchAlerts();

    async function fetchAlerts() {
        try {
            const response = await fetch(`${BACKEND_URL}/api/alerts`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            alerts = await response.json();
            renderAlerts();
        } catch (error) {
            console.error('Error fetching alerts:', error);
            splunkAlertsContainer.innerHTML = `
                <div class="loading-state text-danger">
                    <i class="fa-solid fa-triangle-exclamation"></i>
                    Failed to reach backend. If on Vercel, update BACKEND_URL in app.js with your HF Space URL.
                </div>
            `;
        }
    }

    function renderAlerts() {
        if (alerts.length === 0) {
            splunkAlertsContainer.innerHTML = '<div class="loading-state">No active alerts found.</div>';
            return;
        }

        splunkAlertsContainer.innerHTML = '';
        alerts.forEach(alert => {
            const alertItem = document.createElement('div');
            alertItem.className = `alert-item severity-${alert.severity.toLowerCase()} ${activeAlertId === alert.alert_id ? 'active' : ''}`;
            alertItem.dataset.id = alert.alert_id;
            
            alertItem.innerHTML = `
                <div class="alert-header">
                    <span class="alert-sig">${alert.signature}</span>
                    <span class="alert-badge ${alert.severity.toLowerCase()}">${alert.severity}</span>
                </div>
                <div class="alert-meta-row">
                    <span><i class="fa-solid fa-desktop"></i> ${alert.host}</span>
                    <span><i class="fa-solid fa-user"></i> ${alert.user}</span>
                </div>
            `;

            alertItem.addEventListener('click', () => {
                document.querySelectorAll('.alert-item').forEach(item => item.classList.remove('active'));
                alertItem.classList.add('active');
                activeAlertId = alert.alert_id;
            });

            splunkAlertsContainer.appendChild(alertItem);
        });

        if (alerts.length > 0 && !activeAlertId) {
            const firstAlert = splunkAlertsContainer.querySelector('.alert-item');
            firstAlert.classList.add('active');
            activeAlertId = alerts[0].alert_id;
        }
    }

    // Trigger triage/investigation
    btnTriageAll.addEventListener('click', () => {
        if (alerts.length === 0 || btnTriageAll.disabled) return;
        const selectedAlert = alerts.find(a => a.alert_id === activeAlertId) || alerts[0];
        const task = `Acknowledge and triage Splunk alert ${selectedAlert.alert_id} (${selectedAlert.signature}) on host ${selectedAlert.host}. Log execution stages.`;
        setButtonLoading(btnTriageAll, true, 'Investigating...');
        scrollToSection('splunk');
        startInvestigation('splunk', task, { splunk_alerts: [selectedAlert] });
    });

    btnRunForensics.addEventListener('click', () => {
        if (btnRunForensics.disabled) return;
        const taskText = forensicTask.value.trim();
        setButtonLoading(btnRunForensics, true, 'Running Audit...');
        scrollToSection('sift');
        startInvestigation('sift', taskText, {
            forensic_image: "SEC-PROD-SRV01_disk.raw",
            memory_dump: "SEC-PROD-SRV01_memory.dmp",
            sift_tools: ["fls", "volatility3", "grep"]
        });
    });

    // Forensic target row click selection
    document.querySelectorAll('.target-row').forEach(row => {
        row.style.cursor = 'pointer';
        row.addEventListener('click', () => {
            document.querySelectorAll('.target-row').forEach(r => r.classList.remove('active'));
            row.classList.add('active');
        });
    });

    // Start Investigation & SSE streaming
    function startInvestigation(mode, task, context) {
        // Clear consoles
        const consoleStream = document.getElementById(`console-stream-${mode}`);
        const iterationBadge = document.getElementById(`iteration-badge-${mode}`);
        
        consoleStream.innerHTML = '';
        iterationBadge.innerText = 'Initializing...';
        
        statusText.innerText = 'INVESTIGATION IN PROGRESS';
        statusDot.className = 'status-dot pulse';

        if (eventSource) {
            eventSource.close();
        }

        const url = `${BACKEND_URL}/api/investigate?mode=${encodeURIComponent(mode)}&task=${encodeURIComponent(task)}`;
        eventSource = new EventSource(url);

        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.type === 'log') {
                appendLogLine(mode, data);
                if (data.message.includes('[ITERATION')) {
                    const match = data.message.match(/\[ITERATION (\d+)\]/);
                    if (match) {
                        iterationBadge.innerText = `Iteration ${match[1]}`;
                    }
                }
            } 
            else if (data.type === 'tool_call') {
                appendToolCallLine(mode, data);
            } 
            else if (data.type === 'tool_result') {
                appendToolResultLine(mode, data);
            } 
            else if (data.type === 'self_correction') {
                appendSelfCorrectionLine(mode, data);
                updateSelfCorrectionPanel(data);
            }
            else if (data.type === 'result') {
                finalizeInvestigation(data.data);
            }
            else if (data.type === 'error') {
                appendLogLine(mode, {
                    timestamp: new Date().toISOString(),
                    type: 'log',
                    level: 'ERROR',
                    message: `Error: ${data.message}`
                });
                stopStatus();
            }
        };

        eventSource.onerror = () => {
            if (statusText.innerText !== 'INVESTIGATION COMPLETE') {
                const timeoutMsg = "⚠️ Vercel 10s Serverless Execution Limit Reached. Connection severed by host. To view the full AI autonomous resolution without limits, please run Sentinel Zero locally.";
                
                appendLogLine(mode, {
                    timestamp: new Date().toISOString(),
                    level: 'TIMEOUT',
                    message: timeoutMsg
                });
                
                const runbookContent = document.getElementById('runbook-content');
                if (runbookContent.innerHTML.includes('loading-state')) {
                    runbookContent.innerHTML = `<div class="loading-state text-danger"><i class="fa-solid fa-triangle-exclamation"></i> ${timeoutMsg}</div>`;
                }
                
                statusText.innerText = 'CONNECTION SEVERED (VERCEL TIMEOUT)';
                statusDot.className = 'status-dot';
            }
            eventSource.close();
        };
    }

    function appendLogLine(mode, data) {
        const stream = document.getElementById(`console-stream-${mode}`);
        const time = data.timestamp ? new Date(data.timestamp).toLocaleTimeString() : '';
        const line = document.createElement('div');
        line.className = 'log-line';
        line.innerHTML = `
            <span class="log-time">${time}</span>
            <span class="log-tag info">[${data.level}]</span>
            <span class="log-text">${escapeHtml(data.message)}</span>
        `;
        stream.appendChild(line);
        stream.scrollTop = stream.scrollHeight;
    }

    function appendToolCallLine(mode, data) {
        const stream = document.getElementById(`console-stream-${mode}`);
        const time = data.timestamp ? new Date(data.timestamp).toLocaleTimeString() : '';
        const line = document.createElement('div');
        line.className = 'log-line tool-call';
        line.innerHTML = `
            <span class="log-time">${time}</span>
            <span class="log-tag tool">[TOOL]</span>
            <span class="log-text">Invoked <strong style="color: var(--color-accent);">${escapeHtml(data.tool)}</strong>: <code>${escapeHtml(JSON.stringify(data.arguments))}</code></span>
        `;
        stream.appendChild(line);
        stream.scrollTop = stream.scrollHeight;
    }

    function appendToolResultLine(mode, data) {
        const stream = document.getElementById(`console-stream-${mode}`);
        const time = data.timestamp ? new Date(data.timestamp).toLocaleTimeString() : '';
        const line = document.createElement('div');
        line.className = 'log-line tool-result';
        
        let outputStr = typeof data.result === 'object' ? JSON.stringify(data.result) : String(data.result);
        if (outputStr.length > 200) {
            outputStr = outputStr.substring(0, 200) + '... [TRUNCATED]';
        }
        
        line.innerHTML = `
            <span class="log-time">${time}</span>
            <span class="log-tag result">[RESULT]</span>
            <span class="log-text">Returned: <code style="color: #a7f3d0;">${escapeHtml(outputStr)}</code></span>
        `;
        stream.appendChild(line);
        stream.scrollTop = stream.scrollHeight;
    }

    function appendSelfCorrectionLine(mode, data) {
        const stream = document.getElementById(`console-stream-${mode}`);
        const time = data.timestamp ? new Date(data.timestamp).toLocaleTimeString() : '';
        const line = document.createElement('div');
        line.className = 'log-line self-correction';
        line.innerHTML = `
            <span class="log-time">${time}</span>
            <span class="log-tag correct">[CORRECT]</span>
            <span class="log-text">Audit: <strong>${escapeHtml(data.reason)}</strong></span>
        `;
        stream.appendChild(line);
        stream.scrollTop = stream.scrollHeight;
    }

    function updateSelfCorrectionPanel(data) {
        hallucinationReason.innerText = data.reason;
        
        let findingsList = "";
        if (Array.isArray(data.findings)) {
            data.findings.forEach(f => {
                findingsList += `• [${f.severity}] ${f.finding}\n  Evidence: ${f.evidence}\n\n`;
            });
        } else {
            findingsList = JSON.stringify(data.findings, null, 2);
        }
        correctedFindings.innerText = findingsList || "No findings recorded.";
        
        if (data.confidence) {
            confidenceBadge.innerText = `Confidence: ${Math.round(data.confidence * 100)}%`;
        }
    }

    let activeRunbookMarkdown = "";
    function finalizeInvestigation(resultData) {
        stopStatus();
        
        // Auto scroll to Section 4 (Runbook/Auditor) to showcase findings
        window.scrollTo({
            top: document.documentElement.scrollHeight - window.innerHeight,
            behavior: 'smooth'
        });

        // Set iteration badges to completed
        document.getElementById('iteration-badge-splunk').innerText = 'Completed';
        document.getElementById('iteration-badge-sift').innerText = 'Completed';

        confidenceBadge.innerText = `Confidence: ${Math.round(resultData.confidence * 100)}%`;
        activeRunbookMarkdown = resultData.runbook;
        runbookContent.innerHTML = parseMarkdown(resultData.runbook);

        if (eventSource) {
            eventSource.close();
        }
    }

    function stopStatus() {
        statusText.innerText = 'SYSTEM ACTIVE';
        statusDot.className = 'status-dot';
        setButtonLoading(btnTriageAll, false, '<i class="fa-solid fa-play"></i> Triage Selected Alert');
        setButtonLoading(btnRunForensics, false, '<i class="fa-solid fa-wand-magic-sparkles"></i> Run Forensic Audit');
    }

    // Helper: toggle button loading state
    function setButtonLoading(btn, isLoading, label) {
        btn.disabled = isLoading;
        btn.innerHTML = isLoading
            ? `<i class="fa-solid fa-spinner fa-spin"></i> ${label}`
            : label;
    }

    // Helper: smooth-scroll to a scrollytelling section
    function scrollToSection(key) {
        const targets = { intro: 0.05, splunk: 0.33, sift: 0.63, runbook: 0.90 };
        const pct = targets[key] ?? 0.33;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        window.scrollTo({ top: pct * docHeight, behavior: 'smooth' });
    }

    // Copy Markdown Runbook
    btnCopyRunbook.addEventListener('click', () => {
        if (!activeRunbookMarkdown) return;
        navigator.clipboard.writeText(activeRunbookMarkdown).then(() => {
            const originalText = btnCopyRunbook.innerHTML;
            btnCopyRunbook.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
            setTimeout(() => {
                btnCopyRunbook.innerHTML = originalText;
            }, 2000);
        });
    });

    // Basic markdown parsing
    function parseMarkdown(md) {
        if (!md) return "";
        let html = md;
        html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
        html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
        html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        html = html.replace(/^\s*[\-\*]\s+(.*$)/gim, '<li>$1</li>');
        html = html.replace(/(<li>.*<\/li>)/gms, '<ul>$1</ul>');
        html = html.replace(/```(.*?)\n([\s\S]*?)```/gm, '<pre><code>$2</code></pre>');
        
        html = html.split('\n\n').map(p => {
            if (p.trim().startsWith('<h') || p.trim().startsWith('<u') || p.trim().startsWith('<p') || p.trim().startsWith('<pre')) {
                return p;
            }
            return `<p>${p.replace(/\n/g, '<br>')}</p>`;
        }).join('\n');
        return html;
    }

    function escapeHtml(text) {
        // Defensive: coerce to string — prevents TypeError on null/undefined/number values
        const str = String(text == null ? '' : text);
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return str.replace(/[&<>"']/g, m => map[m]);
    }

    // --- Dock System Logic ---
    const appDock = document.getElementById('app-dock');
    const minimizeButtons = document.querySelectorAll('.btn-minimize');

    minimizeButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const panel = e.target.closest('.glass-panel');
            if (!panel) return;
            
            const title = panel.getAttribute('data-title') || 'Panel';
            const iconClass = panel.getAttribute('data-icon') || 'fa-solid fa-window-restore';
            
            // Minimize panel
            panel.classList.add('minimized-card');
            
            // Create dock orb
            const orb = document.createElement('div');
            orb.className = 'dock-orb';
            orb.title = `Restore: ${title}`;
            orb.innerHTML = `<i class="${iconClass}"></i>`;
            
            // Restore event
            orb.addEventListener('click', () => {
                orb.remove();
                panel.classList.remove('minimized-card');
            });
            
            appDock.appendChild(orb);
        });
    });
});
