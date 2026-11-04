"use strict";
// SQL-Quest – Oberfläche. Spricht mit web.py über /api/<name> (POST, JSON).

const $ = (sel) => document.querySelector(sel);
const S = {
  uebersicht: null,
  aufgabe: null,
  id: null,
  hinweise: 0,
  loesungGesehen: false,
  quizVersuch: 0,
  schemaCache: {},
};
const SPEICHER = "sqlquest.";

function speicher(key, wert) {
  try {
    if (wert === undefined) return localStorage.getItem(SPEICHER + key);
    localStorage.setItem(SPEICHER + key, wert);
  } catch (e) { return null; }
}

async function api(name, daten = {}) {
  const r = await fetch("/api/" + name, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(daten),
  });
  const json = await r.json();
  if (!r.ok) throw new Error(json.fehler || "Serverfehler");
  return json;
}

// ---------------------------------------------------------------------------
// Text-Helfer
// ---------------------------------------------------------------------------
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const inline = (s) => esc(s).replace(/`([^`]+)`/g, "<code>$1</code>");

const KEYWORDS = new Set(("select from where and or not in is null like between as order by group having limit offset " +
  "insert into values update set delete create table drop alter add column rename to primary key foreign references " +
  "unique check default auto_increment autoincrement index on join inner left right full outer cross union all " +
  "intersect except distinct case when then else end exists with recursive view begin commit rollback transaction start " +
  "asc desc if constraint cascade restrict action no truncate explain query plan show tables describe use database " +
  "savepoint release over partition true false using natural grant revoke separator").split(" "));
const TYPEN = new Set("int integer bigint smallint tinyint decimal numeric float double real varchar char text date datetime time timestamp boolean bool enum".split(" "));
const TOKEN = /(--[^\n]*|#[^\n]*|\/\*[\s\S]*?(?:\*\/|$))|('(?:[^']|'')*'?)|("(?:[^"]|"")*"?|`[^`\n]*`?)|(\b\d+(?:\.\d+)?\b)|([A-Za-z_ÄÖÜäöüß][A-Za-z0-9_ÄÖÜäöüß]*)(?=(\s*\())?/g;

function highlight(code) {
  let out = "", letzte = 0, m;
  TOKEN.lastIndex = 0;
  while ((m = TOKEN.exec(code))) {
    out += esc(code.slice(letzte, m.index));
    const [t] = m;
    let klasse = null;
    if (m[1]) klasse = "kom";
    else if (m[2]) klasse = "str";
    else if (m[3]) klasse = null;
    else if (m[4]) klasse = "num";
    else if (m[5]) {
      const w = t.toLowerCase();
      if (TYPEN.has(w)) klasse = "typ";
      else if (KEYWORDS.has(w)) klasse = "kw";
      else if (m[6]) klasse = "fn";
    }
    out += klasse ? `<span class="hl-${klasse}">${esc(t)}</span>` : esc(t);
    letzte = m.index + t.length;
    if (t.length === 0) TOKEN.lastIndex++;
  }
  return out + esc(code.slice(letzte));
}

// Theorie-Markup (gleiche Regeln wie im Terminal): # Überschrift, 4 Leerzeichen = Code,
// ! MySQL-Hinweis, ? Tipp, * Aufzählung, --- Trenner
function markup(text) {
  const zeilen = text.split("\n");
  let html = "", absatz = [], liste = null, i = 0;
  const flush = () => {
    if (absatz.length) { html += "<p>" + absatz.map(inline).join(" ") + "</p>"; absatz = []; }
    if (liste) { html += "<ul>" + liste.map((x) => "<li>" + inline(x) + "</li>").join("") + "</ul>"; liste = null; }
  };
  const block = (prefix, klasse) => {
    const teile = [];
    while (i < zeilen.length && zeilen[i].startsWith(prefix)) teile.push(inline(zeilen[i++].slice(2)));
    html += `<div class="${klasse}">${teile.join("<br>")}</div>`;
  };
  while (i < zeilen.length) {
    const z = zeilen[i];
    if (/^\s*---\s*$/.test(z)) { flush(); html += "<hr>"; i++; }
    else if (z.startsWith("    ")) {
      flush();
      const code = [];
      while (i < zeilen.length && (zeilen[i].startsWith("    ") ||
             (zeilen[i].trim() === "" && (zeilen[i + 1] || "").startsWith("    ")))) code.push(zeilen[i++].slice(4));
      html += `<pre class="code">${highlight(code.join("\n"))}</pre>`;
    }
    else if (z.startsWith("# ")) { flush(); html += `<h3>${inline(z.slice(2))}</h3>`; i++; }
    else if (z.startsWith("! ")) { flush(); block("! ", "mysql"); }
    else if (z.startsWith("? ")) { flush(); block("? ", "tipp"); }
    else if (z.startsWith("* ")) {
      if (absatz.length) { html += "<p>" + absatz.map(inline).join(" ") + "</p>"; absatz = []; }
      (liste = liste || []).push(z.slice(2)); i++;
    }
    else if (z.trim() === "") { flush(); i++; }
    else if (liste && z.startsWith("  ")) { liste[liste.length - 1] += " " + z.trim(); i++; }
    else { if (liste) flush(); absatz.push(z); i++; }
  }
  flush();
  return html;
}

// ---------------------------------------------------------------------------
// Editor
// ---------------------------------------------------------------------------
const code = $("#code");
const hl = $("#hervorhebung");
const nummern = $("#zeilennummern");

function editorAktualisieren() {
  hl.innerHTML = highlight(code.value) + "\n ";
  const n = code.value.split("\n").length;
  nummern.textContent = Array.from({ length: n }, (_, i) => i + 1).join("\n");
  scrollSync();
}
function scrollSync() {
  hl.parentElement.scrollTop = code.scrollTop;
  hl.parentElement.scrollLeft = code.scrollLeft;
  nummern.scrollTop = code.scrollTop;
}
function setCode(text) { code.value = text || ""; editorAktualisieren(); }

function einfuegen(text) {
  code.focus();
  if (!document.execCommand("insertText", false, text)) {
    code.setRangeText(text, code.selectionStart, code.selectionEnd, "end");
  }
  editorAktualisieren();
}

code.addEventListener("input", () => { editorAktualisieren(); speicher("entwurf." + S.id, code.value); });
code.addEventListener("scroll", scrollSync);
code.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
    e.preventDefault();
    e.shiftKey ? abgeben() : ausfuehrenKlick();
    return;
  }
  if (e.key === "Tab") {
    e.preventDefault();
    if (e.shiftKey) {
      const anfang = code.value.lastIndexOf("\n", code.selectionStart - 1) + 1;
      const weg = (code.value.slice(anfang).match(/^ {1,4}/) || [""])[0].length;
      if (weg) { code.setSelectionRange(anfang, anfang + weg); einfuegen(""); }
    } else einfuegen("    ");
    return;
  }
  if (e.key === "Enter" && !e.shiftKey) {
    const anfang = code.value.lastIndexOf("\n", code.selectionStart - 1) + 1;
    const einzug = code.value.slice(anfang).match(/^[ \t]*/)[0];
    e.preventDefault();
    einfuegen("\n" + einzug);
    return;
  }
  if (e.key === "/" && (e.ctrlKey || e.metaKey)) {
    e.preventDefault();
    const v = code.value;
    const a = v.lastIndexOf("\n", code.selectionStart - 1) + 1;
    let b = v.indexOf("\n", code.selectionEnd);
    if (b < 0) b = v.length;
    const zeilen = v.slice(a, b).split("\n");
    const alleKommentiert = zeilen.every((z) => /^\s*--/.test(z) || !z.trim());
    const neu = zeilen.map((z) => alleKommentiert ? z.replace(/^(\s*)-- ?/, "$1") : (z.trim() ? "-- " + z : z)).join("\n");
    code.setSelectionRange(a, b);
    einfuegen(neu);
    code.setSelectionRange(a, a + neu.length);
  }
});

// ---------------------------------------------------------------------------
// Ausgabe
// ---------------------------------------------------------------------------
function tabelleHtml(erg) {
  if (!erg.spalten) return "";
  let h = '<table class="ergebnis"><thead><tr>' + erg.spalten.map((s) => `<th>${esc(s)}</th>`).join("") + "</tr></thead><tbody>";
  for (const z of erg.zeilen) {
    h += "<tr>" + z.map((v) => {
      if (v === null) return '<td class="null">NULL</td>';
      if (typeof v === "number") return `<td class="zahl">${esc(Number.isInteger(v) ? v : Math.round(v * 10000) / 10000)}</td>`;
      return `<td title="${esc(v)}">${esc(v)}</td>`;
    }).join("") + "</tr>";
  }
  h += "</tbody></table>";
  const mehr = erg.anzahl > erg.zeilen.length ? ` – die ersten ${erg.zeilen.length} werden angezeigt` : "";
  return h + `<div class="zeilen-info">${erg.anzahl} Zeile(n)${mehr}</div>`;
}

function ergebnisHtml(erg) {
  let h = erg.meldungen.map((m) => `<div class="meldung">${esc(m)}</div>`).join("");
  h += tabelleHtml(erg);
  if (erg.fehler) {
    h += `<div class="fehler"><b>Fehler:</b> ${esc(erg.fehler)}` +
      (erg.roh_fehler ? `<span class="orig">Original: ${esc(erg.roh_fehler)}</span>` : "") + "</div>";
  }
  if (!h) h = '<p class="leer">Ausgeführt – keine Tabelle zurückgegeben.</p>';
  return h;
}

function ausgabeReiter(name) {
  document.querySelectorAll("#reiter-ausgabe button").forEach((b) => b.classList.toggle("aktiv", b.dataset.ausgabe === name));
  ["ergebnis", "erwartet", "loesung"].forEach((n) => $("#ausgabe-" + n).classList.toggle("versteckt", n !== name));
}
function zeigeAusgabe(html, reiter = "ergebnis") {
  $("#ausgabe-" + reiter).innerHTML = html;
  ausgabeReiter(reiter);
}
function fehlerAnzeigen(e) { zeigeAusgabe(`<div class="fehler"><b>Fehler:</b> ${esc(e.message)}</div>`); }

function toast(text) {
  const t = $("#toast");
  t.textContent = text;
  t.classList.remove("versteckt");
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => t.classList.add("versteckt"), 2800);
}

// ---------------------------------------------------------------------------
// Linke Seite
// ---------------------------------------------------------------------------
function linksReiter(name) {
  document.querySelectorAll("#reiter-links button").forEach((b) => b.classList.toggle("aktiv", b.dataset.reiter === name));
  ["aufgabe", "theorie", "tabellen"].forEach((n) => $("#inhalt-" + n).classList.toggle("versteckt", n !== name));
  if (name === "tabellen") ladeTabellen();
}

const TYP_TEXT = { abfrage: "Abfrage – das Ergebnis wird verglichen", aendern: "Datenbank ändern – der Zustand wird geprüft", quiz: "Quiz" };

function zeichneAufgabe(a) {
  const kopf = a.ist_boss
    ? `<h1 class="titel boss">☠ Bosskampf: ${esc(a.lektion_titel)}</h1>`
    : `<h1 class="titel">Aufgabe ${a.nr} von ${a.anzahl}</h1>`;
  $("#inhalt-aufgabe").innerHTML = `
    <div class="brotkrumen">Kapitel ${a.kapitel_nr} · ${esc(a.kapitel_titel)}${a.ist_boss ? "" : " › " + esc(a.lektion_titel)}</div>
    ${kopf}
    <div class="abzeichen">
      <span class="abz xp">+${a.xp_basis} XP</span>
      <span class="abz">${TYP_TEXT[a.typ]}</span>
      ${a.erledigt ? `<span class="abz ok">✔ gelöst (${a.xp_erhalten} XP)</span>` : ""}
    </div>
    <div class="aufgabentext">${inline(a.text)}</div>
    <div id="hinweise"></div>
    <div class="theorie-link"><button class="knopf leise" id="btn-zur-theorie">📖 Theorie ${a.ist_boss ? "(Story)" : "zur Lektion"} lesen</button></div>`;
  $("#btn-zur-theorie").onclick = () => linksReiter("theorie");
  $("#inhalt-theorie").innerHTML = `<div class="theorie">${markup(a.theorie)}</div>
    <p><button class="knopf gruen" id="btn-zur-aufgabe">Zur Aufgabe →</button></p>`;
  $("#btn-zur-aufgabe").onclick = () => linksReiter("aufgabe");
}

async function ladeTabellen() {
  const ziel = $("#inhalt-tabellen");
  if (!S.schemaCache[S.id]) {
    ziel.innerHTML = '<p class="leer">Lade …</p>';
    try { S.schemaCache[S.id] = (await api("schema", { id: S.id })).tabellen; }
    catch (e) { ziel.innerHTML = `<div class="fehler">${esc(e.message)}</div>`; return; }
  }
  ziel.innerHTML = '<p class="leer">So sieht die Datenbank für diese Aufgabe aus (vor deinem SQL). Klick auf einen Namen fügt ihn in den Editor ein.</p>' +
    S.schemaCache[S.id].map((t) => `
      <details class="tab-karte">
        <summary><span class="name-einfuegen" data-text="${esc(t.name)}">${esc(t.name)}</span><span class="art">${t.art === "view" ? "VIEW" : t.spalten.length + " Spalten"}</span></summary>
        <div class="spalten">${t.spalten.map((s) => `
          <div class="spalte"><span class="name" data-text="${esc(s.name)}">${esc(s.name)}</span>
          <span class="typ">${esc(s.typ || "")}</span>
          ${s.pk ? '<span class="pk">🔑 PK</span>' : ""}${s.notnull && !s.pk ? '<span class="typ">NOT NULL</span>' : ""}
          ${s.fk ? `<span class="fk">→ ${esc(s.fk)}</span>` : ""}</div>`).join("")}
        </div>
        <button class="knopf leise" data-vorschau="${esc(t.name)}">Erste 10 Zeilen zeigen</button>
      </details>`).join("");
}

$("#inhalt-tabellen").addEventListener("click", async (e) => {
  const name = e.target.closest("[data-text]");
  if (name && name.classList.contains("name")) { einfuegen(name.dataset.text); return; }
  const v = e.target.closest("[data-vorschau]");
  if (v) {
    try {
      const r = await api("vorschau", { id: S.id, tabelle: v.dataset.vorschau });
      zeigeAusgabe(`<div class="kontrolle-titel">SELECT * FROM ${esc(v.dataset.vorschau)} LIMIT 10;</div>` + ergebnisHtml(r.ergebnis));
    } catch (err) { fehlerAnzeigen(err); }
  }
});

// ---------------------------------------------------------------------------
// Kopfzeile, Auswahl, Karte
// ---------------------------------------------------------------------------
async function ladeUebersicht() {
  S.uebersicht = await api("uebersicht");
  const u = S.uebersicht;
  $("#rang-name").textContent = u.rang;
  $("#rang-xp").textContent = u.naechster ? `${u.xp} / ${u.naechster.xp} XP` : `${u.xp} XP`;
  $("#xp-fuellung").style.width = (u.naechster ? Math.min(100, (u.xp / u.naechster.xp) * 100) : 100) + "%";
  fuelleAuswahl();
}

function kapitelVon(id) { return S.uebersicht.kapitel.find((k) => String(k.nr) === id.split(".")[0]); }

function fuelleAuswahl() {
  const wk = $("#wahl-kapitel");
  wk.innerHTML = S.uebersicht.kapitel.map((k) =>
    `<option value="${k.nr}">${k.fertig === k.gesamt ? "✔ " : ""}Kap. ${k.nr}: ${esc(k.titel)} (${k.fertig}/${k.gesamt})</option>`).join("");
  if (S.id === "sandbox") {
    wk.insertAdjacentHTML("afterbegin", '<option value="sandbox">🧪 Sandbox</option>');
    wk.value = "sandbox";
    $("#wahl-aufgabe").classList.add("versteckt");
    return;
  }
  $("#wahl-aufgabe").classList.remove("versteckt");
  const k = kapitelVon(S.id);
  wk.value = k.nr;
  let h = "";
  k.lektionen.forEach((l, li) => {
    h += `<optgroup label="${li + 1}. ${esc(l.titel)}">` + l.aufgaben.map((a, ai) =>
      `<option value="${a.id}">${a.erledigt ? "✔" : "○"} Aufgabe ${ai + 1}${a.typ === "quiz" ? " (Quiz)" : ""}</option>`).join("") + "</optgroup>";
  });
  if (k.boss) h += `<optgroup label="Bosskampf"><option value="${k.boss.id}">${k.boss.erledigt ? "✔" : "☠"} ${esc(k.boss.titel)}</option></optgroup>`;
  $("#wahl-aufgabe").innerHTML = h;
  $("#wahl-aufgabe").value = S.id;
}

function ersteOffene(ids) { return ids.find((id) => !istErledigt(id)) || ids[0]; }
function istErledigt(id) {
  for (const k of S.uebersicht.kapitel) {
    if (k.boss && k.boss.id === id) return k.boss.erledigt;
    for (const l of k.lektionen) for (const a of l.aufgaben) if (a.id === id) return a.erledigt;
  }
  return false;
}
function kapitelIds(k) { return k.lektionen.flatMap((l) => l.aufgaben.map((a) => a.id)).concat(k.boss ? [k.boss.id] : []); }

$("#wahl-kapitel").onchange = (e) => {
  const k = S.uebersicht.kapitel.find((k) => String(k.nr) === e.target.value);
  if (k) oeffne(ersteOffene(kapitelIds(k)));
};
$("#wahl-aufgabe").onchange = (e) => oeffne(e.target.value);
$("#btn-zurueck").onclick = () => S.aufgabe && S.aufgabe.vorher && oeffne(S.aufgabe.vorher);
$("#btn-weiter").onclick = () => S.aufgabe && S.aufgabe.nachher && oeffne(S.aufgabe.nachher);

function zeichneKarte() {
  $("#karte-inhalt").innerHTML = S.uebersicht.kapitel.map((k) => {
    const lek = k.lektionen.map((l) => {
      const ids = l.aufgaben.map((a) => a.id);
      return `<div class="lek"><a data-gehe="${ersteOffene(ids)}">${esc(l.titel)}</a>
        <span class="punkte">${l.aufgaben.map((a) => `<span class="punkt ${a.erledigt ? "ok" : ""}"></span>`).join("")}</span></div>`;
    }).join("");
    const boss = k.boss ? `<div class="lek boss"><a data-gehe="${k.boss.id}">☠ ${esc(k.boss.titel)}</a>
        <span class="punkte"><span class="punkt ${k.boss.erledigt ? "ok" : ""}"></span></span></div>` : "";
    return `<div class="kap"><h3>${k.nr}. ${esc(k.titel)}<span>${k.fertig}/${k.gesamt}</span></h3>
      <div class="balken"><div style="width:${(k.fertig / k.gesamt) * 100}%"></div></div>${lek}${boss}</div>`;
  }).join("");
}
$("#btn-karte").onclick = () => { zeichneKarte(); $("#karte").classList.remove("versteckt"); };
$("#btn-karte-zu").onclick = () => $("#karte").classList.add("versteckt");
$("#karte").onclick = (e) => {
  if (e.target.id === "karte") $("#karte").classList.add("versteckt");
  const ziel = e.target.closest("[data-gehe]");
  if (ziel) { $("#karte").classList.add("versteckt"); oeffne(ziel.dataset.gehe); }
};
$("#btn-reset").onclick = async () => {
  if (!confirm("Wirklich den GESAMTEN Fortschritt löschen? (Gilt auch für die Terminal-Version)")) return;
  await api("reset");
  await ladeUebersicht();
  zeichneKarte();
  toast("Fortschritt zurückgesetzt.");
};
document.addEventListener("keydown", (e) => { if (e.key === "Escape") $("#karte").classList.add("versteckt"); });

// ---------------------------------------------------------------------------
// Aufgabe öffnen
// ---------------------------------------------------------------------------
function knoepfeFuer(modus) {
  const sichtbar = {
    sql: ["abgeben", "ausfuehren", "hinweis", "erwartet", "loesung", "leeren"],
    quiz: [],
    sandbox: ["ausfuehren", "sandbox-reset", "leeren"],
  }[modus];
  ["abgeben", "ausfuehren", "hinweis", "erwartet", "loesung", "sandbox-reset", "leeren"].forEach((n) =>
    $("#btn-" + n).classList.toggle("versteckt", !sichtbar.includes(n)));
  $("#editor").classList.toggle("versteckt", modus === "quiz");
  $("#quiz").classList.toggle("versteckt", modus !== "quiz");
  $("#werkzeuge").classList.toggle("versteckt", modus === "quiz");
  document.querySelectorAll('#reiter-ausgabe [data-ausgabe="erwartet"], #reiter-ausgabe [data-ausgabe="loesung"]')
    .forEach((b) => b.classList.toggle("versteckt", modus !== "sql"));
}

function hinweisKnopf() {
  const a = S.aufgabe;
  const b = $("#btn-hinweis");
  b.textContent = a.hinweise ? `💡 Hinweis (${S.hinweise}/${a.hinweise})` : "💡 Hinweis";
  b.disabled = !a.hinweise || S.hinweise >= a.hinweise;
}

async function oeffne(id) {
  $("#karte").classList.add("versteckt");
  if (id === "sandbox") return oeffneSandbox();
  let a;
  try { a = await api("aufgabe", { id }); }
  catch (e) { return oeffne(S.uebersicht.kapitel[0].lektionen[0].aufgaben[0].id); }
  S.aufgabe = a; S.id = id; S.hinweise = 0; S.loesungGesehen = false; S.quizVersuch = 0;
  if (location.hash !== "#" + id) history.replaceState(null, "", "#" + id);
  speicher("letzte", id);
  zeichneAufgabe(a);
  fuelleAuswahl();
  $("#btn-zurueck").disabled = !a.vorher;
  $("#btn-weiter").disabled = !a.nachher;
  $("#dateiname").textContent = a.typ === "quiz" ? "Quiz" : `aufgabe_${id.replace(/\./g, "_")}.sql`;
  $(".tastenhilfe").classList.toggle("versteckt", a.typ === "quiz");
  $("#ausgabe-erwartet").innerHTML = '<p class="leer">Klick auf 🎯 Erwartet, um zu sehen, was herauskommen soll.</p>';
  $("#ausgabe-loesung").innerHTML = '<p class="leer">Die Musterlösung gibt es über 👁 Lösung (dann nur noch 2 XP).</p>';
  zeigeAusgabe('<p class="leer">Noch nichts ausgeführt. Tipp: Strg+Enter führt aus, Strg+Shift+Enter gibt ab.</p>');

  if (a.typ === "quiz") {
    knoepfeFuer("quiz");
    zeichneQuiz(a);
  } else {
    knoepfeFuer("sql");
    hinweisKnopf();
    setCode(speicher("entwurf." + id) || "");
  }
  const neueLektion = !a.erledigt && (a.nr === 1 || a.ist_boss);
  linksReiter(neueLektion ? "theorie" : "aufgabe");
  $("#inhalt-theorie").scrollTop = 0;
  $("#inhalt-aufgabe").scrollTop = 0;
  if (a.typ !== "quiz") code.focus();
}

function oeffneSandbox() {
  S.id = "sandbox"; S.aufgabe = null;
  history.replaceState(null, "", "#sandbox");
  speicher("letzte", "sandbox");
  fuelleAuswahl();
  $("#btn-zurueck").disabled = true;
  $("#btn-weiter").disabled = true;
  $("#dateiname").textContent = "sandbox.sql";
  $(".tastenhilfe").classList.remove("versteckt");
  $("#inhalt-aufgabe").innerHTML = `
    <div class="brotkrumen">Freies Üben</div>
    <h1 class="titel">🧪 Sandbox</h1>
    <div class="aufgabentext">Hier kannst du alles ausprobieren – SELECT, INSERT, CREATE TABLE, DROP …
Änderungen bleiben in der Datei <code>sandbox.db</code> gespeichert (dieselbe wie im Terminal-Menü S).
Kaputt gespielt? Klick auf <code>↺ Welt neu laden</code>.

Nützliche MySQL-Befehle, die hier funktionieren:
<code>SHOW TABLES;</code>   <code>DESCRIBE spieler;</code>   <code>SHOW INDEX FROM spieler;</code></div>
    <div class="theorie-link"><button class="knopf leise" id="btn-zu-tabellen">🗂 Tabellen ansehen</button></div>`;
  $("#btn-zu-tabellen").onclick = () => linksReiter("tabellen");
  $("#inhalt-theorie").innerHTML = '<p class="leer">In der Sandbox gibt es keine Theorie – wähle oben ein Kapitel, um weiterzulernen.</p>';
  knoepfeFuer("sandbox");
  setCode(speicher("entwurf.sandbox") || "SELECT * FROM spieler;");
  delete S.schemaCache.sandbox;
  zeigeAusgabe('<p class="leer">Strg+Enter führt aus.</p>');
  linksReiter("aufgabe");
  code.focus();
}
$("#btn-sandbox").onclick = () => oeffne("sandbox");
$("#btn-sandbox-reset").onclick = async () => {
  if (!confirm("Sandbox-Datenbank auf den Originalzustand zurücksetzen?")) return;
  await api("sandbox_reset");
  delete S.schemaCache.sandbox;
  toast("Spielwelt neu geladen.");
  if (!$("#inhalt-tabellen").classList.contains("versteckt")) ladeTabellen();
};

// ---------------------------------------------------------------------------
// Aktionen
// ---------------------------------------------------------------------------
async function ausfuehrenKlick() {
  if (!code.value.trim()) return toast("Erst SQL schreiben 🙂");
  try {
    const r = await api("ausfuehren", { id: S.id, sql: code.value });
    zeigeAusgabe(ergebnisHtml(r.ergebnis));
    if (S.id === "sandbox") {
      delete S.schemaCache.sandbox;
      if (!$("#inhalt-tabellen").classList.contains("versteckt")) ladeTabellen();
    }
  } catch (e) { fehlerAnzeigen(e); }
}

function erfolgHtml(r, erklaerung) {
  return `<div class="feedback ok"><span class="gross">✔ Richtig!  +${r.xp} XP</span>` +
    `Gesamt: ${r.gesamt_xp} XP · Rang: ${esc(r.rang)}` +
    (r.aufstieg ? `<div class="aufstieg">⚔ Aufstieg! Du bist jetzt: ${esc(r.rang)}</div>` : "") +
    (erklaerung ? `<div class="erklaerung">ℹ ${inline(erklaerung)}</div>` : "") +
    (S.aufgabe.nachher ? '<div><button class="knopf gruen" id="btn-naechste">Nächste Aufgabe →</button></div>' : "") +
    "</div>";
}

async function nachErfolg(r) {
  if (r.aufstieg) toast(`⚔ Aufstieg! Neuer Rang: ${r.rang}`);
  const abz = document.querySelector("#inhalt-aufgabe .abzeichen");
  if (abz && !S.aufgabe.erledigt) {
    S.aufgabe.erledigt = true;
    abz.insertAdjacentHTML("beforeend", `<span class="abz ok">✔ gelöst (${r.xp} XP)</span>`);
  }
  await ladeUebersicht();
  const b = $("#btn-naechste");
  if (b) { b.onclick = () => oeffne(S.aufgabe.nachher); b.focus(); }
}

async function abgeben() {
  if (S.id === "sandbox" || !S.aufgabe || S.aufgabe.typ === "quiz") return;
  if (!code.value.trim()) return toast("Erst SQL schreiben 🙂");
  try {
    const r = await api("abgeben", { id: S.id, sql: code.value, hinweise: S.hinweise, loesung_gesehen: S.loesungGesehen });
    if (r.ok) {
      zeigeAusgabe(erfolgHtml(r, r.erklaerung) + ergebnisHtml(r.ergebnis));
      await nachErfolg(r);
    } else {
      const tipp = S.hinweise < S.aufgabe.hinweise ? "\nTipp: 💡 Hinweis oder 🎯 Erwartet hilft weiter." : "\nTipp: 🎯 Erwartet zeigt, was herauskommen soll.";
      zeigeAusgabe(`<div class="feedback nein"><span class="gross">✘ Noch nicht richtig</span>${esc(r.meldung || "")}${esc(tipp)}</div>` +
        ergebnisHtml(r.ergebnis));
    }
  } catch (e) { fehlerAnzeigen(e); }
}

$("#btn-ausfuehren").onclick = ausfuehrenKlick;
$("#btn-abgeben").onclick = abgeben;
$("#btn-leeren").onclick = () => { if (code.value && confirm("Editor leeren?")) { setCode(""); speicher("entwurf." + S.id, ""); } };

$("#btn-hinweis").onclick = async () => {
  const a = S.aufgabe;
  if (S.hinweise >= a.hinweise) return;
  S.hinweise++;
  const r = await api("hinweis", { id: S.id, nr: S.hinweise });
  $("#hinweise").insertAdjacentHTML("beforeend",
    `<div class="hinweis-box"><b>💡 Hinweis ${S.hinweise}/${a.hinweise}:</b> ${inline(r.text)}</div>`);
  hinweisKnopf();
  linksReiter("aufgabe");
  toast("Jeder Hinweis kostet 3 XP.");
};

$("#btn-erwartet").onclick = async () => {
  try {
    const r = await api("erwartet", { id: S.id });
    let h = "";
    if (!r.teile.length) {
      h = '<p class="leer">Hier wird geprüft, ob sich deine Tabelle richtig verhält: Das Spiel schickt Test-INSERTs ' +
        "hinterher, die erlaubt oder abgelehnt werden müssen. Lies die Aufgabe genau – jede geforderte Regel wird getestet.</p>";
    } else {
      if (r.aendern) h += '<p class="leer">So soll die Datenbank nach deinem SQL aussehen (Kontrollabfragen):</p>';
      for (const t of r.teile) {
        if (r.aendern) h += `<div class="kontrolle-titel">${esc(t.titel)}</div>`;
        h += ergebnisHtml(t.ergebnis);
      }
    }
    zeigeAusgabe(h, "erwartet");
  } catch (e) { fehlerAnzeigen(e); }
};

$("#btn-loesung").onclick = async () => {
  if (!S.loesungGesehen && !confirm("Musterlösung anzeigen? Danach gibt es für diese Aufgabe nur noch 2 XP.")) return;
  S.loesungGesehen = true;
  const r = await api("loesung", { id: S.id });
  zeigeAusgabe(`<pre class="loesung">${highlight(r.loesung)}</pre>
    <button class="knopf" id="btn-uebernehmen">In den Editor übernehmen</button>
    <p class="leer">Tipp: Tipp sie lieber selbst ab – das bleibt besser hängen.</p>`, "loesung");
  $("#btn-uebernehmen").onclick = () => { setCode(r.loesung); speicher("entwurf." + S.id, r.loesung); code.focus(); };
};

// ---------------------------------------------------------------------------
// Quiz
// ---------------------------------------------------------------------------
function zeichneQuiz(a) {
  $("#quiz").innerHTML = "<h4>Wähle die richtige Antwort:</h4>" + a.optionen.map((o, i) =>
    `<button class="option" data-nr="${i + 1}"><span class="nr">${i + 1}</span><span>${inline(o)}</span></button>`).join("");
}

$("#quiz").addEventListener("click", async (e) => {
  const opt = e.target.closest(".option");
  if (!opt || opt.disabled) return;
  S.quizVersuch++;
  try {
    const r = await api("quiz", { id: S.id, antwort: opt.dataset.nr, versuch: S.quizVersuch });
    const alle = document.querySelectorAll("#quiz .option");
    if (r.ok) {
      opt.classList.add("richtig");
      alle.forEach((b) => (b.disabled = true));
      zeigeAusgabe(erfolgHtml(r, r.erklaerung));
      await nachErfolg(r);
      return;
    }
    opt.classList.add("falsch");
    opt.disabled = true;
    if (r.richtig) {
      alle.forEach((b) => { b.disabled = true; if (b.dataset.nr == r.richtig) b.classList.add("richtig"); });
      zeigeAusgabe(`<div class="feedback nein"><span class="gross">✘ Leider falsch</span>Richtig ist Antwort ${r.richtig}.` +
        (r.erklaerung ? `<div class="erklaerung">ℹ ${inline(r.erklaerung)}</div>` : "") +
        (S.aufgabe.nachher ? '<div><button class="knopf" id="btn-naechste">Weiter →</button></div>' : "") + "</div>");
      const b = $("#btn-naechste");
      if (b) b.onclick = () => oeffne(S.aufgabe.nachher);
    } else {
      zeigeAusgabe('<div class="feedback nein"><span class="gross">✘ Leider falsch</span>Versuch es nochmal!</div>');
    }
  } catch (err) { fehlerAnzeigen(err); }
});

// ---------------------------------------------------------------------------
// Reiter & Trenner
// ---------------------------------------------------------------------------
document.querySelectorAll("#reiter-links button").forEach((b) => (b.onclick = () => linksReiter(b.dataset.reiter)));
document.querySelectorAll("#reiter-ausgabe button").forEach((b) => (b.onclick = () => ausgabeReiter(b.dataset.ausgabe)));

function ziehbar(trenner, beimZiehen, key) {
  trenner.addEventListener("mousedown", (e) => {
    e.preventDefault();
    trenner.classList.add("zieht");
    document.body.style.userSelect = "none";
    const bewegen = (ev) => beimZiehen(ev);
    const los = () => {
      trenner.classList.remove("zieht");
      document.body.style.userSelect = "";
      document.removeEventListener("mousemove", bewegen);
      document.removeEventListener("mouseup", los);
      speicher(key, key === "breite" ? $("#links").style.width : $("#ausgabe-bereich").style.height);
    };
    document.addEventListener("mousemove", bewegen);
    document.addEventListener("mouseup", los);
  });
}
ziehbar($("#trenner-mitte"), (e) => {
  const max = window.innerWidth - 340;
  $("#links").style.width = Math.max(280, Math.min(max, e.clientX)) + "px";
}, "breite");
ziehbar($("#trenner-unten"), (e) => {
  const r = $("#rechts").getBoundingClientRect();
  $("#ausgabe-bereich").style.height = Math.max(80, Math.min(r.height - 160, r.bottom - e.clientY)) + "px";
}, "hoehe");

// ---------------------------------------------------------------------------
// Start
// ---------------------------------------------------------------------------
window.addEventListener("hashchange", () => {
  const id = decodeURIComponent(location.hash.slice(1));
  if (id && id !== S.id) oeffne(id);
});

(async function start() {
  if (speicher("breite")) $("#links").style.width = speicher("breite");
  if (speicher("hoehe")) $("#ausgabe-bereich").style.height = speicher("hoehe");
  try {
    S.id = "1.1.1";
    await ladeUebersicht();
  } catch (e) {
    document.body.innerHTML = `<p style="padding:30px">Der SQL-Quest-Server antwortet nicht. Starte ihn mit <code>python web.py</code>.</p>`;
    return;
  }
  const alle = S.uebersicht.kapitel.flatMap(kapitelIds);
  const ausHash = decodeURIComponent(location.hash.slice(1));
  const letzte = speicher("letzte");
  const ziel = ausHash || letzte || ersteOffene(alle);
  oeffne(ziel === "sandbox" || alle.includes(ziel) ? ziel : ersteOffene(alle));
})();
