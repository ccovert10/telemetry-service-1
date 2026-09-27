import random
import time
import httpx

API_URL = "http://127.0.0.1:8000/api/v1/telemetry"
DEVICES = ["EAF-FURNACE-01", "EAF-FURNACE-02", "LF-REFINER-01"]


def generate_reading(device_id: str) -> dict:
    # Baseline nominal operation
    temp = round(random.gauss(1540.0, 12.0), 2)
    flux = round(random.gauss(12.5, 0.8), 2)
    voltage = round(random.gauss(680.0, 10.0), 2)
    current = round(random.gauss(4250.0, 75.0), 2)
    pressure = round(random.gauss(4.2, 0.15), 2)

    # 12% probability of operational anomaly (thermal spike or cooling drop)
    if random.random() < 0.12:
        temp += round(random.uniform(70.0, 110.0), 2)
        flux += round(random.uniform(5.0, 12.0), 2)
        current += round(random.uniform(350.0, 800.0), 2)
        pressure -= round(random.uniform(0.8, 1.5), 2)

    return {
        "device_id": device_id,
        "ts_shell_temp_c": temp,
        "b_ext_leakage_flux_mt": max(0.0, flux),
        "v_n_neutral_voltage_v": max(0.0, voltage),
        "i_n_coil_current_a": max(0.0, current),
        "delta_pc_cooling_pressure_bar": max(0.0, pressure),
    }


def main():
    print("=" * 70)
    print("5-Channel Industrial Gateway Simulator (Press Ctrl+C to stop)")
    print(f"Target: {API_URL}")
    print("=" * 70)

    with httpx.Client(timeout=5.0) as client:
        while True:
            for device in DEVICES:
                payload = generate_reading(device)
                try:
                    resp = client.post(API_URL, json=payload)
                    if resp.status_code == 201:
                        flag = "[ALERT]" if payload["ts_shell_temp_c"] > 1600.0 else "       "
                        print(
                            f"{device} | Ts: {payload['ts_shell_temp_c']:7.2f}°C | "
                            f"In: {payload['i_n_coil_current_a']:7.2f}A | "
                            f"ΔPc: {payload['delta_pc_cooling_pressure_bar']:4.2f}bar {flag}"
                        )
                except httpx.ConnectError:
                    print("Connection failed. Ensure API server is listening on port 8000.")
            time.sleep(2.0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Simulator stopped.")