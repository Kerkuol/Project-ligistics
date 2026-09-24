/**
 * LRE-Visualizer Engine: Интерактивный Canvas-граф концептуально-семантической нейросети.
 */

// Базовый адрес API
const API_BASE = "http://localhost:8000";

// Встроенная схема (все 45 требований из реестра КИС2)
const ALL_REQUIREMENTS_SCHEMA = [
  { id: "TR-01", label: "TR-01 Вид транспорта", area: "Транспорт" },
  { id: "TR-02", label: "TR-02 Тип ТС (ADR)", area: "Транспорт" },
  { id: "TR-03", label: "TR-03 Спецтранспорт", area: "Транспорт" },
  { id: "TR-04", label: "TR-04 Характеристики ТС", area: "Транспорт" },
  { id: "TR-05", label: "TR-05 Способ перевозки", area: "Перевозка" },
  { id: "TR-06", label: "TR-06 Размещение при перевозке", area: "Перевозка" },
  { id: "TR-07", label: "TR-07 Прямой транспорт", area: "Перевозка" },
  { id: "TR-08", label: "TR-08 Перегруз", area: "Перевозка" },
  { id: "TR-09", label: "TR-09 Перецепка", area: "Перевозка" },
  { id: "TR-10", label: "TR-10 Способ размещения груза", area: "Размещение" },
  { id: "TR-11", label: "TR-11 Особые условия размещения", area: "Размещение" },
  { id: "KR-01", label: "KR-01 Спецкрепление", area: "Крепление" },
  { id: "KR-02", label: "KR-02 Способ крепления", area: "Крепление" },
  { id: "KR-03", label: "KR-03 Параметры крепления", area: "Крепление" },
  { id: "PG-01", label: "PG-01 Способ погрузки", area: "Погрузка/разгрузка" },
  { id: "PG-02", label: "PG-02 Способ разгрузки", area: "Погрузка/разгрузка" },
  { id: "PG-03", label: "PG-03 Погрузочное оборуд.", area: "Погрузка/разгрузка" },
  { id: "PG-04", label: "PG-04 Условия площадки", area: "Погрузка/разгрузка" },
  { id: "MR-01", label: "MR-01 Маршрут перевозки", area: "Маршрут" },
  { id: "MR-02", label: "MR-02 Ограничения маршрута", area: "Маршрут" },
  { id: "MR-03", label: "MR-03 Спецразрешение", area: "Маршрут" },
  { id: "MR-04", label: "MR-04 Условия границы", area: "Маршрут" },
  { id: "MR-05", label: "MR-05 Погранпереход", area: "Маршрут" },
  { id: "SR-01", label: "SR-01 Срок перевозки", area: "Сроки" },
  { id: "SR-02", label: "SR-02 Ограничения по срокам", area: "Сроки" },
  { id: "DC-01", label: "DC-01 Техописание груза", area: "Документация" },
  { id: "DC-02", label: "DC-02 Чертежи груза", area: "Документация" },
  { id: "DC-03", label: "DC-03 Центр тяжести", area: "Документация" },
  { id: "DC-04", label: "DC-04 Фотоматериалы", area: "Документация" },
  { id: "DC-05", label: "DC-05 Сертификаты", area: "Документация" },
  { id: "DC-06", label: "DC-06 Разрешительные док.", area: "Документация" },
  { id: "DC-07", label: "DC-07 Экспортные док.", area: "Документация" },
  { id: "DC-08", label: "DC-08 Требования к док.", area: "Документация" },
  { id: "TM-01", label: "TM-01 Место таможни", area: "Таможня" },
  { id: "TM-02", label: "TM-02 Спец СВХ", area: "Таможня" },
  { id: "TM-03", label: "TM-03 Транзитные док.", area: "Таможня" },
  { id: "ST-01", label: "ST-01 Страхование груза", area: "Страхование" },
  { id: "ST-02", label: "ST-02 Страховая сумма", area: "Страхование" },
  { id: "ST-03", label: "ST-03 Сторона страхования", area: "Страхование" },
  { id: "WH-01", label: "WH-01 Временное хранение", area: "Хранение" },
  { id: "WH-02", label: "WH-02 Место хранения", area: "Хранение" },
  { id: "AD-01", label: "AD-01 Доставка до порта", area: "Доп. операции" },
  { id: "AD-02", label: "AD-02 Доп. ПРР операции", area: "Доп. операции" },
  { id: "AD-03", label: "AD-03 Перевалка", area: "Доп. операции" },
  { id: "AD-04", label: "AD-04 Доп. хранение", area: "Доп. операции" }
];

const DEFAULT_GRAPH_SCHEMA = {
  inputs: [
    { id: "x_dim_width", label: "Ширина (>2.55м)", type: "input" },
    { id: "x_dim_height", label: "Высота (>2.80м)", type: "input" },
    { id: "x_dim_length", label: "Длина (>13.6м)", type: "input" },
    { id: "x_weight_single", label: "Вес места (т)", type: "input" },
    { id: "x_weight_heavy_flag", label: "Вес места >1.5т", type: "input" },
    { id: "x_total_weight", label: "Общий вес (>20т)", type: "input" },
    { id: "x_high_cost", label: "Стоимость (>50k$)", type: "input" },
    { id: "x_danger_hazard", label: "Опасность IMO/UN", type: "input" },
    { id: "x_danger_vet_kfk_skk", label: "ВЕТ/СКК/КФК", type: "input" },
    { id: "x_non_stackable", label: "Не штабелировать", type: "input" },
    { id: "x_text_no_tilt", label: "Текст: Не кантовать", type: "input" },
    { id: "x_text_crane_top", label: "Текст: Только кран", type: "input" },
    { id: "x_text_moisture_protect", label: "Текст: Боится влаги", type: "input" },
    { id: "x_text_direct_only", label: "Текст: Без перевалки", type: "input" },
    { id: "x_incoterms_exw_fca", label: "Incoterms EXW/FCA", type: "input" },
    { id: "x_transport_multimodal", label: "Мультимодал / Море", type: "input" }
  ],
  concepts: [
    { id: "Z_OVERSIZE_WIDTH", label: "Негабарит по ширине", description: "Ширина груза превышает дорожный габарит 2.55м", type: "concept" },
    { id: "Z_OVERSIZE_HEIGHT", label: "Негабарит по высоте", description: "Высота требует низкорамного трала или автопоезд >4.0м", type: "concept" },
    { id: "Z_OVERSIZE_LENGTH", label: "Негабарит по длине", description: "Длина превышает стандартный кузов 13.6м", type: "concept" },
    { id: "Z_HEAVY_AXLE_LOAD", label: "Тяжеловесность / Оси", description: "Высокая масса места (>1.5т / >20т), нагрузка на оси", type: "concept" },
    { id: "Z_DYNAMIC_INSTABILITY", label: "Смещение центра тяжести", description: "Риск опрокидывания при маневрах и транспортировке", type: "concept" },
    { id: "Z_FRAGILITY_SENSITIVITY", label: "Хрупкость / Кантование", description: "Чувствительность к ударам, запрет кантования", type: "concept" },
    { id: "Z_WEATHER_CORROSION_RISK", label: "Боится влаги / Осадков", description: "Требует закрытого кузова, тента, вакуумной упаковки", type: "concept" },
    { id: "Z_CARGO_HIGH_VALUE_RISK", label: "Высокая ценность", description: "Высокая инвойсная стоимость, требование сюрвейера/охраны", type: "concept" },
    { id: "Z_TRANSSHIPMENT_PROHIBITED", label: "Запрет перевалки", description: "Недопустимость перетарки в пути (прямой транспорт)", type: "concept" },
    { id: "Z_CRANE_RIGGING_COMPLEXITY", label: "Сложность такелажа", description: "Погрузка краном через верх, траверсы, спецзахваты", type: "concept" },
    { id: "Z_HAZARDOUS_COMPLIANCE", label: "Опасный груз (ADR)", description: "Специальные требования к перевозке опасных веществ", type: "concept" },
    { id: "Z_CUSTOMS_BORDER_FRICTION", label: "Таможня / Карантин", description: "Нетарифное регулирование, погранпереходы с вет/фито", type: "concept" }
  ],
  requirements: ALL_REQUIREMENTS_SCHEMA
};

let graphSchema = DEFAULT_GRAPH_SCHEMA;
let currentTrace = null;
let currentRequirements = [];
let focusedNodeId = null;

// Canvas & анимация
const canvas = document.getElementById("neuralCanvas");
const ctx = canvas.getContext("2d");
let animFrameId = null;
let pulseOffset = 0;

let renderNodes = [];
let renderLinks = [];

// Вспомогательная функция безопасного парсинга чисел (включая русскую запятую)
function safeNum(val, fallback = 0.0) {
  if (val === null || val === undefined) return fallback;
  const s = String(val).trim().replace(',', '.');
  const n = parseFloat(s);
  return isNaN(n) ? fallback : n;
}

window.addEventListener("DOMContentLoaded", async () => {
  setupCanvasResize();
  setupEventListeners();
  
  await fetchSchema();
  await fetchTraceList();
  await fetchLatestTrace();

  startAnimationLoop();
});

function setupCanvasResize() {
  const wrapper = document.getElementById("canvasWrapper");

  const updateSize = () => {
    const width = wrapper.clientWidth || 900;
    const height = wrapper.clientHeight || 650;
    const dpr = window.devicePixelRatio || 1;

    canvas.width = Math.floor(width * dpr);
    canvas.height = Math.floor(height * dpr);
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;

    ctx.resetTransform();
    ctx.scale(dpr, dpr);

    recomputeGraphLayout();
  };

  if (window.ResizeObserver) {
    const ro = new ResizeObserver(() => updateSize());
    ro.observe(wrapper);
  } else {
    window.addEventListener("resize", updateSize);
  }
  updateSize();
}

function setupEventListeners() {
  canvas.addEventListener("click", (e) => {
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    let clicked = null;
    for (const node of renderNodes) {
      const dist = Math.hypot(node.x - mouseX, node.y - mouseY);
      if (dist <= Math.max(node.radius + 8, 14)) {
        clicked = node;
        break;
      }
    }

    if (clicked) {
      setFocusedNode(clicked.id);
    } else {
      setFocusedNode(null);
    }
  });

  document.getElementById("traceSelect").addEventListener("change", (e) => {
    if (e.target.value === "latest") {
      fetchLatestTrace();
    } else {
      fetchTraceById(e.target.value);
    }
  });

  document.getElementById("refreshTracesBtn").addEventListener("click", fetchTraceList);
  document.getElementById("resetFocusBtn").addEventListener("click", () => setFocusedNode(null));

  const sandboxOverlay = document.getElementById("sandboxOverlay");
  document.getElementById("toggleSandboxBtn").addEventListener("click", () => {
    sandboxOverlay.classList.add("active");
  });
  document.getElementById("closeSandboxBtn").addEventListener("click", () => {
    sandboxOverlay.classList.remove("active");
  });

  document.getElementById("sandboxForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    await runSandboxSimulation();
    sandboxOverlay.classList.remove("active");
  });

  document.getElementById("loadSampleBtn").addEventListener("click", fillSampleSandboxData);
}

async function fetchSchema() {
  try {
    const res = await fetch(`${API_BASE}/v1/graph-schema`);
    if (res.ok) {
      const data = await res.json();
      if (data && data.concepts && data.concepts.length > 0) {
        graphSchema = data;
        recomputeGraphLayout();
      }
    }
  } catch (e) {
    console.log("Схема API недоступна, используется встроенная");
  }
}

async function fetchTraceList() {
  try {
    const select = document.getElementById("traceSelect");
    const res = await fetch(`${API_BASE}/v1/traces?limit=15`);
    if (res.ok) {
      const list = await res.json();
      select.innerHTML = '<option value="latest">⚡ Последний расчет (Live)</option>';
      list.forEach((t) => {
        const opt = document.createElement("option");
        opt.value = t.trace_id;
        opt.textContent = `${t.request_id || "Запрос"} [${t.trace_id.slice(-6)}] (${(t.created_at || "").slice(11, 19)})`;
        select.appendChild(opt);
      });
    }
  } catch (err) {
    console.log("История трассировок пока пуста");
  }
}

async function fetchLatestTrace() {
  try {
    const res = await fetch(`${API_BASE}/v1/traces/latest/active`);
    if (res.ok) {
      const trace = await res.json();
      applyTrace(trace);
      return;
    }
  } catch (e) {}
  loadDefaultDemoState();
}

async function fetchTraceById(traceId) {
  try {
    const res = await fetch(`${API_BASE}/v1/traces/${traceId}`);
    if (res.ok) {
      const trace = await res.json();
      applyTrace(trace);
    }
  } catch (e) {
    console.error(e);
  }
}

function applyTrace(trace) {
  currentTrace = trace;
  recomputeGraphLayout();
  if (focusedNodeId) {
    renderInspector(focusedNodeId);
  }
}

function recomputeGraphLayout() {
  const w = canvas.clientWidth || (canvas.width / (window.devicePixelRatio || 1)) || 900;
  const h = canvas.clientHeight || (canvas.height / (window.devicePixelRatio || 1)) || 650;

  renderNodes = [];
  renderLinks = [];

  const colX = {
    input: w * 0.16,
    concept: w * 0.50,
    requirement: w * 0.84
  };

  // 1. Узлы слоя X
  const inps = graphSchema.inputs;
  const inCount = inps.length;
  inps.forEach((inp, idx) => {
    const sig = currentTrace && currentTrace.input_signals ? (currentTrace.input_signals[inp.id] || 0) : 0;
    const yPos = inCount > 1 ? (h * 0.08) + (idx / (inCount - 1)) * (h * 0.84) : h * 0.5;
    renderNodes.push({
      id: inp.id,
      label: inp.label,
      layer: "input",
      x: colX.input,
      y: yPos,
      activation: sig,
      radius: Math.min(12, Math.max(5, 5 + sig * 5)),
      color: "#38bdf8"
    });
  });

  // 2. Узлы слоя Z
  const concs = graphSchema.concepts;
  const cCount = concs.length;
  concs.forEach((c, idx) => {
    const act = currentTrace && currentTrace.concept_activations ? (currentTrace.concept_activations[c.id] || 0) : 0;
    const yPos = cCount > 1 ? (h * 0.08) + (idx / (cCount - 1)) * (h * 0.84) : h * 0.5;
    renderNodes.push({
      id: c.id,
      label: c.label,
      description: c.description,
      layer: "concept",
      x: colX.concept,
      y: yPos,
      activation: act,
      radius: Math.min(14, Math.max(6, 6 + act * 6)),
      color: "#c084fc"
    });
  });

  // 3. Узлы слоя Y (Только активные требования > 0.40 для чистоты графа)
  const reqActivations = currentTrace && currentTrace.requirement_activations ? currentTrace.requirement_activations : {};
  const allReqs = graphSchema.requirements || ALL_REQUIREMENTS_SCHEMA;
  const activeReqs = allReqs.filter(r => (reqActivations[r.id] || 0) >= 0.40);
  const displayReqs = activeReqs.length > 0 ? activeReqs : allReqs.slice(0, 15);
  const rCount = displayReqs.length;

  displayReqs.forEach((r, idx) => {
    const act = reqActivations[r.id] || 0;
    const yPos = rCount > 1 ? (h * 0.08) + (idx / (rCount - 1)) * (h * 0.84) : h * 0.5;
    renderNodes.push({
      id: r.id,
      label: r.label,
      area: r.area,
      layer: "requirement",
      x: colX.requirement,
      y: yPos,
      activation: act,
      radius: Math.min(14, Math.max(6, 6 + act * 6)),
      color: act >= 0.7 ? "#34d399" : (act >= 0.4 ? "#fbbf24" : "#64748b")
    });
  });

  // 4. Связи (ребра)
  if (currentTrace && currentTrace.active_links && currentTrace.active_links.length > 0) {
    const nodeMap = new Map(renderNodes.map(n => [n.id, n]));
    currentTrace.active_links.forEach((l) => {
      const src = nodeMap.get(l.source_id);
      const tgt = nodeMap.get(l.target_id);
      if (src && tgt) {
        renderLinks.push({
          source: src,
          target: tgt,
          weight: l.weight,
          contribution: l.contribution,
          isStimulated: l.contribution > 0
        });
      }
    });
  }
}

function startAnimationLoop() {
  function tick() {
    pulseOffset = (pulseOffset + 0.007) % 1.0;
    drawCanvas();
    animFrameId = requestAnimationFrame(tick);
  }
  if (!animFrameId) {
    tick();
  }
}

function drawCanvas() {
  const w = canvas.clientWidth || (canvas.width / (window.devicePixelRatio || 1));
  const h = canvas.clientHeight || (canvas.height / (window.devicePixelRatio || 1));
  ctx.clearRect(0, 0, w, h);

  // Сетка
  ctx.strokeStyle = "rgba(39, 53, 83, 0.22)";
  ctx.lineWidth = 1;
  ctx.beginPath();
  for (let x = 0; x < w; x += 40) {
    ctx.moveTo(x, 0); ctx.lineTo(x, h);
  }
  for (let y = 0; y < h; y += 40) {
    ctx.moveTo(0, y); ctx.lineTo(w, y);
  }
  ctx.stroke();

  // Линии связей
  renderLinks.forEach((link) => {
    const isFocused = !focusedNodeId ||
      link.source.id === focusedNodeId ||
      link.target.id === focusedNodeId;

    const alpha = isFocused ? 0.85 : 0.08;
    const strokeColor = link.isStimulated
      ? `rgba(6, 182, 212, ${alpha})`
      : `rgba(244, 63, 94, ${alpha})`;

    ctx.strokeStyle = strokeColor;
    ctx.lineWidth = isFocused ? Math.min(Math.abs(link.contribution) * 2.2 + 0.5, 4.0) : 0.6;

    ctx.beginPath();
    ctx.moveTo(link.source.x, link.source.y);
    const cp1x = link.source.x + (link.target.x - link.source.x) * 0.5;
    const cp2x = link.source.x + (link.target.x - link.source.x) * 0.5;
    ctx.bezierCurveTo(cp1x, link.source.y, cp2x, link.target.y, link.target.x, link.target.y);
    ctx.stroke();

    if (isFocused && Math.abs(link.contribution) >= 0.35) {
      const t = pulseOffset;
      const px = Math.pow(1 - t, 3) * link.source.x +
                 3 * Math.pow(1 - t, 2) * t * cp1x +
                 3 * (1 - t) * Math.pow(t, 2) * cp2x +
                 Math.pow(t, 3) * link.target.x;
      const py = Math.pow(1 - t, 3) * link.source.y +
                 3 * Math.pow(1 - t, 2) * t * link.source.y +
                 3 * (1 - t) * Math.pow(t, 2) * link.target.y +
                 Math.pow(t, 3) * link.target.y;

      ctx.fillStyle = link.isStimulated ? "#67e8f9" : "#fda4af";
      ctx.beginPath();
      ctx.arc(px, py, 2.5, 0, Math.PI * 2);
      ctx.fill();
    }
  });

  // Узлы
  renderNodes.forEach((node) => {
    const isFocused = !focusedNodeId ||
      node.id === focusedNodeId ||
      isNodeConnected(node.id, focusedNodeId);

    const alpha = isFocused ? 1.0 : 0.15;
    ctx.save();
    ctx.globalAlpha = alpha;

    if (node.activation > 0.3 && isFocused) {
      ctx.shadowColor = node.color;
      ctx.shadowBlur = Math.min(18, 8 + node.activation * 12);
    }

    ctx.fillStyle = node.color;
    ctx.beginPath();
    ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = "#ffffff";
    ctx.beginPath();
    ctx.arc(node.x, node.y, Math.max(node.radius * 0.35, 2.5), 0, Math.PI * 2);
    ctx.fill();

    ctx.restore();

    ctx.save();
    ctx.globalAlpha = isFocused ? 1.0 : 0.25;
    ctx.font = "11px 'JetBrains Mono', monospace";
    ctx.fillStyle = "#e2e8f0";

    const actStr = node.activation.toFixed(2);
    if (node.layer === "input") {
      ctx.textAlign = "right";
      ctx.fillText(`${node.label} [${actStr}]`, node.x - node.radius - 8, node.y + 4);
    } else if (node.layer === "concept") {
      ctx.textAlign = "center";
      ctx.fillText(`${node.label} (${actStr})`, node.x, node.y - node.radius - 6);
    } else {
      ctx.textAlign = "left";
      ctx.fillText(`${node.label} [${actStr}]`, node.x + node.radius + 8, node.y + 4);
    }
    ctx.restore();
  });
}

function isNodeConnected(nodeIdA, nodeIdB) {
  if (!renderLinks) return false;
  return renderLinks.some(l =>
    (l.source.id === nodeIdA && l.target.id === nodeIdB) ||
    (l.source.id === nodeIdB && l.target.id === nodeIdA)
  );
}

function setFocusedNode(nodeId) {
  focusedNodeId = nodeId;
  renderInspector(nodeId);

  document.querySelectorAll(".req-item").forEach(card => {
    if (card.dataset.id === nodeId) {
      card.classList.add("active");
      card.scrollIntoView({ behavior: "smooth", block: "nearest" });
    } else {
      card.classList.remove("active");
    }
  });
}

function renderInspector(nodeId) {
  const content = document.getElementById("inspectorContent");
  const title = document.getElementById("inspectorTitle");
  const badge = document.getElementById("inspectorBadge");

  if (!nodeId) {
    title.textContent = "Инспектор вывода";
    badge.textContent = "Обзор";
    content.innerHTML = `<p class="empty-state-text">Кликните на требование (колонку Y) или концепт (Z), чтобы увидеть полный путь логического вывода и веса связей.</p>`;
    return;
  }

  const node = renderNodes.find(n => n.id === nodeId);
  if (!node) return;

  title.textContent = `${node.id}: ${node.label}`;
  badge.textContent = `Активация: ${(node.activation * 100).toFixed(0)}%`;

  const incoming = renderLinks.filter(l => l.target.id === nodeId);
  const outgoing = renderLinks.filter(l => l.source.id === nodeId);

  let html = `
    <div style="margin-bottom: 12px; font-size: 0.8rem; color: #94a3b8;">
      Уровень: <strong style="color: #f1f5f9;">${node.layer.toUpperCase()}</strong> | 
      Активация сигмоиды: <strong style="color: #34d399;">${node.activation.toFixed(3)}</strong>
    </div>
  `;

  if (node.description) {
    html += `<div style="margin-bottom: 12px; font-size: 0.78rem; background: rgba(0,0,0,0.3); padding: 8px; border-radius: 4px;">${node.description}</div>`;
  }

  if (incoming.length > 0) {
    html += `<h4 style="font-size: 0.8rem; margin: 10px 0 6px 0; color: #38bdf8;">Входящие влияния (Кто активировал):</h4>`;
    incoming.forEach(l => {
      const sign = l.contribution > 0 ? "+" : "";
      const color = l.contribution > 0 ? "#34d399" : "#f43f5e";
      html += `
        <div style="display: flex; justify-content: space-between; font-size: 0.76rem; font-family: monospace; padding: 3px 0;">
          <span>← ${l.source.label}</span>
          <span style="color: ${color}; font-weight: 700;">вклад: ${sign}${l.contribution.toFixed(2)} (w=${l.weight})</span>
        </div>
      `;
    });
  }

  if (outgoing.length > 0) {
    html += `<h4 style="font-size: 0.8rem; margin: 12px 0 6px 0; color: #c084fc;">Исходящее влияние (На что повлиял):</h4>`;
    outgoing.forEach(l => {
      const sign = l.contribution > 0 ? "+" : "";
      const color = l.contribution > 0 ? "#34d399" : "#f43f5e";
      html += `
        <div style="display: flex; justify-content: space-between; font-size: 0.76rem; font-family: monospace; padding: 3px 0;">
          <span>→ ${l.target.label}</span>
          <span style="color: ${color}; font-weight: 700;">вклад: ${sign}${l.contribution.toFixed(2)}</span>
        </div>
      `;
    });
  }

  content.innerHTML = html;
}

function renderRequirementsList(requirements) {
  const container = document.getElementById("requirementsList");
  document.getElementById("reqCount").textContent = requirements.length;

  if (!requirements || requirements.length === 0) {
    container.innerHTML = `<div class="empty-state-text">Требования не сформированы</div>`;
    return;
  }

  let html = "";
  requirements.forEach(r => {
    let paramsHtml = "";
    if (r.parameters && Object.keys(r.parameters).length > 0) {
      paramsHtml = `<div class="req-params">`;
      for (const [k, v] of Object.entries(r.parameters)) {
        paramsHtml += `<div><strong>${k}:</strong> ${Array.isArray(v) ? v.join(", ") : v}</div>`;
      }
      paramsHtml += `</div>`;
    }

    html += `
      <div class="req-item" data-id="${r.id}" onclick="setFocusedNode('${r.id}')">
        <div class="req-header">
          <span class="req-id-badge">[${r.id}] ${r.area}</span>
          <span class="req-prob-badge">${(r.probability * 100).toFixed(0)}%</span>
        </div>
        <div class="req-title">${r.name}</div>
        <div class="req-rationale">💡 ${r.rationale}</div>
        ${paramsHtml}
      </div>
    `;
  });

  container.innerHTML = html;
}

// СИМУЛЯТОР WHAT-IF: Надежная отправка с парсингом любых чисел и мгновенным обновлением
async function runSandboxSimulation() {
  const lengthVal = Math.max(0.1, safeNum(document.getElementById("sbLength").value, 6.2));
  const widthVal = Math.max(0.1, safeNum(document.getElementById("sbWidth").value, 3.4));
  const heightVal = Math.max(0.1, safeNum(document.getElementById("sbHeight").value, 2.9));
  const weightVal = Math.max(10, safeNum(document.getElementById("sbWeight").value, 24000));
  const costVal = Math.max(0, safeNum(document.getElementById("sbCost").value, 180000));

  const payload = {
    request_id: `SIM-${Date.now().toString().slice(-4)}`,
    incoterms: "FCA",
    origin: { country: "Германия", city: "Кёльн" },
    destination: { country: "Казахстан", city: "Атырау" },
    cargo: {
      name: document.getElementById("sbName").value || "Груз",
      dimensions: {
        length_m: lengthVal,
        width_m: widthVal,
        height_m: heightVal,
        weight_kg: weightVal,
        places_count: 1,
        stackable: document.getElementById("sbStackable").checked,
        heavy_single_place: weightVal >= 1500
      },
      danger: {
        imo: document.getElementById("sbDanger").checked ? "3" : null,
        un: document.getElementById("sbDanger").checked ? "1203" : null,
        vet: document.getElementById("sbControl").checked,
        skk: document.getElementById("sbControl").checked,
        kfk: document.getElementById("sbControl").checked
      },
      cost: {
        value: costVal,
        currency: "USD"
      }
    },
    primary_transport: "автомобильный",
    notes: {
      request_notes: document.getElementById("sbNotes").value || ""
    }
  };

  try {
    const res = await fetch(`${API_BASE}/v1/requirements/infer`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      alert(`Ошибка сервера (${res.status}): ${JSON.stringify(err.detail || err)}`);
      return;
    }

    const data = await res.json();
    currentRequirements = data.requirements;
    
    // 1. Обновляем правую колонку требований
    renderRequirementsList(currentRequirements);
    
    // 2. Обновляем селектор трассировок
    await fetchTraceList();
    
    // 3. Загружаем и применяем новый граф
    await fetchTraceById(data.trace_id);
    
    // 4. Сбрасываем фокус для обзора всей сети
    setFocusedNode(null);

  } catch (err) {
    alert("Ошибка соединения с API LRE-Core: " + err.message);
  }
}

function fillSampleSandboxData() {
  document.getElementById("sbName").value = "Газотурбинная установка в сборе";
  document.getElementById("sbWidth").value = "3.6";
  document.getElementById("sbHeight").value = "3.2";
  document.getElementById("sbLength").value = "9.5";
  document.getElementById("sbWeight").value = "32000";
  document.getElementById("sbCost").value = "450000";
  document.getElementById("sbStackable").checked = false;
  document.getElementById("sbDanger").checked = false;
  document.getElementById("sbControl").checked = false;
  document.getElementById("sbNotes").value = "Не кантовать! Боится осадков. Погрузка спаренными кранами через верх. Прямой рейс без перегрузки.";
}

function loadDefaultDemoState() {
  const demoTrace = {
    trace_id: "demo-live-trace",
    request_id: "DEMO-PROJECT-01",
    input_signals: {
      x_dim_width: 1.7,
      x_dim_height: 1.4,
      x_weight_single: 1.6,
      x_weight_heavy_flag: 1.0,
      x_text_no_tilt: 1.0,
      x_text_crane_top: 1.0,
      x_text_moisture_protect: 1.0,
      x_text_direct_only: 1.0,
      x_high_cost: 1.8
    },
    concept_activations: {
      Z_OVERSIZE_WIDTH: 0.96,
      Z_OVERSIZE_HEIGHT: 0.91,
      Z_HEAVY_AXLE_LOAD: 0.94,
      Z_DYNAMIC_INSTABILITY: 0.88,
      Z_FRAGILITY_SENSITIVITY: 0.97,
      Z_WEATHER_CORROSION_RISK: 0.95,
      Z_CARGO_HIGH_VALUE_RISK: 0.92,
      Z_TRANSSHIPMENT_PROHIBITED: 0.98,
      Z_CRANE_RIGGING_COMPLEXITY: 0.95,
      Z_HAZARDOUS_COMPLIANCE: 0.05,
      Z_CUSTOMS_BORDER_FRICTION: 0.12
    },
    requirement_activations: {
      "TR-03": 0.99,
      "MR-03": 0.99,
      "PG-03": 0.98,
      "KR-01": 0.96,
      "TR-07": 0.97,
      "DC-03": 0.91,
      "MR-02": 0.89,
      "TR-06": 0.85,
      "ST-01": 0.93
    },
    active_links: [
      { source_id: "x_dim_width", target_id: "Z_OVERSIZE_WIDTH", weight: 4.0, contribution: 3.8 },
      { source_id: "x_dim_height", target_id: "Z_OVERSIZE_HEIGHT", weight: 4.0, contribution: 3.6 },
      { source_id: "x_weight_single", target_id: "Z_HEAVY_AXLE_LOAD", weight: 3.0, contribution: 2.8 },
      { source_id: "x_weight_single", target_id: "Z_CRANE_RIGGING_COMPLEXITY", weight: 3.0, contribution: 2.8 },
      { source_id: "x_text_no_tilt", target_id: "Z_FRAGILITY_SENSITIVITY", weight: 4.5, contribution: 4.3 },
      { source_id: "x_text_direct_only", target_id: "Z_TRANSSHIPMENT_PROHIBITED", weight: 4.5, contribution: 4.3 },
      { source_id: "x_text_moisture_protect", target_id: "Z_WEATHER_CORROSION_RISK", weight: 4.5, contribution: 4.3 },
      { source_id: "Z_OVERSIZE_WIDTH", target_id: "TR-03", weight: 3.5, contribution: 3.36 },
      { source_id: "Z_OVERSIZE_WIDTH", target_id: "MR-03", weight: 4.0, contribution: 3.84 },
      { source_id: "Z_OVERSIZE_HEIGHT", target_id: "TR-03", weight: 3.5, contribution: 3.18 },
      { source_id: "Z_HEAVY_AXLE_LOAD", target_id: "KR-01", weight: 3.5, contribution: 3.29 },
      { source_id: "Z_CRANE_RIGGING_COMPLEXITY", target_id: "PG-03", weight: 4.5, contribution: 4.27 },
      { source_id: "Z_FRAGILITY_SENSITIVITY", target_id: "TR-07", weight: 2.5, contribution: 2.42 },
      { source_id: "Z_TRANSSHIPMENT_PROHIBITED", target_id: "TR-07", weight: 4.5, contribution: 4.41 },
      { source_id: "Z_DYNAMIC_INSTABILITY", target_id: "DC-03", weight: 4.0, contribution: 3.52 },
      { source_id: "Z_CARGO_HIGH_VALUE_RISK", target_id: "ST-01", weight: 4.0, contribution: 3.68 }
    ]
  };
  applyTrace(demoTrace);
}
