"""FastAPI application entrypoint for the autonomous content-agent prototype."""

import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response
from fastapi.middleware.cors import CORSMiddleware

from content_agent.settings import get_settings
from content_agent.api.schemas import RunCreateRequest
from content_agent.models.draft import ContentDraftRecord
from content_agent.pipeline import execute_content_pipeline, RUNS_STORE
from content_agent.export.markdown import MarkdownExporter
from content_agent.api.routes import (
    briefs_router,
    runs_router,
    approvals_router,
    exports_router,
)

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description="Autonomous multi-agent content generation system with LangGraph.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount modular API routers
app.include_router(briefs_router, prefix="/api")
app.include_router(runs_router, prefix="/api")
app.include_router(approvals_router, prefix="/api")
app.include_router(exports_router, prefix="/api")


@app.get("/health")
def health_check():
    """Service health and runtime configuration summary."""
    tavily_key = bool(os.getenv("TAVILY_API_KEY") or os.getenv("SEARCH_API_KEY"))
    llm_key = bool(os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY"))

    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "app_env": settings.app_env,
        "mode": "live" if (tavily_key and llm_key) else "demo",
        "workflow": "autonomous_langgraph",
        "integrations": {
            "search_configured": tavily_key,
            "llm_configured": llm_key,
        },
    }


@app.get("/", response_class=HTMLResponse)
def index_page():
    """Render the single-page prototype web interface."""
    return HTML_CONTENT


HTML_CONTENT = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Content Agent — Autonomous Multi-Agent Pipeline</title>
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <style>
    :root {
      --bg: #0b1120;
      --card-bg: #1e293b;
      --border: #334155;
      --primary: #3b82f6;
      --primary-hover: #2563eb;
      --success: #10b981;
      --warning: #f59e0b;
      --danger: #ef4444;
      --purple: #8b5cf6;
      --text: #f8fafc;
      --text-muted: #94a3b8;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.6;
      padding: 24px;
    }
    .container { max-width: 1280px; margin: 0 auto; }
    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 20px;
      margin-bottom: 24px;
      border-bottom: 1px solid var(--border);
    }
    .logo-group h1 { font-size: 1.6rem; color: #fff; font-weight: 700; }
    .logo-group p { font-size: 0.9rem; color: var(--text-muted); }
    .status-badge {
      padding: 6px 14px;
      border-radius: 9999px;
      font-size: 0.8rem;
      font-weight: 600;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .badge-demo { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
    .badge-live { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-purple { background: rgba(139, 92, 246, 0.15); color: #c084fc; border: 1px solid rgba(139, 92, 246, 0.3); }

    .grid { display: grid; grid-template-columns: 360px 1fr; gap: 24px; }
    @media (max-width: 950px) { .grid { grid-template-columns: 1fr; } }

    .card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .card h2 { font-size: 1.15rem; margin-bottom: 16px; color: #fff; border-bottom: 1px solid var(--border); padding-bottom: 8px; }

    .form-group { margin-bottom: 16px; }
    label { display: block; font-size: 0.85rem; font-weight: 600; margin-bottom: 6px; color: var(--text-muted); }
    input[type="text"], input[type="number"], select, textarea {
      width: 100%;
      padding: 10px 12px;
      background: #0f172a;
      border: 1px solid var(--border);
      border-radius: 8px;
      color: var(--text);
      font-size: 0.9rem;
      transition: border-color 0.2s;
    }
    input:focus, select:focus, textarea:focus { outline: none; border-color: var(--primary); }

    .presets { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 6px; }
    .chip {
      background: #334155;
      padding: 4px 8px;
      border-radius: 6px;
      font-size: 0.75rem;
      cursor: pointer;
      color: #cbd5e1;
      border: none;
    }
    .chip:hover { background: #475569; color: #fff; }

    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 10px 18px;
      border-radius: 8px;
      font-weight: 600;
      font-size: 0.9rem;
      cursor: pointer;
      border: none;
      transition: all 0.2s;
      text-decoration: none;
    }
    .btn-primary { background: var(--primary); color: #fff; width: 100%; }
    .btn-primary:hover { background: var(--primary-hover); }
    .btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
    .btn-success { background: var(--success); color: #fff; }
    .btn-success:hover { background: #059669; }
    .btn-secondary { background: #334155; color: #f8fafc; }
    .btn-secondary:hover { background: #475569; }

    /* Autonomous Decision Cards */
    .agent-decisions {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      margin-bottom: 16px;
    }
    @media (max-width: 700px) { .agent-decisions { grid-template-columns: 1fr; } }
    .decision-card {
      background: #0f172a;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px 14px;
    }
    .decision-card h4 { font-size: 0.85rem; color: #94a3b8; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; }
    .decision-tag {
      display: inline-block;
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 0.75rem;
      font-weight: 700;
      margin-bottom: 6px;
    }
    .tag-approve { background: rgba(16, 185, 129, 0.2); color: #34d399; }
    .tag-revise { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
    .tag-research { background: rgba(59, 130, 246, 0.2); color: #60a5fa; }
    .tag-failure { background: rgba(239, 68, 68, 0.2); color: #f87171; }
    .decision-card p { font-size: 0.8rem; color: #cbd5e1; }

    .tabs { display: flex; gap: 8px; border-bottom: 1px solid var(--border); margin-bottom: 16px; flex-wrap: wrap; }
    .tab {
      padding: 8px 14px;
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--text-muted);
      cursor: pointer;
      border-bottom: 2px solid transparent;
    }
    .tab.active { color: var(--primary); border-bottom-color: var(--primary); }

    .tab-pane { display: none; }
    .tab-pane.active { display: block; }

    .draft-container {
      background: #0f172a;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 24px;
      font-size: 0.95rem;
      line-height: 1.7;
    }
    .draft-container h1 { font-size: 1.45rem; margin-bottom: 16px; color: #60a5fa; }
    .draft-container h2 { font-size: 1.2rem; margin-top: 20px; margin-bottom: 12px; color: #93c5fd; }
    .draft-container h3 { font-size: 1.05rem; margin-top: 16px; margin-bottom: 8px; color: #bfdbfe; }
    .draft-container p { margin-bottom: 14px; }
    .draft-container ul, .draft-container ol { margin-left: 20px; margin-bottom: 14px; }
    .draft-container blockquote {
      border-left: 4px solid var(--primary);
      padding-left: 14px;
      color: #94a3b8;
      margin: 14px 0;
      font-style: italic;
    }
    .draft-container a { color: #38bdf8; text-decoration: underline; }

    .source-card {
      background: #0f172a;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 14px;
      margin-bottom: 12px;
    }
    .source-card h4 { font-size: 0.95rem; margin-bottom: 4px; color: #38bdf8; }
    .source-card a { font-size: 0.8rem; color: #64748b; text-decoration: none; word-break: break-all; }
    .source-card a:hover { text-decoration: underline; color: #94a3b8; }
    .source-card p { font-size: 0.85rem; color: #cbd5e1; margin-top: 8px; }

    .check-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px;
      background: #0f172a;
      border: 1px solid var(--border);
      border-radius: 8px;
      margin-bottom: 8px;
    }
    .check-info strong { display: block; font-size: 0.9rem; color: #f8fafc; }
    .check-info small { color: #94a3b8; font-size: 0.8rem; }
    .badge-pass { background: rgba(16, 185, 129, 0.2); color: #34d399; padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; }
    .badge-warn { background: rgba(245, 158, 11, 0.2); color: #fbbf24; padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; }
    .badge-fail { background: rgba(239, 68, 68, 0.2); color: #f87171; padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; }

    .log-box {
      background: #0f172a;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 14px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 0.8rem;
      max-height: 400px;
      overflow-y: auto;
      color: #94a3b8;
    }
    .log-entry { margin-bottom: 6px; line-height: 1.4; border-bottom: 1px solid #1e293b; padding-bottom: 4px; }
    .log-entry:last-child { border-bottom: none; }

    .spinner {
      border: 3px solid rgba(255,255,255,0.2);
      border-radius: 50%;
      border-top: 3px solid #fff;
      width: 16px;
      height: 16px;
      animation: spin 1s linear infinite;
      display: inline-block;
    }
    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

    .placeholder-state {
      text-align: center;
      padding: 60px 20px;
      color: var(--text-muted);
    }
    .notice {
      padding: 10px 14px;
      border-radius: 8px;
      font-size: 0.85rem;
      margin-bottom: 16px;
      line-height: 1.4;
    }
    .notice-demo { background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); color: #fcd34d; }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="logo-group">
        <h1>Content Agent</h1>
        <p>Autonomous multi-agent writing & quality verification via LangGraph</p>
      </div>
      <div style="display:flex; gap:10px;">
        <div id="graphBadge" class="status-badge badge-purple">LangGraph Autonomous Engine</div>
        <div id="modeBadge" class="status-badge badge-demo">
          <span id="headerModeText">Checking mode...</span>
        </div>
      </div>
    </header>

    <div class="grid">
      <!-- Input Panel -->
      <div class="card">
        <h2>Content Brief</h2>
        <form id="generateForm">
          <div class="form-group">
            <label for="topic">Topic / Subject *</label>
            <input type="text" id="topic" name="topic" required placeholder="e.g. AI-Assisted Verification in Production" value="Autonomous Multi-Agent Orchestration">
            <div class="presets">
              <span class="chip" onclick="setTopic('Observability in Modern Microservices')">Observability</span>
              <span class="chip" onclick="setTopic('Zero-Trust Architecture in Cloud Native')">Zero Trust</span>
              <span class="chip" onclick="setTopic('Autonomous Multi-Agent Orchestration')">Agents</span>
            </div>
          </div>

          <div class="form-group">
            <label for="contentType">Content Type</label>
            <select id="contentType" name="contentType">
              <option value="blog" selected>Blog Post</option>
              <option value="press_release">Press Release</option>
              <option value="white_paper">White Paper</option>
            </select>
          </div>

          <div class="form-group">
            <label for="targetAudience">Target Audience</label>
            <input type="text" id="targetAudience" name="targetAudience" value="Engineering leaders and technical practitioners">
          </div>

          <div class="form-group">
            <label for="wordCount">Target Word Count</label>
            <input type="number" id="wordCount" name="wordCount" min="100" max="3000" step="50" value="500">
          </div>

          <button type="submit" id="submitBtn" class="btn btn-primary">
            <span id="btnSpinner" class="spinner" style="display: none;"></span>
            <span id="btnText">Run Autonomous Pipeline</span>
          </button>
        </form>

        <div style="margin-top: 20px; font-size: 0.8rem; color: #64748b;">
          <p><strong>Autonomous Workflow:</strong> Strategist &rarr; Outline Review Agent &rarr; Writer &rarr; QA Auditor &rarr; Quality Decision Agent &rarr; Auto-Export.</p>
        </div>
      </div>

      <!-- Output Panel -->
      <div class="card">
        <div id="outputArea">
          <div class="placeholder-state" id="emptyState">
            <p style="font-size: 1.1rem; margin-bottom: 8px;">No pipeline run executed yet</p>
            <p style="font-size: 0.85rem;">Click <strong>Run Autonomous Pipeline</strong> to execute LangGraph agents, review outlines, run QA gates, and auto-export.</p>
          </div>

          <div id="resultsContent" style="display: none;">
            <div id="modeNotice" class="notice notice-demo"></div>

            <!-- Agent Decision Cards -->
            <div class="agent-decisions">
              <div class="decision-card">
                <h4>1. Outline Review Agent</h4>
                <span id="outlineDecisionBadge" class="decision-tag tag-approve">Approved</span>
                <span id="outlineRetriesText" style="font-size:0.75rem; color:#94a3b8; float:right;">Revisions: 0/2</span>
                <p id="outlineRationaleText">Outline validated.</p>
              </div>

              <div class="decision-card">
                <h4>2. Quality Decision Agent</h4>
                <span id="qualityDecisionBadge" class="decision-tag tag-approve">Export Ready</span>
                <span id="qualityRetriesText" style="font-size:0.75rem; color:#94a3b8; float:right;">Iterations: 0/2</span>
                <p id="qualityRationaleText">Passed all mandatory quality gates.</p>
              </div>
            </div>

            <!-- Tabs Header & Export Button -->
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
              <div class="tabs" style="margin-bottom: 0;">
                <div class="tab active" onclick="switchTab('draft')">Generated Article</div>
                <div class="tab" onclick="switchTab('outline')">Approved Outline</div>
                <div class="tab" onclick="switchTab('evidence')">Sources (<span id="sourceCountBadge">0</span>)</div>
                <div class="tab" onclick="switchTab('checks')">Quality Gates (<span id="gatePassBadge">0</span>)</div>
                <div class="tab" onclick="switchTab('logs')">Execution Trace</div>
              </div>
              <div style="display:flex; gap:6px;">
                <a id="downloadHtmlBtn" href="#" class="btn btn-secondary" style="padding: 6px 12px; font-size: 0.8rem;">HTML</a>
                <a id="downloadBtn" href="#" class="btn btn-success" style="padding: 6px 14px; font-size: 0.8rem;">Auto-Exported .md</a>
              </div>
            </div>

            <!-- Tab 1: Draft -->
            <div id="tab-draft" class="tab-pane active">
              <div class="draft-container" id="draftRender"></div>
            </div>

            <!-- Tab 2: Outline -->
            <div id="tab-outline" class="tab-pane">
              <div class="draft-container" id="outlineRender"></div>
            </div>

            <!-- Tab 3: Evidence -->
            <div id="tab-evidence" class="tab-pane">
              <div id="evidenceList"></div>
            </div>

            <!-- Tab 4: Checks -->
            <div id="tab-checks" class="tab-pane">
              <div id="checksList"></div>
            </div>

            <!-- Tab 5: Logs -->
            <div id="tab-logs" class="tab-pane">
              <div class="log-box" id="traceLogBox"></div>
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>

  <script>
    let currentRun = null;

    function setTopic(text) {
      document.getElementById('topic').value = text;
    }

    function switchTab(name) {
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
      event.target.classList.add('active');
      document.getElementById('tab-' + name).classList.add('active');
    }

    async function checkHealth() {
      try {
        const res = await fetch('/health');
        const data = await res.json();
        const badge = document.getElementById('modeBadge');
        const text = document.getElementById('headerModeText');
        if (data.mode === 'live') {
          badge.className = 'status-badge badge-live';
          text.textContent = 'Live Mode Active';
        } else {
          badge.className = 'status-badge badge-demo';
          text.textContent = 'Demo Mode (Offline Evidence)';
        }
      } catch (e) {
        document.getElementById('headerModeText').textContent = 'Server Connected';
      }
    }

    function renderMarkdown(md) {
      if (window.marked && window.marked.parse) {
        return marked.parse(md);
      }
      return md
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
        .replace(/\n\n/gim, '<p></p>')
        .replace(/\n/gim, '<br>');
    }

    document.getElementById('generateForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      const submitBtn = document.getElementById('submitBtn');
      const btnSpinner = document.getElementById('btnSpinner');
      const btnText = document.getElementById('btnText');

      submitBtn.disabled = true;
      btnSpinner.style.display = 'inline-block';
      btnText.textContent = 'Routing LangGraph Agents...';

      const payload = {
        topic: document.getElementById('topic').value,
        content_type: document.getElementById('contentType').value,
        target_audience: document.getElementById('targetAudience').value,
        target_word_count: parseInt(document.getElementById('wordCount').value, 10),
      };

      try {
        const res = await fetch('/api/runs', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (!res.ok) {
          const err = await res.json();
          alert('Pipeline error: ' + (err.detail || res.statusText));
          return;
        }

        const run = await res.json();
        currentRun = run;
        displayRun(run);
      } catch (err) {
        alert('Request failed: ' + err.message);
      } finally {
        submitBtn.disabled = false;
        btnSpinner.style.display = 'none';
        btnText.textContent = 'Run Autonomous Pipeline';
      }
    });

    function displayRun(run) {
      document.getElementById('emptyState').style.display = 'none';
      document.getElementById('resultsContent').style.display = 'block';

      // Mode notice
      const modeNotice = document.getElementById('modeNotice');
      modeNotice.innerHTML = `<strong>${run.mode_label}:</strong> ${run.mode_explanation}`;
      if (run.is_demo_mode) {
        modeNotice.className = 'notice notice-demo';
      } else {
        modeNotice.className = 'notice';
        modeNotice.style.background = 'rgba(16, 185, 129, 0.1)';
        modeNotice.style.border = '1px solid rgba(16, 185, 129, 0.3)';
        modeNotice.style.color = '#34d399';
      }

      // Outline Review Agent Decision
      if (run.outline_decision) {
        const badge = document.getElementById('outlineDecisionBadge');
        badge.textContent = run.outline_decision.decision.toUpperCase();
        badge.className = 'decision-tag ' + (run.outline_decision.decision === 'approve' ? 'tag-approve' : (run.outline_decision.decision === 'revise' ? 'tag-revise' : 'tag-research'));
        document.getElementById('outlineRetriesText').textContent = `Revisions: ${run.outline_revision_count}/2`;
        document.getElementById('outlineRationaleText').textContent = run.outline_decision.rationale;
      }

      // Quality Decision Agent Decision
      if (run.quality_decision) {
        const badge = document.getElementById('qualityDecisionBadge');
        badge.textContent = run.quality_decision.action.toUpperCase();
        badge.className = 'decision-tag ' + (run.quality_decision.action === 'export' ? 'tag-approve' : (run.quality_decision.action === 'terminate_failure' ? 'tag-failure' : 'tag-revise'));
        document.getElementById('qualityRetriesText').textContent = `Iterations: ${run.quality_iteration_count}/2`;
        document.getElementById('qualityRationaleText').textContent = run.quality_decision.rationale;
      }

      // Download Buttons (Automatic Export)
      const downloadBtn = document.getElementById('downloadBtn');
      const downloadHtmlBtn = document.getElementById('downloadHtmlBtn');
      if (run.export_ready) {
        downloadBtn.style.display = 'inline-flex';
        downloadBtn.className = 'btn btn-success';
        downloadBtn.textContent = 'Auto-Exported .md';
        downloadBtn.href = `/api/exports/${run.id}?format=markdown`;

        downloadHtmlBtn.style.display = 'inline-flex';
        downloadHtmlBtn.href = `/api/exports/${run.id}?format=html`;
      } else {
        downloadBtn.style.display = 'inline-flex';
        downloadBtn.className = 'btn btn-secondary';
        downloadBtn.textContent = 'QA Failed (No Export)';
        downloadBtn.removeAttribute('href');
        downloadHtmlBtn.style.display = 'none';
      }

      // Tab 1: Render Draft
      document.getElementById('draftRender').innerHTML = renderMarkdown(run.markdown_content);

      // Tab 2: Render Outline
      if (run.outline) {
        let outlineHtml = `<h2>${run.outline.title}</h2><p><strong>Estimated Word Count:</strong> ${run.outline.estimated_word_count}</p><h3 style="margin-top:14px;">Target Sections:</h3><ul>`;
        run.outline.target_sections.forEach(s => { outlineHtml += `<li>${s}</li>`; });
        outlineHtml += `</ul><h3 style="margin-top:14px;">Key Claims to Cover:</h3><ul>`;
        run.outline.key_claims_to_cover.forEach(c => { outlineHtml += `<li>${c}</li>`; });
        outlineHtml += `</ul><h3 style="margin-top:14px;">Mapped Sources:</h3><p>Sources [${run.outline.source_ids_referenced.join(', ')}]</p>`;
        document.getElementById('outlineRender').innerHTML = outlineHtml;
      }

      // Tab 3: Sources
      document.getElementById('sourceCountBadge').textContent = run.sources.length;
      const evidenceList = document.getElementById('evidenceList');
      evidenceList.innerHTML = '';
      run.sources.forEach(s => {
        const div = document.createElement('div');
        div.className = 'source-card';
        div.innerHTML = `
          <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <h4>[${s.id}] ${s.title}</h4>
            <span style="font-size: 0.7rem; color: #94a3b8; background: #1e293b; padding: 2px 6px; border-radius: 4px;">${s.is_mock ? 'Curated Benchmark' : 'Live Web'}</span>
          </div>
          <a href="${s.url}" target="_blank" rel="noopener">${s.url}</a>
          <p>${s.snippet}</p>
          ${s.key_facts && s.key_facts.length ? '<ul style="margin: 8px 0 0 16px; font-size: 0.8rem; color:#94a3b8;">' + s.key_facts.map(f => `<li>${f}</li>`).join('') + '</ul>' : ''}
        `;
        evidenceList.appendChild(div);
      });

      // Tab 4: Quality Checks
      const passedCount = run.quality_checks.filter(c => c.passed).length;
      document.getElementById('gatePassBadge').textContent = `${passedCount}/${run.quality_checks.length}`;
      const checksList = document.getElementById('checksList');
      checksList.innerHTML = '';
      run.quality_checks.forEach(c => {
        const div = document.createElement('div');
        div.className = 'check-row';
        const badgeClass = c.passed ? 'badge-pass' : (c.severity === 'warning' ? 'badge-warn' : 'badge-fail');
        const badgeLabel = c.passed ? 'PASSED' : (c.severity === 'warning' ? 'WARNING' : 'FAILED');

        div.innerHTML = `
          <div class="check-info">
            <strong>${c.name} — <span style="color:#94a3b8; font-weight:normal;">${c.score_or_metric}</span></strong>
            <small>${c.details}</small>
          </div>
          <span class="${badgeClass}">${badgeLabel}</span>
        `;
        checksList.appendChild(div);
      });

      // Tab 5: Execution Trace Log
      const traceBox = document.getElementById('traceLogBox');
      traceBox.innerHTML = '';
      if (run.execution_log && run.execution_log.length) {
        run.execution_log.forEach(item => {
          const entry = document.createElement('div');
          entry.className = 'log-entry';
          entry.textContent = item;
          traceBox.appendChild(entry);
        });
      }
    }

    checkHealth();
  </script>
</body>
</html>
"""
