from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime

import models
import schemas
from database import engine, get_db

# 自動建立資料表 (通常正式環境會使用 Alembic 遷移，此處為快速開發)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Digital Asset Management System (DAMS) API")

# 設定 CORS，讓前方 Vanilla JS 可以順利呼叫 API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 允許所有來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to DAMS API"}

@app.post("/devices/", response_model=schemas.DeviceSchema)
def create_device(device: schemas.DeviceCreate, db: Session = Depends(get_db)):
    db_device = models.Device(**device.dict())
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    
    # 紀錄新增歷史
    history = models.DeviceHistory(
        device_id=db_device.id,
        action="Add",
        assignee=db_device.assignee,
        notes="Newly added equipment"
    )
    db.add(history)
    db.commit()
    
    return db_device

@app.get("/devices/", response_model=List[schemas.DeviceSchema])
def read_devices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    devices = db.query(models.Device).offset(skip).limit(limit).all()
    return devices

@app.get("/devices/{device_id}", response_model=schemas.DeviceWithHistorySchema)
def read_device(device_id: int, db: Session = Depends(get_db)):
    db_device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if db_device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return db_device

@app.put("/devices/{device_id}/checkout", response_model=schemas.DeviceSchema)
def checkout_device(device_id: int, assignee: str, department: str, checkout_date: date, db: Session = Depends(get_db)):
    db_device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if not db_device:
        raise HTTPException(status_code=404, detail="Device not found")
    if db_device.status == "In Use":
        raise HTTPException(status_code=400, detail="Device is already in use")
        
    db_device.status = "In Use"
    db_device.assignee = assignee
    db_device.department = department
    db_device.checkout_date = checkout_date
    db_device.return_date = None # 清空歸還日
    
    # 新增歷史紀錄
    history = models.DeviceHistory(
        device_id=db_device.id,
        action="Checkout",
        assignee=assignee,
        notes=f"Checked out to {assignee} ({department})"
    )
    db.add(history)
    db.commit()
    db.refresh(db_device)
    return db_device

@app.put("/devices/{device_id}/return", response_model=schemas.DeviceSchema)
def return_device(device_id: int, return_date: date, db: Session = Depends(get_db)):
    db_device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if not db_device:
        raise HTTPException(status_code=404, detail="Device not found")
    if db_device.status == "Available":
        raise HTTPException(status_code=400, detail="Device is already available")
        
    old_assignee = db_device.assignee
    db_device.status = "Available"
    db_device.return_date = return_date
    
    # 新增歷史紀錄
    history = models.DeviceHistory(
        device_id=db_device.id,
        action="Return",
        assignee=old_assignee,
        notes=f"Returned by {old_assignee}"
    )
    db.add(history)
    db.commit()
    db.refresh(db_device)
    return db_device

@app.delete("/devices/{device_id}")
def delete_device(device_id: int, db: Session = Depends(get_db)):
    db_device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if not db_device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # 刪除相關歷史 (cascade deletion 較理想，此處手動清理)
    db.query(models.DeviceHistory).filter(models.DeviceHistory.device_id == device_id).delete()
    db.delete(db_device)
    db.commit()
    return {"message": "Device deleted successfully"}