# SPA Management System (Flask + Socket.IO + MySQL)

Real-time multi-role SPA management system (Customer, Therapist, Cashier, Monitor) with FIFO queues, concurrency-safe claiming, live updates, and payments.

## Tech Stack

- Python Flask
- Flask-SocketIO (eventlet)
- SQLAlchemy ORM (via Flask-SQLAlchemy) with MySQL (PyMySQL driver)
- HTML, CSS, Vanilla JS

## Setup

1. Install Python 3.10+.
2. Install MySQL (XAMPP) and create database `spa_db`.
3. Copy `.env.example` to `.env` and adjust values.
4. Create and activate a virtualenv.
5. Install deps:
   ```bash
   pip install -r requirements.txt
   ```
6. Initialize DB and seed sample data:
   - Start the server once:
     ```bash
     python run.py
     ```
   - In browser, open `http://localhost:5000/initdb` to create tables and seed.

## Run

```bash
python run.py
```

- Customer: `http://localhost:5000/customer`
- Therapist: `http://localhost:5000/therapist`
- Cashier: `http://localhost:5000/cashier`
- Monitor: `http://localhost:5000/monitor`
