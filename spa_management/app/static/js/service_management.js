// Get auth token from sessionStorage
const authToken = sessionStorage.getItem('therapist_auth_token');

// Initialize socket.io with auth token
const socket = io({
  auth: {
    token: authToken
  },
  query: {
    auth_token: authToken
  }
});

// Add token to fetch requests
function fetchWithAuth(url, options = {}) {
  const headers = {
    ...options.headers,
    'X-Auth-Token': authToken
  };
  return fetch(url, { ...options, headers });
}

let currentTxn = null;
let finishTimeout = null;
let intervalId = null;

function formatSeconds(totalSeconds) {
  const s = Math.max(0, Math.floor(totalSeconds));
  const hours = Math.floor(s / 3600);
  const minutes = Math.floor((s % 3600) / 60);
  const seconds = s % 60;
  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

function stopTimer() {
  if (intervalId) {
    clearInterval(intervalId);
    intervalId = null;
  }
}

function startTimer(tx) {
  stopTimer();
  const timerEl = document.getElementById("service_timer");
  if (!timerEl) return;

  // If service_start_at is provided, compute elapsed; else start now
  const startMs = tx.service_start_at
    ? Date.parse(tx.service_start_at)
    : Date.now();
  const totalMs = tx.total_duration_minutes * 1000;

  function tick() {
    const now = Date.now();
    const elapsed = now - startMs;
    const remaining = Math.max(0, Math.ceil((totalMs - elapsed) / 1000));
    timerEl.textContent = formatSeconds(remaining);
    if (remaining <= 0) {
      stopTimer();
      // Show timer finished layout
      showTimerFinishedLayout(tx);
    }
  }
  tick();
  intervalId = setInterval(tick, 1000);
}

function renderTimerLayout(tx) {
  const panel = document.getElementById("current_txn");
  const items = tx.items
    .map(
      (it) =>
        `<li>
          <div class="spa-service-item-info">
            <div class="spa-service-name">${it.service_name}</div>
            <div class="spa-service-details">${it.duration_minutes} MINUTES<br>${it.area || 'FULL BACK'}</div>
          </div>
          <div class="spa-service-price">₱${it.price.toFixed(0)}</div>
        </li>`
    )
    .join("");
  
  panel.innerHTML = `
    <div class="card">
      <div class="spa-timer-finished">
        <div class="spa-timer-display" id="service_timer">00:00:00</div>
      </div>
      <ul id="items_list">${items}</ul>
      <div class="controls">
        <button id="btn_finish" disabled>SERVICE FINISHED</button>
      </div>
    </div>
  `;

  // Bind the finish button
  const finishBtn = document.getElementById("btn_finish");
  if (finishBtn) {
    finishBtn.onclick = () => {
      socket.emit("therapist_finish_service", { transaction_id: tx.id });
    };
  }
}

function showTimerFinishedLayout(tx) {
  const panel = document.getElementById("current_txn");
  const items = tx.items
    .map(
      (it) =>
        `<li>
          <div class="spa-service-item-info">
            <div class="spa-service-name">${it.service_name}</div>
            <div class="spa-service-details">${it.duration_minutes} MINUTES<br>${it.area || 'FULL BACK'}</div>
          </div>
          <div class="spa-service-price">₱${it.price.toFixed(0)}</div>
        </li>`
    )
    .join("");
  
  panel.innerHTML = `
    <div class="card">
      <div class="spa-timer-finished">
        <div class="spa-timer-display">00:00:00</div>
      </div>
      <ul id="items_list">${items}</ul>
      <div class="controls">
        <button id="btn_done_service">DONE SERVICE</button>
      </div>
    </div>
  `;

  // Bind the done service button
  document.getElementById("btn_done_service").onclick = () => {
    socket.emit("therapist_finish_service", { transaction_id: tx.id });
  };
}

function renderCurrent(tx) {
  const panel = document.getElementById("current_txn");

  if (!tx) {
    panel.innerHTML = '<div class="spa-no-transaction">No current transaction. Please go back to the queue to confirm a customer.</div>';
    currentTxn = null;
    if (finishTimeout) {
      clearTimeout(finishTimeout);
      finishTimeout = null;
    }
    stopTimer();
    return;
  }
  currentTxn = tx;
  const items = tx.items
    .map(
      (it) =>
        `<li>
          <div class="spa-service-item-info">
            <div class="spa-service-name">${it.service_name}</div>
            <div class="spa-service-details">${it.duration_minutes} MINUTES<br>${it.area || 'FULL BACK'}</div>
          </div>
          <div class="spa-service-price">₱${it.price.toFixed(0)}</div>
          <button class="remove_item" data-itemid="${it.id}">REMOVE</button>
        </li>`
    )
    .join("");
  
  // Check if service is in progress and show timer layout
  const isInService = tx.status === "in_service" && tx.service_start_at;
  
  if (isInService) {
    panel.innerHTML = `
      <div class="card">
        <div class="spa-timer-finished">
          <div class="spa-timer-display" id="service_timer">00:00:00</div>
        </div>
        <ul id="items_list">${items}</ul>
        <div class="controls">
          <button id="btn_finish" disabled>SERVICE FINISHED</button>
        </div>
      </div>
    `;
  } else {
    panel.innerHTML = `
      <div class="card">
        <div class="spa-service-status">
          <div class="spa-service-code">Code: ${tx.code || ""} <span class="badge">${tx.status}</span></div>
          <div class="spa-service-total">Total: ₱${tx.total_amount.toFixed(2)} | Duration: ${tx.total_duration_minutes} min</div>
        </div>
        <ul id="items_list">${items}</ul>
        <div class="controls">
          <div class="spa-add-service-container">
            <select id="add_service_select"></select>
            <button id="btn_add">ADD</button>
          </div>
          <button id="btn_start">START SERVICE</button>
        </div>
      </div>
    `;
  }

  fetchWithAuth("/api/services")
    .then((r) => r.json())
    .then((list) => {
      const sel = document.getElementById("add_service_select");
      sel.innerHTML = "";
      list.forEach((s) => {
        const opt = document.createElement("option");
        opt.value = s.id;
        opt.textContent = `${s.name} - ₱${s.price}`;
        sel.appendChild(opt);
      });
    });

  const startBtn = document.getElementById("btn_start");
  const addBtn = document.getElementById("btn_add");
  const finishBtn = document.getElementById("btn_finish");
  const addSelect = document.getElementById("add_service_select");

  const itemsList = document.getElementById("items_list");
  // Disable Start button if there are no selected services
  const hasServices = Array.isArray(tx.items) && tx.items.length > 0;
  if (startBtn) startBtn.disabled = !hasServices;
  function setRemoveButtonsDisabled(disabled) {
    itemsList
      .querySelectorAll(".remove_item")
      .forEach((btn) => (btn.disabled = disabled));
  }

  // Only add remove button listeners if not in service
  if (!isInService) {
    itemsList.addEventListener("click", (e) => {
      if (e.target.classList.contains("remove_item")) {
        const id = parseInt(e.target.getAttribute("data-itemid"));
        socket.emit("therapist_remove_item", { transaction_item_id: id });
        // Prevent starting while waiting for server update
        if (startBtn) startBtn.disabled = true;
      }
    });
  }

  // If already in service, start timer immediately
  if (isInService) {
    startTimer(tx);
  }

  // Bind start button only if it exists (not in service)
  if (startBtn) {
    startBtn.onclick = () => {
      socket.emit("therapist_start_service", { transaction_id: tx.id });
      
      // Immediately show timer layout
      const updatedTx = { ...tx, status: "in_service", service_start_at: new Date().toISOString() };
      renderTimerLayout(updatedTx);
      startTimer(updatedTx);
    };
  }

  // Bind add button only if it exists (not in service)
  if (addBtn) {
    addBtn.onclick = () => {
      const sid = document.getElementById("add_service_select").value;
      socket.emit("therapist_add_service", {
        transaction_id: tx.id,
        service_id: sid,
      });
    };
  }

  // Bind finish button if it exists
  if (finishBtn) {
    finishBtn.onclick = () => {
      socket.emit("therapist_finish_service", { transaction_id: tx.id });
    };
  }
}

function bindControls() {
  socket.emit("therapist_subscribe");
}

socket.on("customer_txn_update", (tx) => {
  if (currentTxn && tx.id === currentTxn.id) renderCurrent(tx);
});

socket.on("therapist_finish_result", (res) => {
  if (res && res.ok) {
    alert("Service has been completed. Redirecting back to queue...");
    // Redirect back to therapist queue page
    const url = new URL('/therapist', window.location.origin);
    if (authToken) url.searchParams.set('auth_token', authToken);
    window.location.href = url.toString();
  }
});

socket.on("therapist_edit_done", (res) => {
  if (res.ok && res.transaction) renderCurrent(res.transaction);
});

// Check if there's a current transaction when page loads
socket.on("connect", () => {
  socket.emit("therapist_get_current_transaction");
});

socket.on("therapist_current_transaction", (tx) => {
  renderCurrent(tx);
});

bindControls();
renderCurrent(null);
