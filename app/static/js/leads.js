(function () {
    "use strict";

    const page = document.body.dataset.page;
    const apiBase = "/api/leads";

    const $ = (id) => document.getElementById(id);
    const show = (element) => { if (element) element.hidden = false; };
    const hide = (element) => { if (element) element.hidden = true; };

    function escapeHtml(value) {
        return String(value ?? "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function displayValue(value, fallback = "Not provided") {
        return value === null || value === undefined || value === "" ? fallback : value;
    }

    function formatDate(value) {
        if (!value) return "Not recorded";
        const date = new Date(value);
        return Number.isNaN(date.getTime()) ? value : date.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
    }

    function errorText(payload, fallback) {
        if (!payload) return fallback;
        if (typeof payload.detail === "string") return payload.detail;
        if (Array.isArray(payload.detail)) return payload.detail.map((item) => item.msg || "Invalid value").join(" ");
        return payload.message || fallback;
    }

    async function apiRequest(url, options = {}) {
        let response;
        try {
            response = await fetch(url, { credentials: "same-origin", headers: { "Content-Type": "application/json", ...(options.headers || {}) }, ...options });
        } catch (error) {
            throw new Error("We could not reach the lead service. Check your connection and try again.");
        }

        let payload = null;
        try { payload = await response.json(); } catch (_) { /* empty response */ }
        if (response.status === 401) {
            window.location.href = "/login?next=" + encodeURIComponent(window.location.pathname);
            throw new Error("Your session has expired. Please sign in again.");
        }
        if (!response.ok) throw new Error(errorText(payload, "The lead service returned an unexpected error."));
        return payload;
    }

    function setError(element, message) {
        if (!element) return;
        element.textContent = message;
        show(element);
    }

    function badgeClass(value, kind) {
        const normalized = String(value || "").toLowerCase();
        if (kind === "priority") {
            if (normalized === "urgent") return "border-rose-400/30 bg-rose-400/10 text-rose-300";
            if (normalized === "high") return "border-amber-400/30 bg-amber-400/10 text-amber-300";
            if (normalized === "low") return "border-slate-600 bg-slate-800 text-slate-400";
            return "border-cyan-400/30 bg-cyan-400/10 text-cyan-300";
        }
        if (normalized.includes("won")) return "border-emerald-400/30 bg-emerald-400/10 text-emerald-300";
        if (normalized.includes("lost")) return "border-rose-400/30 bg-rose-400/10 text-rose-300";
        if (normalized === "qualified") return "border-violet-400/30 bg-violet-400/10 text-violet-300";
        return "border-cyan-400/30 bg-cyan-400/10 text-cyan-300";
    }

    function badge(value, kind) {
        const safeValue = escapeHtml(displayValue(value, kind === "priority" ? "Medium" : "New"));
        return `<span class="inline-flex rounded-full border px-2.5 py-1 text-xs font-medium ${badgeClass(value, kind)}">${safeValue}</span>`;
    }

    function initList() {
        const state = { page: 1, pageSize: 10, sortBy: "created_at", sortOrder: "desc", search: "", status: "", priority: "", specialty: "" };
        let debounce;

        function queryString() {
            const params = new URLSearchParams({ page: state.page, page_size: state.pageSize, sort_by: state.sortBy, sort_order: state.sortOrder });
            ["search", "status", "priority", "specialty"].forEach((key) => { if (state[key]) params.set(key, state[key]); });
            return params.toString();
        }

        function renderRows(leads) {
            $("lead-table-body").innerHTML = leads.map((lead) => `
                <tr class="transition hover:bg-slate-800/40">
                    <td class="px-5 py-4"><a href="/leads/${lead.id}" class="font-medium text-white hover:text-cyan-300">${escapeHtml(displayValue(lead.practice_name, "Untitled practice"))}</a><p class="mt-1 text-xs text-slate-500">${escapeHtml(displayValue(lead.practice_type, "Practice"))}</p></td>
                    <td class="px-4 py-4"><p class="text-sm text-slate-200">${escapeHtml(displayValue(lead.contact_person || lead.doctor_name))}</p><p class="mt-1 text-xs text-slate-500">${escapeHtml(displayValue(lead.email, "No email"))}</p></td>
                    <td class="px-4 py-4 text-sm text-slate-300">${escapeHtml(displayValue(lead.specialty))}</td>
                    <td class="px-4 py-4 text-sm text-slate-300">${escapeHtml([lead.city, lead.state].filter(Boolean).join(", ") || "Not provided")}</td>
                    <td class="px-4 py-4">${badge(lead.priority, "priority")}</td>
                    <td class="px-4 py-4">${badge(lead.status, "status")}</td>
                    <td class="px-4 py-4"><span class="text-sm font-semibold text-slate-200">${escapeHtml(displayValue(lead.lead_score, "0"))}</span><span class="text-xs text-slate-600"> / 100</span></td>
                    <td class="px-5 py-4 text-right"><div class="inline-flex items-center gap-3 text-xs"><a href="/leads/${lead.id}" class="font-medium text-slate-300 hover:text-cyan-300">View</a><a href="/leads/${lead.id}/edit" class="font-medium text-cyan-400 hover:text-cyan-300">Edit</a><button type="button" data-delete-lead="${lead.id}" data-lead-name="${escapeHtml(lead.practice_name || "this lead")}" class="font-medium text-rose-300 hover:text-rose-200">Delete</button></div></td>
                </tr>`).join("");
        }

        function render(data) {
            hide($("lead-loading"));
            $("lead-result-count").textContent = `${data.total} ${data.total === 1 ? "lead" : "leads"} in view`;
            if (!data.items.length) {
                hide($("lead-table-wrap"));
                hide($("lead-pagination"));
                $("lead-empty-title").textContent = state.search || state.status || state.priority || state.specialty ? "No matching leads" : "No leads yet";
                $("lead-empty-copy").textContent = state.search || state.status || state.priority || state.specialty ? "Try adjusting your search or filters to find a better match." : "Add your first healthcare practice to start building the pipeline.";
                show($("lead-empty"));
                return;
            }
            hide($("lead-empty"));
            renderRows(data.items);
            show($("lead-table-wrap"));
            show($("lead-pagination"));
            $("lead-page-label").textContent = `Page ${data.page} of ${Math.max(data.pages, 1)}`;
            $("lead-prev").disabled = data.page <= 1;
            $("lead-next").disabled = data.page >= data.pages;
        }

        async function load() {
            hide($("lead-list-error"));
            show($("lead-loading"));
            hide($("lead-table-wrap"));
            hide($("lead-empty"));
            try { render(await apiRequest(`${apiBase}?${queryString()}`)); }
            catch (error) { hide($("lead-loading")); setError($("lead-list-error"), error.message); }
        }

        function resetPageAndLoad() { state.page = 1; load(); }
        $("lead-search").addEventListener("input", (event) => { state.search = event.target.value.trim(); clearTimeout(debounce); debounce = setTimeout(resetPageAndLoad, 250); });
        $("lead-status-filter").addEventListener("change", (event) => { state.status = event.target.value; resetPageAndLoad(); });
        $("lead-priority-filter").addEventListener("change", (event) => { state.priority = event.target.value; resetPageAndLoad(); });
        $("lead-specialty-filter").addEventListener("input", (event) => { state.specialty = event.target.value.trim(); clearTimeout(debounce); debounce = setTimeout(resetPageAndLoad, 250); });
        $("clear-lead-filters").addEventListener("click", () => { ["lead-search", "lead-specialty-filter"].forEach((id) => { $(id).value = ""; }); $("lead-status-filter").value = ""; $("lead-priority-filter").value = ""; state.search = state.specialty = state.status = state.priority = ""; resetPageAndLoad(); });
        $("lead-sort").addEventListener("change", (event) => { state.sortBy = event.target.value; resetPageAndLoad(); });
        $("lead-sort-direction").addEventListener("click", () => { state.sortOrder = state.sortOrder === "desc" ? "asc" : "desc"; $("lead-sort-direction").textContent = state.sortOrder === "desc" ? "Newest" : "Oldest"; load(); });
        $("lead-prev").addEventListener("click", () => { if (state.page > 1) { state.page -= 1; load(); } });
        $("lead-next").addEventListener("click", () => { state.page += 1; load(); });
        $("lead-table-body").addEventListener("click", async (event) => {
            const button = event.target.closest("[data-delete-lead]");
            if (!button || !window.confirm(`Delete ${button.dataset.leadName}? This cannot be undone.`)) return;
            try { await apiRequest(`${apiBase}/${button.dataset.deleteLead}`, { method: "DELETE" }); load(); }
            catch (error) { setError($("lead-list-error"), error.message); }
        });
        load();
    }

    function formFields() {
        return ["practice_name", "doctor_name", "contact_person", "designation", "specialty", "city", "state", "country", "website", "email", "phone", "linkedin_url", "npi", "practice_type", "insurance_status", "lead_source", "lead_score", "priority", "status", "notes", "tags", "independent_practice"];
    }

    function fillForm(lead) {
        formFields().forEach((name) => { const field = document.querySelector(`[name="${name}"]`); if (!field) return; field.type === "checkbox" ? field.checked = Boolean(lead[name]) : field.value = lead[name] ?? (name === "lead_score" ? 0 : ""); });
    }

    function initForm() {
        const leadId = document.body.dataset.leadId;
        const isEdit = Boolean(leadId);
        const form = $("lead-form");
        const submit = $("lead-form-submit");

        async function loadLead() {
            if (!isEdit) return;
            show($("lead-form-loading"));
            try { fillForm(await apiRequest(`${apiBase}/${leadId}`)); show($("form-detail-link")); }
            catch (error) { setError($("lead-form-error"), error.message); form.querySelectorAll("input,select,textarea,button[type=submit]").forEach((field) => { field.disabled = true; }); }
            finally { hide($("lead-form-loading")); }
        }

        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            hide($("lead-form-error"));
            const payload = {};
            formFields().forEach((name) => { const field = form.elements[name]; if (field.type === "checkbox") payload[name] = field.checked; else if (name === "lead_score") payload[name] = field.value === "" ? 0 : Number(field.value); else payload[name] = field.value.trim() || null; });
            submit.disabled = true;
            $("lead-form-submit-label").textContent = isEdit ? "Saving…" : "Creating…";
            try { const lead = await apiRequest(isEdit ? `${apiBase}/${leadId}` : apiBase, { method: isEdit ? "PUT" : "POST", body: JSON.stringify(payload) }); window.location.href = `/leads/${lead.id}`; }
            catch (error) { setError($("lead-form-error"), error.message); submit.disabled = false; $("lead-form-submit-label").textContent = isEdit ? "Save changes" : "Create lead"; }
        });
        loadLead();
    }

    function initDetail() {
        const leadId = document.body.dataset.leadId;
        const detailMap = ["contact_person", "designation", "practice_type", "email", "phone", "website", "linkedin_url", "npi", "insurance_status", "country", "state", "city", "tags", "notes"];
        function setDetail(id, value) { const element = $(`detail-${id}`); if (element) element.textContent = displayValue(value); }
        async function load() {
            try {
                const lead = await apiRequest(`${apiBase}/${leadId}`);
                $("detail-title").textContent = displayValue(lead.practice_name, "Untitled practice");
                $("detail-subtitle").textContent = [lead.specialty, lead.city, lead.state].filter(Boolean).join(" · ") || "Healthcare practice";
                $("detail-practice").textContent = displayValue(lead.practice_name, "Untitled practice");
                $("detail-doctor").textContent = lead.doctor_name ? `Attn: ${lead.doctor_name}` : "Primary doctor not provided";
                $("detail-status").textContent = displayValue(lead.status, "New");
                $("detail-priority").textContent = `${displayValue(lead.priority, "Medium")} priority`;
                $("detail-status").className = `status-badge ${badgeClass(lead.status, "status")}`;
                $("detail-priority").className = `priority-badge ${badgeClass(lead.priority, "priority")}`;
                $("detail-specialty").textContent = displayValue(lead.specialty);
                $("detail-location").textContent = [lead.city, lead.state, lead.country].filter(Boolean).join(", ") || "Not provided";
                $("detail-score").textContent = `${displayValue(lead.lead_score, "0")} / 100`;
                $("detail-source").textContent = displayValue(lead.lead_source);
                detailMap.forEach((id) => setDetail(id, lead[id]));
                $("detail-independent_practice").textContent = lead.independent_practice ? "Yes" : "No";
                $("detail-created").textContent = formatDate(lead.created_at);
                $("detail-updated").textContent = `Last updated ${formatDate(lead.updated_at)}`;
                hide($("detail-loading")); show($("detail-content"));
                $("detail-delete").addEventListener("click", async () => { if (!window.confirm(`Delete ${lead.practice_name || "this lead"}? This cannot be undone.`)) return; try { await apiRequest(`${apiBase}/${leadId}`, { method: "DELETE" }); window.location.href = "/leads"; } catch (error) { setError($("detail-error"), error.message); } });
            } catch (error) { hide($("detail-loading")); setError($("detail-error"), error.message); }
        }
        load();
    }

    if (page === "lead-list") initList();
    if (page === "lead-form") initForm();
    if (page === "lead-detail") initDetail();
}());
