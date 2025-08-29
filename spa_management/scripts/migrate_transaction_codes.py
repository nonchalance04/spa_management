#!/usr/bin/env python3
"""
Migration script to update transaction codes from alphanumeric to sequential integers.
This script:
1. Creates the transaction_counter table
2. Updates existing transaction codes to sequential integers
3. Modifies the transaction code column length
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models import Transaction, TransactionCounter
from sqlalchemy import text

def migrate_transaction_codes():
    app = create_app()
    
    with app.app_context():
        print("Starting transaction code migration...")
        
        # Create the transaction_counter table if it doesn't exist
        print("Creating transaction_counter table...")
        db.create_all()
        
        # Get all existing transactions ordered by creation date
        existing_transactions = Transaction.query.order_by(Transaction.created_at.asc()).all()
        
        if existing_transactions:
            print(f"Found {len(existing_transactions)} existing transactions to migrate...")
            
            # Update existing transaction codes to sequential integers
            for i, transaction in enumerate(existing_transactions, start=1):
                old_code = transaction.code
                new_code = f"{i:04d}"
                transaction.code = new_code
                print(f"Updated transaction {transaction.id}: {old_code} -> {new_code}")
            
            # Initialize the counter to the next number after the last migrated transaction
            next_number = len(existing_transactions) + 1
        else:
            print("No existing transactions found.")
            next_number = 1
        
        # Create or update the counter record
        counter = TransactionCounter.query.first()
        if counter:
            counter.next_number = next_number
            print(f"Updated counter to start from {next_number}")
        else:
            counter = TransactionCounter(next_number=next_number)
            db.session.add(counter)
            print(f"Created new counter starting from {next_number}")
        
        # Commit all changes
        db.session.commit()
        
        print("Migration completed successfully!")
        print(f"Next transaction will use code: {next_number:04d}")

if __name__ == "__main__":
    migrate_transaction_codes()
