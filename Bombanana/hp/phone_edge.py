import json
import subprocess
import sys
import time
import paho.mqtt.client as mqtt

PROJECT_ID = "bombanana_kelompok16_4951"
BROKER = "broker.hivemq.com"
PORT = 8883

if len(sys.argv) != 2 or sys.argv[1] not in ["A", "B"]:
    print("Cara pakai: python phone_edge.py A  atau  python phone_edge.py B")
    sys.exit()

NAMA_HP = sys.argv[1]
TOPIC = PROJECT_ID + "/phone/" + NAMA_HP

def baca_sensor(nama_sensor):
    """Meminta satu data sensor dari Termux:API."""
    hasil = subprocess.run(
        ["termux-sensor", "-s", nama_sensor, "-n", "1"],
        capture_output=True, text=True
    )
    data = json.loads(hasil.stdout)

    # Termux mengembalikan data dalam bentuk JSON.
    sensor = data.get(nama_sensor)
    if sensor is None and data:
        sensor = list(data.values())[0]

    nilai = sensor.get("values", [0, 0, 0])
    return nilai

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.tls_set()
client.connect(BROKER, PORT, 60)
client.loop_start()

print("HP", NAMA_HP, "siap. Gerakkan HP untuk mengirim data.")
print("Tekan Ctrl+C untuk berhenti.")

try:
    while True:
        # Sensor pertama: accelerometer, untuk mendeteksi guncangan.
        akselerasi = baca_sensor("accelerometer")

        # Sensor kedua: gyroscope, untuk mendeteksi putaran HP.
        putaran = baca_sensor("gyroscope")

        pesan = {
            "hp": NAMA_HP,
            "ax": float(akselerasi[0]),
            "ay": float(akselerasi[1]),
            "az": float(akselerasi[2]),
            "gx": float(putaran[0]),
            "gy": float(putaran[1]),
            "gz": float(putaran[2]),
            "waktu": time.time()
        }

        client.publish(TOPIC, json.dumps(pesan), qos=1)
        time.sleep(0.3)

except KeyboardInterrupt:
    print("\nProgram HP dihentikan.")
finally:
    client.loop_stop()
    client.disconnect()
