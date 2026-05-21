from fastapi import FastAPI, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from .models import MessageLog
from .tasks import poll_soroush
from .config import settings

# Initialize database
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Soroush Syncer", description="Synchronize Soroush messages to multiple platforms")

@app.get("/")
def read_root():
    return {"status": "running", "version": "1.0.0"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Check DB connection
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.post("/sync/trigger")
def trigger_sync(background_tasks: BackgroundTasks):
    """Manually trigger the polling task."""
    poll_soroush.delay()
    return {"message": "Sync task triggered in background"}

@app.get("/logs")
def get_logs(limit: int = 10, db: Session = Depends(get_db)):
    """Retrieve recent sync logs."""
    return db.query(MessageLog).order_by(MessageLog.synced_at.desc()).limit(limit).all()
