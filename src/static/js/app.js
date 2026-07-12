/* Chokepoint Research Workstation — professional UI client */
(function () {
  "use strict";

  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => Array.from(document.querySelectorAll(sel));

  function apiKey() {
    return ($("#key") && $("#key").value.trim()) || localStorage.getItem("chokepoint_api_key") || "";
  }

  function headers(json = true) {
    const h = {};
    if (json) h["Content-Type"] = "application/json";
    const k = apiKey();
    if (k) h["X-API-Key"] = k;
    return h;
  }

  function toast(msg, ms = 2800) {
    const el = $("#toast");
    if (!el) return;
    el.textContent = msg;
    el.classList.add("show");
    clearTimeout(toast._t);
    toast._t = setTimeout(() => el.classList.remove("show"), ms);
  }

  function pretty(obj) {
    try {
      return typeof obj === "string" ? obj : JSON.stringify(obj, null, 2);
    } catch {
      return String(obj);
    }
  }

  function setOut(el, data) {
    if (!el) return;
    el.textContent = pretty(data);
  }

  async function api(path, opts = {}) {
    const res = await fetch(path, {
      ...opts,
      headers: { ...headers(!(opts.body instanceof FormData) && opts.method !== "GET"), ...(opts.headers || {}) },
    });
    const ct = res.headers.get("content-type") || "";
    let body;
    if (ct.includes("application/json")) {
      body = await res.json();
    } else if (ct.includes("image/") || ct.includes("svg")) {
      body = await res.blob();
    } else {
      body = await res.text();
    }
    if (!res.ok) {
      const detail = body && body.detail ? body.detail : pretty(body);
      throw new Error(typeof detail === "string" ? detail : pretty(detail));
    }
    return body;
  }

  /* ── Language ─────────────────────────────────────────────── */
  function initLang() {
    const saved = localStorage.getItem("chokepoint_lang") || "zh";
    if (typeof window.applyI18n === "function") window.applyI18n(saved);
    const zh = $("#lang-zh");
    const en = $("#lang-en");
    function setActive(lang) {
      if (zh) zh.classList.toggle("active", lang === "zh");
      if (en) en.classList.toggle("active", lang === "en");
    }
    setActive(saved);
    if (zh)
      zh.addEventListener("click", () => {
        window.applyI18n("zh");
        setActive("zh");
      });
    if (en)
      en.addEventListener("click", () => {
        window.applyI18n("en");
        setActive("en");
      });
  }

  /* ── Tabs ─────────────────────────────────────────────────── */
  function switchTab(name) {
    $$(".nav-btn").forEach((b) => b.classList.toggle("active", b.dataset.tab === name));
    $$("main.content > section").forEach((sec) => {
      const id = sec.id.replace(/^tab-/, "");
      sec.classList.toggle("hidden", id !== name);
    });
    localStorage.setItem("chokepoint_tab", name);
    if (name === "desk") loadDesk();
    if (name === "watch") loadWatch();
    if (name === "thesis") loadTheses();
    if (name === "reports") loadReports();
    if (name === "templates") loadTemplates();
    if (name === "jobs") loadJobs();
  }

  function initTabs() {
    $$(".nav-btn").forEach((btn) => {
      btn.addEventListener("click", () => switchTab(btn.dataset.tab));
    });
    const initial = localStorage.getItem("chokepoint_tab") || "desk";
    switchTab(initial);
  }

  /* ── Health pill ──────────────────────────────────────────── */
  async function pingHealth() {
    const pill = $("#health-pill");
    try {
      const h = await api("/health");
      if (pill) {
        pill.textContent = h.status === "ok" ? `OK · v${h.version || "?"}` : "DEGRADED";
        pill.classList.toggle("bad", h.status !== "ok");
        pill.classList.add("ok");
      }
    } catch (e) {
      if (pill) {
        pill.textContent = "OFFLINE";
        pill.classList.add("bad");
      }
    }
  }

  /* ── Desk ─────────────────────────────────────────────────── */
  function renderKpis(desk) {
    const grid = $("#desk-kpis");
    if (!grid) return;
    const wh = desk.workspace_health || {};
    const pro = desk.pro_ops || {};
    const q = desk.quality || {};
    const queue = desk.queue || {};
    const items = [
      { label: "Health", value: `${wh.score ?? "—"} ${wh.grade ? "(" + wh.grade + ")" : ""}` },
      { label: "Pro modules", value: `${pro.active_modules ?? 0} / ${pro.modules ?? "—"}` },
      { label: "Quality avg", value: q.avg_score != null ? Number(q.avg_score).toFixed(1) : "—" },
      { label: "Queue", value: pretty(queue).slice(0, 40) },
      { label: "Kill risk", value: desk.kill_monitor_high_risk ?? 0 },
      { label: "Version", value: desk.version || "—" },
    ];
    grid.innerHTML = items
      .map(
        (it) =>
          `<div class="kpi"><div class="label">${escapeHtml(it.label)}</div><div class="value">${escapeHtml(String(it.value))}</div></div>`
      )
      .join("");
  }

  function renderActions(actions) {
    const ul = $("#desk-actions");
    if (!ul) return;
    const list = actions || [];
    if (!list.length) {
      ul.innerHTML = `<li class="muted">No actions — workspace looks healthy.</li>`;
      return;
    }
    ul.innerHTML = list.map((a) => `<li>${escapeHtml(String(a))}</li>`).join("");
  }

  async function loadDesk() {
    try {
      const desk = await api("/desk");
      renderKpis(desk);
      renderActions(desk.next_actions);
      setOut($("#desk-out"), desk);
    } catch (e) {
      setOut($("#desk-out"), { error: e.message });
      toast("Desk: " + e.message);
    }
  }

  function initDesk() {
    $("#desk-refresh")?.addEventListener("click", loadDesk);
    $("#desk-weekly")?.addEventListener("click", async () => {
      try {
        const r = await api("/weekly-ops", { method: "POST", body: "{}" });
        setOut($("#desk-out"), r);
        toast("Weekly ops generated");
      } catch (e) {
        toast(e.message);
      }
    });
    $("#desk-about")?.addEventListener("click", async () => {
      try {
        setOut($("#desk-out"), await api("/about"));
      } catch (e) {
        toast(e.message);
      }
    });
  }

  /* ── Research ─────────────────────────────────────────────── */
  function initResearch() {
    $("#newSession")?.addEventListener("click", async () => {
      try {
        const s = await api("/sessions", { method: "POST", body: "{}" });
        if ($("#session")) $("#session").value = s.session_id || s.id || "";
        toast("Session created");
      } catch (e) {
        // fallback local id
        const id = "sess_" + Math.random().toString(36).slice(2, 10);
        if ($("#session")) $("#session").value = id;
        toast("Local session id");
      }
    });

    $("#run")?.addEventListener("click", runResearch);
  }

  async function runResearch() {
    const question = ($("#q")?.value || "").trim();
    if (!question) {
      toast("Enter a research question");
      return;
    }
    const mode = $("#mode")?.value || "full";
    const skill = ($("#skill")?.value || "").trim();
    const session_id = ($("#session")?.value || "").trim() || null;
    const bilingual = !!$("#bilingual")?.checked;
    const useStream = !!$("#stream")?.checked;
    const status = $("#status");
    const live = $("#live");
    const out = $("#out");
    const meta = $("#meta");
    if (status) status.textContent = "Running…";
    if (live) live.textContent = "";
    if (out) out.textContent = "";
    if (meta) meta.innerHTML = "";

    const body = {
      question,
      mode,
      save_report: true,
      bilingual,
      export: true,
      session_id,
    };
    if (skill) body.skill = skill;

    try {
      if (useStream) {
        await streamResearch(body, { status, live, out, meta });
      } else {
        const res = await api("/research", { method: "POST", body: JSON.stringify(body) });
        if (out) out.textContent = res.report || pretty(res);
        if (meta) {
          meta.innerHTML = buildMetaBadges(res);
        }
        if (status) status.textContent = "Done";
        if (res.saved_path) toast("Saved: " + res.saved_path);
      }
    } catch (e) {
      if (status) status.textContent = "Error";
      if (out) out.textContent = e.message;
      toast(e.message);
    }
  }

  function buildMetaBadges(res) {
    const q = res.quality || {};
    const score = q.score != null ? q.score : q.quality_score;
    const parts = [
      badge("mode", res.mode),
      badge("quality", score != null ? score : "—"),
      badge("nodes", res.scorecard_nodes),
      res.saved_path ? badge("saved", shortPath(res.saved_path)) : "",
    ];
    return parts.filter(Boolean).join(" ");
  }

  function badge(k, v) {
    if (v == null || v === "") return "";
    return `<span class="badge"><b>${escapeHtml(k)}</b> ${escapeHtml(String(v))}</span>`;
  }

  function shortPath(p) {
    if (!p) return "";
    const parts = String(p).split(/[/\\]/);
    return parts.slice(-2).join("/");
  }

  async function streamResearch(body, els) {
    const res = await fetch("/research/stream", {
      method: "POST",
      headers: headers(true),
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const t = await res.text();
      throw new Error(t || res.statusText);
    }
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buf = "";
    let eventName = "message";
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });
      const chunks = buf.split("\n");
      buf = chunks.pop() || "";
      for (const line of chunks) {
        if (line.startsWith("event:")) {
          eventName = line.slice(6).trim();
        } else if (line.startsWith("data:")) {
          const data = line.slice(5).trim();
          handleSse(eventName, data, els);
          eventName = "message";
        }
      }
    }
    if (els.status) els.status.textContent = "Done";
  }

  function handleSse(event, data, els) {
    if (data === "[DONE]") return;
    let parsed;
    try {
      parsed = JSON.parse(data);
    } catch {
      parsed = data;
    }
    if (event === "start") {
      if (els.live) els.live.textContent += `[start] ${pretty(parsed)}\n`;
    } else if (event === "update") {
      const node = parsed.node || "?";
      const preview = (parsed.preview || "").slice(0, 200).replace(/\s+/g, " ");
      if (els.live) els.live.textContent += `[${node}] ${preview}\n`;
      if (els.live) els.live.scrollTop = els.live.scrollHeight;
    } else if (event === "final") {
      if (els.out) els.out.textContent = parsed.report || pretty(parsed);
      if (els.meta) els.meta.innerHTML = buildMetaBadges(parsed);
      if (parsed.saved_path) toast("Saved: " + parsed.saved_path);
    } else if (event === "error") {
      const msg = parsed.error || pretty(parsed);
      if (els.out) els.out.textContent = msg;
      toast(msg);
    }
  }

  /* ── Watch ────────────────────────────────────────────────── */
  async function loadWatch() {
    try {
      const data = await api("/watchlist");
      const items = data.items || data || [];
      const body = $("#w-body");
      if (!body) return;
      body.innerHTML = (Array.isArray(items) ? items : [])
        .map(
          (it) => `<tr>
          <td class="mono">${escapeHtml(it.id || "")}</td>
          <td>${escapeHtml(it.symbol || "")}</td>
          <td>${escapeHtml(it.name || "")}</td>
          <td><span class="tag">${escapeHtml(it.priority || "")}</span></td>
          <td>${escapeHtml(it.thesis || "")}</td>
        </tr>`
        )
        .join("");
    } catch (e) {
      toast(e.message);
    }
  }

  function initWatch() {
    $("#w-refresh")?.addEventListener("click", loadWatch);
    $("#w-add")?.addEventListener("click", async () => {
      const symbol = ($("#w-sym")?.value || "").trim();
      if (!symbol) return toast("Symbol required");
      const tags = ($("#w-tags")?.value || "")
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
      try {
        await api("/watchlist", {
          method: "POST",
          body: JSON.stringify({
            symbol,
            name: $("#w-name")?.value || "",
            thesis: $("#w-thesis")?.value || "",
            priority: $("#w-pri")?.value || "medium",
            tags,
          }),
        });
        toast("Added " + symbol);
        $("#w-sym").value = "";
        loadWatch();
      } catch (e) {
        toast(e.message);
      }
    });
    $("#w-bulk")?.addEventListener("click", async () => {
      const raw = prompt("Comma-separated symbols (e.g. NVDA,AAPL,600519)");
      if (!raw) return;
      const symbols = raw
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
      try {
        const r = await api("/watchlist/bulk", {
          method: "POST",
          body: JSON.stringify({ symbols, priority: $("#w-pri")?.value || "medium" }),
        });
        toast("Bulk: " + pretty(r).slice(0, 80));
        loadWatch();
      } catch (e) {
        toast(e.message);
      }
    });
  }

  /* ── Thesis ───────────────────────────────────────────────── */
  async function loadTheses() {
    try {
      const data = await api("/theses");
      const items = data.items || data.theses || data || [];
      const box = $("#t-list");
      if (!box) return;
      if (!Array.isArray(items) || !items.length) {
        box.innerHTML = `<p class="muted">No theses yet.</p>`;
        return;
      }
      box.innerHTML = items
        .map((t) => {
          const kills = (t.kill_criteria || []).join("; ");
          return `<div class="list-card">
            <div class="list-card-head">
              <strong>${escapeHtml(t.title || t.id || "")}</strong>
              <span class="tag">${escapeHtml(t.status || "active")}</span>
            </div>
            <div class="tiny mono">${escapeHtml(t.id || "")}</div>
            <p>${escapeHtml(t.statement || "")}</p>
            <div class="tiny">System: ${escapeHtml(t.system || "—")}</div>
            <div class="tiny">Kills: ${escapeHtml(kills || "—")}</div>
          </div>`;
        })
        .join("");
    } catch (e) {
      toast(e.message);
    }
  }

  function initThesis() {
    $("#t-refresh")?.addEventListener("click", loadTheses);
    $("#t-add")?.addEventListener("click", async () => {
      const title = ($("#t-title")?.value || "").trim();
      const statement = ($("#t-statement")?.value || "").trim();
      if (!title || !statement) return toast("Title + statement required");
      const kills = ($("#t-kills")?.value || "")
        .split(";")
        .map((s) => s.trim())
        .filter(Boolean);
      try {
        await api("/theses", {
          method: "POST",
          body: JSON.stringify({
            title,
            statement,
            system: $("#t-system")?.value || "",
            kill_criteria: kills,
          }),
        });
        toast("Thesis added");
        $("#t-title").value = "";
        $("#t-statement").value = "";
        loadTheses();
      } catch (e) {
        toast(e.message);
      }
    });
    $("#t-health")?.addEventListener("click", async () => {
      try {
        const h = await api("/thesis-health");
        const box = $("#t-list");
        if (box) box.innerHTML = `<pre class="panel-out">${escapeHtml(pretty(h))}</pre>`;
      } catch (e) {
        toast(e.message);
      }
    });
  }

  /* ── Reports ──────────────────────────────────────────────── */
  async function loadReports() {
    try {
      const q = ($("#r-q")?.value || "").trim();
      const path = q ? `/reports?q=${encodeURIComponent(q)}` : "/reports";
      const data = await api(path);
      const items = data.reports || data.items || data || [];
      const body = $("#r-body");
      if (!body) return;
      body.innerHTML = (Array.isArray(items) ? items : [])
        .map((r) => {
          const name = r.name || r.filename || r.path || "";
          const mode = r.mode || "";
          const qscore = r.quality_score != null ? r.quality_score : r.quality?.score ?? "—";
          const mod = r.modified || r.mtime || r.updated_at || "";
          return `<tr>
            <td class="mono">${escapeHtml(shortPath(name))}</td>
            <td>${escapeHtml(mode)}</td>
            <td>${escapeHtml(String(qscore))}</td>
            <td class="tiny">${escapeHtml(String(mod).slice(0, 19))}</td>
            <td class="row-actions">
              <button class="btn sm ghost" data-act="view" data-name="${escapeAttr(name)}">View</button>
              <button class="btn sm ghost" data-act="check" data-name="${escapeAttr(name)}">Check</button>
              <button class="btn sm ghost" data-act="grade" data-name="${escapeAttr(name)}">Grade</button>
              <button class="btn sm sec" data-act="pack" data-name="${escapeAttr(name)}">Pack</button>
            </td>
          </tr>`;
        })
        .join("");
      body.querySelectorAll("button[data-act]").forEach((btn) => {
        btn.addEventListener("click", () => reportAction(btn.dataset.act, btn.dataset.name));
      });
    } catch (e) {
      setOut($("#r-out"), { error: e.message });
    }
  }

  async function reportAction(act, name) {
    if (!name) return;
    const base = name.split(/[/\\]/).pop();
    try {
      if (act === "view") {
        const r = await api("/reports/" + encodeURIComponent(base));
        setOut($("#r-out"), r.content || r.body || r.markdown || r);
      } else if (act === "check") {
        setOut($("#r-out"), await api("/checklist/" + encodeURIComponent(base)));
      } else if (act === "grade") {
        setOut($("#r-out"), await api("/grade/" + encodeURIComponent(base)));
      } else if (act === "pack") {
        setOut(
          $("#r-out"),
          await api("/export-pack", {
            method: "POST",
            body: JSON.stringify({ report: base }),
          })
        );
        toast("Export pack ready");
      }
    } catch (e) {
      setOut($("#r-out"), { error: e.message });
      toast(e.message);
    }
  }

  function initReports() {
    $("#r-refresh")?.addEventListener("click", loadReports);
    $("#r-q")?.addEventListener("keydown", (e) => {
      if (e.key === "Enter") loadReports();
    });
  }

  /* ── Templates ────────────────────────────────────────────── */
  async function loadTemplates() {
    try {
      const data = await api("/templates");
      const items = data.templates || data.items || data || [];
      const box = $("#tpl-list");
      if (!box) return;
      if (Array.isArray(items)) {
        box.innerHTML =
          "<ul>" +
          items
            .map((t) => {
              const id = t.id || t.name || t;
              return `<li><button type="button" class="linkish" data-tpl="${escapeAttr(id)}">${escapeHtml(id)}</button> ${escapeHtml(t.title || t.description || "")}</li>`;
            })
            .join("") +
          "</ul>";
        box.querySelectorAll("[data-tpl]").forEach((b) => {
          b.addEventListener("click", () => {
            if ($("#tpl-id")) $("#tpl-id").value = b.dataset.tpl;
          });
        });
      } else {
        setOut(box, items);
      }
    } catch (e) {
      setOut($("#tpl-list"), e.message);
    }
  }

  function initTemplates() {
    $("#tpl-run")?.addEventListener("click", async () => {
      const id = ($("#tpl-id")?.value || "").trim();
      if (!id) return toast("Template id required");
      let vars = {};
      try {
        const raw = ($("#tpl-vars")?.value || "").trim();
        if (raw) vars = JSON.parse(raw);
      } catch {
        return toast("Invalid JSON vars");
      }
      try {
        const r = await api("/templates/" + encodeURIComponent(id) + "/render", {
          method: "POST",
          body: JSON.stringify({ vars }),
        });
        const text = r.question || r.rendered || r.text || pretty(r);
        if ($("#q")) $("#q").value = text;
        switchTab("research");
        toast("Filled Research tab");
      } catch (e) {
        toast(e.message);
      }
    });
  }

  /* ── Search ───────────────────────────────────────────────── */
  function initSearch() {
    $("#s-run")?.addEventListener("click", doSearch);
    $("#s-q")?.addEventListener("keydown", (e) => {
      if (e.key === "Enter") doSearch();
    });
  }

  async function doSearch() {
    const q = ($("#s-q")?.value || "").trim();
    if (!q) return toast("Query required");
    try {
      let data;
      try {
        data = await api("/search/memos?q=" + encodeURIComponent(q));
      } catch {
        data = await api("/index/search?q=" + encodeURIComponent(q));
      }
      setOut($("#s-out"), data);
    } catch (e) {
      setOut($("#s-out"), { error: e.message });
    }
  }

  /* ── Knowledge ────────────────────────────────────────────── */
  function initKnowledge() {
    $("#k-maps")?.addEventListener("click", async () => {
      try {
        setOut($("#k-out"), await api("/maps"));
      } catch (e) {
        toast(e.message);
      }
    });
    $("#k-mkt")?.addEventListener("click", async () => {
      try {
        setOut($("#k-out"), await api("/marketplace"));
      } catch (e) {
        toast(e.message);
      }
    });
    $("#k-vert")?.addEventListener("click", async () => {
      try {
        setOut($("#k-out"), await api("/pro/verticals"));
      } catch (e) {
        toast(e.message);
      }
    });
    $("#k-gloss-go")?.addEventListener("click", async () => {
      const q = ($("#k-gloss")?.value || "").trim();
      try {
        const path = q ? "/glossary?q=" + encodeURIComponent(q) : "/glossary";
        setOut($("#k-out"), await api(path));
      } catch (e) {
        toast(e.message);
      }
    });
  }

  /* ── Analytics ────────────────────────────────────────────── */
  function initAnalytics() {
    const bind = (id, path, method = "GET") => {
      $(id)?.addEventListener("click", async () => {
        try {
          const opts = method === "POST" ? { method: "POST", body: "{}" } : {};
          setOut($("#a-out"), await api(path, opts));
        } catch (e) {
          setOut($("#a-out"), { error: e.message });
        }
      });
    };
    bind("#a-run", "/analytics");
    bind("#a-health", "/workspace-health");
    bind("#a-qboard", "/quality-board");
    bind("#a-brev", "/batch-review");
    bind("#a-weekly", "/weekly-ops", "POST");
  }

  /* ── Ops ──────────────────────────────────────────────────── */
  function initOps() {
    const out = () => $("#o-out");
    $("#o-graph")?.addEventListener("click", async () => {
      try {
        setOut(out(), await api("/graph"));
      } catch (e) {
        toast(e.message);
      }
    });
    $("#o-cov")?.addEventListener("click", async () => {
      try {
        setOut(out(), await api("/coverage"));
        const img = $("#o-covimg");
        if (img) {
          img.style.display = "block";
          img.src = "/charts/coverage?" + Date.now();
        }
      } catch (e) {
        toast(e.message);
      }
    });
    $("#o-kill")?.addEventListener("click", async () => {
      try {
        setOut(out(), await api("/kill-monitor"));
      } catch (e) {
        toast(e.message);
      }
    });
    $("#o-ev")?.addEventListener("click", async () => {
      try {
        setOut(out(), await api("/evidence"));
      } catch (e) {
        toast(e.message);
      }
    });
    $("#o-queue")?.addEventListener("click", async () => {
      try {
        setOut(out(), await api("/queue"));
      } catch (e) {
        toast(e.message);
      }
    });
    $("#o-qrun")?.addEventListener("click", async () => {
      try {
        setOut(
          out(),
          await api("/queue/run", {
            method: "POST",
            body: JSON.stringify({ max_items: 1, mock: true }),
          })
        );
        toast("Queue mock ×1");
      } catch (e) {
        toast(e.message);
      }
    });
    $("#o-pdash")?.addEventListener("click", async () => {
      try {
        setOut(out(), await api("/pro/dashboard"));
      } catch (e) {
        toast(e.message);
      }
    });
    $("#o-runbook")?.addEventListener("click", async () => {
      try {
        setOut(out(), await api("/runbook"));
      } catch (e) {
        toast(e.message);
      }
    });
    $("#o-snap")?.addEventListener("click", async () => {
      try {
        setOut(out(), await api("/snapshot", { method: "POST", body: "{}" }));
        toast("Snapshot taken");
      } catch (e) {
        toast(e.message);
      }
    });
    $("#o-plan")?.addEventListener("click", async () => {
      const topic = ($("#o-topic")?.value || "").trim() || "chokepoint coverage";
      try {
        setOut(
          out(),
          await api("/plan", {
            method: "POST",
            body: JSON.stringify({ topic }),
          })
        );
      } catch (e) {
        toast(e.message);
      }
    });
  }

  /* ── Jobs ─────────────────────────────────────────────────── */
  async function loadJobs() {
    try {
      setOut($("#j-out"), await api("/jobs"));
    } catch (e) {
      setOut($("#j-out"), { error: e.message });
    }
  }

  function initJobs() {
    $("#j-refresh")?.addEventListener("click", loadJobs);
    $("#j-submit")?.addEventListener("click", async () => {
      const question = ($("#j-q")?.value || "").trim();
      if (!question) return toast("Question required");
      try {
        const r = await api("/jobs", {
          method: "POST",
          body: JSON.stringify({
            question,
            mode: $("#j-mode")?.value || "chokepoint_fast",
          }),
        });
        setOut($("#j-out"), r);
        toast("Job submitted");
        loadJobs();
      } catch (e) {
        toast(e.message);
      }
    });
  }

  /* ── Doctor ───────────────────────────────────────────────── */
  function initDoctor() {
    $("#d-run")?.addEventListener("click", async () => {
      try {
        setOut($("#d-out"), await api("/doctor"));
      } catch (e) {
        setOut($("#d-out"), { error: e.message });
      }
    });
    $("#d-about")?.addEventListener("click", async () => {
      try {
        setOut($("#d-out"), await api("/about"));
      } catch (e) {
        setOut($("#d-out"), { error: e.message });
      }
    });
  }

  /* ── Utils ────────────────────────────────────────────────── */
  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function escapeAttr(s) {
    return escapeHtml(s).replace(/'/g, "&#39;");
  }

  /* ── Persist API key ──────────────────────────────────────── */
  function initKey() {
    const el = $("#key");
    if (!el) return;
    el.value = localStorage.getItem("chokepoint_api_key") || "";
    el.addEventListener("change", () => {
      localStorage.setItem("chokepoint_api_key", el.value.trim());
    });
  }

  /* ── Boot ─────────────────────────────────────────────────── */
  function boot() {
    initLang();
    initKey();
    initTabs();
    initDesk();
    initResearch();
    initWatch();
    initThesis();
    initReports();
    initTemplates();
    initSearch();
    initKnowledge();
    initAnalytics();
    initOps();
    initJobs();
    initDoctor();
    pingHealth();
    setInterval(pingHealth, 60000);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
