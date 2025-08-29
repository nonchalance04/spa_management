from __future__ import annotations
from datetime import datetime, timedelta
from typing import Any

from flask import session, request
from flask_socketio import emit, join_room
from sqlalchemy import select

from .extensions import db, socketio
from .models import (
    Service,
    ServiceClassification,
    Therapist,
    Cashier,
    Transaction,
    TransactionItem,
    TransactionStatus,
    Payment,
)
from .utils.auth_helpers import get_current_therapist, get_current_cashier


# Utility serializers

def _iso(dt: datetime | None) -> str | None:
    if not dt:
        return None
    # Use local time instead of UTC
    try:
        return dt.isoformat()
    except Exception:
        return None


def serialize_transaction(tx: Transaction) -> dict[str, Any]:
    data = {
        "id": tx.id,
        "code": tx.code,
        "customer_name": tx.customer_name,
        "status": tx.status.value,
        "therapist": tx.therapist.name if tx.therapist else None,
        "room_number": tx.room_number,
        "total_amount": tx.total_amount,
        "total_duration_minutes": tx.total_duration_minutes,
        "service_start_at": _iso(tx.service_start_at),
        "items": [
            {
                "id": it.id,
                "service_id": it.service_id,
                "service_name": it.service.service_name,
                "price": it.price,
                "duration_minutes": it.duration_minutes,
            }
            for it in tx.items
        ],
    }
    if tx.payment:
        data["payment"] = {
            "amount_due": tx.payment.amount_due,
            "amount_paid": tx.payment.amount_paid,
            "change_amount": tx.payment.change_amount,
            "method": tx.payment.method,
            "created_at": _iso(tx.payment.created_at),
        }
    return data


# Rooms
# - Global broadcast rooms: "therapist_queue", "cashier_queue", "monitor"
# - Per-transaction room: f"txn_{tx.id}"


@socketio.on("connect")
def on_connect():
    emit("connected", {"message": "connected"})


@socketio.on("join_room")
def on_join_room(data):
    room = data.get("room")
    if room:
        join_room(room)
        emit("joined_room", {"room": room})

# Dito napupunta yung confirm signal after iclick ni customer yung confirm button
@socketio.on("customer_confirm_selection")
def customer_confirm_selection(data):
    customer_name = data.get("customer_name")
    items = data.get("items", [])  # list of service items with classification info

    tx = Transaction(customer_name=customer_name, status=TransactionStatus.pending_therapist)
    db.session.add(tx)
    db.session.flush()

    for item in items:
        # Handle both old format (just service_id) and new format (with classification)
        if isinstance(item, dict):
            service_id = item.get("service_id")
            service_classification_id = item.get("service_classification_id")
        else:
            # Backward compatibility: treat as service_id
            service_id = item
            service_classification_id = None

        service = db.session.get(Service, int(service_id))
        if not service:
            continue

        # Get price and duration from classification if available, otherwise use default
        price = 0.0
        duration_minutes = 60  # Default duration

        if service_classification_id:
            classification = db.session.get(ServiceClassification, int(service_classification_id))
            if classification:
                price = classification.price
                duration_minutes = classification.duration_minutes
        
        db.session.add(
            TransactionItem(
                transaction_id=tx.id,
                service_id=service.id,
                service_classification_id=service_classification_id,
                price=price,
                duration_minutes=duration_minutes,
            )
        )
    tx.selection_confirmed_at = datetime.now()  # Use local time instead of UTC
    tx.recompute_totals()
    # Generate a transaction code immediately so both customer and therapist can see it
    tx.code = Transaction.generate_code()

    db.session.commit()

    emit("therapist_queue_updated", broadcast=True, to="therapist_queue")
    emit("monitor_updated", broadcast=True, to="monitor")
    emit("monitor_customer_confirmed", {"code": tx.code, "customer": customer_name}, to="monitor")

    # Send initial transaction snapshot back to the customer so UI can show code, items, and total right away
    emit("customer_selection_received", {"transaction_id": tx.id, "transaction": serialize_transaction(tx)})


@socketio.on("therapist_subscribe")
def therapist_subscribe():
    join_room("therapist_queue")


@socketio.on("cashier_subscribe")
def cashier_subscribe():
    join_room("cashier_queue")


@socketio.on("monitor_subscribe")
def monitor_subscribe():
    join_room("monitor")


@socketio.on("therapist_confirm_next")
def therapist_confirm_next(data):
    # Get authenticated therapist from token or session
    therapist, _ = get_current_therapist()
    
    if not therapist:
        emit("therapist_confirm_result", {"ok": False, "error": "Authentication required"})
        return

    room_number = therapist.room_number

    tx: Transaction | None = (
        Transaction.query
        .filter_by(status=TransactionStatus.pending_therapist)
        .order_by(Transaction.selection_confirmed_at.asc())
        .with_for_update(skip_locked=True)
        .first()
    )

    if not tx:
        emit("therapist_confirm_result", {"ok": False, "error": "No pending customers."})
        return

    tx.therapist = therapist
    tx.room_number = room_number
    tx.status = TransactionStatus.therapist_confirmed
    tx.therapist_confirmed_at = datetime.now()  # Use local time instead of UTC
    if not tx.code:
        tx.code = Transaction.generate_code()

    db.session.commit()

    room = f"txn_{tx.id}"
    emit("joined_room", {"room": room})

    emit("therapist_queue_updated", broadcast=True, to="therapist_queue")
    emit("monitor_updated", broadcast=True, to="monitor")
    emit("monitor_therapist_confirmed", {"code": tx.code, "therapist": therapist.name, "room": room_number}, to="monitor")
    emit("customer_txn_update", serialize_transaction(tx), to=room)

    emit("therapist_confirm_result", {"ok": True, "transaction": serialize_transaction(tx)})


@socketio.on("therapist_start_service")
def therapist_start_service(data):
    tx_id = int(data.get("transaction_id"))
    tx = db.session.get(Transaction, tx_id)
    if not tx:
        emit("error", {"error": "Transaction not found"})
        return

    tx.status = TransactionStatus.in_service
    tx.service_start_at = datetime.now()  # Use local time instead of UTC
    db.session.commit()

    room = f"txn_{tx.id}"
    emit("monitor_updated", broadcast=True, to="monitor")
    emit("monitor_service_started", {"code": tx.code, "therapist": tx.therapist.name if tx.therapist else None}, to="monitor")
    emit("customer_txn_update", serialize_transaction(tx), to=room)


@socketio.on("therapist_add_service")
def therapist_add_service(data):
    tx_id = int(data.get("transaction_id"))
    service_id = int(data.get("service_id"))
    service_classification_id = data.get("service_classification_id")

    tx = db.session.get(Transaction, tx_id)
    service = db.session.get(Service, service_id)
    if not tx or not service:
        emit("error", {"error": "Invalid transaction or service"})
        return

    # Get price and duration from classification if provided, otherwise use first available classification
    price = 0.0
    duration_minutes = 60  # Default duration
    classification_id = None

    if service_classification_id:
        classification = db.session.get(ServiceClassification, int(service_classification_id))
        if classification:
            price = classification.price
            duration_minutes = classification.duration_minutes
            classification_id = classification.id
    elif service.classifications:
        # Use first available classification if none specified
        classification = service.classifications[0]
        price = classification.price
        duration_minutes = classification.duration_minutes
        classification_id = classification.id

    db.session.add(
        TransactionItem(
            transaction_id=tx.id,
            service_id=service.id,
            service_classification_id=classification_id,
            price=price,
            duration_minutes=duration_minutes,
        )
    )
    tx.recompute_totals()
    db.session.commit()

    room = f"txn_{tx.id}"
    emit("customer_txn_update", serialize_transaction(tx), to=room)
    emit("monitor_updated", broadcast=True, to="monitor")
    emit("therapist_edit_done", {"ok": True, "transaction": serialize_transaction(tx)})


@socketio.on("therapist_remove_item")
def therapist_remove_item(data):
    item_id = int(data.get("transaction_item_id"))
    item = db.session.get(TransactionItem, item_id)
    if not item:
        emit("error", {"error": "Item not found"})
        return

    tx = item.transaction
    if tx.status not in (TransactionStatus.therapist_confirmed, TransactionStatus.in_service):
        emit("error", {"error": "Cannot remove in current state"})
        return

    db.session.delete(item)
    db.session.flush()
    tx.recompute_totals()
    db.session.commit()

    room = f"txn_{tx.id}"
    emit("customer_txn_update", serialize_transaction(tx), to=room)
    emit("monitor_updated", broadcast=True, to="monitor")
    emit("therapist_edit_done", {"ok": True, "transaction": serialize_transaction(tx)})


@socketio.on("therapist_get_current_transaction")
def therapist_get_current_transaction():
    therapist, _ = get_current_therapist()
    if not therapist:
        emit("therapist_current_transaction", None)
        return
    
    # Find current transaction for this therapist
    tx = Transaction.query.filter(
        Transaction.therapist_id == therapist.id,
        Transaction.status.in_([TransactionStatus.therapist_confirmed, TransactionStatus.in_service])
    ).first()
    
    if tx:
        emit("therapist_current_transaction", serialize_transaction(tx))
    else:
        emit("therapist_current_transaction", None)


@socketio.on("therapist_finish_service")
def therapist_finish_service(data):
    tx_id = int(data.get("transaction_id"))
    tx = db.session.get(Transaction, tx_id)
    if not tx:
        emit("error", {"error": "Transaction not found"})
        return

    tx.status = TransactionStatus.finished
    tx.service_finish_at = datetime.now()  # Use local time instead of UTC
    db.session.commit()

    emit("therapist_finish_result", {"ok": True, "transaction": serialize_transaction(tx)})

    emit("cashier_queue_updated", broadcast=True, to="cashier_queue")
    emit("monitor_updated", broadcast=True, to="monitor")
    emit("monitor_service_finished", {"code": tx.code, "therapist": tx.therapist.name if tx.therapist else None}, to="monitor")


@socketio.on("cashier_claim_next")
def cashier_claim_next(data):
    cashier, _ = get_current_cashier()
    if not cashier:
        emit("cashier_claim_result", {"ok": False, "error": "Login required"})
        return

    tx: Transaction | None = (
        Transaction.query
        .filter_by(status=TransactionStatus.finished)
        .order_by(Transaction.service_finish_at.asc())
        .with_for_update(skip_locked=True)
        .first()
    )

    if not tx:
        emit("cashier_claim_result", {"ok": False, "error": "No finished customers."})
        return

    tx.status = TransactionStatus.awaiting_payment
    tx.assigned_cashier = cashier
    tx.cashier_claimed_at = datetime.now()  # Use local time instead of UTC
    db.session.commit()

    emit("monitor_payment_counter", {"code": tx.code, "cashier": cashier.name, "counter": cashier.counter_number}, to="monitor")
    emit("cashier_queue_updated", broadcast=True, to="cashier_queue")
    emit("cashier_claim_result", {"ok": True, "transaction": serialize_transaction(tx)})


@socketio.on("cashier_pay")
def cashier_pay(data):
    amount_paid = float(data.get("amount_paid"))
    # Automatically set method to "cash" - no need to get from data
    method = "cash"

    cashier, _ = get_current_cashier()
    if not cashier:
        emit("cashier_pay_result", {"ok": False, "error": "Login required"})
        return

    tx_id = int(data.get("transaction_id"))
    tx = db.session.get(Transaction, tx_id)
    if not tx or tx.status not in (TransactionStatus.awaiting_payment, TransactionStatus.paying):
        emit("cashier_pay_result", {"ok": False, "error": "Invalid transaction state"})
        return

    tx.status = TransactionStatus.paying
    amount_due = tx.total_amount
    if amount_paid < amount_due:
        emit("cashier_pay_result", {"ok": False, "error": "Insufficient payment"})
        return

    change = round(amount_paid - amount_due, 2)

    payment = Payment(
        transaction_id=tx.id,
        cashier_id=cashier.id,
        amount_due=amount_due,
        amount_paid=amount_paid,
        change_amount=change,
        method=method,  # Always "cash"
    )
    db.session.add(payment)
    tx.status = TransactionStatus.paid
    tx.paid_at = datetime.now()  # Use local time instead of UTC
    db.session.commit()

    emit("monitor_updated", broadcast=True, to="monitor")
    emit("monitor_payment_completed", {"code": tx.code, "cashier": cashier.name}, to="monitor")
    emit("cashier_queue_updated", broadcast=True, to="cashier_queue")
    emit("cashier_pay_result", {"ok": True, "transaction": serialize_transaction(tx)})
