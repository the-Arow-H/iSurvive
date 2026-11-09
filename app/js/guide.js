/* iSurvive NA field guide. MIT. Reads only local pages.json. */
(function () {
  const MODULES = [
    ["shelter", "Shelter"],
    ["water", "Water"],
    ["first-aid", "First aid"],
    ["flora", "Edible plants"],
    ["fauna", "Fish and game"],
    ["biomes", "Biomes"],
    ["about", "About"],
  ];
  const BIOME_LABELS = {
    "eastern-deciduous": "Eastern deciduous forest",
    "boreal-taiga": "Boreal / taiga",
    "great-plains": "Great Plains",
    "desert-southwest": "Desert Southwest",
    "pacific-northwest": "Pacific Northwest rainforest",
    "rockies-alpine": "Rockies alpine",
    "arctic-tundra": "Arctic tundra",
    "gulf-southeast": "Gulf / Southeast subtropical",
  };

  const main = document.getElementById("main");
  const hits = document.getElementById("hits");
  const q = document.getElementById("q");
  const biomeSelect = document.getElementById("biome");
  const net = document.getElementById("net");
  let pages = [];
  let byId = new Map();
  let search = null;

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function setNet() {
    const off = !navigator.onLine;
    net.dataset.state = off ? "offline" : "online";
    net.textContent = off ? "Offline — reading the cache" : "Online — cache is ready after this load";
  }

  function moduleLabel(id) {
    const found = MODULES.find((row) => row[0] === id);
    return found ? found[1] : id;
  }

  function pagesIn(module, biome) {
    return pages.filter((page) => {
      if (module && page.module !== module) return false;
      if (biome && page.biomes && page.biomes.length && !page.biomes.includes(biome)) return false;
      return true;
    });
  }

  function card(page) {
    const review = page.review === "pending-clinical" ? " · clinical review pending" : "";
    return `<a href="#/page/${escapeHtml(page.id)}"><strong>${escapeHtml(page.title)}</strong><br><span class="meta">${escapeHtml(page.summary)}${review}</span></a>`;
  }

  function renderHome() {
    const biome = biomeSelect.value;
    const biomeNote = biome
      ? `<p>Showing pages tagged <strong>${escapeHtml(BIOME_LABELS[biome] || biome)}</strong>, plus pages that apply everywhere.</p>`
      : `<p>Pick a biome if you know it. Pages without a biome tag stay in the list.</p>`;
    const blocks = MODULES.filter((row) => row[0] !== "about")
      .map(([id, label]) => {
        const list = pagesIn(id, biome).slice(0, 8);
        if (!list.length) return "";
        return `<section><h2>${escapeHtml(label)}</h2><div class="cards">${list.map(card).join("")}</div></section>`;
      })
      .join("");
    main.innerHTML = `<article class="sheet">
      <p class="kicker">Field guide</p>
      <h2>What do you need first?</h2>
      <p>Shelter from exposure, then water you have treated, then a way to get help. Food can wait. Nothing here is medical advice.</p>
      ${biomeNote}
      ${blocks}
    </article>`;
  }

  function renderModule(id) {
    const biome = biomeSelect.value;
    const list = pagesIn(id, biome);
    main.innerHTML = `<article class="sheet">
      <p class="kicker">${escapeHtml(moduleLabel(id))}</p>
      <h2>${escapeHtml(moduleLabel(id))}</h2>
      <div class="cards">${list.map(card).join("") || "<p>No pages for this filter.</p>"}</div>
    </article>`;
  }

  function renderPage(id) {
    const page = byId.get(id);
    if (!page) {
      main.innerHTML = `<article class="sheet"><h2>Page not in the guide</h2><p><a href="#/">Back home</a></p></article>`;
      return;
    }
    const clinical = page.module === "first-aid"
      ? `<div class="clinical"><strong>NOT MEDICAL ADVICE.</strong> This page is a draft. Frontmatter <span class="mono">review: pending-clinical</span>. A licensed pharmacist does a last look before this is treated as ready. No drug doses. Get professional care. <a href="#/page/disclaimer">Disclaimer</a></div>`
      : "";
    const sci = page.sci ? `<p class="meta"><em>${escapeHtml(page.sci)}</em>${page.usda_symbol ? " · USDA " + escapeHtml(page.usda_symbol) : ""}</p>` : "";
    const meta = `<p class="meta">${escapeHtml(moduleLabel(page.module))} · checked ${escapeHtml(page.last_reviewed)} · sources ${page.sources.map(escapeHtml).join(", ")}</p>`;
    main.innerHTML = `<article class="sheet" data-page="${escapeHtml(page.id)}">
      <p class="kicker"><a href="#/module/${escapeHtml(page.module)}">${escapeHtml(moduleLabel(page.module))}</a></p>
      <h2>${escapeHtml(page.title)}</h2>
      ${sci}
      ${clinical}
      ${meta}
      ${page.html}
    </article>`;
    const look = main.querySelector("h2");
    main.querySelectorAll("h2").forEach((node) => {
      if (node.textContent.trim() === "DEADLY LOOK-ALIKES") {
        const box = document.createElement("div");
        box.className = "lookalike";
        node.parentNode.insertBefore(box, node);
        box.appendChild(node);
        let sib = box.nextSibling;
        while (sib && !(sib.nodeType === 1 && sib.tagName === "H2")) {
          const next = sib.nextSibling;
          box.appendChild(sib);
          sib = next;
        }
      }
    });
    if (look) look.focus?.();
  }

  function route() {
    const hash = location.hash || "#/";
    const parts = hash.replace(/^#\/?/, "").split("/").filter(Boolean);
    if (!parts.length) return renderHome();
    if (parts[0] === "module" && parts[1]) return renderModule(decodeURIComponent(parts[1]));
    if (parts[0] === "page" && parts[1]) return renderPage(decodeURIComponent(parts[1]));
    renderHome();
  }

  function wireSearch() {
    search = new MiniSearch({
      fields: ["title", "summary", "text", "sci", "name"],
      storeFields: ["title", "summary", "module"],
      searchOptions: { prefix: true, fuzzy: 0.2, combineWith: "AND" },
    });
    search.addAll(pages);
    q.addEventListener("input", () => {
      const query = q.value.trim();
      if (query.length < 2) {
        hits.hidden = true;
        hits.innerHTML = "";
        return;
      }
      const found = search.search(query).slice(0, 8);
      hits.hidden = false;
      hits.innerHTML = found.length
        ? found.map((hit) => `<a href="#/page/${escapeHtml(hit.id)}">${escapeHtml(hit.title)} <span class="meta">${escapeHtml(moduleLabel(hit.module))}</span></a>`).join("")
        : `<p class="fine">No match in the offline index.</p>`;
    });
  }

  function wireNav() {
    const host = document.getElementById("modules");
    MODULES.forEach(([id, label]) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "mod";
      button.textContent = label;
      button.addEventListener("click", () => {
        location.hash = id === "about" ? "#/page/disclaimer" : `#/module/${id}`;
      });
      host.appendChild(button);
    });
    Object.entries(BIOME_LABELS).forEach(([id, label]) => {
      const option = document.createElement("option");
      option.value = id;
      option.textContent = label;
      biomeSelect.appendChild(option);
    });
    biomeSelect.addEventListener("change", route);
  }

  async function start() {
    wireNav();
    setNet();
    window.addEventListener("online", setNet);
    window.addEventListener("offline", setNet);
    const response = await fetch("/data/pages.json");
    const data = await response.json();
    pages = data.pages;
    byId = new Map(pages.map((page) => [page.id, page]));
    wireSearch();
    window.addEventListener("hashchange", route);
    route();
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.register("/sw.js").catch(() => {});
    }
  }

  start().catch((error) => {
    main.innerHTML = `<article class="sheet"><h2>The guide did not load</h2><p>${escapeHtml(error.message)}</p><p>Serve this folder over http from the app directory. Opening the file directly will not register the service worker.</p></article>`;
  });
})();
