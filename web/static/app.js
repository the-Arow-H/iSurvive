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
  banner.textContent = `Checkout complete for ${params.get("sku") || "kit"}. Pack against the BOM.`;
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

function kitCard(kit, checkoutEnabled) {
  const el = document.createElement("article");
  el.className = "card";
  el.innerHTML = `
    <img src="${kit.photo}" alt="${kit.sku}" />
    <div class="sku">${esc(kit.sku)} · ${esc(kit.path)}</div>
    <h3>${esc(kit.name)}</h3>
    <p>${esc(kit.summary)}</p>
    <div class="price">${money(kit.price_cents)}</div>
    <div class="muted">landed ${money(kit.landed_cents)} · floor ${money(kit.min_price_cents)}</div>
    <div class="margin ${kit.margin_ok ? "ok" : "fail"}">
      ${kit.margin_ok ? "margin OK" : "MARGIN FAIL"} · ${(kit.gross_margin * 100).toFixed(0)}%
    </div>
    <details>
      <summary>BOM</summary>
      <ul class="bom">
        ${kit.bom
          .map(
            (line) =>
              `<li>${line.qty}× ${esc(line.pn)} ${esc(line.name)} (${esc(line.process)}) ${money(line.ext_landed_cents)}</li>`
          )
          .join("")}
      </ul>
    </details>
    <button class="buy" ${checkoutEnabled && kit.margin_ok ? "" : "disabled"} data-sku="${kit.sku}">
      ${checkoutEnabled ? "Checkout" : "Checkout needs STRIPE_SECRET_KEY"}
    </button>
  `;
  el.querySelector(".buy").addEventListener("click", () => buy(kit.sku));
  return el;
}

async function buy(sku) {
  const res = await fetch("/api/checkout", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sku, quantity: 1 }),
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
  document.getElementById("kit-notes").textContent = data.notes;
  const grid = document.getElementById("kit-grid");
  data.kits.forEach((kit) => grid.append(kitCard(kit, data.checkout_enabled)));
}

async function loadHub() {
  const data = await jget("/api/hub");
  document.getElementById("hub-status").textContent = JSON.stringify(data, null, 2);
}

document.getElementById("situation-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.target;
  const problems = [...form.querySelectorAll("input[name=problems]:checked")].map(
    (n) => n.value
  );
  const payload = {
    setting: form.setting.value,
    climate: form.climate.value,
    hours: Number(form.hours.value),
    people: Number(form.people.value),
    problems,
    gear: form.gear.value ? [form.gear.value] : [],
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
  `;
});

loadKits().catch((err) => {
  banner.hidden = false;
  banner.classList.add("bad");
  banner.textContent = String(err);
});
loadHub().catch(() => {});
