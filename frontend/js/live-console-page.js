import { api } from "./api.js";
import { getCurrentUser, signIn, signOut } from "./supabase-client.js";
import { subscribeFacultyChanges } from "./realtime.js";

const el = (id) => document.getElementById(id);
let activeSubscription;
let currentUser;

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[char]));
}

function safeRichHtml(value) {
  const parser = new DOMParser();
  const doc = parser.parseFromString(String(value || ""), "text/html");
  doc.querySelectorAll("script,style,iframe,frame,object,embed,svg,link,meta,base,form,audio,video").forEach((node) => node.remove());
  doc.querySelectorAll("*").forEach((node) => {
    [...node.attributes].forEach((attr) => {
      const name = attr.name.toLowerCase();
      if (name.startsWith("on") || ["style","srcdoc","href","src","srcset","xlink:href","formaction","poster"].includes(name)) {
        node.removeAttribute(attr.name);
      }
    });
  });
  return doc.body.innerHTML;
}

function notify(message, isError = false) {
  el("page-error").textContent = isError ? message : "";
  if (!isError) el("connection").textContent = message;
}

function renderQueue(rows) {
  el("metric-open").textContent = rows.length;
  el("metric-proposals").textContent = rows.filter((row) => row.proposal_status === "pending").length;
  el("metric-user").textContent = currentUser?.email || "Faculty";
  el("metric-refresh").textContent = new Date().toLocaleTimeString();

  if (!rows.length) {
    el("queue").innerHTML = '<div class="panel p-8 text-center text-slate-400">No open review cases.</div>';
    return;
  }

  el("queue").innerHTML = rows.map((row) => {
    const reportId = escapeHtml(row.id);
    const proposalId = escapeHtml(row.proposal_id || "");
    const content = row.content || {};
    const editable = row.proposal_status === "pending" && row.proposal_id;
    const repairs = ["spelling","noise","exam_reference","markup_leak","answer_form","notation","stem_data","option_repair","solution_fix","solution_missing","answer_key","type_mismatch","identical_options","diagram","wrong_question","unsound","wrong_chapter","syllabus"];
    const repairOptions = repairs.map((name) =>
      '<option value="' + name + '"' + (row.repair === name ? " selected" : "") + '>' + name + '</option>'
    ).join("");
    const fieldOptions = ["question","solution","answer","questionType"].map((name) =>
      '<option value="' + name + '"' + (row.edit?.field === name ? " selected" : "") + '>' + name + '</option>'
    ).join("");

    return '<article class="panel p-5 space-y-4" data-report="' + reportId + '">' +
      '<div class="flex items-start justify-between gap-3"><div>' +
      '<div class="text-xs text-blue-300 font-mono">' + escapeHtml(row.question_id) + '</div>' +
      '<h3 class="font-bold">' + escapeHtml(row.subject || "Subject") + ' · ' + escapeHtml(row.chapter || "Chapter") + '</h3>' +
      '<div class="text-xs text-slate-500 mt-1">Report ' + reportId + ' · question version ' + escapeHtml(row.version) + '</div></div>' +
      '<span class="text-[10px] uppercase rounded-full px-3 py-1 bg-amber-950 text-amber-300">' + escapeHtml(row.status) + '</span></div>' +
      '<div class="rounded-xl bg-[#070d1e] p-3"><div class="text-[10px] uppercase text-slate-500 mb-2">Student comment</div><p class="text-sm">' + escapeHtml(row.comment) + '</p></div>' +
      '<div class="grid md:grid-cols-2 gap-3">' +
      '<div class="rounded-xl bg-[#070d1e] p-3"><div class="text-[10px] uppercase text-slate-500 mb-2">Question</div><div class="text-sm leading-6">' + safeRichHtml(content.question || "") + '</div></div>' +
      '<div class="rounded-xl bg-[#070d1e] p-3"><div class="text-[10px] uppercase text-slate-500 mb-2">Solution</div><div class="text-sm leading-6">' + safeRichHtml(content.solution || "") + '</div></div></div>' +
      '<div class="text-xs space-y-1"><div><b>AI verdict:</b> ' + escapeHtml(row.verdict || "Not triaged") + ' · ' + escapeHtml(row.triage_repair || "No repair category") + ' · confidence ' + escapeHtml(row.confidence ?? "-") + '</div>' +
      '<p class="text-slate-400">' + escapeHtml(row.evidence || "No triage evidence. New reports are routed directly to faculty review.") + '</p>' +
      (row.student_reply ? '<p class="text-emerald-300">Student reply preview: ' + escapeHtml(row.student_reply) + '</p>' : "") + '</div>' +
      '<form class="proposal-form border-t border-blue-950 pt-4 space-y-2" data-report="' + reportId + '">' +
      '<div class="text-xs font-bold">Create / replace faculty proposal</div>' +
      '<div class="grid md:grid-cols-2 gap-2"><select name="repair" class="field" required><option value="">Select repair type</option>' + repairOptions + '</select>' +
      '<select name="field" class="field"><option value="">No direct text edit (manual review)</option>' + fieldOptions + '</select></div>' +
      '<input name="find" class="field" placeholder="Exact text to find" value="' + escapeHtml(row.edit?.find || "") + '">' +
      '<input name="replace" class="field" placeholder="Replacement text" value="' + escapeHtml(row.edit?.replace || "") + '">' +
      '<input name="note" class="field" placeholder="Faculty note (optional)">' +
      '<button class="btn bg-blue-700" type="submit">Save proposal</button></form>' +
      (editable ? '<div class="flex flex-wrap gap-2 border-t border-blue-950 pt-3">' +
        '<button class="approve btn bg-emerald-700" data-report="' + reportId + '" data-proposal="' + proposalId + '" data-version="' + escapeHtml(row.version) + '">Approve</button>' +
        '<button class="reject btn bg-rose-900" data-report="' + reportId + '" data-proposal="' + proposalId + '">Reject</button>' +
        '<span class="text-xs text-slate-500 self-center">Proposal based on version ' + escapeHtml(row.base_question_version) + '.</span></div>' :
        (row.proposal_status ? '<div class="text-xs text-slate-400">Latest proposal: ' + escapeHtml(row.proposal_status) + '</div>' : "")) +
      '</article>';
  }).join("");

  el("queue").querySelectorAll(".proposal-form").forEach((form) => {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const values = new FormData(form);
      const field = values.get("field");
      const find = values.get("find");
      const replace = values.get("replace");
      const edit = field ? { field, find, replace } : null;
      try {
        await api.createProposal(form.dataset.report, {
          repair: values.get("repair"), edit, note: values.get("note") || null
        });
        await refreshQueue();
        notify("Proposal saved.");
      } catch (error) { notify(error.message, true); }
    });
  });

  el("queue").querySelectorAll(".approve").forEach((button) => {
    button.addEventListener("click", async () => {
      const reason = window.prompt("Reason for approving this proposal:", "Reviewed by faculty");
      if (!reason) return;
      try {
        const result = await api.approve(
          button.dataset.report, button.dataset.proposal,
          Number(button.dataset.version), reason
        );
        await refreshQueue();
        notify(result.question_changed ? "Correction committed to database." : "Faculty decision recorded; manual follow-up is required.");
        await refreshAudit();
      } catch (error) {
        notify(error.message, true);
        if (error.status === 409) await refreshQueue();
      }
    });
  });

  el("queue").querySelectorAll(".reject").forEach((button) => {
    button.addEventListener("click", async () => {
      const reason = window.prompt("Reason for rejecting this proposal:");
      if (!reason) return;
      try {
        await api.reject(button.dataset.report, button.dataset.proposal, reason);
        await refreshQueue();
        notify("Proposal rejected.");
        await refreshAudit();
      } catch (error) { notify(error.message, true); }
    });
  });
}

async function refreshQueue() {
  const rows = await api.getQueue("open");
  renderQueue(rows);
}

async function refreshAudit() {
  const rows = await api.getAuditLogs();
  el("audit").innerHTML = rows.length ? rows.map((row) =>
    '<div class="border-b border-blue-950 py-2 flex flex-wrap gap-x-3">' +
    '<span class="text-slate-500">' + escapeHtml(new Date(row.created_at).toLocaleString()) + '</span>' +
    '<b>' + escapeHtml(row.action) + '</b>' +
    '<span>' + escapeHtml(row.entity_type) + ' ' + escapeHtml(row.entity_id) + '</span>' +
    '<span class="text-slate-500">' + escapeHtml(row.actor_id || "system") + '</span></div>'
  ).join("") : "No audit entries yet.";
}

async function enterApp() {
  currentUser = await getCurrentUser();
  const rows = await api.getQueue("open");
  el("login-panel").classList.add("hidden");
  el("app-panel").classList.remove("hidden");
  el("signout").classList.remove("hidden");
  renderQueue(rows);
  await refreshAudit();
  if (activeSubscription) activeSubscription();
  activeSubscription = subscribeFacultyChanges(
    async () => {
      try { await refreshQueue(); await refreshAudit(); }
      catch (error) { notify(error.message, true); }
    },
    (status) => {
      if (status === "SUBSCRIBED") {
        notify("Realtime connected — database changes will refresh this queue.");
      } else if (["CHANNEL_ERROR", "TIMED_OUT", "CLOSED"].includes(status)) {
        notify("Realtime is unavailable (" + status + "). Use Refresh Queue to fetch the latest data.", true);
      } else {
        notify("Signed in — realtime status: " + status);
      }
    }
  );
}

el("login-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  el("login-error").textContent = "";
  try {
    await signIn(el("email").value, el("password").value);
    await enterApp();
  } catch (error) { el("login-error").textContent = error.message; }
});

el("signout").addEventListener("click", async () => {
  if (activeSubscription) activeSubscription();
  await signOut();
  el("app-panel").classList.add("hidden");
  el("login-panel").classList.remove("hidden");
  el("signout").classList.add("hidden");
  el("connection").textContent = "Signed out";
});

el("refresh").addEventListener("click", () => refreshQueue().catch((error) => notify(error.message, true)));
el("refresh-audit").addEventListener("click", () => refreshAudit().catch((error) => notify(error.message, true)));

const configStatus = window.ACADZA_CONFIG_STATUS;
if (!configStatus?.configured) {
  const missing = configStatus?.missing?.join(", ") || "frontend runtime configuration endpoint";
  el("login-error").textContent =
    "Frontend is not configured yet. Missing: " + missing +
    ". Set SUPABASE_PUBLISHABLE_KEY in the frontend Vercel project, then redeploy.";
  el("login-form").querySelector('button[type="submit"]').disabled = true;
} else {
  try {
    await getCurrentUser();
    await enterApp();
  } catch {
    // No current session: show the sign-in card.
  }
}
