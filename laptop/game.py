import json
import random
import time
import threading
import pandas as pd
import paho.mqtt.client as mqtt
import joblib

PROJECT_ID = "bombanana_kelompok16_4951"
BROKER = "broker.hivemq.com"
PORT = 8883

TOPIC_A = PROJECT_ID + "/phone/A"
TOPIC_B = PROJECT_ID + "/phone/B"
TOPIC_STATUS = PROJECT_ID + "/game/status"

# Memuat model AI
FILE_MODEL = "model/movement_model.pkl"
model_ai = joblib.load(FILE_MODEL)

# Nama kolom sensor
kolom_sensor = [
    "ax", "ay", "az",
    "gx", "gy", "gz"
]

DURASI_GAME = 30
DURASI_TAMBAHAN = 0
DURASI_COUNTDOWN = 3

# Jeda minimum agar prediksi yang berulang tidak memicu aksi terus-menerus
JEDA_AKSI = 0.7

# Menyimpan data sensor kedua HP
data_hp = {
    "A": None,
    "B": None
}

# Menyimpan gerakan terakhir setiap HP
gerakan_terakhir = {
    "A": "DIAM",
    "B": "DIAM"
}

bom_di_hp = random.choice(["A", "B"])
skor = 0

waktu_mulai = None
waktu_countdown = None

permainan_aktif = True

aksi_terakhir = {
    "A": 0,
    "B": 0
}

event_game = "Menunggu kedua HP"
status_game = "MENUNGGU"

kunci = threading.Lock()


def kirim_status(client, status, sisa_waktu):
    with kunci:
        total_waktu = DURASI_GAME + DURASI_TAMBAHAN

        isi = {
            "owner": bom_di_hp,
            "holder": bom_di_hp,
            "score": skor,
            "time_left": max(0, sisa_waktu),
            "total_time": total_waktu,
            "status": status,
            "event": event_game
        }

    client.publish(
        TOPIC_STATUS,
        json.dumps(isi),
        qos=1,
        retain=True
    )


def saat_pesan(client, userdata, pesan):
    global bom_di_hp, skor
    global DURASI_TAMBAHAN, event_game

    try:
        isi = json.loads(pesan.payload.decode())
        hp = isi.get("hp")

        if hp not in ("A", "B"):
            return

        with kunci:
            data_hp[hp] = isi

            # Sensor hanya digunakan ketika game berlangsung
            if status_game != "PLAYING" or waktu_mulai is None:
                return

            durasi_total = DURASI_GAME + DURASI_TAMBAHAN

            if time.time() - waktu_mulai >= durasi_total:
                return

            # Mengambil enam nilai sensor
            ax = float(isi["ax"])
            ay = float(isi["ay"])
            az = float(isi["az"])
            gx = float(isi["gx"])
            gy = float(isi["gy"])
            gz = float(isi["gz"])

            # Menyiapkan data sensor untuk AI
            data_sensor = pd.DataFrame([[
                ax, ay, az,
                gx, gy, gz
            ]], columns=kolom_sensor)

            # Meminta AI mengenali gerakan
            prediksi = model_ai.predict(data_sensor)[0]

            print(
                "HP:", hp,
                "| Prediksi AI:", prediksi
            )

            # Hanya HP pemegang bom yang boleh melakukan aksi
            if hp != bom_di_hp:
                return

            sekarang = time.time()

            # Jika terdeteksi DIAM, gerakan berikutnya bisa dihitung lagi
            if prediksi == "DIAM":
                gerakan_terakhir[hp] = "DIAM"
                return

            # Mendeteksi GUNCANG
            if prediksi == "GUNCANG":

                # Hanya satu kali oper untuk satu rangkaian gerakan
                if gerakan_terakhir[hp] != "GUNCANG":

                    if sekarang - aksi_terakhir[hp] < JEDA_AKSI:
                        return

                    # Memindahkan bom ke HP lainnya
                    hp_penerima = "B" if hp == "A" else "A"

                    bom_di_hp = hp_penerima
                    skor += 1

                    aksi_terakhir[hp] = sekarang

                    # Reset status HP penerima
                    gerakan_terakhir[hp_penerima] = "DIAM"
                    aksi_terakhir[hp_penerima] = 0

                    event_game = (
                        "Bom dioper ke Player " + bom_di_hp
                    )

                    print(
                        "\n" + event_game,
                        "| Skor:", skor
                    )

                gerakan_terakhir[hp] = "GUNCANG"

            # Mendeteksi PUTAR
            elif prediksi == "PUTAR":

                # Hanya satu kali penambahan untuk satu rangkaian gerakan
                if gerakan_terakhir[hp] != "PUTAR":

                    if sekarang - aksi_terakhir[hp] < JEDA_AKSI:
                        return

                    # Menambah waktu permainan sebanyak 3 detik
                    DURASI_TAMBAHAN += 3
                    aksi_terakhir[hp] = sekarang

                    event_game = (
                        "Player " + hp
                        + " mendapat tambahan 3 detik"
                    )

                    print(
                        "\n" + event_game,
                        "| Total waktu:",
                        DURASI_GAME + DURASI_TAMBAHAN
                    )

                gerakan_terakhir[hp] = "PUTAR"

    except (
        ValueError,
        TypeError,
        KeyError,
        json.JSONDecodeError
    ) as e:
        print("\nData sensor tidak valid:", e)


def reset_permainan():
    global data_hp, bom_di_hp, skor
    global DURASI_TAMBAHAN, waktu_mulai
    global waktu_countdown, aksi_terakhir
    global event_game, status_game

    with kunci:
        data_hp = {
            "A": None,
            "B": None
        }

        bom_di_hp = random.choice(["A", "B"])
        skor = 0

        DURASI_TAMBAHAN = 0
        waktu_mulai = None
        waktu_countdown = None

        aksi_terakhir = {
            "A": 0,
            "B": 0
        }

        gerakan_terakhir["A"] = "DIAM"
        gerakan_terakhir["B"] = "DIAM"

        event_game = "Menunggu kedua HP"
        status_game = "MENUNGGU"


def main():
    global permainan_aktif
    global waktu_mulai, waktu_countdown, status_game
    global skor, DURASI_TAMBAHAN, bom_di_hp, aksi_terakhir

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

        # Reset semua data permainan
        reset_permainan()

        print("=== BOM-BANANA ===")
        print("Project ID:", PROJECT_ID)
        print("Durasi awal:", DURASI_GAME, "detik")
        print("Tambahan waktu setiap PUTAR: 3 detik")
        print("Model AI berhasil dimuat.")
        print("Menunggu data sensor dari HP A dan HP B...")

        while permainan_aktif:
            sekarang = time.time()

            with kunci:
                kedua_hp_terhubung = (
                    data_hp["A"] is not None
                    and data_hp["B"] is not None
                )

                if not kedua_hp_terhubung:
                    status = "MENUNGGU"
                    sisa_waktu = DURASI_GAME

                elif status_game == "MENUNGGU":
                    status_game = "COUNTDOWN"
                    waktu_countdown = sekarang

                    event_game = "Bersiap! Game segera dimulai"

                    status = "COUNTDOWN"
                    sisa_waktu = DURASI_GAME

                    print("\nKedua HP terhubung. Countdown dimulai!")

                elif status_game == "COUNTDOWN":
                    lama_countdown = (
                        sekarang - waktu_countdown
                    )

                    if lama_countdown >= DURASI_COUNTDOWN:

                        # Reset data sebelum permainan dimulai
                        skor = 0
                        DURASI_TAMBAHAN = 0

                        aksi_terakhir = {
                            "A": 0,
                            "B": 0
                        }

                        gerakan_terakhir["A"] = "DIAM"
                        gerakan_terakhir["B"] = "DIAM"

                        bom_di_hp = random.choice(["A", "B"])

                        waktu_mulai = sekarang
                        status_game = "PLAYING"

                        event_game = "START! Game dimulai"

                        status = "PLAYING"
                        sisa_waktu = DURASI_GAME

                        print("\nSTART! Game dimulai!")
                        print("Bom awal di Player", bom_di_hp)

                    else:
                        hitungan = (
                            DURASI_COUNTDOWN - int(lama_countdown)
                        )

                        status = "COUNTDOWN"
                        sisa_waktu = DURASI_GAME

                        event_game = (
                            "Game dimulai dalam " + str(hitungan)
                        )

                elif status_game == "PLAYING":
                    durasi_total = (
                        DURASI_GAME + DURASI_TAMBAHAN
                    )

                    sudah_berjalan = (
                        sekarang - waktu_mulai
                    )

                    sisa_waktu = max(
                        0,
                        int(durasi_total - sudah_berjalan)
                    )

                    if sisa_waktu <= 0:
                        status_game = "FINISHED"
                        status = "FINISHED"
                        sisa_waktu = 0

                        event_game = (
                            "Waktu habis! Skor akhir: " + str(skor)
                        )

                        print(
                            "\n\nWaktu habis! Skor akhir:",
                            skor
                        )

                    else:
                        status = "PLAYING"

                else:
                    status = status_game
                    sisa_waktu = 0

                # Simpan nilai untuk ditampilkan di terminal
                pemegang_sekarang = bom_di_hp
                skor_sekarang = skor

            # Mengirim status permainan ke dashboard
            kirim_status(
                client,
                status,
                sisa_waktu
            )

            # Menampilkan informasi permainan
            if status == "PLAYING":
                print(
                    "\rBom: Player " + pemegang_sekarang
                    + " | Skor: " + str(skor_sekarang)
                    + " | Waktu: " + str(sisa_waktu)
                    + " detik   ",
                    end="",
                    flush=True
                )

            if status == "FINISHED":
                print(
                    "\nGame selesai. "
                    "Jalankan ulang game.py untuk bermain lagi."
                )
                break

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nGame dihentikan.")

    except Exception as e:
        print("\nTerjadi kesalahan:", e)

    finally:
        permainan_aktif = False
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()