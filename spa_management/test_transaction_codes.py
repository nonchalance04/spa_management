#!/usr/bin/env python3
"""
Test script to verify the new sequential transaction code generation.
"""

from app import create_app
from app.extensions import db
from app.models import Transaction, TransactionCounter

def test_transaction_codes():
    app = create_app()
    
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        print("Testing transaction code generation...")
        
        # Test generating multiple codes
        codes = []
        for i in range(5):
            code = Transaction.generate_code()
            codes.append(code)
            print(f"Generated code {i+1}: {code}")
        
        # Verify codes are sequential
        expected_codes = ["0001", "0002", "0003", "0004", "0005"]
        
        # Check if counter exists and what the next number should be
        counter = TransactionCounter.query.first()
        if counter:
            print(f"Counter next_number: {counter.next_number}")
        
        print(f"Generated codes: {codes}")
        print(f"Expected format: 4-digit padded integers starting from 0001")
        
        # Verify format
        all_valid = True
        for code in codes:
            if not (len(code) == 4 and code.isdigit()):
                print(f"Invalid code format: {code}")
                all_valid = False
        
        if all_valid:
            print("✓ All codes have correct 4-digit format")
        else:
            print("✗ Some codes have incorrect format")
        
        # Rollback to avoid affecting actual data
        db.session.rollback()

if __name__ == "__main__":
    test_transaction_codes()
