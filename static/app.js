let profileId = "diabetes",
  profile = null,
  rows = [],
  attributes = [],
  targetName = "Kết quả",
  lastModel = null;
const $ = (id) => document.getElementById(id);
const esc = (s) =>
  String(s ?? "").replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
async function api(url, options = {}) {
  const r = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await r.json();
  if (!r.ok) throw new Error(data.error || "Có lỗi xảy ra");
  return data;
}
function rowToObject(row) {
  return Object.fromEntries([
    ...attributes.map((a, i) => [a.name, row[i]]),
    [targetName, row[5]],
  ]);
}
function showTab(name) {
  document
    .querySelectorAll(".tab")
    .forEach((b) => b.classList.toggle("active", b.dataset.tab === name));
  document
    .querySelectorAll(".tab-panel")
    .forEach((p) => p.classList.toggle("active", p.id === name));
}
document
  .querySelectorAll(".tab")
  .forEach((b) => b.addEventListener("click", () => showTab(b.dataset.tab)));
async function loadProfile(id) {
  profileId = id;
  profile = await api(`/api/profile/${id}`);
  attributes = profile.attributes.map((a) => ({ ...a, values: [...a.values] }));
  rows = profile.rows.map((r) => [...r]);
  targetName = profile.target || "Kết quả";
  $("profileDescription").textContent =
    profile.description + " Dữ liệu mẫu là dữ liệu mô phỏng.";
  renderAll();
  await trainAndPredict(false);
}
async function init() {
  const profiles = await api("/api/profiles");
  $("profileSelect").innerHTML = profiles
    .map((p) => `<option value="${p.id}">${esc(p.title)}</option>`)
    .join("");
  $("profileSelect").addEventListener("change", (e) =>
    loadProfile(e.target.value),
  );
  await loadProfile("diabetes");
}
function renderPredict() {
  $("predictFields").innerHTML = attributes
    .map(
      (a, i) =>
        `<div class="field"><label>${esc(a.name)}</label><select id="p${i}">${a.values.map((v) => `<option>${esc(v)}</option>`).join("")}</select></div>`,
    )
    .join("");
}
function renderTable() {
  const head =
    attributes.map((a) => `<th>${esc(a.name)}</th>`).join("") +
    `<th>${esc(targetName)}</th><th>Thao tác</th>`;
  $("dataTable").innerHTML =
    `<thead><tr>${head}</tr></thead><tbody>${rows.map((r, i) => `<tr>${attributes.map((a, j) => `<td><select data-row="${i}" data-col="${j}">${a.values.map((v) => `<option ${r[j] === v ? "selected" : ""}>${esc(v)}</option>`).join("")}</select></td>`).join("")}<td><input data-row="${i}" data-col="5" value="${esc(r[5])}"></td><td><button class="btn danger mini" data-delete="${i}">Xóa</button></td></tr>`).join("")}</tbody>`;
  $("dataTable")
    .querySelectorAll("[data-row]")
    .forEach((el) =>
      el.addEventListener("change", (e) => {
        const i = +e.target.dataset.row,
          j = +e.target.dataset.col;
        rows[i][j] = e.target.value;
      }),
    );
  $("dataTable")
    .querySelectorAll("[data-delete]")
    .forEach((el) =>
      el.addEventListener("click", () => {
        rows.splice(+el.dataset.delete, 1);
        renderTable();
      }),
    );
}
function renderAttributeEditor() {
  $("attributeEditor").innerHTML = attributes
    .map(
      (a, i) =>
        `<div class="attr-edit"><div class="field"><label>Tên thuộc tính ${i + 1}</label><input id="attrName${i}" value="${esc(a.name)}"></div><div class="field"><label>Các giá trị, cách nhau bằng dấu phẩy</label><input id="attrValues${i}" value="${esc(a.values.join(", "))}"></div></div>`,
    )
    .join("");
  $("targetName").value = targetName;
}
function renderAll() {
  renderPredict();
  renderTable();
  renderAttributeEditor();
}
function drawTree(node, prefix = "", edge = "") {
  if (node.type === "leaf")
    return `${prefix}${edge}→ ${node.label} (${node.samples} mẫu)\n`;
  let out = `${prefix}${edge}[${node.attribute}] Gain=${Number(node.gain).toFixed(4)}\n`;
  const entries = Object.entries(node.children);
  entries.forEach(([v, ch], i) => {
    const last = i === entries.length - 1;
    out += drawTree(ch, prefix + (last ? "   " : "│  "), `├─ ${v}: `);
  });
  return out;
}
async function trainAndPredict(showResult = true) {
  if (rows.length === 0) throw new Error("Chưa có dữ liệu huấn luyện.");
  const sample = Object.fromEntries(
    attributes.map((a, i) => [a.name, $(`p${i}`)?.value || a.values[0]]),
  );
  const data = await api("/api/train-predict", {
    method: "POST",
    body: JSON.stringify({
      attributes: attributes.map((a) => a.name),
      target: targetName,
      rows,
      sample,
    }),
  });
  lastModel = data;
  $("treeView").textContent = drawTree(data.tree);
  const gains = Object.entries(data.root_gains).sort((a, b) => b[1] - a[1]);
  $("gainView").innerHTML = gains
    .map(
      ([name, g], i) =>
        `<div class="gain-row"><b>${esc(name)} ${i === 0 ? "★" : ""}</b><span>${g.toFixed(6)}</span><div class="bar"><span style="width:${Math.max(0, (g / (gains[0]?.[1] || 1)) * 100)}%"></span></div></div>`,
    )
    .join("");
  $("entropyView").textContent =
    `Entropy(S) = ${data.entropy.toFixed(6)} bit • ${data.sample_count} mẫu • ${data.class_count} lớp.`;
  $("stats").innerHTML = [
    ["Mẫu huấn luyện", data.sample_count],
    ["Số lớp kết quả", data.class_count],
    ["Thuộc tính đầu vào", 5],
  ]
    .map(
      ([l, v]) =>
        `<div class="stat"><span>${l}</span><strong>${v}</strong></div>`,
    )
    .join("");
  if (showResult) {
    const path = data.path.length
      ? data.path.map((p) => `${p.attribute} = ${p.value}`).join(" → ")
      : "Nút gốc";
    $("result").classList.remove("hidden");
    $("result").innerHTML =
      `<h3>Kết quả phân lớp: ${esc(data.prediction)}</h3><p><b>Đường đi trong cây:</b> ${esc(path)}</p><p class="hint">Kết quả chỉ phản ánh dữ liệu huấn luyện mô phỏng, không phải chẩn đoán y khoa.</p>`;
  }
}
$("predictBtn").addEventListener("click", () =>
  trainAndPredict(true).catch((e) => alert(e.message)),
);
$("trainBtn").addEventListener("click", () =>
  trainAndPredict(false)
    .then(() => alert("Đã huấn luyện lại cây ID3."))
    .catch((e) => alert(e.message)),
);
$("clearResultBtn").addEventListener("click", () =>
  $("result").classList.add("hidden"),
);
$("addRowBtn").addEventListener("click", () => {
  rows.push([...attributes.map((a) => a.values[0]), "Chưa xác định"]);
  renderTable();
});
$("restoreBtn").addEventListener("click", () => {
  if (confirm("Khôi phục dữ liệu mẫu của bộ bệnh đang chọn?"))
    loadProfile(profileId);
});
$("saveAttributesBtn").addEventListener("click", () => {
  const next = attributes.map((a, i) => ({
    name: $(`attrName${i}`).value.trim(),
    values: $(`attrValues${i}`)
      .value.split(",")
      .map((v) => v.trim())
      .filter(Boolean),
  }));
  if (next.some((a) => !a.name || a.values.length < 2)) {
    alert("Mỗi thuộc tính cần tên và ít nhất 2 giá trị.");
    return;
  }
  const old = attributes;
  attributes = next;
  targetName = $("targetName").value.trim() || "Kết quả";
  const invalid = rows.filter((r) =>
    attributes.some((a, i) => !a.values.includes(r[i])),
  );
  if (invalid.length) {
    if (
      !confirm(
        `${invalid.length} mẫu không khớp cấu hình mới. Loại bỏ các mẫu đó?`,
      )
    ) {
      attributes = old;
      return;
    }
    rows = rows.filter((r) =>
      attributes.every((a, i) => a.values.includes(r[i])),
    );
  }
  renderAll();
  $("customMessage").textContent =
    "Đã lưu cấu hình. Hãy nhập dữ liệu huấn luyện phù hợp rồi huấn luyện lại.";
});
$("exportBtn").addEventListener("click", () => {
  const csv = [[...attributes.map((a) => a.name), targetName], ...rows]
    .map((r) => r.map((x) => `"${String(x).replace(/"/g, '""')}"`).join(","))
    .join("\r\n");
  const blob = new Blob(["\ufeff" + csv], { type: "text/csv;charset=utf-8" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "du-lieu-id3.csv";
  a.click();
  URL.revokeObjectURL(a.href);
});
$("csvFile").addEventListener("change", async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  try {
    const content = await file.text();
    const result = await api("/api/import-csv", {
      method: "POST",
      body: JSON.stringify({ content }),
    });
    attributes = result.header
      .slice(0, 5)
      .map((name, i) => ({
        name,
        values: [...new Set(result.rows.map((r) => r[i]))],
      }));
    targetName = result.header[5];
    rows = result.rows;
    renderAll();
    await trainAndPredict(false);
    showTab("dataset");
    alert(`Đã nhập ${rows.length} mẫu CSV.`);
  } catch (err) {
    alert(err.message);
  }
  e.target.value = "";
});
init().catch((e) => alert("Không thể khởi động ứng dụng: " + e.message));
