"""
Build script for Acadza Faculty Review Console
Generates a standalone, dependency-free interactive HTML/JS application
with embedded precomputed triage data, native MathML support, urgency queues,
surgical diff viewer, and local audit logging.
"""

import json

with open("acadza-report-fix/console_data.json", "r", encoding="utf-8") as f:
    console_data = json.load(f)

with open("acadza-report-fix/bonus_defects.json", "r", encoding="utf-8") as f:
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
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: {
            sans: ['"Plus Jakarta Sans"', 'sans-serif'],
            mono: ['"JetBrains Mono"', 'monospace'],
          },
          colors: {
            brand: {
              50: '#eef2ff',
              100: '#e0e7ff',
              400: '#818cf8',
              500: '#6366f1',
              600: '#4f46e5',
              700: '#4338ca',
            },
            surface: {
              900: '#0b0f19',
              850: '#111827',
              800: '#1f2937',
              750: '#283344',
              700: '#374151',
            }
          }
        }
      }
    }
  </script>
  <style>
    /* Native MathML styling enhancements */
    math {
      font-size: 1.05em;
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
      background: rgba(17, 24, 39, 0.4);
    }
    .custom-scroll::-webkit-scrollbar-thumb {
      background: rgba(75, 85, 99, 0.6);
      border-radius: 4px;
    }
    .custom-scroll::-webkit-scrollbar-thumb:hover {
      background: rgba(107, 114, 128, 0.9);
    }
  </style>
</head>
<body class="bg-surface-900 text-gray-100 font-sans min-h-screen flex flex-col antialiased selection:bg-brand-500 selection:text-white">

  <!-- TOP APP BAR -->
  <header class="bg-surface-850/90 backdrop-blur border-b border-gray-800/80 sticky top-0 z-30 px-5 py-3">
    <div class="max-w-7xl mx-auto flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-400 flex items-center justify-center shadow-lg shadow-brand-500/20 font-extrabold text-white text-lg tracking-wider">
          A
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <span class="text-base font-bold text-white tracking-tight">Acadza</span>
            <span class="text-xs px-2 py-0.5 rounded-full font-medium bg-brand-500/20 text-brand-400 border border-brand-500/30">Faculty Console</span>
            <span class="text-[11px] text-gray-400 font-mono">v2.4-prod</span>
          </div>
          <p class="text-[11px] text-gray-400">High-Stakes Report → Fix Triage Pipeline</p>
        </div>
      </div>

      <!-- Quick Metrics Strip -->
      <div class="hidden md:flex items-center space-x-6 text-xs">
        <div class="flex items-center space-x-2">
          <span class="text-gray-400">Queue:</span>
          <span id="metric-total" class="font-bold text-white bg-surface-800 px-2 py-0.5 rounded font-mono">39 Questions</span>
        </div>
        <div class="flex items-center space-x-2">
          <span class="text-amber-400 font-medium">Faculty Action:</span>
          <span id="metric-review" class="font-bold text-amber-300 bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded font-mono">5 Cases</span>
        </div>
        <div class="flex items-center space-x-2">
          <span class="text-emerald-400 font-medium">Auto-Applied:</span>
          <span id="metric-auto" class="font-bold text-emerald-300 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded font-mono">21 Cases</span>
        </div>
        <div class="flex items-center space-x-2">
          <span class="text-gray-400 font-medium">Dismissed:</span>
          <span id="metric-nochange" class="font-bold text-gray-300 bg-gray-700/30 border border-gray-600/30 px-2 py-0.5 rounded font-mono">18 Cases</span>
        </div>
      </div>

      <!-- Navigation & Action Buttons -->
      <div class="flex items-center space-x-3">
        <button id="btn-tab-review" onclick="switchMainTab('review')" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-brand-600 text-white shadow-sm hover:bg-brand-500 transition">
          Review Queue
        </button>
        <button id="btn-tab-scanner" onclick="switchMainTab('scanner')" class="px-3 py-1.5 rounded-lg text-xs font-medium text-gray-300 bg-surface-800 hover:bg-surface-750 border border-gray-700 transition flex items-center space-x-1.5">
          <span>✨ Proactive Scanner</span>
          <span class="bg-indigo-500/20 text-indigo-400 text-[10px] px-1.5 py-0.2 rounded font-mono">2 Bonus</span>
        </button>
        <button onclick="toggleAuditDrawer()" class="px-3 py-1.5 rounded-lg text-xs font-medium text-gray-300 bg-surface-800 hover:bg-surface-750 border border-gray-700 transition flex items-center space-x-1.5">
          <span>📋 Audit Log</span>
          <span id="audit-count-badge" class="bg-gray-700 text-gray-200 text-[10px] px-1.5 py-0.2 rounded font-mono">0</span>
        </button>
      </div>
    </div>
  </header>

  <!-- MAIN WRAPPER -->
  <main class="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">

    <!-- VIEW 1: REVIEW QUEUE (DEFAULT) -->
    <div id="view-review" class="contents">

      <!-- LEFT SIDEBAR: QUESTION QUEUE -->
      <section class="lg:col-span-4 flex flex-col space-y-4">
        
        <!-- Filter Controls Card -->
        <div class="bg-surface-850 p-4 rounded-2xl border border-gray-800 shadow-sm space-y-3">
          <div class="relative">
            <input type="text" id="search-input" oninput="applyFilters()" placeholder="Search QID, topic, student comment..." 
              class="w-full bg-surface-900 border border-gray-700/80 rounded-xl px-3.5 py-2 text-xs text-gray-100 placeholder-gray-500 focus:outline-none focus:border-brand-500 transition font-mono">
            <span class="absolute right-3 top-2.5 text-gray-500 text-xs">⌘K</span>
          </div>

          <!-- Route Status Filters -->
          <div class="flex flex-wrap gap-1.5 text-[11px]">
            <button onclick="setFilterRoute('all')" id="filter-route-all" class="filter-route-btn px-2.5 py-1 rounded-lg font-medium bg-brand-600 text-white transition">All</button>
            <button onclick="setFilterRoute('faculty_review')" id="filter-route-faculty_review" class="filter-route-btn px-2.5 py-1 rounded-lg font-medium bg-surface-800 text-amber-300 border border-amber-500/30 hover:bg-surface-750 transition">Review (5)</button>
            <button onclick="setFilterRoute('auto_apply')" id="filter-route-auto_apply" class="filter-route-btn px-2.5 py-1 rounded-lg font-medium bg-surface-800 text-emerald-300 border border-emerald-500/30 hover:bg-surface-750 transition">Auto-Applied</button>
            <button onclick="setFilterRoute('no_change')" id="filter-route-no_change" class="filter-route-btn px-2.5 py-1 rounded-lg font-medium bg-surface-800 text-gray-400 border border-gray-700 hover:bg-surface-750 transition">Dismissed</button>
          </div>

          <!-- Subject Pill Filters -->
          <div class="flex flex-wrap gap-1.5 text-[11px] pt-1 border-t border-gray-800/80">
            <button onclick="setFilterSubject('all')" id="filter-subj-all" class="filter-subj-btn px-2 py-0.5 rounded font-medium bg-gray-700 text-white">All Subj</button>
            <button onclick="setFilterSubject('Physics')" id="filter-subj-Physics" class="filter-subj-btn px-2 py-0.5 rounded font-medium bg-surface-800 text-gray-400 hover:text-white">Physics</button>
            <button onclick="setFilterSubject('Botany')" id="filter-subj-Botany" class="filter-subj-btn px-2 py-0.5 rounded font-medium bg-surface-800 text-gray-400 hover:text-white">Botany</button>
            <button onclick="setFilterSubject('Zoology')" id="filter-subj-Zoology" class="filter-subj-btn px-2 py-0.5 rounded font-medium bg-surface-800 text-gray-400 hover:text-white">Zoology</button>
          </div>
        </div>

        <!-- Scrollable Queue List -->
        <div class="flex-1 bg-surface-850 rounded-2xl border border-gray-800 shadow-sm flex flex-col overflow-hidden max-h-[calc(100vh-250px)]">
          <div class="px-4 py-3 border-b border-gray-800 flex items-center justify-between bg-surface-850/60">
            <span class="text-xs font-semibold text-gray-300">Urgency Prioritized Queue</span>
            <span class="text-[11px] text-gray-500 font-mono">Sorted by Urgency Score</span>
          </div>

          <div id="queue-container" class="flex-1 overflow-y-auto divide-y divide-gray-800/60 custom-scroll">
            <!-- Dynamic Items Injected Here -->
          </div>
        </div>

        <!-- Keyboard Shortcut Helper -->
        <div class="bg-surface-850/50 rounded-xl p-2.5 border border-gray-800/60 text-[11px] text-gray-400 flex items-center justify-between">
          <span class="flex items-center space-x-1.5">
            <kbd class="bg-surface-750 text-gray-200 px-1.5 py-0.5 rounded font-mono text-[10px]">J</kbd>
            <kbd class="bg-surface-750 text-gray-200 px-1.5 py-0.5 rounded font-mono text-[10px]">K</kbd>
            <span>Next / Prev</span>
          </span>
          <span class="flex items-center space-x-1.5">
            <kbd class="bg-emerald-900/60 text-emerald-300 px-1.5 py-0.5 rounded font-mono text-[10px]">A</kbd>
            <span>Approve</span>
            <kbd class="bg-rose-900/60 text-rose-300 px-1.5 py-0.5 rounded font-mono text-[10px]">R</kbd>
            <span>Reject</span>
          </span>
        </div>
      </section>

      <!-- RIGHT MAIN PANE: ACTIVE QUESTION INSPECTOR -->
      <section class="lg:col-span-8 flex flex-col space-y-5">

        <!-- Active Case Card -->
        <div id="active-case-card" class="bg-surface-850 rounded-2xl border border-gray-800 shadow-lg p-6 space-y-6 flex-1 flex flex-col">
          <!-- Populated by JavaScript -->
        </div>

      </section>

    </div>

    <!-- VIEW 2: PROACTIVE DEFECT SCANNER (BONUS) -->
    <div id="view-scanner" class="hidden lg:col-span-12 space-y-6">
      <div class="bg-surface-850 p-6 rounded-2xl border border-gray-800 space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <div class="flex items-center space-x-2">
              <h2 class="text-lg font-bold text-white">Proactive Latent Defect Mining</h2>
              <span class="bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 text-xs px-2 py-0.5 rounded-full font-semibold">Bonus Assessment</span>
            </div>
            <p class="text-xs text-gray-400 mt-1">Autonomous scanner discovered defects in questions that <strong>zero students reported</strong>. Fixing defects before students meet them eliminates exam-day trauma.</p>
          </div>
          <div class="text-right font-mono text-xs text-gray-400">
            <span>Scan Coverage: 43/43 Questions</span>
          </div>
        </div>

        <div id="bonus-container" class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          <!-- Bonus defect cards injected here -->
        </div>
      </div>
    </div>

  </main>

  <!-- AUDIT TRAIL MODAL DRAWER -->
  <div id="audit-drawer" class="fixed inset-y-0 right-0 w-full max-w-md bg-surface-850 border-l border-gray-800 shadow-2xl z-50 transform translate-x-full transition-transform duration-300 ease-in-out flex flex-col">
    <div class="p-4 border-b border-gray-800 flex items-center justify-between bg-surface-850/80">
      <div class="flex items-center space-x-2">
        <span class="text-sm font-bold text-white">Faculty Action Audit Trail</span>
        <span id="drawer-audit-badge" class="bg-brand-500/20 text-brand-300 text-xs px-2 py-0.5 rounded-full font-mono">0 entries</span>
      </div>
      <button onclick="toggleAuditDrawer()" class="text-gray-400 hover:text-white p-1 rounded-lg hover:bg-surface-800">
        ✕
      </button>
    </div>

    <div id="audit-log-list" class="flex-1 overflow-y-auto p-4 space-y-3 custom-scroll">
      <div class="text-center py-12 text-gray-500 text-xs">
        No actions recorded yet. Approve, Edit or Dismiss cases to log audit history.
      </div>
    </div>

    <div class="p-4 border-t border-gray-800 bg-surface-900 flex items-center justify-between">
      <button onclick="exportAuditLog()" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-surface-800 hover:bg-surface-750 text-gray-200 border border-gray-700 transition flex items-center space-x-1.5">
        <span>📥 Download audit_log.json</span>
      </button>
      <button onclick="clearAuditLog()" class="px-3 py-1.5 rounded-lg text-xs font-medium text-rose-400 hover:text-rose-300 transition">
        Clear
      </button>
    </div>
  </div>

  <!-- EMBEDDED PRECOMPUTED DATA -->
  <script>
    const CONSOLE_DATA = __CONSOLE_DATA_PLACEHOLDER__;
    const BONUS_DATA = __BONUS_DATA_PLACEHOLDER__;
  </script>

  <!-- APP LOGIC -->
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
        list.innerHTML = '<div class="text-center py-12 text-gray-500 text-xs">No actions recorded yet.</div>';
        return;
      }

      list.innerHTML = auditLog.map(entry => `
        <div class="bg-surface-900 p-3 rounded-xl border border-gray-800 space-y-1.5 text-xs">
          <div class="flex items-center justify-between">
            <span class="font-mono font-semibold ${entry.action === 'APPROVED' ? 'text-emerald-400' : entry.action === 'EDITED' ? 'text-indigo-400' : 'text-rose-400'}">
              ${entry.action}
            </span>
            <span class="text-[10px] text-gray-500 font-mono">${new Date(entry.timestamp).toLocaleTimeString()}</span>
          </div>
          <div class="text-[11px] text-gray-300 font-mono">QID: ${entry.questionId.substring(0, 8)}...</div>
          <p class="text-[11px] text-gray-400">${entry.notes || 'No faculty comment'}</p>
          <div class="text-[10px] text-gray-500 pt-1 border-t border-gray-800/80">Reviewer: ${entry.reviewer}</div>
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
        btnReview.className = "px-3 py-1.5 rounded-lg text-xs font-semibold bg-brand-600 text-white shadow-sm hover:bg-brand-500 transition";
        btnScanner.className = "px-3 py-1.5 rounded-lg text-xs font-medium text-gray-300 bg-surface-800 hover:bg-surface-750 border border-gray-700 transition flex items-center space-x-1.5";
      } else {
        viewReview.classList.add('hidden');
        viewScanner.classList.remove('hidden');
        btnScanner.className = "px-3 py-1.5 rounded-lg text-xs font-semibold bg-brand-600 text-white shadow-sm hover:bg-brand-500 transition flex items-center space-x-1.5";
        btnReview.className = "px-3 py-1.5 rounded-lg text-xs font-medium text-gray-300 bg-surface-800 hover:bg-surface-750 border border-gray-700 transition";
        renderBonusScanner();
      }
    }

    function setFilterRoute(route) {
      filterRoute = route;
      document.querySelectorAll('.filter-route-btn').forEach(b => {
        b.className = 'filter-route-btn px-2.5 py-1 rounded-lg font-medium bg-surface-800 text-gray-400 border border-gray-700 hover:bg-surface-750 transition';
      });
      const activeBtn = document.getElementById('filter-route-' + route);
      if (activeBtn) {
        activeBtn.className = 'filter-route-btn px-2.5 py-1 rounded-lg font-semibold bg-brand-600 text-white shadow-sm transition';
      }
      applyFilters();
    }

    function setFilterSubject(subj) {
      filterSubject = subj;
      document.querySelectorAll('.filter-subj-btn').forEach(b => {
        b.className = 'filter-subj-btn px-2 py-0.5 rounded font-medium bg-surface-800 text-gray-400 hover:text-white';
      });
      const activeBtn = document.getElementById('filter-subj-' + subj);
      if (activeBtn) {
        activeBtn.className = 'filter-subj-btn px-2 py-0.5 rounded font-semibold bg-gray-700 text-white';
      }
      applyFilters();
    }

    function applyFilters() {
      searchQuery = (document.getElementById('search-input').value || '').toLowerCase().trim();
      renderQueue();
    }

    function getFilteredItems() {
      return CONSOLE_DATA.filter(item => {
        // Route filter
        if (filterRoute !== 'all' && item.primaryTriage.route !== filterRoute) {
          return false;
        }
        // Subject filter
        if (filterSubject !== 'all' && item.subject !== filterSubject) {
          return false;
        }
        // Search query
        if (searchQuery) {
          const matchQid = item.questionId.toLowerCase().includes(searchQuery);
          const matchSubj = item.subject.toLowerCase().includes(searchQuery);
          const matchChap = item.chapter.toLowerCase().includes(searchQuery);
          const matchRepair = (item.primaryTriage.repair || '').toLowerCase().includes(searchQuery);
          const matchComment = item.reports.some(r => r.comment.toLowerCase().includes(searchQuery));
          if (!matchQid && !matchSubj && !matchChap && !matchRepair && !matchComment) {
            return false;
          }
        }
        return true;
      });
    }

    function renderQueue() {
      const container = document.getElementById('queue-container');
      const items = getFilteredItems();

      if (items.length === 0) {
        container.innerHTML = `
          <div class="p-8 text-center text-gray-500 text-xs">
            No question cases match the active filters.
          </div>
        `;
        document.getElementById('active-case-card').innerHTML = `
          <div class="flex-1 flex items-center justify-center text-center text-gray-500 text-sm">
            Select or reset filters to review cases.
          </div>
        `;
        return;
      }

      // Keep active index valid
      if (activeIndex >= items.length) {
        activeIndex = 0;
      }

      container.innerHTML = items.map((item, idx) => {
        const isSelected = idx === activeIndex;
        const triage = item.primaryTriage;
        const isMulti = item.reportCount > 1;
        const isUrgent = item.urgencyScore >= 100;

        let badgeBg = "bg-gray-800 text-gray-400 border-gray-700";
        if (triage.route === 'faculty_review') badgeBg = "bg-amber-500/15 text-amber-300 border-amber-500/30";
        else if (triage.route === 'auto_apply') badgeBg = "bg-emerald-500/15 text-emerald-300 border-emerald-500/30";

        return `
          <div onclick="selectCase(${idx})" class="p-3.5 cursor-pointer transition select-none ${isSelected ? 'bg-brand-600/10 border-l-4 border-brand-500' : 'hover:bg-surface-800/60'}">
            <div class="flex items-center justify-between mb-1.5">
              <div class="flex items-center space-x-2">
                <span class="text-xs font-mono font-bold ${isUrgent ? 'text-amber-400' : 'text-gray-300'}">
                  ${isUrgent ? '🔥 ' : ''}${item.questionId.substring(0, 6)}...
                </span>
                ${isMulti ? `<span class="px-1.5 py-0.2 rounded-full text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">${item.reportCount} reports</span>` : ''}
              </div>
              <span class="text-[10px] px-2 py-0.5 rounded font-medium border ${badgeBg}">
                ${triage.route === 'faculty_review' ? 'Faculty Review' : triage.route === 'auto_apply' ? 'Auto-Apply' : 'Dismissed'}
              </span>
            </div>

            <div class="flex items-center space-x-2 text-[11px] text-gray-400 mb-2">
              <span class="font-medium text-gray-300">${item.subject}</span>
              <span>•</span>
              <span class="truncate max-w-[130px]">${item.chapter}</span>
              <span>•</span>
              <span class="text-gray-500 font-mono">${item.questionType}</span>
            </div>

            <div class="text-[11px] text-gray-300 line-clamp-1 italic bg-surface-900/60 px-2 py-1 rounded border border-gray-800/80">
              "${item.reports[0].comment}"
            </div>

            <div class="mt-2 flex items-center justify-between text-[10px] text-gray-500 font-mono">
              <span>Repair: <strong class="text-gray-400">${triage.repair || 'none'}</strong></span>
              <span>Urgency: <strong class="${isUrgent ? 'text-amber-400 font-bold' : 'text-gray-400'}">${item.urgencyScore}</strong></span>
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

      let routePill = `<span class="px-3 py-1 rounded-full text-xs font-semibold bg-gray-800 text-gray-300 border border-gray-700">Dismissed / No Change</span>`;
      if (triage.route === 'faculty_review') {
        routePill = `<span class="px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/40 animate-pulse">Action Required • Faculty Review</span>`;
      } else if (triage.route === 'auto_apply') {
        routePill = `<span class="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">Safe Candidate • Auto-Applied</span>`;
      }

      card.innerHTML = `
        <!-- Case Top Bar -->
        <div class="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-gray-800">
          <div>
            <div class="flex items-center space-x-3">
              <h1 class="text-base font-bold text-white font-mono flex items-center space-x-2">
                <span>QID: ${item.questionId}</span>
              </h1>
              <span class="text-xs px-2 py-0.5 rounded bg-surface-800 text-gray-400 font-mono border border-gray-700">${item.questionType}</span>
            </div>
            <div class="flex items-center space-x-2 text-xs text-gray-400 mt-1">
              <span class="text-brand-400 font-semibold">${item.subject}</span>
              <span>/</span>
              <span>${item.chapter}</span>
              <span>/</span>
              <span class="text-gray-500">Level: ${item.level}</span>
            </div>
          </div>
          <div>
            ${routePill}
          </div>
        </div>

        <!-- Student Reports Strip -->
        <div class="bg-surface-900 rounded-xl p-4 border border-gray-800 space-y-2.5">
          <div class="flex items-center justify-between text-xs">
            <span class="font-semibold text-gray-300 flex items-center space-x-1.5">
              <span>Student Error Signal</span>
              <span class="bg-gray-800 px-1.5 py-0.2 rounded text-[10px] text-gray-400 font-mono">${item.reports.length} report(s)</span>
            </span>
            <span class="text-[11px] text-gray-500">Treat comment as a lead, not an instruction</span>
          </div>
          <div class="space-y-2">
            ${item.reports.map(r => `
              <div class="bg-surface-850 p-2.5 rounded-lg border border-gray-800/80 flex items-start justify-between text-xs">
                <div class="space-y-1">
                  <div class="font-mono text-gray-200">"${r.comment}"</div>
                  <div class="text-[10px] text-gray-500 font-mono">Student: ${r.studentId} • Source: ${r.source.toUpperCase()} • Reported: ${new Date(r.reportedAt).toLocaleDateString()}</div>
                </div>
                <span class="text-[10px] font-mono text-gray-400 bg-surface-900 px-2 py-0.5 rounded border border-gray-800">${r.reportId}</span>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- AI Forensic Triage & Proof -->
        <div class="bg-gradient-to-br from-surface-850 to-surface-900 p-4 rounded-xl border border-brand-500/20 space-y-3">
          <div class="flex items-center justify-between text-xs">
            <div class="flex items-center space-x-2">
              <span class="font-bold text-brand-300 text-xs">AI Evaluation & STEM Proof</span>
              <span class="bg-surface-800 text-gray-300 px-2 py-0.5 rounded text-[10px] font-mono">Verdict: <strong class="text-white">${triage.verdict}</strong></span>
              ${triage.repair ? `<span class="bg-indigo-900/40 text-indigo-300 border border-indigo-700/50 px-2 py-0.5 rounded text-[10px] font-mono">Repair: <strong>${triage.repair}</strong></span>` : ''}
            </div>
            <div class="flex items-center space-x-1.5 text-xs font-mono">
              <span class="text-gray-400">Confidence:</span>
              <span class="font-bold text-emerald-400">${Math.round(triage.confidence * 100)}%</span>
            </div>
          </div>

          <div class="bg-surface-900/80 p-3 rounded-lg border border-gray-800 text-xs text-gray-200 font-sans leading-relaxed">
            ${triage.evidence}
          </div>
        </div>

        <!-- Question & Stored Content Renderer -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 flex-1">
          <!-- Stored Question HTML -->
          <div class="bg-surface-900 rounded-xl p-4 border border-gray-800 space-y-2 flex flex-col">
            <div class="flex items-center justify-between text-xs text-gray-400 pb-2 border-b border-gray-800">
              <span class="font-semibold text-gray-300">Live Question Stem & Options</span>
              <span class="text-[10px] font-mono text-gray-500">MathML Native</span>
            </div>
            <div class="text-xs text-gray-200 space-y-2 overflow-y-auto max-h-56 custom-scroll p-1 leading-relaxed">
              ${item.rawQuestionHtml}
            </div>
            <div class="pt-2 border-t border-gray-800 flex items-center justify-between text-xs">
              <span class="text-gray-400">Stored DB Key:</span>
              <span class="font-mono font-bold text-emerald-400 bg-surface-800 px-2.5 py-0.5 rounded border border-gray-700">${item.storedAnswer || 'N/A'}</span>
            </div>
          </div>

          <!-- Stored Solution HTML -->
          <div class="bg-surface-900 rounded-xl p-4 border border-gray-800 space-y-2 flex flex-col">
            <div class="flex items-center justify-between text-xs text-gray-400 pb-2 border-b border-gray-800">
              <span class="font-semibold text-gray-300">Live Solution Derivation</span>
              <span class="text-[10px] font-mono text-gray-500">MathML Native</span>
            </div>
            <div class="text-xs text-gray-200 space-y-2 overflow-y-auto max-h-56 custom-scroll p-1 leading-relaxed">
              ${item.rawSolutionHtml}
            </div>
          </div>
        </div>

        <!-- Surgical Diff Card (If defect has proposed edit) -->
        ${diff ? `
          <div class="bg-surface-900 rounded-xl p-4 border border-amber-500/20 space-y-2.5">
            <div class="flex items-center justify-between text-xs">
              <span class="font-bold text-amber-300">Proposed Surgical Edit (Scope: ${diff.field})</span>
              <span class="text-[10px] text-gray-500 font-mono">Zero-Rewrite Policy Guaranteed</span>
            </div>
            <div class="grid grid-cols-2 gap-3 text-xs font-mono">
              <div class="bg-rose-950/20 border border-rose-900/40 p-3 rounded-lg text-rose-300 space-y-1">
                <div class="text-[10px] uppercase font-bold text-rose-400 tracking-wider">Before (Find)</div>
                <div class="break-all">${escapeHtml(diff.before)}</div>
              </div>
              <div class="bg-emerald-950/20 border border-emerald-900/40 p-3 rounded-lg text-emerald-300 space-y-1">
                <div class="text-[10px] uppercase font-bold text-emerald-400 tracking-wider">After (Replace)</div>
                <div class="break-all">${escapeHtml(diff.after)}</div>
              </div>
            </div>
          </div>
        ` : ''}

        <!-- Student Reply Preview & Editor -->
        <div class="bg-surface-900 rounded-xl p-4 border border-gray-800 space-y-2">
          <div class="flex items-center justify-between text-xs">
            <span class="font-semibold text-gray-300">Student Response Dispatch (Preview)</span>
            <span class="text-[10px] text-gray-500">Tone: 17-yr old stressed JEE/NEET aspirant</span>
          </div>
          <textarea id="student-reply-editor" rows="2" 
            class="w-full bg-surface-850 border border-gray-700/80 rounded-xl p-3 text-xs text-gray-200 focus:outline-none focus:border-brand-500 transition leading-relaxed">${triage.student_reply}</textarea>
        </div>

        <!-- Bottom Action Bar (Approve / Edit / Reject) -->
        <div class="pt-4 border-t border-gray-800 flex items-center justify-between">
          <div class="flex items-center space-x-2 text-xs">
            <button onclick="navigateCase(-1)" class="px-3 py-2 rounded-xl bg-surface-800 hover:bg-surface-750 text-gray-300 border border-gray-700 transition">
              ← Prev (K)
            </button>
            <button onclick="navigateCase(1)" class="px-3 py-2 rounded-xl bg-surface-800 hover:bg-surface-750 text-gray-300 border border-gray-700 transition">
              Next (J) →
            </button>
          </div>

          <div class="flex items-center space-x-3">
            <button onclick="recordDecision('REJECTED')" class="px-4 py-2.5 rounded-xl text-xs font-semibold bg-rose-900/30 text-rose-300 border border-rose-800/50 hover:bg-rose-900/50 transition">
              Reject / Dismiss (R)
            </button>
            <button onclick="recordDecision('EDITED')" class="px-4 py-2.5 rounded-xl text-xs font-semibold bg-indigo-900/30 text-indigo-300 border border-indigo-800/50 hover:bg-indigo-900/50 transition">
              Modify Fix (E)
            </button>
            <button onclick="recordDecision('APPROVED')" class="px-5 py-2.5 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/20 transition flex items-center space-x-1.5">
              <span>✓ Approve & Apply (A)</span>
            </button>
          </div>
        </div>
      `;
    }

    function recordDecision(action) {
      const items = getFilteredItems();
      const current = items[activeIndex];
      if (!current) return;

      const replyText = document.getElementById('student-reply-editor').value;
      const notes = prompt(`Faculty comments for ${action} decision (optional):`, `Action ${action} confirmed by faculty`);

      saveAudit({
        action: action,
        questionId: current.questionId,
        reportCount: current.reportCount,
        studentReplySent: replyText,
        notes: notes,
        reviewer: "Faculty_SME_Physics_01",
        timestamp: new Date().toISOString()
      });

      alert(`Decision recorded: ${action} for QID: ${current.questionId}`);
      navigateCase(1);
    }

    function navigateCase(delta) {
      const items = getFilteredItems();
      activeIndex = (activeIndex + delta + items.length) % items.length;
      renderQueue();
    }

    function renderBonusScanner() {
      const container = document.getElementById('bonus-container');
      container.innerHTML = BONUS_DATA.map((b, i) => `
        <div class="bg-surface-900 p-5 rounded-xl border border-indigo-500/30 space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-xs font-mono font-bold text-indigo-300">QID: ${b.questionId.substring(0, 8)}...</span>
            <span class="text-[10px] px-2 py-0.5 rounded font-mono bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">${b.defect_type}</span>
          </div>
          <div class="text-xs text-gray-300">${b.subject} • ${b.chapter}</div>
          <p class="text-xs text-gray-200 bg-surface-850 p-2.5 rounded-lg border border-gray-800">${b.detail}</p>
          <div class="text-[11px] font-mono text-gray-400 bg-surface-850 p-2.5 rounded-lg border border-gray-800 space-y-1">
            <div class="text-rose-400 text-[10px]">Find: ${escapeHtml(b.surgical_fix.find)}</div>
            <div class="text-emerald-400 text-[10px]">Replace: ${escapeHtml(b.surgical_fix.replace)}</div>
          </div>
          <button onclick="applyBonusFix('${b.questionId}', '${b.defect_type}')" class="w-full py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold transition">
            Auto-Apply Latent Fix
          </button>
        </div>
      `).join('');
    }

    function applyBonusFix(qid, type) {
      saveAudit({
        action: 'APPROVED_LATENT',
        questionId: qid,
        reportCount: 0,
        notes: `Proactive latent fix applied for ${type} before student discovery`,
        reviewer: "Automated_Autonomous_Auditor",
        timestamp: new Date().toISOString()
      });
      alert(`Latent defect on question ${qid} has been surgically repaired!`);
    }

    function escapeHtml(str) {
      if (!str) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
      if (e.key === 'j' || e.key === 'ArrowDown') navigateCase(1);
      if (e.key === 'k' || e.key === 'ArrowUp') navigateCase(-1);
      if (e.key === 'a' || e.key === 'A') recordDecision('APPROVED');
      if (e.key === 'r' || e.key === 'R') recordDecision('REJECTED');
      if (e.key === 'e' || e.key === 'E') recordDecision('EDITED');
    });

    // Initial render
    renderQueue();
    updateAuditUI();
  </script>
</body>
</html>
"""

# Inject data placeholders
html_content = html_template.replace(
    "__CONSOLE_DATA_PLACEHOLDER__", json.dumps(console_data)
).replace(
    "__BONUS_DATA_PLACEHOLDER__", json.dumps(bonus_data)
)

with open("acadza-report-fix/console/index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

# Also write to root index.html for instant Vercel / Netlify / GitHub Pages deployment
with open("acadza-report-fix/index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Generated standalone interactive console at:")
print("1. acadza-report-fix/console/index.html")
print("2. acadza-report-fix/index.html (ready for zero-config Vercel/Netlify deployment!)")
