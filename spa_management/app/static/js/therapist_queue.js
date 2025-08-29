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

function renderQueue(list) {
  const ul = document.getElementById("waiting_queue");
  if (!ul) return;

  ul.innerHTML = list
    .map((t) => {
      // Build single card with all services for the same code
      const servicesHTML =
        t.selected_services && t.selected_services.length > 0
          ? `
            <div class="service-card">
              <div class="service-header">
                <div class="service-title">
                  ${t.selected_services
                    .map(
                      (service) => `
                      <div class="service-item">
                        <div class="service-name">${service.service_name.toUpperCase()}</div>
                        <div class="service-details">
                          <div class="service-duration">${service.duration_minutes * 60} SECONDS</div>
                          <div class="service-area">${service.classification_name.toUpperCase()}</div>
                        </div>
                      </div>
                    `
                    )
                    .join("")}
                </div>
                <div class="service-code">
                  <div class="code-label">CODE</div>
                  <div class="code-number">${t.code}</div>
                </div>
              </div>
            </div>
          `
          : "";

      return `
      <li class="queue-item">
        <div class="queue-card-container">
          ${servicesHTML}
        </div>
      </li>
    `;
    })
    .join("");
}

{
  /* <div class="center-info">${customerNameHTML}</div>; */
}

function refreshQueue() {
  fetchWithAuth("/monitor_snapshot")
    .then((r) => r.json())
    .then((data) => {
      renderQueue(data.waiting || []);
    });
}

function bindControls() {
  socket.emit("therapist_subscribe");
  document.getElementById("confirm_next").addEventListener("click", () => {
    const therapist_name =
      document.getElementById("therapist_name").value || "Therapist 1";
    const room_number = document.getElementById("room_number").value || "101";
    socket.emit("therapist_confirm_next", { therapist_name, room_number });
  });
}

socket.on("therapist_confirm_result", (res) => {
  if (res.ok) {
    // Redirect to service management page
    const url = new URL('/therapist/service-management', window.location.origin);
    if (authToken) url.searchParams.set('auth_token', authToken);
    window.location.href = url.toString();
  } else {
    alert(res.error || "No pending customers");
  }
});

socket.on("cashier_queue_updated", () => {
  refreshQueue();
});

socket.on("therapist_queue_updated", () => {
  refreshQueue();
});

bindControls();
refreshQueue();
