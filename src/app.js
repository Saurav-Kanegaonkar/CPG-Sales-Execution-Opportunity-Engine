const data = window.CPG_DATA;

const currency = (value) =>
  new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(value);

const number = (value) => new Intl.NumberFormat("en-US").format(value);

const pct = (value) => `${(Number(value) * 100).toFixed(1)}%`;

const tabs = [
  { id: "cockpit", label: "Cockpit" },
  { id: "queue", label: "Opportunity Queue" },
  { id: "model", label: "Retail Model" },
  { id: "quality", label: "Data Quality" },
  { id: "field", label: "Field Actions" },
];

function tierClass(tier) {
  return tier.toLowerCase();
}

function renderShell() {
  document.querySelector("#app").innerHTML = `
    <section class="hero">
      <div>
        <p class="eyebrow">CPG Sales Execution Analytics</p>
        <h1>Sales Execution Opportunity Engine</h1>
        <p class="lede">A retail execution decision product that combines syndicated-style POS, distribution, promotion compliance, field visits, and validation checks into a ranked commercial action queue.</p>
      </div>
      <aside class="brief">
        <span>Decision Question</span>
        <strong>Where should commercial teams focus to close the largest execution gaps?</strong>
      </aside>
    </section>

    <section class="kpis">
      <article><span>Retail Stores</span><strong>${data.kpis.stores}</strong><em>modeled panel</em></article>
      <article><span>Weekly Rows</span><strong>${number(data.kpis.weeklyRows)}</strong><em>store-SKU grain</em></article>
      <article><span>Opportunity</span><strong>${currency(data.kpis.totalOpportunity)}</strong><em>margin weighted</em></article>
      <article><span>Critical Gaps</span><strong>${data.kpis.critical}</strong><em>priority actions</em></article>
    </section>

    <nav class="tabs" aria-label="Engine views">
      ${tabs.map((tab) => `<button class="${tab.id === "cockpit" ? "active" : ""}" data-tab="${tab.id}">${tab.label}</button>`).join("")}
    </nav>

    <section id="view"></section>
  `;

  document.querySelectorAll(".tabs button").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".tabs button").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      renderView(button.dataset.tab);
    });
  });

  renderView("cockpit");
}

function renderView(tab) {
  if (tab === "cockpit") renderCockpit();
  if (tab === "queue") renderQueue();
  if (tab === "model") renderModel();
  if (tab === "quality") renderQuality();
  if (tab === "field") renderField();
}

function renderCockpit() {
  document.querySelector("#view").innerHTML = `
    <section class="grid two">
      <article class="panel">
        <div class="panel-title">
          <p class="eyebrow">Commercial Pulse</p>
          <h2>Opportunity by retailer</h2>
        </div>
        <div class="bars">
          ${data.retailers.map((row) => `
            <div class="bar-row">
              <div>
                <strong>${row.retailer}</strong>
                <span>${row.channel} · ${row.critical_count} critical gaps</span>
              </div>
              <div class="bar-track"><i style="width:${Math.min(100, Number(row.opportunity_value) / data.retailers[0].opportunity_value * 100)}%"></i></div>
              <b>${currency(row.opportunity_value)}</b>
            </div>
          `).join("")}
        </div>
      </article>
      <article class="panel callout">
        <p class="eyebrow">Recommendation</p>
        <h2>Use value and confidence together</h2>
        <p>The largest commercial opportunities are not always the cleanest data stories. The engine pairs margin-weighted upside with validation status so sales leaders can act while BI and data engineering close trust gaps.</p>
        <dl>
          <div><dt>Modeled sales</dt><dd>${currency(data.kpis.totalSales)}</dd></div>
          <div><dt>Checks to investigate</dt><dd>${data.kpis.checksInvestigate}</dd></div>
        </dl>
      </article>
    </section>
  `;
}

function renderQueue() {
  document.querySelector("#view").innerHTML = `
    <section class="panel">
      <div class="panel-title">
        <p class="eyebrow">Sales Enablement Queue</p>
        <h2>Ranked retailer-region-category actions</h2>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr><th>Retailer</th><th>Region</th><th>Category</th><th>Value</th><th>ACV</th><th>OOS</th><th>Promo</th><th>Risk</th><th>Action</th></tr>
          </thead>
          <tbody>
            ${data.opportunities.map((row) => `
              <tr>
                <td><strong>${row.retailer}</strong></td>
                <td>${row.region}</td>
                <td>${row.category}</td>
                <td>${currency(row.opportunity_value)}</td>
                <td>${row.avg_acv_distribution}%</td>
                <td>${pct(row.avg_oos_rate)}</td>
                <td>${pct(row.avg_promo_compliance)}</td>
                <td><mark class="${tierClass(row.tier)}">${row.tier}</mark></td>
                <td>${row.recommended_action}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    </section>
  `;
}

function renderModel() {
  document.querySelector("#view").innerHTML = `
    <section class="grid two">
      <article class="panel">
        <div class="panel-title">
          <p class="eyebrow">Model Drivers</p>
          <h2>Category opportunity and margin context</h2>
        </div>
        <div class="score-list">
          ${data.categories.map((row) => `
            <div>
              <span>${row.category}</span>
              <strong>${currency(row.opportunity_value)}</strong>
              <em>${row.critical_count} critical · ${Math.round(row.margin_rate * 100)}% modeled margin</em>
            </div>
          `).join("")}
        </div>
      </article>
      <article class="panel model-card">
        <p class="eyebrow">Explainable Scoring</p>
        <h2>How the engine ranks work</h2>
        <div class="formula">
          <span>Distribution gap</span>
          <span>OOS risk</span>
          <span>Promo compliance</span>
          <span>Feature and display</span>
          <span>Data confidence</span>
          <span>Field capacity</span>
        </div>
        <p>Opportunity value is margin weighted. Priority score adds urgency from execution gaps, validation failure rates, and open field sales follow-up so the queue can support both leadership review and rep-level enablement.</p>
      </article>
    </section>
  `;
}

function renderQuality() {
  document.querySelector("#view").innerHTML = `
    <section class="panel">
      <div class="panel-title">
        <p class="eyebrow">Snowflake Readiness</p>
        <h2>Validation and reconciliation checks</h2>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Retailer</th><th>Check</th><th>Failure Rate</th><th>Rows</th><th>Owner</th><th>Status</th></tr></thead>
          <tbody>
            ${data.checks.map((row) => `
              <tr>
                <td><strong>${row.retailer}</strong></td>
                <td>${row.check_name}</td>
                <td>${pct(row.failure_rate)}</td>
                <td>${number(row.rows_checked)}</td>
                <td>${row.owner}</td>
                <td><mark class="${row.status === "Investigate" ? "critical" : row.status === "Monitor" ? "watch" : "stable"}">${row.status}</mark></td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    </section>
  `;
}

function renderField() {
  document.querySelector("#view").innerHTML = `
    <section class="grid two">
      <article class="panel">
        <div class="panel-title">
          <p class="eyebrow">Field Sales Follow-up</p>
          <h2>Open execution work</h2>
        </div>
        <div class="event-list">
          ${data.visits.map((row) => `
            <div>
              <strong>${row.issue_found}</strong>
              <span>${row.retailer} · ${row.region} · ${row.store_id}</span>
              <b>${row.status}</b>
            </div>
          `).join("")}
        </div>
      </article>
      <article class="panel callout">
        <p class="eyebrow">End User Adoption</p>
        <h2>Designed for the weekly sales cadence</h2>
        <p>The queue can be filtered into retailer decks, field manager call lists, and BI-certified tables. That makes the artifact useful as both a strategic planning view and a repeatable reporting output.</p>
      </article>
    </section>
  `;
}

renderShell();
