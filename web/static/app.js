const money = (cents) =>
  new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(
    cents / 100
  );

const esc = (value) =>
  String(value).replace(/[&<>"']/g, (char) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char])
  );

const params = new URLSearchParams(location.search);
const banner = document.getElementById("banner");
if (params.get("checkout") === "success") {
  banner.hidden = false;
  banner.textContent = `Checkout complete for ${params.get("sku") || "kit"}. Pack against the QC list on the card.`;
}
if (params.get("checkout") === "cancel") {
  banner.hidden = false;
  banner.classList.add("bad");
  banner.textContent = "Checkout canceled. Catalog still stands.";
}

async function jget(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function bomLines(kit, selfSource) {
  const rows = selfSource ? kit.self_source_bom || [] : kit.bom || [];
  return rows
    .map(
      (line) =>
        `<li>${line.qty}× ${esc(line.pn)} ${esc(line.name)} (${esc(line.process)} · ${esc(line.source)}) ${money(line.ext_landed_cents)}</li>`
    )
    .join("");
}

function kitCard(kit, checkoutEnabled) {
  const el = document.createElement("article");
  el.className = "card";
  const canBuy = checkoutEnabled && kit.margin_ok && kit.costing_status === "quoted";
  const buyLabel = !checkoutEnabled
    ? "Checkout needs STRIPE_SECRET_KEY"
    : kit.costing_status !== "quoted"
      ? "Estimate — no live charge"
      : "Checkout";
  el.innerHTML = `
    <img src="${kit.photo}" alt="${kit.sku}" />
    <div class="sku">${esc(kit.sku)} · ${esc(kit.availability)} · ${esc(kit.costing_status)}</div>
    <h3>${esc(kit.name)}</h3>
    <p>${esc(kit.summary)}</p>
    <div class="price">${money(kit.price_cents)}</div>
    <div class="muted">kit landed ${money(kit.landed_cents)} · self-source ${money(kit.self_source_cents)} · floor ${money(kit.min_price_cents)}</div>
    <div class="margin ${kit.margin_ok ? "ok" : "fail"}">
      ${kit.margin_ok ? "margin OK" : "MARGIN FAIL"} · ${(kit.gross_margin * 100).toFixed(0)}%
    </div>
    <label class="check"><input type="checkbox" class="self-src" /> Self-source BOM</label>
    <details open>
      <summary>BOM</summary>
      <ul class="bom">${bomLines(kit, false)}</ul>
    </details>
    <details>
      <summary>Pack / QC</summary>
      <ul class="bom">${(kit.pack_list || []).map((step) => `<li>${esc(step)}</li>`).join("")}</ul>
    </details>
    <label>Qty <input class="qty" type="number" min="1" max="20" value="1" /></label>
    <button class="buy" ${canBuy ? "" : "disabled"} data-sku="${esc(kit.sku)}">${buyLabel}</button>
  `;
  const list = el.querySelector(".bom");
  el.querySelector(".self-src").addEventListener("change", (event) => {
    list.innerHTML = bomLines(kit, event.target.checked);
  });
  el.querySelector(".buy").addEventListener("click", () => {
    const qty = Number(el.querySelector(".qty").value || 1);
    buy(kit.sku, qty);
  });
  return el;
}

async function buy(sku, quantity) {
  const res = await fetch("/api/checkout", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sku, quantity }),
  });
  const data = await res.json();
  if (!res.ok) {
    banner.hidden = false;
    banner.classList.add("bad");
    banner.textContent = typeof data.detail === "string" ? data.detail : "Checkout failed";
    return;
  }
  location.href = data.url;
}

async function loadKits() {
  const data = await jget("/api/kits");
  document.getElementById("kit-notes").textContent =
    `${data.notes} Costing ${data.costing_status} as of ${data.costing_as_of}.`;
  const grid = document.getElementById("kit-grid");
  data.kits.forEach((kit) => grid.append(kitCard(kit, data.checkout_enabled)));
  const gearBox = document.getElementById("gear-box");
  data.kits.forEach((kit) => {
    const label = document.createElement("label");
    label.innerHTML = `<input type="checkbox" name="gear" value="${esc(kit.sku)}" /> ${esc(kit.sku)}`;
    gearBox.append(label);
  });
}

async function loadHub() {
  const data = await jget("/api/hub");
  const dual = await jget("/api/dual-host");
  const drafts = await jget("/api/drafts").catch(() => ({ drafts: [] }));
  document.getElementById("hub-status").textContent = JSON.stringify(
    { hub: data, dual_host: dual, drafts },
    null,
    2
  );
}

async function loadManual() {
  const data = await jget("/api/knowledge");
  const root = document.getElementById("manual-list");
  (data.modules || []).forEach((mod) => {
    const art = document.createElement("article");
    art.className = "panel manual-mod";
    art.innerHTML = `<h3>${esc(mod.title)}</h3><p class="sku">${esc(mod.id)} · ${esc((mod.problems || []).join(", "))}</p><pre>${esc(mod.body)}</pre>`;
    root.append(art);
  });
}

document.getElementById("situation-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.target;
  const problems = [...form.querySelectorAll("input[name=problems]:checked")].map(
    (n) => n.value
  );
  const gear = [...form.querySelectorAll("input[name=gear]:checked")].map((n) => n.value);
  const payload = {
    setting: form.setting.value,
    climate: form.climate.value,
    hours: Number(form.hours.value),
    people: Number(form.people.value),
    problems,
    gear,
    notes: form.notes.value,
    use_local_model: form.use_local_model.checked,
  };
  const res = await fetch("/api/operator", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  const out = document.getElementById("briefing");
  out.hidden = false;
  const modules = (data.modules || [])
    .map((mod) => `<h3>${esc(mod.title)}</h3><pre>${esc(mod.body)}</pre>`)
    .join("");
  out.innerHTML = `
    <p><strong>${esc(data.disclaimer)}</strong></p>
    <ul>${(data.briefing || []).map((line) => `<li>${esc(line)}</li>`).join("")}</ul>
    ${data.local_rewrite ? `<h3>Local model</h3><pre>${esc(data.local_rewrite)}</pre>` : ""}
    ${modules}
    <button class="print" type="button">Print briefing</button>
  `;
  out.querySelector(".print").addEventListener("click", () => window.print());
});

loadKits().catch((err) => {
  banner.hidden = false;
  banner.classList.add("bad");
  banner.textContent = String(err);
});
loadHub().catch(() => {});
loadManual().catch(() => {});
