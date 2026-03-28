// background.js — PyWebFlx Chrome Extension Service Worker
//
// Responsibilities:
// 1. WebSocket client: connects to Python server at ws://localhost:PORT
// 2. Keep-alive: chrome.alarms prevent service worker from sleeping
// 3. Command dispatcher: receives JSON commands, injects scripts into tabs
// 4. Tab manager: finds tabs by title/URL, creates new tabs, reports events
//
// Protocol:
//   Command (from Python):  { id, action, tabId, params }
//   Response (to Python):   { id, success, data } or { id, success:false, error, message }
//   Event (to Python):      { event, tabId }

const DEFAULT_PORT = 9819;
const RECONNECT_DELAY_MS = 3000;
const KEEPALIVE_ALARM = "pywebflx-keepalive";
const KEEPALIVE_INTERVAL_MIN = 0.4; // ~25 seconds (minimum chrome.alarms allows)

let ws = null;
let port = DEFAULT_PORT;

// ---------------------------------------------------------------------------
// WebSocket connection
// ---------------------------------------------------------------------------

function connect() {
  if (ws && ws.readyState === WebSocket.OPEN) return;

  try {
    ws = new WebSocket(`ws://localhost:${port}`);
  } catch (e) {
    scheduleReconnect();
    return;
  }

  ws.onopen = () => {
    console.log("[PyWebFlx] Connected to Python server");
    startKeepalive();
  };

  ws.onmessage = (event) => {
    handleCommand(event.data);
  };

  ws.onclose = () => {
    console.log("[PyWebFlx] Disconnected from Python server");
    ws = null;
    stopKeepalive();
    scheduleReconnect();
  };

  ws.onerror = () => {
    // onclose will fire after onerror, triggering reconnect
  };
}

function scheduleReconnect() {
  setTimeout(connect, RECONNECT_DELAY_MS);
}

function send(data) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(data));
  }
}

// ---------------------------------------------------------------------------
// Keep-alive (prevents service worker from sleeping)
// ---------------------------------------------------------------------------

function startKeepalive() {
  chrome.alarms.create(KEEPALIVE_ALARM, { periodInMinutes: KEEPALIVE_INTERVAL_MIN });
}

function stopKeepalive() {
  chrome.alarms.clear(KEEPALIVE_ALARM);
}

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === KEEPALIVE_ALARM) {
    // Just being called keeps the service worker alive
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      connect();
    }
  }
});

// ---------------------------------------------------------------------------
// Tab events — notify Python
// ---------------------------------------------------------------------------

chrome.tabs.onRemoved.addListener((tabId) => {
  send({ event: "tab_closed", tabId });
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo) => {
  if (changeInfo.status === "complete") {
    send({ event: "tab_loaded", tabId });
  }
});

// ---------------------------------------------------------------------------
// Command dispatcher
// ---------------------------------------------------------------------------

async function handleCommand(raw) {
  let cmd;
  try {
    cmd = JSON.parse(raw);
  } catch (e) {
    return;
  }

  const { id, action, tabId, params } = cmd;

  try {
    let result;

    switch (action) {
      case "find_tabs":
        result = await findTabs(params);
        break;
      case "create_tab":
        result = await createTab(params);
        break;
      case "close_tab":
        await chrome.tabs.remove(tabId);
        result = null;
        break;
      case "navigate":
        await chrome.tabs.update(tabId, { url: params.url });
        result = null;
        break;
      case "go_back":
        result = await executeInTab(tabId, () => { history.back(); });
        break;
      case "go_forward":
        result = await executeInTab(tabId, () => { history.forward(); });
        break;
      case "refresh":
        await chrome.tabs.reload(tabId);
        result = null;
        break;
      case "execute_js":
        result = await executeInTab(tabId, params.code, true);
        break;
      default:
        // All DOM actions: click, type_into, get_text, inspect, etc.
        result = await executeDomAction(tabId, action, params);
        break;
    }

    send({ id, success: true, data: result });
  } catch (e) {
    send({
      id,
      success: false,
      error: e.name || "Error",
      message: e.message || String(e),
    });
  }
}

// ---------------------------------------------------------------------------
// Tab management
// ---------------------------------------------------------------------------

async function findTabs(params) {
  const { title, url } = params;
  const allTabs = await chrome.tabs.query({});
  return allTabs
    .filter((t) => {
      if (title && !t.title.toLowerCase().includes(title.toLowerCase())) return false;
      if (url && !t.url.toLowerCase().includes(url.toLowerCase())) return false;
      return true;
    })
    .map((t) => ({ id: t.id, title: t.title, url: t.url }));
}

async function createTab(params) {
  const tab = await chrome.tabs.create({ url: params.url, active: true });
  return { id: tab.id, title: tab.title, url: tab.url };
}

// ---------------------------------------------------------------------------
// Script injection
// ---------------------------------------------------------------------------

async function executeInTab(tabId, codeOrFunc, isRawCode = false) {
  let results;

  if (isRawCode) {
    // Execute raw JS code string
    results = await chrome.scripting.executeScript({
      target: { tabId },
      func: (code) => {
        return new Function(code)();
      },
      args: [codeOrFunc],
    });
  } else {
    results = await chrome.scripting.executeScript({
      target: { tabId },
      func: codeOrFunc,
    });
  }

  if (results && results.length > 0) {
    return results[0].result;
  }
  return null;
}

async function executeDomAction(tabId, action, params) {
  // Inject the action script with params and execute it
  const results = await chrome.scripting.executeScript({
    target: { tabId },
    func: domActionHandler,
    args: [action, params],
  });

  if (results && results.length > 0) {
    const result = results[0].result;
    if (result && result.__error) {
      const err = new Error(result.message);
      err.name = result.name;
      throw err;
    }
    return result;
  }
  return null;
}

// ---------------------------------------------------------------------------
// DOM action handler — injected into page context
// ---------------------------------------------------------------------------

function domActionHandler(action, params) {
  // Selector resolution
  function resolveElement(params) {
    const { selector, selectorType, text, tag, role, name } = params;

    if (selector && selectorType === "xpath") {
      const result = document.evaluate(
        selector, document, null,
        XPathResult.FIRST_ORDERED_NODE_TYPE, null
      );
      return result.singleNodeValue;
    }

    if (selector && selectorType === "css") {
      return document.querySelector(selector);
    }

    // Attribute-based selector
    if (text || role || name) {
      const baseTag = tag || "*";
      let candidates;
      if (role) {
        candidates = document.querySelectorAll(`${baseTag}[role="${role}"]`);
      } else {
        candidates = document.querySelectorAll(baseTag);
      }
      for (const el of candidates) {
        let match = true;
        if (text && el.textContent.trim() !== text) match = false;
        if (name) {
          const ariaLabel = el.getAttribute("aria-label") || el.getAttribute("name") || "";
          if (ariaLabel !== name) match = false;
        }
        if (match) return el;
      }
    }

    // Fallback: try CSS if selector provided without type
    if (selector) {
      return document.querySelector(selector);
    }

    return null;
  }

  function makeError(name, message) {
    return { __error: true, name, message };
  }

  try {
    switch (action) {
      case "click": {
        const el = resolveElement(params);
        if (!el) return makeError("ElementNotFoundError", `Element not found: ${params.selector || "attributes"}`);
        if (params.clickType === "double") {
          el.dispatchEvent(new MouseEvent("dblclick", { bubbles: true }));
        } else if (params.mouseButton === "right") {
          el.dispatchEvent(new MouseEvent("contextmenu", { bubbles: true }));
        } else {
          el.click();
        }
        return null;
      }

      case "type_into": {
        const el = resolveElement(params);
        if (!el) return makeError("ElementNotFoundError", `Element not found: ${params.selector || "attributes"}`);
        if (params.clearBefore !== false) {
          el.value = "";
          el.dispatchEvent(new Event("input", { bubbles: true }));
        }
        if (params.clickBefore !== false) {
          el.focus();
          el.click();
        }
        el.value = params.text;
        el.dispatchEvent(new Event("input", { bubbles: true }));
        el.dispatchEvent(new Event("change", { bubbles: true }));
        return null;
      }

      case "set_text": {
        const el = resolveElement(params);
        if (!el) return makeError("ElementNotFoundError", `Element not found: ${params.selector || "attributes"}`);
        el.value = params.text;
        el.dispatchEvent(new Event("input", { bubbles: true }));
        el.dispatchEvent(new Event("change", { bubbles: true }));
        return null;
      }

      case "check": {
        const el = resolveElement(params);
        if (!el) return makeError("ElementNotFoundError", `Element not found: ${params.selector || "attributes"}`);
        if (!el.checked) {
          el.click();
        }
        return null;
      }

      case "uncheck": {
        const el = resolveElement(params);
        if (!el) return makeError("ElementNotFoundError", `Element not found: ${params.selector || "attributes"}`);
        if (el.checked) {
          el.click();
        }
        return null;
      }

      case "select_item": {
        const el = resolveElement(params);
        if (!el) return makeError("ElementNotFoundError", `Element not found: ${params.selector || "attributes"}`);
        const { item, by } = params;
        if (by === "index") {
          el.selectedIndex = parseInt(item, 10);
        } else if (by === "value") {
          el.value = item;
        } else {
          // by text (default)
          const option = Array.from(el.options).find(o => o.text === item);
          if (option) option.selected = true;
        }
        el.dispatchEvent(new Event("change", { bubbles: true }));
        return null;
      }

      case "hover": {
        const el = resolveElement(params);
        if (!el) return makeError("ElementNotFoundError", `Element not found: ${params.selector || "attributes"}`);
        el.dispatchEvent(new MouseEvent("mouseenter", { bubbles: true }));
        el.dispatchEvent(new MouseEvent("mouseover", { bubbles: true }));
        return null;
      }

      case "send_hotkey": {
        const keys = params.keys.toLowerCase().split("+").map(k => k.trim());
        const eventInit = { bubbles: true };
        if (keys.includes("ctrl")) eventInit.ctrlKey = true;
        if (keys.includes("shift")) eventInit.shiftKey = true;
        if (keys.includes("alt")) eventInit.altKey = true;
        if (keys.includes("meta")) eventInit.metaKey = true;
        const mainKey = keys.filter(k => !["ctrl", "shift", "alt", "meta"].includes(k))[0] || "";
        eventInit.key = mainKey;
        document.activeElement.dispatchEvent(new KeyboardEvent("keydown", eventInit));
        document.activeElement.dispatchEvent(new KeyboardEvent("keyup", eventInit));
        return null;
      }

      case "get_text": {
        const el = resolveElement(params);
        if (!el) return makeError("ElementNotFoundError", `Element not found: ${params.selector || "attributes"}`);
        return el.innerText || el.textContent || "";
      }

      case "get_attribute": {
        const el = resolveElement(params);
        if (!el) return makeError("ElementNotFoundError", `Element not found: ${params.selector || "attributes"}`);
        return el.getAttribute(params.attribute);
      }

      case "get_full_text": {
        return document.body.innerText || "";
      }

      case "element_exists": {
        const el = resolveElement(params);
        return el !== null;
      }

      case "find_element": {
        const el = resolveElement(params);
        if (!el) return makeError("ElementNotFoundError", `Element not found: ${params.selector || "attributes"}`);
        return {
          tag: el.tagName.toLowerCase(),
          id: el.id || null,
          classes: Array.from(el.classList),
          text: (el.innerText || "").substring(0, 200),
          visible: el.offsetParent !== null,
        };
      }

      case "inspect": {
        return inspectDom(params.selector || null, params.depth || 2, params.samples || 2);
      }

      case "extract_table": {
        return extractTable(params.selector);
      }

      case "take_screenshot": {
        // Screenshots are handled by background.js via chrome.tabs.captureVisibleTab
        return makeError("ActionError", "Screenshots must be handled by background.js");
      }

      default:
        return makeError("ActionError", `Unknown action: ${action}`);
    }
  } catch (e) {
    return makeError(e.name || "Error", e.message || String(e));
  }

  // -----------------------------------------------------------------------
  // Inspect DOM — summarize structure for AI consumption
  // -----------------------------------------------------------------------
  function inspectDom(rootSelector, maxDepth, sampleCount) {
    const root = rootSelector ? document.querySelector(rootSelector) : document.body;
    if (!root) return `Element not found: ${rootSelector}`;

    const lines = [];
    walk(root, 0, maxDepth, sampleCount, lines);
    return lines.join("\n");
  }

  function walk(el, depth, maxDepth, sampleCount, lines) {
    if (depth > maxDepth) return;
    const indent = "  ".repeat(depth);
    const desc = describeElement(el);

    // Special handling for <table>
    if (el.tagName === "TABLE") {
      const rows = el.querySelectorAll("tr");
      const cols = rows.length > 0 ? rows[0].querySelectorAll("th, td").length : 0;
      lines.push(`${indent}${desc} ${cols} cols x ${rows.length} rows`);
      // Show header if exists
      const headers = el.querySelectorAll("th");
      if (headers.length > 0) {
        const headerTexts = Array.from(headers).map(h => h.textContent.trim());
        lines.push(`${indent}  headers: ${JSON.stringify(headerTexts)}`);
      }
      // Show sample rows
      const dataRows = el.querySelectorAll("tbody tr");
      for (let i = 0; i < Math.min(sampleCount, dataRows.length); i++) {
        const cells = Array.from(dataRows[i].querySelectorAll("td")).map(td => td.textContent.trim());
        lines.push(`${indent}  sample[${i}]: ${JSON.stringify(cells)}`);
      }
      return;
    }

    // Special handling for <select>
    if (el.tagName === "SELECT") {
      const opts = Array.from(el.options).map(o => o.text);
      const display = opts.length > 5 ? opts.slice(0, 5).concat([`... +${opts.length - 5} more`]) : opts;
      lines.push(`${indent}${desc} ${opts.length} options: ${JSON.stringify(display)}`);
      return;
    }

    // Check for repeated children (lists, card grids)
    const childTags = {};
    for (const child of el.children) {
      const key = child.tagName + (child.className ? `.${child.className.split(" ")[0]}` : "");
      childTags[key] = (childTags[key] || 0) + 1;
    }
    const repeated = Object.entries(childTags).find(([, count]) => count > 3);

    if (repeated) {
      const [pattern, count] = repeated;
      const tag = pattern.split(".")[0].toLowerCase();
      const cls = pattern.includes(".") ? `.${pattern.split(".")[1]}` : "";
      lines.push(`${indent}${desc}`);
      lines.push(`${indent}  <${tag}${cls}> x ${count} items`);
      // Show samples
      const items = el.querySelectorAll(`:scope > ${tag}${cls ? `.${cls}` : ""}`);
      for (let i = 0; i < Math.min(sampleCount, items.length); i++) {
        const text = items[i].textContent.trim().substring(0, 100);
        lines.push(`${indent}    sample[${i}]: "${text}"`);
      }
      return;
    }

    // Interactive elements get extra detail
    const isInteractive = ["INPUT", "BUTTON", "TEXTAREA", "A", "SELECT"].includes(el.tagName);
    if (isInteractive || el.children.length === 0) {
      const text = el.textContent ? el.textContent.trim().substring(0, 80) : "";
      if (text && !desc.includes('"')) {
        lines.push(`${indent}${desc} "${text}"`);
      } else {
        lines.push(`${indent}${desc}`);
      }
      return;
    }

    lines.push(`${indent}${desc}`);
    for (const child of el.children) {
      walk(child, depth + 1, maxDepth, sampleCount, lines);
    }
  }

  function describeElement(el) {
    let desc = `<${el.tagName.toLowerCase()}`;
    if (el.id) desc += `#${el.id}`;
    if (el.classList.length > 0) {
      desc += `.${Array.from(el.classList).join(".")}`;
    }
    desc += ">";

    // Add useful attributes for interactive elements
    const tag = el.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA") {
      const type = el.getAttribute("type");
      const placeholder = el.getAttribute("placeholder");
      const required = el.hasAttribute("required");
      const parts = [];
      if (type) parts.push(`type="${type}"`);
      if (placeholder) parts.push(`placeholder="${placeholder}"`);
      if (required) parts.push("[required]");
      if (parts.length > 0) desc = desc.slice(0, -1) + " " + parts.join(" ") + ">";
    }

    if (tag === "A") {
      const href = el.getAttribute("href");
      if (href) desc = desc.slice(0, -1) + ` href="${href.substring(0, 60)}">`;
    }

    return desc;
  }

  // -----------------------------------------------------------------------
  // Extract Table
  // -----------------------------------------------------------------------
  function extractTable(selector) {
    const table = document.querySelector(selector);
    if (!table) return { __error: true, name: "ElementNotFoundError", message: `Table not found: ${selector}` };

    // Get headers
    const headers = [];
    const ths = table.querySelectorAll("thead th, thead td, tr:first-child th");
    if (ths.length > 0) {
      ths.forEach(th => headers.push(th.textContent.trim()));
    } else {
      // If no headers, use first row
      const firstRow = table.querySelector("tr");
      if (firstRow) {
        firstRow.querySelectorAll("td, th").forEach((cell, i) => {
          headers.push(cell.textContent.trim() || `col_${i}`);
        });
      }
    }

    // Get data rows
    const rows = [];
    const trs = table.querySelectorAll("tbody tr");
    const dataRows = trs.length > 0 ? trs : table.querySelectorAll("tr:not(:first-child)");

    dataRows.forEach(tr => {
      const row = {};
      const cells = tr.querySelectorAll("td");
      cells.forEach((cell, i) => {
        const key = headers[i] || `col_${i}`;
        row[key] = cell.textContent.trim();
      });
      if (Object.keys(row).length > 0) {
        rows.push(row);
      }
    });

    return rows;
  }
}

// ---------------------------------------------------------------------------
// Initialize: start connecting
// ---------------------------------------------------------------------------

connect();
