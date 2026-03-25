from sqlalchemy import Column, Integer, String, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from database import Base

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    asset_tag = Column(String(50), unique=True, index=True, nullable=False) # 設備辨識碼
    name = Column(String(100), nullable=False) # 設備名稱
    department = Column(String(100)) # 部門
    assignee = Column(String(100)) # 使用人
    checkout_date = Column(Date, nullable=True) # 領用日期
    return_date = Column(Date, nullable=True) # 歸還日期
    system_model = Column(String(100)) # 系統型號
    office_number = Column(String(50)) # 辦公室號碼
    notes = Column(Text) # 備註
    status = Column(String(50), default="Available") # 狀態: Available, In Use

    history_records = relationship("DeviceHistory", back_populates="device")


class DeviceHistory(Base):
    __tablename__ = "device_history"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    action = Column(String(50), nullable=False) # 'Checkout', 'Return', 'Add', 'Edit'
    assignee = Column(String(100)) # 該次操作對應的使用人
    action_date = Column(DateTime, default=datetime.datetime.utcnow) # 操作時間
    notes = Column(Text) # 備註

    device = relationship("Device", back_populates="history_records")
