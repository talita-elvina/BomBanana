import json
import joblib
import pandas as pd
import paho.mqtt.client as mqtt

PROJECT_ID = "bombanana_kelompok16_4951"
BROKER = "broker.hivemq.com"
PORT = 8883

TOPIC_A = PROJECT_ID + "/phone/A"
TOPIC_B = PROJECT_ID + "/phone/B"

FILE_MODEL = "model/movement_model.pkl"

# Memuat model AI yang sudah dilatih
model = joblib.load(FILE_MODEL)

kolom_sensor = [
    "ax", "ay", "az",
    "gx", "gy", "gz"
]


def saat_pesan(client, userdata, pesan):
    try:
        isi = json.loads(pesan.payload.decode())

        hp = isi["hp"]

        # mengambil enam nilai sensor
        data_sensor = pd.DataFrame([[
            float(isi["ax"]),
            float(isi["ay"]),
            float(isi["az"]),
            float(isi["gx"]),
            float(isi["gy"]),
            float(isi["gz"])
        ]], columns=kolom_sensor)

        # meminta AI memprediksi gerakan
        hasil = model.predict(data_sensor)[0]

        # menampilkan hasil prediksi
        print(
            "HP:", hp,
            "| Prediksi AI:", hasil
        )

    except (ValueError, TypeError, KeyError, json.JSONDecodeError) as e:
        print("Data tidak valid:", e)


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    client.tls_set()
    client.on_message = saat_pesan

    try:
        client.connect(BROKER, PORT, 60)

        client.subscribe([
            (TOPIC_A, 1),
            (TOPIC_B, 1)
        ])

        print("=== PENGUJIAN MODEL AI BOM-BANANA ===")
        print("Model berhasil dimuat.")
        print("Menunggu data sensor dari kedua HP...")
        print("Tekan Ctrl+C untuk berhenti.\n")

        client.loop_forever()

    except KeyboardInterrupt:
        print("\nPengujian dihentikan.")

    except Exception as e:
        print("Terjadi kesalahan:", e)

    finally:
        client.disconnect()


if __name__ == "__main__":
    main()