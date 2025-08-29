// Get auth token from sessionStorage
const authToken = sessionStorage.getItem('cashier_auth_token');

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
let myName = null;

function printReceipt(tx, amountPaid, changeAmount, cashierName) {
  // Create a new window for printing
  const printWindow = window.open("", "_blank", "width=600,height=600");

  // Create receipt HTML content
  const receiptHTML = `
    <!DOCTYPE html>
    <html>
    <head>
      <title>Payment Receipt - ${tx.code}</title>
      <style>
        body {
          font-family: 'Courier New', monospace;
          margin: 20px;
          font-size: 12px;
          line-height: 1.4;
        }
        .receipt-header {
          text-align: center;
          border-bottom: 2px dashed #000;
          padding-bottom: 10px;
          margin-bottom: 20px;
        }
        .business-name {
          font-size: 18px;
          font-weight: bold;
          margin-bottom: 5px;
        }
        .transaction-info {
          margin-bottom: 20px;
        }
        .services-list {
          margin-bottom: 20px;
        }
        .service-item {
          display: flex;
          justify-content: space-between;
          margin-bottom: 8px;
          padding: 5px 0;
          border-bottom: 1px dotted #ccc;
        }
        .service-name {
          flex: 1;
        }
        .service-price {
          text-align: right;
          min-width: 80px;
        }
        .payment-section {
          border-top: 2px dashed #000;
          padding-top: 10px;
          margin-top: 20px;
        }
        .payment-row {
          display: flex;
          justify-content: space-between;
          margin-bottom: 5px;
        }
        .total-section {
          border-top: 2px dashed #000;
          padding-top: 10px;
          margin-top: 20px;
          text-align: right;
          font-weight: bold;
          font-size: 14px;
        }
        .footer {
          text-align: center;
          margin-top: 30px;
          font-size: 10px;
          color: #666;
        }
        @media print {
          body { margin: 0; }
          .no-print { display: none; }
        }
      </style>
    </head>
    <body>
      <div class="receipt-header">
        <div class="business-name">SPA & WELLNESS CENTER</div>
        <div>Payment Receipt</div>
      </div>
      
      <div class="transaction-info">
        <div><strong>Transaction Code:</strong> ${tx.code}</div>
        <div><strong>Date:</strong> ${new Date().toLocaleDateString()}</div>
        <div><strong>Time:</strong> ${new Date().toLocaleTimeString()}</div>
        <div><strong>Cashier:</strong> ${cashierName}</div>
        <div><strong>Counter:</strong> ${document.getElementById('counter_number').value || '1'}</div>
        <div><strong>Status:</strong> PAID</div>
      </div>
      
      <div class="services-list">
        <div style="font-weight: bold; margin-bottom: 10px;">Services Rendered:</div>
        ${tx.items
          .map(
            (item) => `
          <div class="service-item">
            <span class="service-name">${item.service_name} (${
              item.duration_minutes
            }m)</span>
            <span class="service-price">₱${item.price.toFixed(2)}</span>
          </div>
        `
          )
          .join("")}
      </div>
      
      <div class="payment-section">
        <div class="payment-row">
          <span>Subtotal:</span>
          <span>₱${tx.total_amount.toFixed(2)}</span>
        </div>
        <div class="payment-row">
          <span>Amount Paid:</span>
          <span>₱${amountPaid.toFixed(2)}</span>
        </div>
        <div class="payment-row">
          <span>Change:</span>
          <span>₱${changeAmount.toFixed(2)}</span>
        </div>
      </div>
      
      <div class="total-section">
        <div><strong>TOTAL AMOUNT: ₱${tx.total_amount.toFixed(2)}</strong></div>
      </div>
      
      <div class="footer">
        <div>Thank you for your payment!</div>
        <div>Please keep this receipt for your records</div>
        <div>Transaction completed successfully</div>
      </div>
      
      <div class="no-print" style="margin-top: 30px; text-align: center;">
        <button onclick="window.print()">Print Receipt</button>
        <button onclick="window.close()">Close</button>
      </div>
    </body>
    </html>
  `;

  // Write the receipt content to the new window
  printWindow.document.write(receiptHTML);
  printWindow.document.close();

  // Wait for content to load, then print
  printWindow.onload = function () {
    printWindow.print();
  };
}

function renderPaymentPanel(tx) {
  const panel = document.getElementById("current_payment_txn");
  if (!tx) {
    panel.innerHTML = '<div class="spa-no-transaction">No current transaction. Please go back to the queue to confirm a customer.</div>';
    currentTxn = null;
    return;
  }
  
  currentTxn = tx;
  const items = tx.items
    .map(
      (it) =>
        `<li class="payment-service-item">
          <div class="payment-service-info">
            <div class="payment-service-name">${it.service_name}</div>
            <div class="payment-service-details">${it.duration_minutes} MINUTES • ${it.area || 'FULL BODY'}</div>
          </div>
          <div class="payment-service-price">₱${it.price.toFixed(2)}</div>
        </li>`
    )
    .join("");
    
  panel.innerHTML = `
    <div class="payment-card">
      <div class="payment-transaction-header">
        <div class="payment-transaction-code">Transaction Code: ${tx.code}</div>
        <div class="payment-transaction-status">
          <span class="payment-status-badge ${tx.status}">${tx.status.toUpperCase()}</span>
        </div>
      </div>
      
      <div class="payment-services-section">
        <h4>Services Rendered:</h4>
        <ul class="payment-services-list">${items}</ul>
      </div>
      
      <div class="payment-total-section">
        <div class="payment-total-amount">
          <strong>Total Due: ₱<span id="due">${tx.total_amount.toFixed(2)}</span></strong>
        </div>
      </div>
      
      <div class="payment-controls">
        <div class="payment-input-group">
          <label for="amount_paid">Payment Amount:</label>
          <input id="amount_paid" type="number" min="0" step="0.01" placeholder="Enter amount">
        </div>
        <div class="payment-buttons">
          <button id="btn_pay" class="payment-btn primary" disabled>Process Payment</button>
        </div>
        <div id="change_line" class="payment-change"></div>
      </div>
      
      <div id="receipt_section" style="display:none" class="payment-receipt-section">
        <button id="btn_print_receipt" class="payment-btn success">Print Receipt</button>
        <button id="btn_new_transaction" class="payment-btn primary">New Transaction</button>
      </div>
    </div>
  `;

  const due = tx.total_amount;
  const amountInput = document.getElementById("amount_paid");
  const payBtn = document.getElementById("btn_pay");
  const changeLine = document.getElementById("change_line");
  const receiptSection = document.getElementById("receipt_section");
  const printReceiptBtn = document.getElementById("btn_print_receipt");
  const newTransactionBtn = document.getElementById("btn_new_transaction");

  function updateState() {
    const paid = parseFloat(amountInput.value || "0");
    if (!isNaN(paid) && paid >= due) {
      payBtn.disabled = false;
      changeLine.innerHTML = `<strong>Change: ₱${(paid - due).toFixed(2)}</strong>`;
      changeLine.style.color = "#28a745";
    } else if (paid > 0) {
      payBtn.disabled = true;
      changeLine.innerHTML = `<span style="color: #dc3545;">Insufficient amount. Need ₱${(due - paid).toFixed(2)} more.</span>`;
    } else {
      payBtn.disabled = true;
      changeLine.innerHTML = "";
    }
  }
  
  amountInput.addEventListener("input", updateState);
  amountInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !payBtn.disabled) {
      payBtn.click();
    }
  });
  updateState();

  payBtn.onclick = () => {
    const cashier_name = myName || document.getElementById("cashier_name").value || "Cashier 1";
    const counter_number = document.getElementById("counter_number").value || "1";
    const amount_paid = parseFloat(amountInput.value || "0");
    const change_amount = amount_paid - due;

    // Disable pay button immediately after clicking
    payBtn.disabled = true;
    payBtn.textContent = "Processing...";

    socket.emit("cashier_pay", {
      transaction_id: tx.id,
      amount_paid,
      method: "cash",
      cashier_name,
      counter_number
    });

    // Show receipt section after successful payment
    setTimeout(() => {
      receiptSection.style.display = "block";
      payBtn.style.display = "none";
      amountInput.disabled = true;
    }, 1000);
  };

  printReceiptBtn.onclick = () => {
    const cashier_name = myName || document.getElementById("cashier_name").value || "Cashier 1";
    const amount_paid = parseFloat(amountInput.value || "0");
    const change_amount = amount_paid - due;
    printReceipt(tx, amount_paid, change_amount, cashier_name);
  };

  newTransactionBtn.onclick = () => {
    // Redirect back to cashier queue for next transaction
    window.location.href = "/cashier";
  };

  // Focus on amount input for better UX
  amountInput.focus();
}

function bindControls() {
  socket.emit("cashier_subscribe");
  myName = document.getElementById("cashier_name").value || "Cashier 1";
}

// Socket event handlers
socket.on("cashier_pay_result", (res) => {
  if (res.ok) {
    const tx = res.transaction;
    const payBtn = document.getElementById("btn_pay");
    const changeLine = document.getElementById("change_line");
    const receiptSection = document.getElementById("receipt_section");
    
    if (payBtn) {
      payBtn.textContent = "Payment Completed";
      payBtn.disabled = true;
      payBtn.style.backgroundColor = "#28a745";
    }

    const change = tx && tx.payment ? tx.payment.change_amount || 0 : 0;
    if (changeLine) {
      changeLine.innerHTML = `<strong style="color: #28a745;">Payment Successful! Change: ₱${change.toFixed(2)}</strong>`;
    }

    if (receiptSection) {
      receiptSection.style.display = "block";
    }

    const msg = change > 0 
      ? `Payment successful! Change: ₱${change.toFixed(2)}`
      : "Payment successful!";
    
    // Show success message
    setTimeout(() => alert(msg), 500);
  } else {
    // Re-enable pay button if payment failed
    const payBtn = document.getElementById("btn_pay");
    if (payBtn) {
      payBtn.disabled = false;
      payBtn.textContent = "Process Payment";
      payBtn.style.backgroundColor = "#902726";
    }
    alert(res.error || "Payment failed");
  }
});

// Check if there's a current transaction when page loads
socket.on("connect", () => {
  // First check if there's a transaction in sessionStorage
  const storedTransaction = sessionStorage.getItem('current_transaction');
  if (storedTransaction) {
    try {
      const tx = JSON.parse(storedTransaction);
      renderPaymentPanel(tx);
      // Clear from sessionStorage after loading
      sessionStorage.removeItem('current_transaction');
    } catch (e) {
      console.error('Error parsing stored transaction:', e);
      socket.emit("cashier_get_current_transaction");
    }
  } else {
    socket.emit("cashier_get_current_transaction");
  }
});

socket.on("cashier_current_transaction", (tx) => {
  renderPaymentPanel(tx);
});

socket.on("customer_txn_update", (tx) => {
  if (currentTxn && tx.id === currentTxn.id) {
    renderPaymentPanel(tx);
  }
});

bindControls();

// Check for stored transaction immediately on page load
const storedTransaction = sessionStorage.getItem('current_transaction');
if (storedTransaction) {
  try {
    const tx = JSON.parse(storedTransaction);
    renderPaymentPanel(tx);
    sessionStorage.removeItem('current_transaction');
  } catch (e) {
    console.error('Error parsing stored transaction:', e);
    renderPaymentPanel(null);
  }
} else {
  renderPaymentPanel(null);
}
