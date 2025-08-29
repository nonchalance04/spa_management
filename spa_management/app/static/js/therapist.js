// const socket = io();

// let currentTxn = null;
// let finishTimeout = null;
// let intervalId = null;

// function formatHMS(totalSeconds) {
//   const s = Math.max(0, Math.floor(totalSeconds));
//   const h = Math.floor(s / 3600);
//   const m = Math.floor((s % 3600) / 60);
//   const sec = s % 60;
//   return `${h.toString().padStart(2, "0")}:${m
//     .toString()
//     .padStart(2, "0")}:${sec.toString().padStart(2, "0")}`;
// }

// function renderQueue(list) {
//   const ul = document.getElementById("waiting_queue");
//   if (!ul) return;
//   ul.innerHTML = "";
//   list.forEach((t) => {
//     const li = document.createElement("li");
//     li.className = "queue-item";

//     // Main container div for the entire queue item
//     const itemContainer = document.createElement("div");
//     itemContainer.className = "item-container";

//     // Header section div for customer info
//     const headerSection = document.createElement("div");
//     headerSection.className = "header-section";

//     // Left side div for transaction code
//     const leftDiv = document.createElement("div");
//     leftDiv.className = "left-info";

//     const codeSpan = document.createElement("span");
//     codeSpan.className = "transaction-code";
//     codeSpan.textContent = `${t.code || "—"}`;
//     leftDiv.appendChild(codeSpan);

//     // Center div for customer name
//     const centerDiv = document.createElement("div");
//     centerDiv.className = "center-info";

//     if (t.customer_name) {
//       const nameSpan = document.createElement("span");
//       nameSpan.className = "customer-name";
//       nameSpan.textContent = t.customer_name;
//       centerDiv.appendChild(nameSpan);
//     }

//     // Right side div for total info
//     const rightDiv = document.createElement("div");
//     rightDiv.className = "right-info";

//     const totalSpan = document.createElement("span");
//     totalSpan.className = "total-info";
//     totalSpan.textContent = `₱${t.total_amount.toFixed(2)} (${
//       t.total_duration_minutes
//     }m)`;
//     rightDiv.appendChild(totalSpan);

//     // Append left, center, right to header section
//     headerSection.appendChild(leftDiv);
//     headerSection.appendChild(centerDiv);
//     headerSection.appendChild(rightDiv);

//     // Add header section to main container
//     itemContainer.appendChild(headerSection);

//     // Services section div
//     if (t.selected_services && t.selected_services.length > 0) {
//       const servicesSection = document.createElement("div");
//       servicesSection.className = "services-section";

//       const servicesHeader = document.createElement("div");
//       servicesHeader.className = "services-header";

//       const servicesTitle = document.createElement("div");
//       servicesTitle.className = "services-title";
//       servicesTitle.textContent = ":";
//       servicesHeader.appendChild(servicesTitle);

//       const servicesContent = document.createElement("div");
//       servicesContent.className = "services-content";

//       const servicesList = document.createElement("ul");
//       servicesList.className = "services-list";

//       t.selected_services.forEach((service) => {
//         const serviceItemDiv = document.createElement("div");
//         serviceItemDiv.className = "service-item-wrapper";

//         const serviceLi = document.createElement("li");
//         serviceLi.className = "service-item";

//         const serviceNameDiv = document.createElement("div");
//         serviceNameDiv.className = "service-name";
//         serviceNameDiv.textContent = service.service_name;

//         const servicePriceDiv = document.createElement("div");
//         servicePriceDiv.className = "service-price";
//         servicePriceDiv.textContent = `₱${service.price.toFixed(2)} (${
//           service.duration_minutes
//         }m)`;

//         serviceLi.appendChild(serviceNameDiv);
//         serviceLi.appendChild(servicePriceDiv);
//         serviceItemDiv.appendChild(serviceLi);
//         servicesList.appendChild(serviceItemDiv);
//       });

//       servicesContent.appendChild(servicesList);
//       servicesSection.appendChild(servicesHeader);
//       servicesSection.appendChild(servicesContent);
//       itemContainer.appendChild(servicesSection);
//     }

//     // Add main container to list item
//     li.appendChild(itemContainer);
//     ul.appendChild(li);
//   });
// }

// function refreshQueue() {
//   fetch("/monitor_snapshot")
//     .then((r) => r.json())
//     .then((data) => {
//       renderQueue(data.waiting || []);
//     });
// }

// function stopTimer() {
//   if (intervalId) {
//     clearInterval(intervalId);
//     intervalId = null;
//   }
// }

// function startTimer(tx) {
//   stopTimer();
//   const timerEl = document.getElementById("service_timer");
//   if (!timerEl) return;

//   // If service_start_at is provided, compute elapsed; else start now
//   const startMs = tx.service_start_at
//     ? Date.parse(tx.service_start_at)
//     : Date.now();
//   const totalMs = tx.total_duration_minutes * 60 * 0.1667;

//   function tick() {
//     const now = Date.now();
//     const elapsed = now - startMs;
//     const remaining = Math.max(0, Math.ceil((totalMs - elapsed) / 1000));
//     timerEl.textContent = formatHMS(remaining);
//     if (remaining <= 0) {
//       stopTimer();
//       // enable finish button if present
//       const finishBtn = document.getElementById("btn_finish");
//       if (finishBtn) finishBtn.disabled = false;
//     }
//   }
//   tick();
//   intervalId = setInterval(tick, 1000);
// }

// function renderCurrent(tx) {
//   const panel = document.getElementById("current_txn");
//   const confirmNextBtn = document.getElementById("confirm_next");

//   if (confirmNextBtn) confirmNextBtn.disabled = !!tx;

//   if (!tx) {
//     panel.innerHTML = "<p>No current transaction.</p>";
//     currentTxn = null;
//     if (finishTimeout) {
//       clearTimeout(finishTimeout);
//       finishTimeout = null;
//     }
//     stopTimer();
//     return;
//   }
//   currentTxn = tx;
//   const items = tx.items
//     .map(
//       (it) =>
//         `<li>${it.service_name} - ₱${it.price.toFixed(2)} (${
//           it.duration_minutes
//         }m)
//           <button class=\"remove_item\" data-itemid=\"${it.id}\">Remove</button>
//         </li>`
//     )
//     .join("");
//   panel.innerHTML = `
//     <div class=\"card\">
//       <div><strong>Code:</strong> ${tx.code || ""} <span class=\"badge\">${
//     tx.status
//   }</span></div>
//       <div><strong>Room:</strong> ${tx.room_number || ""}</div>
//       <div><strong>Total:</strong> ₱${tx.total_amount.toFixed(
//         2
//       )} | <strong>Duration:</strong> ${tx.total_duration_minutes}m</div>
//       <div><strong>Timer:</strong> <span id=\"service_timer\">--:--:--</span></div>
//       <ul id=\"items_list\">${items}</ul>
//       <div class=\"controls\">
//         <button id=\"btn_start\">Start Service</button>
//         <select id=\"add_service_select\"></select>
//         <button id=\"btn_add\">Add Service</button>
//         <button id=\"btn_finish\" disabled>Service Finished</button>
//       </div>
//     </div>
//   `;

//   fetch("/api/services")
//     .then((r) => r.json())
//     .then((list) => {
//       const sel = document.getElementById("add_service_select");
//       sel.innerHTML = "";
//       list.forEach((s) => {
//         const opt = document.createElement("option");
//         opt.value = s.id;
//         opt.textContent = `${s.name} - ₱${s.price}`;
//         sel.appendChild(opt);
//       });
//     });

//   const startBtn = document.getElementById("btn_start");
//   const addBtn = document.getElementById("btn_add");
//   const finishBtn = document.getElementById("btn_finish");
//   const addSelect = document.getElementById("add_service_select");

//   const itemsList = document.getElementById("items_list");
//   // Disable Start button if there are no selected services
//   const hasServices = Array.isArray(tx.items) && tx.items.length > 0;
//   if (startBtn) startBtn.disabled = !hasServices;
//   function setRemoveButtonsDisabled(disabled) {
//     itemsList
//       .querySelectorAll(".remove_item")
//       .forEach((btn) => (btn.disabled = disabled));
//   }
//   itemsList.addEventListener("click", (e) => {
//     if (e.target.classList.contains("remove_item")) {
//       const id = parseInt(e.target.getAttribute("data-itemid"));
//       socket.emit("therapist_remove_item", { transaction_item_id: id });
//       // Prevent starting while waiting for server update
//       if (startBtn) startBtn.disabled = true;
//     }
//   });

//   // If already in service, start timer immediately
//   if (tx.status === "in_service" && tx.service_start_at) {
//     // disable edits during timer
//     startBtn.disabled = true;
//     addBtn.disabled = true;
//     addSelect.disabled = true;
//     setRemoveButtonsDisabled(true);
//     startTimer(tx);
//   }

//   startBtn.onclick = () => {
//     socket.emit("therapist_start_service", { transaction_id: tx.id });
//     const disableSecs = tx.total_duration_minutes * 1000;
//     startBtn.disabled = true;
//     addBtn.disabled = true;
//     finishBtn.disabled = true;
//     setRemoveButtonsDisabled(true);
//     const confirmNextBtn2 = document.getElementById("confirm_next");
//     if (confirmNextBtn2) confirmNextBtn2.disabled = true;
//     if (addSelect) addSelect.disabled = true;

//     // start local timer now
//     startTimer({ ...tx, service_start_at: new Date().toISOString() });

//     if (finishTimeout) clearTimeout(finishTimeout);
//     finishTimeout = setTimeout(() => {
//       finishBtn.disabled = false;
//     }, disableSecs * 1000);
//   };

//   document.getElementById("btn_add").onclick = () => {
//     const sid = document.getElementById("add_service_select").value;
//     socket.emit("therapist_add_service", {
//       transaction_id: tx.id,
//       service_id: sid,
//     });
//   };

//   finishBtn.onclick = () => {
//     socket.emit("therapist_finish_service", { transaction_id: tx.id });
//   };
// }

// function bindControls() {
//   socket.emit("therapist_subscribe");
//   document.getElementById("confirm_next").addEventListener("click", () => {
//     const therapist_name =
//       document.getElementById("therapist_name").value || "Therapist 1";
//     const room_number = document.getElementById("room_number").value || "101";
//     socket.emit("therapist_confirm_next", { therapist_name, room_number });
//   });
// }

// socket.on("therapist_confirm_result", (res) => {
//   if (res.ok) {
//     renderCurrent(res.transaction);
//     refreshQueue();
//   } else {
//     alert(res.error || "No pending customers");
//   }
// });

// socket.on("customer_txn_update", (tx) => {
//   if (currentTxn && tx.id === currentTxn.id) renderCurrent(tx);
// });

// socket.on("therapist_finish_result", (res) => {
//   if (res && res.ok) {
//     alert("Service has been completed.");
//     renderCurrent(null);
//     stopTimer();
//   }
// });

// socket.on("cashier_queue_updated", () => {
//   renderCurrent(null);
//   refreshQueue();
//   stopTimer();
// });

// socket.on("therapist_edit_done", (res) => {
//   if (res.ok && res.transaction) renderCurrent(res.transaction);
// });

// socket.on("therapist_queue_updated", () => {
//   refreshQueue();
// });

// bindControls();
// renderCurrent(null);
// refreshQueue();
