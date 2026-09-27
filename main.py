from datetime import datetime, timezone, timedelta
from typing import List
from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

import models
import schemas
from database import get_db

app = FastAPI(
    title="Industrial Furnace Edge Telemetry & Diagnostics API",
    version="1.0.0",
    description="High-integrity telemetry ingestion and diagnostics platform for Electric Arc and Ladle Furnaces.",
)


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc)}


@app.post(
    "/api/v1/telemetry",
    response_model=schemas.TelemetryResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Telemetry"],
)
def ingest_telemetry(
    reading: schemas.TelemetryCreate, db: Session = Depends(get_db)
):
    db_record = models.SensorTelemetry(
        device_id=reading.device_id,
        ts_shell_temp_c=reading.ts_shell_temp_c,
        b_ext_leakage_flux_mt=reading.b_ext_leakage_flux_mt,
        v_n_neutral_voltage_v=reading.v_n_neutral_voltage_v,
        i_n_coil_current_a=reading.i_n_coil_current_a,
        delta_pc_cooling_pressure_bar=reading.delta_pc_cooling_pressure_bar,
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


@app.get(
    "/api/v1/telemetry/{device_id}",
    response_model=List[schemas.TelemetryResponse],
    tags=["Telemetry"],
)
def get_device_telemetry(
    device_id: str,
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    records = (
        db.query(models.SensorTelemetry)
        .filter(models.SensorTelemetry.device_id == device_id)
        .order_by(models.SensorTelemetry.timestamp.desc())
        .limit(limit)
        .all()
    )
    return records


@app.get(
    "/api/v1/telemetry/{device_id}/stats",
    response_model=schemas.TelemetryStats,
    tags=["Analytics"],
)
def get_device_stats(
    device_id: str,
    hours: float = Query(
        default=1.0, ge=0.01, le=168.0, description="Window size in hours"
    ),
    db: Session = Depends(get_db),
):
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

    stats = (
        db.query(
            func.count(models.SensorTelemetry.id).label("sample_count"),
            func.avg(models.SensorTelemetry.ts_shell_temp_c).label(
                "avg_shell_temp_c"
            ),
            func.max(models.SensorTelemetry.ts_shell_temp_c).label(
                "max_shell_temp_c"
            ),
            func.avg(models.SensorTelemetry.i_n_coil_current_a).label(
                "avg_coil_current_a"
            ),
            func.max(models.SensorTelemetry.i_n_coil_current_a).label(
                "max_coil_current_a"
            ),
            func.min(
                models.SensorTelemetry.delta_pc_cooling_pressure_bar
            ).label("min_cooling_pressure_bar"),
        )
        .filter(
            models.SensorTelemetry.device_id == device_id,
            models.SensorTelemetry.timestamp >= cutoff_time,
        )
        .one()
    )

    if not stats.sample_count or stats.sample_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No telemetry found for device '{device_id}' in the last {hours} hour(s).",
        )

    # Fourier conduction boundary threshold check (> 1600 C)
    anomaly_detected = (
        stats.max_shell_temp_c is not None and stats.max_shell_temp_c > 1600.0
    )

    return schemas.TelemetryStats(
        device_id=device_id,
        sample_count=stats.sample_count,
        avg_shell_temp_c=round(float(stats.avg_shell_temp_c), 2),
        max_shell_temp_c=round(float(stats.max_shell_temp_c), 2),
        avg_coil_current_a=round(float(stats.avg_coil_current_a), 2),
        max_coil_current_a=round(float(stats.max_coil_current_a), 2),
        min_cooling_pressure_bar=round(
            float(stats.min_cooling_pressure_bar), 2
        ),
        thermal_anomaly_detected=anomaly_detected,
    )


@app.post(
    "/api/v1/maintenance",
    response_model=schemas.MaintenanceEventResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Maintenance"],
)
def log_maintenance_event(
    event: schemas.MaintenanceEventCreate, db: Session = Depends(get_db)
):
    db_event = models.MaintenanceEvent(
        device_id=event.device_id,
        event_type=event.event_type,
        start_time=event.start_time,
        end_time=event.end_time,
        description=event.description,
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event