from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class TelemetryCreate(BaseModel):
  device_id: str = Field(
      ..., min_length=3, max_length=64, examples=["EAF-FURNACE-01"]
  )
  ts_shell_temp_c: float = Field(
      ...,
      ge=-50.0,
      le=3000.0,
      description="Shell surface temperature in Celsius",
  )
  b_ext_leakage_flux_mt: float = Field(
      ...,
      ge=0.0,
      le=500.0,
      description="External magnetic leakage flux in millitesla",
  )
  v_n_neutral_voltage_v: float = Field(
      ..., ge=0.0, le=50000.0, description="Neutral point voltage in Volts"
  )
  i_n_coil_current_a: float = Field(
      ..., ge=0.0, le=100000.0, description="Coil/electrode current in Amperes"
  )
  delta_pc_cooling_pressure_bar: float = Field(
      ...,
      ge=0.0,
      le=100.0,
      description="Cooling differential pressure in bar",
  )


class TelemetryResponse(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: int
  device_id: str
  ts_shell_temp_c: float
  b_ext_leakage_flux_mt: float
  v_n_neutral_voltage_v: float
  i_n_coil_current_a: float
  delta_pc_cooling_pressure_bar: float
  timestamp: datetime


class MaintenanceEventCreate(BaseModel):
  device_id: str = Field(..., min_length=3, max_length=64)
  event_type: str = Field(
      ..., examples=["CLASS_A_REFRACTORY", "CLASS_B_ARCING", "CLASS_C_COOLING"]
  )
  start_time: datetime
  end_time: Optional[datetime] = None
  description: Optional[str] = None


class MaintenanceEventResponse(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: int
  device_id: str
  event_type: str
  start_time: datetime
  end_time: Optional[datetime]
  description: Optional[str]


class TelemetryStats(BaseModel):
  device_id: str
  sample_count: int
  avg_shell_temp_c: float
  max_shell_temp_c: float
  avg_coil_current_a: float
  max_coil_current_a: float
  min_cooling_pressure_bar: float
  thermal_anomaly_detected: bool