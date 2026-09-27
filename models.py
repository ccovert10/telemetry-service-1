from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Index,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship
from database import Base


class SensorTelemetry(Base):
  __tablename__ = "sensor_telemetry"

  id = Column(Integer, primary_key=True, index=True)
  device_id = Column(String(64), nullable=False)

  # 5 Physical Channels
  ts_shell_temp_c = Column(
      Float, nullable=False
  )  # Shell temp (Fourier conduction limit)
  b_ext_leakage_flux_mt = Column(
      Float, nullable=False
  )  # Magnetic leakage flux (mT)
  v_n_neutral_voltage_v = Column(Float, nullable=False)  # Neutral voltage (V)
  i_n_coil_current_a = Column(
      Float, nullable=False
  )  # Primary coil / electrode current (A)
  delta_pc_cooling_pressure_bar = Column(
      Float, nullable=False
  )  # Differential water pressure (bar)

  timestamp = Column(
      DateTime(timezone=True),
      default=lambda: datetime.now(timezone.utc),
      nullable=False,
  )

  # Composite B-Tree Index for high-throughput time-series slicing
  __table_args__ = (
      Index("ix_sensor_device_timestamp", "device_id", "timestamp"),
  )


class MaintenanceEvent(Base):
  __tablename__ = "maintenance_events"

  id = Column(Integer, primary_key=True, index=True)
  device_id = Column(String(64), nullable=False, index=True)
  event_type = Column(
      String(32), nullable=False
  )  # e.g., 'CLASS_A_REFRACTORY', 'CLASS_B_ARCING', 'CLASS_C_COOLING'
  start_time = Column(DateTime(timezone=True), nullable=False)
  end_time = Column(DateTime(timezone=True), nullable=True)
  description = Column(Text, nullable=True)

  __table_args__ = (Index("ix_maint_device_time", "device_id", "start_time"),)