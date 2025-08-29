from flask import Blueprint, jsonify
from ..models import Transaction, TransactionStatus

snapshot_bp = Blueprint('monitor_snapshot', __name__)


@snapshot_bp.get('/monitor_snapshot/')
def monitor_snapshot():
    waiting = Transaction.query.filter_by(status=TransactionStatus.pending_therapist).order_by(Transaction.selection_confirmed_at.asc()).all()
    confirmed = Transaction.query.filter_by(status=TransactionStatus.therapist_confirmed).order_by(Transaction.therapist_confirmed_at.asc()).all()
    in_service = Transaction.query.filter_by(status=TransactionStatus.in_service).order_by(Transaction.service_start_at.asc()).all()
    finished = Transaction.query.filter_by(status=TransactionStatus.finished).order_by(Transaction.service_finish_at.asc()).all()
    paid = Transaction.query.filter_by(status=TransactionStatus.paid).order_by(Transaction.paid_at.asc()).all()

    def s(tx):
        return {
            'id': tx.id,
            'code': tx.code,
            'customer_name': tx.customer_name,
            'therapist': tx.therapist.name if tx.therapist else None,
            'room_number': tx.room_number,
            'total_amount': tx.total_amount,
            'total_duration_minutes': tx.total_duration_minutes,
            'cashier': tx.assigned_cashier.name if tx.assigned_cashier else None,
            'counter': tx.assigned_cashier.counter_number if tx.assigned_cashier else None,
            'selected_services': [
                {
                    'service_name': item.service.service_name,
                    'price': item.price,
                    'duration_minutes': item.duration_minutes,
                    'classification_name': item.service_classification.classification_name
                } for item in tx.items
            ]
        }

    payment_assigned = Transaction.query.filter_by(status=TransactionStatus.awaiting_payment).order_by(Transaction.cashier_claimed_at.asc()).all()

    return jsonify({
        'waiting': [s(t) for t in waiting],
        'confirmed': [s(t) for t in confirmed],
        'in_service': [s(t) for t in in_service],
        'finished': [s(t) for t in finished],
        'payment_assigned': [s(t) for t in payment_assigned],
        'paid': [s(t) for t in paid],
    })
