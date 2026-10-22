const API_BASE = "http://127.0.0.1:8000";

/* ---------- auth guard ---------- */
function requireRole(role) {
    const token = localStorage.getItem("sc_token");
    const savedRole = localStorage.getItem("sc_role");
    if (!token || savedRole !== role) {
        window.location.href = "index.html";
        return false;
    }
    return true;
}

function currentUser() {
    return {
        id: Number(localStorage.getItem("sc_id")),
        email: localStorage.getItem("sc_email") || "",
        role: localStorage.getItem("sc_role")
    };
}

function logout() {
    ["sc_token", "sc_role", "sc_id", "sc_email"].forEach(k => localStorage.removeItem(k));
    window.location.href = "index.html";
}

/* ---------- api ---------- */
async function api(path, method = "GET", body = null) {
    const headers = { "Content-Type": "application/json" };
    const token = localStorage.getItem("sc_token");
    if (token) headers["Authorization"] = `Bearer ${token}`;

    let res;
    try {
        res = await fetch(API_BASE + path, { method, headers, body: body ? JSON.stringify(body) : null });
    } catch (e) {
        throw new Error("Can't reach the backend. Check that uvicorn is running.");
    }

    const data = await res.json().catch(() => null);
    if (!res.ok) {
        let msg = "Something went wrong.";
        if (data && typeof data.detail === "string") msg = data.detail;
        else if (data && Array.isArray(data.detail)) msg = "Some fields are missing or invalid.";
        throw new Error(msg);
    }
    return data;
}

/* ---------- safe text ---------- */
function esc(value) {
    const d = document.createElement("div");
    d.textContent = value == null ? "" : String(value);
    return d.innerHTML;
}

/* ---------- icons ---------- */
const ICONS = {
    ask:     '<circle cx="12" cy="12" r="9"/><path d="M12 8v8M8 12h8"/>',
    list:    '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
    inbox:   '<path d="M22 12h-6l-2 3h-4l-2-3H2"/><path d="M5.5 5h13l3.5 7v6a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-6z"/>',
    users:   '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/>',
    chart:   '<path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 5-6"/>',
    trophy:  '<path d="M8 21h8M12 17v4M7 4h10v5a5 5 0 0 1-10 0z"/><path d="M17 5h3v2a3 3 0 0 1-3 3M7 5H4v2a3 3 0 0 0 3 3"/>',
    logout:  '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="M16 17l5-5-5-5M21 12H9"/>',
    chevron: '<path d="M9 18l6-6-6-6"/>',
    check:   '<circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/>',
    clock:   '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    message: '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    alert:   '<path d="M12 9v4M12 17h.01"/><path d="M10.3 3.9L1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/>',
    refresh: '<path d="M21 12a9 9 0 1 1-3-6.7L21 8"/><path d="M21 3v5h-5"/>',
    send:    '<path d="M22 2L11 13"/><path d="M22 2l-7 20-4-9-9-4z"/>'
};
function icon(name) {
    return `<svg class="ic" viewBox="0 0 24 24" aria-hidden="true">${ICONS[name] || ""}</svg>`;
}

/* ---------- status helpers ---------- */
function statusLabel(s) {
    return { pending: "Pending", resolved: "Resolved", escalated: "Escalated", auto_resolved: "Auto-resolved" }[s] || s;
}
function badge(status) {
    return `<span class="badge ${esc(status)}">${esc(statusLabel(status))}</span>`;
}

/* ---------- toast ---------- */
function toast(text, type = "ok") {
    let host = document.getElementById("toasts");
    if (!host) {
        host = document.createElement("div");
        host.id = "toasts";
        host.className = "toast-host";
        host.setAttribute("aria-live", "polite");
        document.body.appendChild(host);
    }
    const t = document.createElement("div");
    t.className = "toast " + (type === "error" ? "error" : "");
    t.textContent = text;
    host.appendChild(t);
    setTimeout(() => t.remove(), 3500);
}

/* ---------- sidebar shell ---------- */
function buildShell(portalLabel, navItems) {
    const u = currentUser();
    const initial = (u.email || "?").charAt(0).toUpperCase();
    document.getElementById("sidebar").innerHTML = `
        <div class="logo">
            <span class="mark"><svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/><path d="M8.5 10l2.5 2.5L15.5 8"/></svg></span>
            SmartClarify
        </div>
        <div class="portal-tag">${esc(portalLabel)}</div>
        <nav class="nav">
            ${navItems.map((n, i) => `<a class="nav-link ${i === 0 ? "active" : ""}" href="${n.href}">${icon(n.icon)}${esc(n.label)}</a>`).join("")}
        </nav>
        <div class="user">
            <div class="avatar">${esc(initial)}</div>
            <div class="u-meta">
                <div class="u-role">${esc(portalLabel)}</div>
                <div class="u-mail" title="${esc(u.email)}">${esc(u.email)}</div>
            </div>
            <button class="logout" id="logout-btn" type="button" aria-label="Log out" title="Log out">${icon("logout")}</button>
        </div>`;

    document.getElementById("logout-btn").addEventListener("click", logout);
    document.querySelectorAll(".nav-link").forEach(a => {
        a.addEventListener("click", () => {
            document.querySelectorAll(".nav-link").forEach(x => x.classList.remove("active"));
            a.classList.add("active");
        });
    });
}

function statCard(iconName, tone, num, name) {
    return `<div class="stat">
        <div class="s-ic ${tone}">${icon(iconName)}</div>
        <div><div class="s-num">${esc(num)}</div><div class="s-name">${esc(name)}</div></div>
    </div>`;
}

const FONT_LINK = "https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@600;700&family=Figtree:wght@400;500;600;700&display=swap";