from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime
import openpyxl
from io import BytesIO

import models
import schemas
from database import engine, get_db

# 自動建立資料表
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Digital Asset Management System (DAMS) API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root(): return {"message": "DAMS API with Excel Support"}

# ----------------
# Employee & Office Endpoints
# ----------------
@app.get("/employees/", response_model=List[schemas.EmployeeSchema])
def get_employees(db: Session = Depends(get_db)):
    return db.query(models.Employee).all()

@app.post("/employees/", response_model=schemas.EmployeeSchema)
def create_employee(emp: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    db_emp = models.Employee(**emp.dict())
    db.add(db_emp)
    db.commit()
    db.refresh(db_emp)
    return db_emp

@app.delete("/employees/{emp_id}")
def delete_employee(emp_id: int, db: Session = Depends(get_db)):
    db_emp = db.query(models.Employee).filter(models.Employee.id == emp_id).first()
    if not db_emp: raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(db_emp)
    db.commit()
    return {"message": "Deleted"}

@app.get("/offices/", response_model=List[schemas.OfficeSchema])
def get_offices(db: Session = Depends(get_db)):
    return db.query(models.Office).all()

@app.post("/offices/", response_model=schemas.OfficeSchema)
def create_office(off: schemas.OfficeCreate, db: Session = Depends(get_db)):
    db_off = models.Office(**off.dict())
    db.add(db_off)
    db.commit()
    db.refresh(db_off)
    return db_off

@app.delete("/offices/{off_id}")
def delete_office(off_id: int, db: Session = Depends(get_db)):
    db_off = db.query(models.Office).filter(models.Office.id == off_id).first()
    if not db_off: raise HTTPException(status_code=404, detail="Office not found")
    db.delete(db_off)
    db.commit()
    return {"message": "Deleted"}

@app.get("/departments/", response_model=List[schemas.DepartmentSchema])
def get_departments(db: Session = Depends(get_db)):
    return db.query(models.Department).all()

@app.post("/departments/", response_model=schemas.DepartmentSchema)
def create_department(dept: schemas.DepartmentCreate, db: Session = Depends(get_db)):
    db_dept = models.Department(**dept.dict())
    db.add(db_dept)
    db.commit()
    db.refresh(db_dept)
    return db_dept

@app.delete("/departments/{dept_id}")
def delete_department(dept_id: int, db: Session = Depends(get_db)):
    db_dept = db.query(models.Department).filter(models.Department.id == dept_id).first()
    if not db_dept: raise HTTPException(status_code=404, detail="Department not found")
    db.delete(db_dept)
    db.commit()
    return {"message": "Deleted"}

# ----------------
# Device Endpoints
# ----------------
@app.post("/devices/", response_model=schemas.DeviceSchema)
def create_device(device: schemas.DeviceCreate, db: Session = Depends(get_db)):
    db_device = models.Device(**device.dict())
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    
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
    return db.query(models.Device).offset(skip).limit(limit).all()

@app.get("/devices/{device_id}", response_model=schemas.DeviceWithHistorySchema)
def read_device(device_id: int, db: Session = Depends(get_db)):
    db_device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if not db_device: raise HTTPException(status_code=404, detail="Device not found")
    return db_device

@app.put("/devices/{device_id}/checkout", response_model=schemas.DeviceSchema)
def checkout_device(device_id: int, assignee: str, department: str, checkout_date: date, office_number: str = "", db: Session = Depends(get_db)):
    db_device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if not db_device: raise HTTPException(status_code=404, detail="Device not found")
    
    db_device.status = "In Use"
    db_device.assignee = assignee
    db_device.department = department
    if office_number: db_device.office_number = office_number
    db_device.checkout_date = checkout_date
    db_device.return_date = None
    
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
    if not db_device: raise HTTPException(status_code=404, detail="Device not found")
    
    old_assignee = db_device.assignee
    db_device.status = "Available"
    db_device.return_date = return_date
    
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
    if not db_device: raise HTTPException(status_code=404, detail="Device not found")
    db.query(models.DeviceHistory).filter(models.DeviceHistory.device_id == device_id).delete()
    db.delete(db_device)
    db.commit()
    return {"message": "Deleted"}

# ----------------
# Excel Import Endpoint
# ----------------
def parse_date(val):
    if not val: return None
    if isinstance(val, datetime): return val.date()
    try:
        from dateutil import parser
        return parser.parse(str(val)).date()
    except:
        return None

@app.post("/devices/import")
async def import_devices_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    wb = openpyxl.load_workbook(BytesIO(content), data_only=True)
    sheet = wb.active
    rows = list(sheet.iter_rows(values_only=True))
    
    if len(rows) < 2: raise HTTPException(status_code=400, detail="Excel content is empty or invalid.")
    
    headers = [str(h).strip() if h else "" for h in rows[0]]
    imported_count = 0
    
    for row in rows[1:]:
        data = dict(zip(headers, row))
        tag = data.get("設備識別碼")
        if not tag: continue # Required field
        
        # Merge notes
        notes_arr = []
        if data.get("說明"): notes_arr.append(f"說明: {data.get('說明')}")
        if data.get("備註"): notes_arr.append(f"備註: {data.get('備註')}")
        final_notes = "\n".join(notes_arr)

        dept = str(data.get("部門") or "").strip()
        assignee = str(data.get("指派給") or "").strip()
        office = str(data.get("辦公室") or "").strip()
        co_date = parse_date(data.get("領用"))
        rt_date = parse_date(data.get("歸還"))

        # Auto create missing Department
        if dept:
            if not db.query(models.Department).filter_by(name=dept).first():
                db.add(models.Department(name=dept))
                db.commit()

        # Auto create missing Employee
        if assignee:
            if not db.query(models.Employee).filter_by(name=assignee).first():
                db.add(models.Employee(name=assignee, department=dept))
                db.commit()

        # Auto create missing Office
        if office:
            if not db.query(models.Office).filter_by(name=office).first():
                db.add(models.Office(name=office))
                db.commit()

        # Determine status
        status = "Available"
        if co_date and not rt_date:
            status = "In Use"
        elif co_date and rt_date and co_date > rt_date:
            status = "In Use"
            
        # Create Device if not exists
        exist_dev = db.query(models.Device).filter_by(asset_tag=str(tag).strip()).first()
        if not exist_dev:
            new_dev = models.Device(
                asset_tag=str(tag).strip(),
                name=str(data.get("項目名稱") or "未命名"),
                system_model=str(data.get("型號") or ""),
                office_number=office,
                department=dept,
                assignee=assignee,
                checkout_date=co_date,
                return_date=rt_date,
                notes=final_notes,
                status=status
            )
            db.add(new_dev)
            db.commit()
            imported_count += 1
            
            # History track
            history = models.DeviceHistory(
                device_id=new_dev.id,
                action="Imported",
                assignee=assignee,
                notes="Legacy data imported"
            )
            db.add(history)
            db.commit()
            
    return {"message": f"Successfully imported {imported_count} devices."}