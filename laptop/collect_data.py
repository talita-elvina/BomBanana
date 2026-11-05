import json
import csv
import time
import os
import threading
import paho.mqtt.client as mqtt

PROJECT_ID = "bombanana_kelompok16_4951"
BROKER = "broker.hivemq.com"
PORT = 8883

TOPIC_A = PROJECT_ID + "/phone/A"
TOPIC_B = PROJECT_ID + "/phone/B"

FILE_DATASET = "dataset/data_sensor.csv"

hp_dipilih = None
label_aktif = None
sedang_merekam = False

kunci = threading.Lock()


def saat_pesan(client, userdata, pesan):
    global hp_dipilih, label_aktif, sedang_merekam

    try:
        isi = json.loads(pesan.payload.decode())

        hp = isi.get("hp")

        with kunci:
            if not sedang_merekam:
                return

            if hp != hp_dipilih:
                return

            label = label_aktif

        baris = {
            "hp": hp,
            "ax": float(isi["ax"]),
            "ay": float(isi["ay"]),
            "az": float(isi["az"]),
            "gx": float(isi["gx"]),
            "gy": float(isi["gy"]),
            "gz": float(isi["gz"]),
            "label": label
        }

        with open(FILE_DATASET, "a", newline="") as file:
            penulis = csv.DictWriter(
                file,
                fieldnames=[
                    "hp", "ax", "ay", "az",
                    "gx", "gy", "gz", "label"
                ]
            )
            penulis.writerow(baris)

    except (ValueError, TypeError, KeyError, json.JSONDecodeError) as e:
        print("Data tidak valid:", e)


def main():
    global hp_dipilih, label_aktif, sedang_merekam

    os.makedirs("dataset", exist_ok=True)

    # Membuat file CSV jika belum tersedia.
    if not os.path.exists(FILE_DATASET):
        with open(FILE_DATASET, "w", newline="") as file:
            penulis = csv.writer(file)
            penulis.writerow([
                "hp", "ax", "ay", "az",
                "gx", "gy", "gz", "label"
            ])

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.tls_set()
    client.on_message = saat_pesan

    try:
        client.connect(BROKER, PORT, 60)

        client.subscribe([
            (TOPIC_A, 1),
            (TOPIC_B, 1)
        ])

        client.loop_start()

        print("=== PENGUMPULAN DATA BOM-BANANA ===")
        print("Menunggu data sensor dari HP A dan HP B...")
        print("Pastikan kedua HP menjalankan phone_edge.py.\n")

        while True:
            hp =input("Pilih HP (A/B) atau X untuk selesai: ").upper()

            if hp == "X":
                break

            if hp not in ["A", "B"]:
                print("Pilihan HP tidak valid.\n")
                continue

            label = input(
                "Pilih gerakan (DIAM/GUNCANG/PUTAR): "
            ).upper()

            if label not in ["DIAM", "GUNCANG", "PUTAR"]:
                print("Label tidak valid.\n")
                continue

            try:
                durasi = float(input("Durasi rekaman (detik): "))
            except ValueError:
                print("Durasi harus berupa angka.\n")
                continue

            if durasi <=0:
                print("Durasi harus lebih dari 0.\n")
                continue

            with kunci:
                hp_dipilih = hp
                label_aktif = label
                sedang_merekam = True

            print("\nMerekam data...")
            print("HP:", hp)
            print("Gerakan:", label)
            print("Durasi:", durasi, "detik")

            time.sleep(durasi)

            with kunci:
                sedang_merekam = False

            print("Rekaman selesai!\n")
            print("Data tersimpan di:", FILE_DATASET)
            print("----------------------------------")

    except KeyboardInterrupt:
        print("\nPengumpulan data dihentikan.")

    except Exception as e:
        print("Terjadi kesalahan:", e)

    finally:
        with kunci:
            sedang_merekam = False

        client.loop_stop()
        client.disconnect()

        print("Program pengumpulan data telah selesai.")


if __name__ == "__main__":
    main()