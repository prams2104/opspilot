import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Create engine
engine = create_engine("sqlite:///../../opspilot.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define models inline
class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(String, unique=True, index=True)
    trader = Column(String)
    instrument = Column(String)
    quantity = Column(Float)
    price = Column(Float)
    side = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")

class LedgerEntry(Base):
    __tablename__ = "ledger"
    
    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(String, index=True)
    amount = Column(Float)
    currency = Column(String)
    entry_type = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    reconciled = Column(Boolean, default=False)

# Create tables
Base.metadata.create_all(bind=engine)

def load_trades():
    db = SessionLocal()
    
    # Clear existing data
    db.query(Trade).delete()
    db.commit()
    
    # Read CSV
    df = pd.read_csv('../../data/sample_trades.csv')
    
    for _, row in df.iterrows():
        trade = Trade(
            trade_id=row['trade_id'],
            trader=row['trader'],
            instrument=row['instrument'],
            quantity=float(row['quantity']),
            price=float(row['price']),
            side=row['side'],
            timestamp=datetime.fromisoformat(str(row['timestamp'])),
            status='pending'
        )
        db.add(trade)
    
    db.commit()
    print(f"Loaded {len(df)} trades")
    db.close()

def load_ledger():
    db = SessionLocal()
    
    # Clear existing data
    db.query(LedgerEntry).delete()
    db.commit()
    
    # Read CSV
    df = pd.read_csv('../../data/sample_ledger.csv')
    
    for _, row in df.iterrows():
        entry = LedgerEntry(
            trade_id=row['trade_id'],
            amount=float(row['amount']),
            currency=row['currency'],
            entry_type=row['entry_type'],
            timestamp=datetime.fromisoformat(str(row['timestamp'])),
            reconciled=False
        )
        db.add(entry)
    
    db.commit()
    print(f"Loaded {len(df)} ledger entries")
    db.close()

if __name__ == "__main__":
    print("Loading sample data...")
    load_trades()
    load_ledger()
    print("Done! Start the server and refresh the frontend.")