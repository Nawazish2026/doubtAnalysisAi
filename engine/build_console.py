import json
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]

with open(PROJECT_DIR / "console_data.json", "r", encoding="utf-8") as f:
    console_data = json.load(f)

with open(PROJECT_DIR / "bonus_defects.json", "r", encoding="utf-8") as f:
    bonus_data = json.load(f)

html_template = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Acadza • Faculty Review Console</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;500;600;700;800;900&family=Nunito:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: {
            sans: ['"Lexend"', '"Nunito"', 'sans-serif'],
            body: ['"Nunito"', 'sans-serif'],
            mono: ['"JetBrains Mono"', 'monospace'],
          },
          colors: {
            acadza: {
              navy: '#070d1e',
              surface: '#0f1a36',
              card: '#132145',
              cardHover: '#182b59',
              border: '#1f3468',
              borderLight: '#2b478a',
              blue: '#006AB6',
              royal: '#2563EB',
              amber: '#F4B23A',
              amberLight: '#FACC15',
              orange: '#E06A19',
              emerald: '#10B981',
              rose: '#EF4444',
            }
          },
          boxShadow: {
            'glow-blue': '0 0 25px -5px rgba(0, 106, 182, 0.3)',
            'glow-amber': '0 0 25px -5px rgba(244, 178, 58, 0.3)',
            'pill': '0 10px 30px -5px rgba(2, 8, 23, 0.8), 0 0 0 1px rgba(37, 99, 235, 0.2)',
          }
        }
      }
    }
  </script>
  <style>
    math {
      font-size: 1.08em;
      font-family: "STIX Two Math", "Cambria Math", "Latin Modern Math", serif;
      padding: 0 2px;
    }
    mfrac {
      padding: 0 2px;
    }
    .custom-scroll::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }
    .custom-scroll::-webkit-scrollbar-track {
      background: rgba(15, 26, 54, 0.4);
    }
    .custom-scroll::-webkit-scrollbar-thumb {
      background: rgba(43, 71, 138, 0.6);
      border-radius: 9999px;
    }
    .custom-scroll::-webkit-scrollbar-thumb:hover {
      background: rgba(0, 106, 182, 0.8);
    }
    .spherical-navbar {
      border-radius: 9999px;
      background: linear-gradient(135deg, rgba(15, 26, 54, 0.92) 0%, rgba(10, 18, 42, 0.95) 100%);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.7), 0 0 0 1px rgba(43, 71, 138, 0.35), 0 0 20px 0 rgba(0, 106, 182, 0.15);
    }
    .header-metric {
      white-space: nowrap;
      flex: 0 0 auto;
    }
  </style>
</head>
<body class="bg-acadza-navy text-slate-100 font-body min-h-screen flex flex-col antialiased selection:bg-acadza-blue selection:text-white relative overflow-x-hidden">

  <div class="fixed top-0 left-1/4 w-96 h-96 bg-acadza-blue/10 rounded-full blur-3xl pointer-events-none -z-10"></div>
  <div class="fixed top-20 right-1/4 w-96 h-96 bg-acadza-amber/5 rounded-full blur-3xl pointer-events-none -z-10"></div>

  <header class="sticky top-3 z-40 px-4 max-w-7xl mx-auto w-full">
    <div class="spherical-navbar px-4 xl:px-5 py-2.5 flex items-center gap-3 xl:gap-4 transition-all duration-300">
      
      <div class="flex items-center space-x-3.5 pl-1">
        <a href="https://www.acadza.com/" target="_blank" rel="noopener noreferrer" class="flex items-center space-x-2.5 group">
          <div class="w-9 h-9 rounded-full bg-gradient-to-tr from-acadza-blue via-blue-600 to-acadza-amber flex items-center justify-center shadow-lg shadow-blue-500/20 group-hover:scale-105 transition">
            <svg class="w-5 h-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
            </svg>
          </div>
          <div class="flex flex-col">
            <div class="flex items-center space-x-2">
              <span class="font-sans font-extrabold text-base tracking-wider text-white">ACADZA</span>
              <span class="text-[10px] font-sans font-bold px-2 py-0.5 rounded-full bg-acadza-amber/20 text-acadza-amber border border-acadza-amber/30 uppercase tracking-widest">
                Faculty
              </span>
            </div>
            <span class="text-[10px] text-slate-400 font-sans tracking-tight">Report → Fix Review Demo</span>
          </div>
        </a>
      </div>

      <div class="hidden xl:flex min-w-0 flex-1 items-center justify-center gap-1.5 2xl:gap-2 text-xs font-sans">
        <div class="header-metric flex items-center gap-1.5 px-2.5 2xl:px-3 py-1 rounded-full bg-acadza-surface border border-acadza-border text-slate-200">
          <span class="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
          <span>Queue:</span>
          <span id="metric-total" class="font-bold text-white font-mono">39</span>
        </div>
        <div class="header-metric flex items-center gap-1.5 px-2.5 2xl:px-3 py-1 rounded-full bg-acadza-amber/10 border border-acadza-amber/30 text-acadza-amber font-medium">
          <span class="w-1.5 h-1.5 rounded-full bg-acadza-amber animate-pulse"></span>
          <span>Review:</span>
          <span id="metric-review" class="font-bold text-white font-mono">5</span>
        </div>
        <div class="header-metric flex items-center gap-1.5 px-2.5 2xl:px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 font-medium">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
          <span>Auto-Apply:</span>
          <span id="metric-auto" class="font-bold text-white font-mono">21</span>
        </div>
        <div class="header-metric flex items-center gap-1.5 px-2.5 2xl:px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700 text-slate-300">
          <span>Dismissed:</span>
          <span id="metric-nochange" class="font-bold text-white font-mono">18</span>
        </div>
      </div>

      <div class="ml-auto flex flex-none items-center gap-1.5 xl:gap-2 font-sans pr-1 whitespace-nowrap">
        <button id="btn-tab-review" onclick="switchMainTab('review')" 
          class="px-4 py-1.5 rounded-full text-xs font-bold bg-acadza-blue hover:bg-blue-600 text-white shadow-glow-blue transition">
          Review Queue
        </button>
        <button id="btn-tab-scanner" onclick="switchMainTab('scanner')" 
          class="px-3.5 py-1.5 rounded-full text-xs font-semibold text-slate-300 bg-acadza-surface hover:bg-acadza-card border border-acadza-border hover:border-acadza-amber/50 transition flex items-center space-x-1.5">
          <span>✨ Scanner</span>
          <span class="bg-acadza-amber/20 text-acadza-amber text-[10px] px-1.5 py-0.2 rounded-full font-mono font-bold">2 Bonus</span>
        </button>
        <button onclick="toggleAuditDrawer()" 
          class="px-3.5 py-1.5 rounded-full text-xs font-semibold text-slate-300 bg-acadza-surface hover:bg-acadza-card border border-acadza-border transition flex items-center space-x-1.5">
          <span>📋 Audit</span>
          <span id="audit-count-badge" class="bg-acadza-cardHover text-slate-200 text-[10px] px-1.5 py-0.2 rounded-full font-mono">0</span>
        </button>
      </div>

    </div>
  </header>

  <main class="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 mt-2">

    <div id="view-review" class="contents">

      <section class="lg:col-span-4 flex flex-col space-y-4">
        
        <div class="bg-acadza-surface p-4 rounded-3xl border border-acadza-border shadow-lg space-y-3">
          <div class="relative">
            <input type="text" id="search-input" oninput="applyFilters()" placeholder="Search QID, topic, student comment..." 
              class="w-full bg-acadza-navy/80 border border-acadza-border rounded-full px-4 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-acadza-blue focus:ring-1 focus:ring-acadza-blue transition font-mono">
            <span class="absolute right-3.5 top-2.5 text-slate-500 text-xs font-mono">⌘K</span>
          </div>

          <div class="flex flex-wrap gap-1.5 text-[11px] font-sans">
            <button onclick="setFilterRoute('all')" id="filter-route-all" class="filter-route-btn px-3 py-1 rounded-full font-semibold bg-acadza-blue text-white shadow-sm transition">All</button>
            <button onclick="setFilterRoute('faculty_review')" id="filter-route-faculty_review" class="filter-route-btn px-3 py-1 rounded-full font-semibold bg-acadza-card text-acadza-amber border border-acadza-amber/30 hover:bg-acadza-cardHover transition">Review (5)</button>
            <button onclick="setFilterRoute('auto_apply')" id="filter-route-auto_apply" class="filter-route-btn px-3 py-1 rounded-full font-semibold bg-acadza-card text-emerald-400 border border-emerald-500/30 hover:bg-acadza-cardHover transition">Auto-Apply Candidates</button>
            <button onclick="setFilterRoute('no_change')" id="filter-route-no_change" class="filter-route-btn px-3 py-1 rounded-full font-semibold bg-acadza-card text-slate-400 border border-acadza-border hover:bg-acadza-cardHover transition">Dismissed</button>
          </div>

          <div class="flex flex-wrap gap-1.5 text-[11px] font-sans pt-2 border-t border-acadza-border/60">
            <button onclick="setFilterSubject('all')" id="filter-subj-all" class="filter-subj-btn px-2.5 py-0.5 rounded-full font-semibold bg-acadza-border text-white">All Subjects</button>
            <button onclick="setFilterSubject('Physics')" id="filter-subj-Physics" class="filter-subj-btn px-2.5 py-0.5 rounded-full font-semibold bg-acadza-card text-slate-400 hover:text-white">Physics</button>
            <button onclick="setFilterSubject('Botany')" id="filter-subj-Botany" class="filter-subj-btn px-2.5 py-0.5 rounded-full font-semibold bg-acadza-card text-slate-400 hover:text-white">Botany</button>
            <button onclick="setFilterSubject('Zoology')" id="filter-subj-Zoology" class="filter-subj-btn px-2.5 py-0.5 rounded-full font-semibold bg-acadza-card text-slate-400 hover:text-white">Zoology</button>
          </div>
        </div>

        <div class="flex-1 bg-acadza-surface rounded-3xl border border-acadza-border shadow-lg flex flex-col overflow-hidden max-h-[calc(100vh-270px)]">
          <div class="px-5 py-3.5 border-b border-acadza-border flex items-center justify-between bg-acadza-surface/80">
            <span class="text-xs font-sans font-bold text-slate-200 uppercase tracking-wider">Priority Queue</span>
            <span class="text-[11px] text-acadza-amber font-mono font-semibold flex items-center space-x-1">
              <span>⚡ Ranked by Urgency</span>
            </span>
          </div>

          <div id="queue-container" class="flex-1 overflow-y-auto divide-y divide-acadza-border/60 custom-scroll">
          </div>
        </div>

        <div class="bg-acadza-surface/60 rounded-2xl p-3 border border-acadza-border text-[11px] text-slate-400 flex items-center justify-between font-sans">
          <span class="flex items-center space-x-1.5">
            <kbd class="bg-acadza-card text-slate-200 px-2 py-0.5 rounded-md font-mono text-[10px] border border-acadza-border">J</kbd>
            <kbd class="bg-acadza-card text-slate-200 px-2 py-0.5 rounded-md font-mono text-[10px] border border-acadza-border">K</kbd>
            <span>Next / Prev</span>
          </span>
          <span class="flex items-center space-x-1.5">
            <kbd class="bg-emerald-950/80 text-emerald-300 px-2 py-0.5 rounded-md font-mono text-[10px] border border-emerald-800">A</kbd>
            <span>Approve</span>
            <kbd class="bg-rose-950/80 text-rose-300 px-2 py-0.5 rounded-md font-mono text-[10px] border border-rose-800">R</kbd>
            <span>Reject</span>
          </span>
        </div>
      </section>

      <section class="lg:col-span-8 flex flex-col space-y-5">

        <div id="active-case-card" class="bg-acadza-surface rounded-3xl border border-acadza-border shadow-xl p-6 md:p-7 space-y-6 flex-1 flex flex-col">
        </div>

      </section>

    </div>

    <div id="view-scanner" class="hidden lg:col-span-12 space-y-6">
      <div class="bg-acadza-surface p-7 rounded-3xl border border-acadza-border shadow-xl space-y-5">
        <div class="flex items-center justify-between pb-4 border-b border-acadza-border">
          <div>
            <div class="flex items-center space-x-3">
              <h2 class="text-xl font-sans font-bold text-white">Proactive Latent Defect Mining</h2>
              <span class="bg-acadza-amber/20 text-acadza-amber border border-acadza-amber/30 text-xs px-3 py-1 rounded-full font-sans font-bold uppercase tracking-wider">
                Bonus Checks
              </span>
            </div>
            <p class="text-xs text-slate-300 mt-1 max-w-2xl leading-relaxed">
              Deterministic checks scanned questions with <strong>zero student reports</strong> and flagged possible defects for faculty review.
            </p>
          </div>
          <div class="text-right font-mono text-xs text-slate-400 bg-acadza-card px-3 py-2 rounded-2xl border border-acadza-border">
            <div class="text-white font-bold">Audit Coverage: 43/43</div>
            <div class="text-acadza-amber">2 Latent Defects Found</div>
          </div>
        </div>

        <div id="bonus-container" class="grid grid-cols-1 md:grid-cols-2 gap-5 pt-2">
        </div>
      </div>
    </div>

  </main>

  <div id="audit-drawer" class="fixed inset-y-0 right-0 w-full max-w-md bg-acadza-surface border-l border-acadza-border shadow-2xl z-50 transform translate-x-full transition-transform duration-300 ease-in-out flex flex-col">
    <div class="p-5 border-b border-acadza-border flex items-center justify-between bg-acadza-surface/90">
      <div class="flex items-center space-x-2.5">
        <span class="text-base font-sans font-bold text-white">Faculty Action Audit Trail</span>
        <span id="drawer-audit-badge" class="bg-acadza-blue/20 text-acadza-blue text-xs px-2.5 py-0.5 rounded-full font-mono font-semibold">0 entries</span>
      </div>
      <button onclick="toggleAuditDrawer()" class="text-slate-400 hover:text-white p-1.5 rounded-full hover:bg-acadza-card transition">
        ✕
      </button>
    </div>

    <div id="audit-log-list" class="flex-1 overflow-y-auto p-5 space-y-3 custom-scroll">
      <div class="text-center py-12 text-slate-500 text-xs">
        No actions recorded yet. Approve, Edit or Dismiss cases to log audit history.
      </div>
    </div>
    <p class="px-5 pb-3 text-[10px] text-slate-500">This audit log is local to this browser and is not a server-side record.</p>

    <div class="p-5 border-t border-acadza-border bg-acadza-navy flex items-center justify-between font-sans">
      <button onclick="exportAuditLog()" class="px-4 py-2 rounded-full text-xs font-bold bg-acadza-card hover:bg-acadza-cardHover text-slate-200 border border-acadza-border transition flex items-center space-x-2">
        <span>📥 Download browser audit log</span>
      </button>
      <button onclick="clearAuditLog()" class="px-3 py-1.5 rounded-full text-xs font-semibold text-rose-400 hover:text-rose-300 transition">
        Clear
      </button>
    </div>
  </div>

  <script>
    const CONSOLE_DATA = __CONSOLE_DATA_PLACEHOLDER__;
    const BONUS_DATA = __BONUS_DATA_PLACEHOLDER__;
  </script>

  <script>
    let activeIndex = 0;
    let filterRoute = 'all';
    let filterSubject = 'all';
    let searchQuery = '';
    let auditLog = JSON.parse(localStorage.getItem('acadza_audit_log') || '[]');

    function saveAudit(entry) {
      auditLog.unshift(entry);
      localStorage.setItem('acadza_audit_log', JSON.stringify(auditLog));
      updateAuditUI();
    }

    function updateAuditUI() {
      const badge = document.getElementById('audit-count-badge');
      const drawerBadge = document.getElementById('drawer-audit-badge');
      const list = document.getElementById('audit-log-list');
      if (badge) badge.innerText = auditLog.length;
      if (drawerBadge) drawerBadge.innerText = auditLog.length + ' entries';

      if (!list) return;
      if (auditLog.length === 0) {
        list.innerHTML = '<div class="text-center py-12 text-slate-500 text-xs">No actions recorded yet.</div>';
        return;
      }

      list.innerHTML = auditLog.map(entry => `
        <div class="bg-acadza-navy p-3.5 rounded-2xl border border-acadza-border space-y-1.5 text-xs">
          <div class="flex items-center justify-between">
            <span class="font-mono font-bold ${entry.action === 'APPROVED' ? 'text-emerald-400' : entry.action === 'EDITED' ? 'text-acadza-amber' : 'text-rose-400'}">
              ${escapeHtml(entry.action)}
            </span>
            <span class="text-[10px] text-slate-500 font-mono">${escapeHtml(new Date(entry.timestamp).toLocaleTimeString())}</span>
          </div>
          <div class="text-[11px] text-slate-300 font-mono">QID: ${escapeHtml(entry.questionId || '')}...</div>
          <p class="text-[11px] text-slate-400 leading-relaxed">${escapeHtml(entry.notes || 'No faculty comment')}</p>
          <div class="text-[10px] text-slate-500 pt-1.5 border-t border-acadza-border font-mono">Reviewer: ${escapeHtml(entry.reviewer || '')}</div>
        </div>
      `).join('');
    }

    function toggleAuditDrawer() {
      const drawer = document.getElementById('audit-drawer');
      drawer.classList.toggle('translate-x-full');
      updateAuditUI();
    }

    function clearAuditLog() {
      if (confirm('Clear all audit entries from this browser session?')) {
        auditLog = [];
        localStorage.removeItem('acadza_audit_log');
        updateAuditUI();
      }
    }

    function exportAuditLog() {
      const blob = new Blob([JSON.stringify(auditLog, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'acadza_audit_log.json';
      a.click();
    }

    function switchMainTab(tab) {
      const viewReview = document.getElementById('view-review');
      const viewScanner = document.getElementById('view-scanner');
      const btnReview = document.getElementById('btn-tab-review');
      const btnScanner = document.getElementById('btn-tab-scanner');

      if (tab === 'review') {
        viewReview.classList.remove('hidden');
        viewScanner.classList.add('hidden');
        btnReview.className = "px-4 py-1.5 rounded-full text-xs font-bold bg-acadza-blue hover:bg-blue-600 text-white shadow-glow-blue transition";
        btnScanner.className = "px-3.5 py-1.5 rounded-full text-xs font-semibold text-slate-300 bg-acadza-surface hover:bg-acadza-card border border-acadza-border hover:border-acadza-amber/50 transition flex items-center space-x-1.5";
      } else {
        viewReview.classList.add('hidden');
        viewScanner.classList.remove('hidden');
        btnScanner.className = "px-4 py-1.5 rounded-full text-xs font-bold bg-acadza-amber hover:bg-yellow-500 text-slate-900 shadow-glow-amber transition flex items-center space-x-1.5";
        btnReview.className = "px-3.5 py-1.5 rounded-full text-xs font-semibold text-slate-300 bg-acadza-surface hover:bg-acadza-card border border-acadza-border transition";
        renderBonusScanner();
      }
    }

    function setFilterRoute(route) {
      filterRoute = route;
      document.querySelectorAll('.filter-route-btn').forEach(b => {
        b.className = 'filter-route-btn px-3 py-1 rounded-full font-semibold bg-acadza-card text-slate-400 border border-acadza-border hover:bg-acadza-cardHover transition';
      });
      const activeBtn = document.getElementById('filter-route-' + route);
      if (activeBtn) {
        activeBtn.className = 'filter-route-btn px-3 py-1 rounded-full font-semibold bg-acadza-blue text-white shadow-sm transition';
      }
      applyFilters();
    }

    function setFilterSubject(subj) {
      filterSubject = subj;
      document.querySelectorAll('.filter-subj-btn').forEach(b => {
        b.className = 'filter-subj-btn px-2.5 py-0.5 rounded-full font-semibold bg-acadza-card text-slate-400 hover:text-white';
      });
      const activeBtn = document.getElementById('filter-subj-' + subj);
      if (activeBtn) {
        activeBtn.className = 'filter-subj-btn px-2.5 py-0.5 rounded-full font-semibold bg-acadza-border text-white';
      }
      applyFilters();
    }

    function applyFilters() {
      searchQuery = (document.getElementById('search-input').value || '').toLowerCase().trim();
      renderQueue();
    }

    function getFilteredItems() {
      return CONSOLE_DATA.filter(item => {
        if (filterRoute !== 'all' && item.primaryTriage.route !== filterRoute) return false;
        if (filterSubject !== 'all' && item.subject !== filterSubject) return false;
        if (searchQuery) {
          const matchQid = item.questionId.toLowerCase().includes(searchQuery);
          const matchSubj = item.subject.toLowerCase().includes(searchQuery);
          const matchChap = item.chapter.toLowerCase().includes(searchQuery);
          const matchRepair = (item.primaryTriage.repair || '').toLowerCase().includes(searchQuery);
          const matchComment = item.reports.some(r => r.comment.toLowerCase().includes(searchQuery));
          if (!matchQid && !matchSubj && !matchChap && !matchRepair && !matchComment) return false;
        }
        return true;
      });
    }

    function renderQueue() {
      const container = document.getElementById('queue-container');
      const items = getFilteredItems();

      if (items.length === 0) {
        container.innerHTML = `
          <div class="p-8 text-center text-slate-500 text-xs font-sans">
            No question cases match active filters.
          </div>
        `;
        document.getElementById('active-case-card').innerHTML = `
          <div class="flex-1 flex items-center justify-center text-center text-slate-500 text-sm font-sans">
            Select or reset filters to review cases.
          </div>
        `;
        return;
      }

      if (activeIndex >= items.length) activeIndex = 0;

      container.innerHTML = items.map((item, idx) => {
        const isSelected = idx === activeIndex;
        const triage = item.primaryTriage;
        const isMulti = item.reportCount > 1;
        const isUrgent = item.urgencyScore >= 100;

        let badgeBg = "bg-acadza-card text-slate-400 border-acadza-border";
        if (triage.route === 'faculty_review') badgeBg = "bg-acadza-amber/15 text-acadza-amber border-acadza-amber/30";
        else if (triage.route === 'auto_apply') badgeBg = "bg-emerald-500/15 text-emerald-300 border-emerald-500/30";

        return `
          <div onclick="selectCase(${idx})" class="p-4 cursor-pointer transition select-none ${isSelected ? 'bg-acadza-card border-l-4 border-acadza-blue' : 'hover:bg-acadza-card/50'}">
            <div class="flex items-center justify-between mb-1.5">
              <div class="flex items-center space-x-2">
                <span class="text-xs font-mono font-bold ${isUrgent ? 'text-acadza-amber' : 'text-slate-200'}">
                  ${isUrgent ? '🔥 ' : ''}${escapeHtml(item.questionId.substring(0, 6))}...
                </span>
                ${isMulti ? `<span class="px-2 py-0.2 rounded-full text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">${item.reportCount} reports</span>` : ''}
              </div>
              <span class="text-[10px] px-2.5 py-0.5 rounded-full font-sans font-semibold border ${badgeBg}">
                ${triage.route === 'faculty_review' ? 'Faculty Review' : triage.route === 'auto_apply' ? 'Auto-Apply Candidate' : 'No Change'}
              </span>
            </div>

            <div class="flex items-center space-x-2 text-[11px] text-slate-400 mb-2 font-sans">
              <span class="font-bold text-slate-300">${escapeHtml(item.subject)}</span>
              <span>•</span>
              <span class="truncate max-w-[130px]">${escapeHtml(item.chapter)}</span>
              <span>•</span>
              <span class="text-slate-500 font-mono">${escapeHtml(item.questionType)}</span>
            </div>

            <div class="text-[11px] text-slate-300 line-clamp-1 italic bg-acadza-navy/80 px-2.5 py-1.5 rounded-xl border border-acadza-border">
              "${escapeHtml(item.reports[0].comment)}"
            </div>

            <div class="mt-2.5 flex items-center justify-between text-[10px] text-slate-400 font-mono">
              <span>Repair: <strong class="text-slate-300">${escapeHtml(triage.repair || 'none')}</strong></span>
              <span>Urgency: <strong class="${isUrgent ? 'text-acadza-amber font-bold' : 'text-slate-300'}">${item.urgencyScore}</strong></span>
            </div>
          </div>
        `;
      }).join('');

      renderActiveCase(items[activeIndex]);
    }

    function selectCase(idx) {
      activeIndex = idx;
      renderQueue();
    }

    function renderActiveCase(item) {
      const card = document.getElementById('active-case-card');
      if (!item) return;

      const triage = item.primaryTriage;
      const diff = item.diff;

      let routePill = `<span class="px-3.5 py-1 rounded-full text-xs font-sans font-bold bg-acadza-card text-slate-300 border border-acadza-border">Dismissed / No Change</span>`;
      if (triage.route === 'faculty_review') {
        routePill = `<span class="px-3.5 py-1 rounded-full text-xs font-sans font-bold bg-acadza-amber/20 text-acadza-amber border border-acadza-amber/40 animate-pulse">Action Required • Faculty Review</span>`;
      } else if (triage.route === 'auto_apply') {
        routePill = `<span class="px-3.5 py-1 rounded-full text-xs font-sans font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">Auto-Apply Candidate</span>`;
      }

      card.innerHTML = `
        <div class="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-acadza-border">
          <div>
            <div class="flex items-center space-x-3">
              <h1 class="text-base font-bold text-white font-mono flex items-center space-x-2">
                <span>QID: ${escapeHtml(item.questionId)}</span>
              </h1>
              <span class="text-xs px-2.5 py-0.5 rounded-full bg-acadza-card text-slate-300 font-mono border border-acadza-border">${escapeHtml(item.questionType)}</span>
            </div>
            <div class="flex items-center space-x-2 text-xs text-slate-400 mt-1 font-sans">
              <span class="text-acadza-blue font-bold">${escapeHtml(item.subject)}</span>
              <span>/</span>
              <span class="text-slate-200">${escapeHtml(item.chapter)}</span>
              <span>/</span>
              <span class="text-slate-400">Level: <strong class="text-slate-200">${escapeHtml(item.level)}</strong></span>
            </div>
          </div>
          <div>
            ${routePill}
          </div>
        </div>

        <div class="bg-acadza-navy/90 rounded-2xl p-4 border border-acadza-border space-y-2.5">
          <div class="flex items-center justify-between text-xs font-sans">
            <span class="font-bold text-slate-300 flex items-center space-x-1.5">
              <span>Student Error Signal</span>
              <span class="bg-acadza-card px-2 py-0.5 rounded-full text-[10px] text-acadza-amber font-mono font-bold">${item.reports.length} report(s)</span>
            </span>
            <span class="text-[11px] text-slate-300">Sensor lead, not an instruction</span>
          </div>
          <div class="space-y-2">
            ${item.reports.map(r => `
              <div class="bg-acadza-surface p-3 rounded-xl border border-acadza-border flex items-start justify-between text-xs">
                <div class="space-y-1">
                  <div class="font-mono text-slate-200 font-medium">"${escapeHtml(r.comment)}"</div>
                  <div class="text-[10px] text-slate-300 font-mono">Student: ${escapeHtml(r.studentId)} • Platform: ${escapeHtml(r.source.toUpperCase())} • Reported: ${escapeHtml(new Date(r.reportedAt).toLocaleDateString())}</div>
                </div>
                <span class="text-[10px] font-mono text-slate-400 bg-acadza-navy px-2 py-0.5 rounded-full border border-acadza-border">${escapeHtml(r.reportId)}</span>
              </div>
            `).join('')}
          </div>
        </div>

        <div class="bg-gradient-to-br from-acadza-card via-acadza-surface to-acadza-navy p-5 rounded-2xl border border-blue-500/30 space-y-3">
          <div class="flex items-center justify-between text-xs font-sans">
            <div class="flex items-center space-x-2">
              <span class="font-bold text-blue-300">Triage Evaluation & Evidence</span>
              <span class="bg-acadza-navy text-slate-300 px-2.5 py-0.5 rounded-full text-[10px] font-mono border border-acadza-border">Verdict: <strong class="text-white">${escapeHtml(triage.verdict)}</strong></span>
              ${triage.repair ? `<span class="bg-blue-950/60 text-blue-300 border border-blue-800/80 px-2.5 py-0.5 rounded-full text-[10px] font-mono">Repair: <strong>${escapeHtml(triage.repair)}</strong></span>` : ''}
            </div>
            <div class="flex items-center space-x-1.5 text-xs font-mono">
              <span class="text-slate-400">Confidence:</span>
              <span class="font-bold text-emerald-400">${Math.round(triage.confidence * 100)}%</span>
            </div>
          </div>

          <div class="bg-acadza-navy/90 p-3.5 rounded-xl border border-acadza-border text-xs text-slate-200 leading-relaxed font-body">
            ${escapeHtml(triage.evidence)}
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 flex-1">
          <div class="bg-acadza-navy/90 rounded-2xl p-4 border border-acadza-border space-y-2 flex flex-col">
            <div class="flex items-center justify-between text-xs text-slate-400 pb-2 border-b border-acadza-border font-sans">
              <span class="font-bold text-slate-300">Question Stem & Options</span>
              <span class="text-[10px] font-mono text-acadza-blue">MathML Native</span>
            </div>
            <div id="stored-question-html" class="text-xs text-slate-200 space-y-2 overflow-y-auto max-h-56 custom-scroll p-1 leading-relaxed"></div>
            <div class="pt-2 border-t border-acadza-border flex items-center justify-between text-xs font-sans">
              <span class="text-slate-400">Stored DB Key:</span>
              <span class="font-mono font-bold text-emerald-400 bg-acadza-card px-3 py-1 rounded-full border border-acadza-border">${escapeHtml(item.storedAnswer || 'N/A')}</span>
            </div>
          </div>

          <div class="bg-acadza-navy/90 rounded-2xl p-4 border border-acadza-border space-y-2 flex flex-col">
            <div class="flex items-center justify-between text-xs text-slate-400 pb-2 border-b border-acadza-border font-sans">
              <span class="font-bold text-slate-300">Solution Derivation</span>
              <span class="text-[10px] font-mono text-acadza-blue">MathML Native</span>
            </div>
            <div id="stored-solution-html" class="text-xs text-slate-200 space-y-2 overflow-y-auto max-h-56 custom-scroll p-1 leading-relaxed"></div>
          </div>
        </div>

        ${diff ? `
          <div class="bg-acadza-navy/90 rounded-2xl p-4 border border-acadza-amber/30 space-y-2.5">
            <div class="flex items-center justify-between text-xs font-sans">
              <span class="font-bold text-acadza-amber flex items-center space-x-1.5">
                <span>Proposed Surgical Patch</span>
                <span class="text-[10px] font-mono text-slate-400">Target Field: <strong>${escapeHtml(diff.field)}</strong></span>
              </span>
              <span class="text-[10px] text-slate-400 font-mono">Zero-Rewrite Policy Guaranteed</span>
            </div>
            <div class="grid grid-cols-2 gap-3 text-xs font-mono">
              <div class="bg-rose-950/20 border border-rose-900/40 p-3 rounded-xl text-rose-300 space-y-1">
                <div class="text-[10px] uppercase font-bold text-rose-400 tracking-wider">Before (Find)</div>
                <div class="break-all">${escapeHtml(diff.before)}</div>
              </div>
              <div class="bg-emerald-950/20 border border-emerald-900/40 p-3 rounded-xl text-emerald-300 space-y-1">
                <div class="text-[10px] uppercase font-bold text-emerald-400 tracking-wider">After (Replace)</div>
                <textarea id="proposed-edit-value" rows="3" aria-label="Proposed replacement value" class="w-full bg-transparent border-0 outline-none resize-y break-all">${escapeHtml(diff.after)}</textarea>
              </div>
            </div>
          </div>
        ` : ''}

        <div class="bg-acadza-navy/90 rounded-2xl p-4 border border-acadza-border space-y-2">
          <div class="flex items-center justify-between text-xs font-sans">
            <span class="font-bold text-slate-300">Student Response Preview</span>
            <span class="text-[10px] text-slate-500">Tone: 17-yr old stressed JEE/NEET aspirant</span>
          </div>
          <textarea id="student-reply-editor" rows="2" 
            class="w-full bg-acadza-surface border border-acadza-border rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-acadza-blue focus:ring-1 focus:ring-acadza-blue transition leading-relaxed">${escapeHtml(triage.student_reply)}</textarea>
        </div>

        <div class="pt-4 border-t border-acadza-border flex items-center justify-between font-sans">
          <div class="flex items-center space-x-2 text-xs">
            <button onclick="navigateCase(-1)" class="px-3.5 py-2 rounded-full bg-acadza-card hover:bg-acadza-cardHover text-slate-300 border border-acadza-border transition">
              ← Prev (K)
            </button>
            <button onclick="navigateCase(1)" class="px-3.5 py-2 rounded-full bg-acadza-card hover:bg-acadza-cardHover text-slate-300 border border-acadza-border transition">
              Next (J) →
            </button>
          </div>

          <div class="flex items-center space-x-3">
            <button onclick="recordDecision('REJECTED')" class="px-4 py-2.5 rounded-full text-xs font-bold bg-rose-950/50 text-rose-300 border border-rose-800/60 hover:bg-rose-900/70 transition">
              Reject / Dismiss (R)
            </button>
            ${diff ? `<button onclick="recordDecision('EDITED')" class="px-4 py-2.5 rounded-full text-xs font-bold bg-acadza-card text-acadza-amber border border-acadza-amber/40 hover:bg-acadza-cardHover transition">
              Save Edited Fix (E)
            </button>` : ''}
            <button onclick="recordDecision('APPROVED')" class="px-5 py-2.5 rounded-full text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/30 transition flex items-center space-x-1.5">
              <span>✓ Approve Decision (A)</span>
            </button>
          </div>
        </div>
      `;
      document.getElementById('stored-question-html').replaceChildren(
        createSafeQuestionFragment(item.rawQuestionHtml)
      );
      document.getElementById('stored-solution-html').replaceChildren(
        createSafeQuestionFragment(item.rawSolutionHtml)
      );
    }

    function recordDecision(action) {
      if (!['APPROVED', 'EDITED', 'REJECTED'].includes(action)) {
        throw new Error(`Unsupported decision: ${action}`);
      }

      const items = getFilteredItems();
      const current = items[activeIndex];
      if (!current) return;

      const replyText = document.getElementById('student-reply-editor').value;
      const proposedEdit = current.diff
        ? {
            field: current.diff.field,
            find: current.diff.find,
            replace: action === 'EDITED'
              ? document.getElementById('proposed-edit-value').value
              : current.diff.replace
          }
        : null;
      const notes = prompt(`Faculty comments for ${action} decision (optional):`, `Action ${action} confirmed by faculty`);

      saveAudit({
        action: action,
        questionId: current.questionId,
        reportCount: current.reportCount,
        studentReplySent: replyText,
        proposedEdit: proposedEdit,
        notes: notes,
        reviewer: "Faculty_SME_01",
        timestamp: new Date().toISOString()
      });

      alert(`Decision logged in this browser: ${action} for QID: ${current.questionId}. No question data was changed.`);
      navigateCase(1);
    }

    function navigateCase(delta) {
      const items = getFilteredItems();
      if (items.length === 0) return;
      activeIndex = (activeIndex + delta + items.length) % items.length;
      renderQueue();
    }

    function renderBonusScanner() {
      const container = document.getElementById('bonus-container');
      container.innerHTML = BONUS_DATA.map((b, i) => `
        <div class="bg-acadza-navy p-5 rounded-2xl border border-acadza-border hover:border-acadza-amber/40 transition space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-xs font-mono font-bold text-acadza-amber">QID: ${escapeHtml(b.questionId.substring(0, 8))}...</span>
            <span class="text-[10px] px-2.5 py-0.5 rounded-full font-mono bg-acadza-card text-blue-300 border border-acadza-border">${escapeHtml(b.defect_type)}</span>
          </div>
          <div class="text-xs text-slate-300 font-sans font-bold">${escapeHtml(b.subject)} • ${escapeHtml(b.chapter)}</div>
          <p class="text-xs text-slate-300 bg-acadza-surface p-3 rounded-xl border border-acadza-border leading-relaxed">${escapeHtml(b.detail)}</p>
          <div class="text-[11px] font-mono text-slate-400 bg-acadza-surface p-3 rounded-xl border border-acadza-border space-y-1">
            <div class="text-rose-400 text-[10px]">Find: ${escapeHtml(b.surgical_fix.find)}</div>
            <div class="text-emerald-400 text-[10px]">Replace: ${escapeHtml(b.surgical_fix.replace)}</div>
          </div>
          <button data-question-id="${escapeHtml(b.questionId)}" data-defect-type="${escapeHtml(b.defect_type)}" class="bonus-review-button w-full py-2.5 bg-acadza-blue hover:bg-blue-600 text-white rounded-full text-xs font-sans font-bold transition shadow-sm">
            Log Faculty Review
          </button>
        </div>
      `).join('');
      container.querySelectorAll('.bonus-review-button').forEach(button => {
        button.addEventListener('click', () => recordBonusReview(
          button.dataset.questionId,
          button.dataset.defectType
        ));
      });
    }

    function recordBonusReview(qid, type) {
      saveAudit({
        action: 'REVIEWED_LATENT',
        questionId: qid,
        reportCount: 0,
        notes: `Faculty review recorded for proposed ${type} fix`,
        reviewer: "Faculty_SME_01",
        timestamp: new Date().toISOString()
      });
      alert(`Faculty review logged for question ${qid}. No question data was changed.`);
    }

    function escapeHtml(str) {
      if (!str) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    }

    function createSafeQuestionFragment(markup) {
      const template = document.createElement('template');
      template.innerHTML = String(markup || '');
      template.content.querySelectorAll(
        'script, style, iframe, frame, frameset, object, embed, svg, link, meta, base, form, audio, video'
      ).forEach(element => element.remove());
      template.content.querySelectorAll('*').forEach(element => {
        Array.from(element.attributes).forEach(attribute => {
          const name = attribute.name.toLowerCase();
          if (
            name.startsWith('on') ||
            name === 'style' ||
            name === 'srcdoc' ||
            ['href', 'src', 'srcset', 'xlink:href', 'formaction', 'poster'].includes(name)
          ) {
            element.removeAttribute(attribute.name);
          }
        });
      });
      return template.content;
    }

    document.addEventListener('keydown', (e) => {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
      if (e.key === 'j' || e.key === 'ArrowDown') navigateCase(1);
      if (e.key === 'k' || e.key === 'ArrowUp') navigateCase(-1);
      if (e.key === 'a' || e.key === 'A') recordDecision('APPROVED');
      if (e.key === 'r' || e.key === 'R') recordDecision('REJECTED');
      if (e.key === 'e' || e.key === 'E') recordDecision('EDITED');
    });

    renderQueue();
    updateAuditUI();
  </script>
</body>
</html>
"""

html_content = html_template.replace(
    "__CONSOLE_DATA_PLACEHOLDER__", json.dumps(console_data).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
).replace(
    "__BONUS_DATA_PLACEHOLDER__", json.dumps(bonus_data).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
)

with open(PROJECT_DIR / "console/index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

with open(PROJECT_DIR / "index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Generated Acadza-branded spherical console at:")
print(f"1. {PROJECT_DIR / 'console/index.html'}")
print(f"2. {PROJECT_DIR / 'index.html'}")
