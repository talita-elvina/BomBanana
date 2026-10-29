
import json
import math
import random
import time
import threading
import paho.mqtt.client as mqtt

PROJECT_ID = "bombanana_kelompok16_4951"
BROKER = "broker.hivemq.com"
PORT = 8883

TOPIC_A = PROJECT_ID + "/phone/A"
TOPIC_B = PROJECT_ID + "/phone/B"
TOPIC_STATUS = PROJECT_ID + "/game/status"

DURASI_GAME = 30
DURASI_TAMBAHAN = 0
DURASI_COUNTDOWN = 3

BATAS_GUNCANG = 10
BATAS_PUTAR = 0.3
JEDA_AKSI = 1.0

data_hp = {"A": None, "B": None}
bom_di_hp = random.choice(["A", "B"])
skor = 0
waktu_mulai = None
waktu_countdown = None
permainan_aktif = True
aksi_terakhir = {"A": 0, "B": 0}
event_game = "Menunggu kedua HP"
status_game = "MENUNGGU"

kunci = threading.Lock()


def kirim_status(client, status, sisa_waktu):
    with kunci:
        isi = {
            "owner": bom_di_hp,
            "holder": bom_di_hp,
            "score": skor,
            "time_left": max(0, sisa_waktu),
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
    global bom_di_hp, skor, waktu_mulai
    global DURASI_TAMBAHAN, event_game

    try:
        isi = json.loads(pesan.payload.decode())
        hp = isi.get("hp")

        if hp not in ("A", "B"):
            return

        with kunci:
            data_hp[hp] = isi

            # Sensor hanya dipakai untuk aksi ketika game berlangsung.
            if status_game != "PLAYING" or waktu_mulai is None:
                return

            durasi_total = DURASI_GAME + DURASI_TAMBAHAN

            if time.time() - waktu_mulai >= durasi_total:
                return

            ax = float(isi["ax"])
            ay = float(isi["ay"])
            az = float(isi["az"])
            gx = float(isi["gx"])
            gy = float(isi["gy"])
            gz = float(isi["gz"])

            besar_akselerasi = math.sqrt(
                ax ** 2 + ay ** 2 + az ** 2
            )

            besar_putaran = math.sqrt(
                gx ** 2 + gy ** 2 + gz ** 2
            )

            sekarang = time.time()

            if hp != bom_di_hp:
                return

            if sekarang - aksi_terakhir[hp] < JEDA_AKSI:
                return

            if besar_akselerasi > BATAS_GUNCANG:
                bom_di_hp = "B" if hp == "A" else "A"
                skor += 1
                aksi_terakhir[hp] = sekarang

                event_game = "Bom dioper ke Player " + bom_di_hp

                print(
                    "\n" + event_game + " | Skor:", skor
                )

            elif besar_putaran > BATAS_PUTAR:
                DURASI_TAMBAHAN += 3
                aksi_terakhir[hp] = sekarang

                event_game = (
                    "Player " + hp
                    + " mendapat tambahan 3 detik"
                )

                print("\n" + event_game)

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
        data_hp = {"A": None, "B": None}
        bom_di_hp = random.choice(["A", "B"])
        skor = 0
        DURASI_TAMBAHAN = 0
        waktu_mulai = None
        waktu_countdown = None
        aksi_terakhir = {"A": 0, "B": 0}
        event_game = "Menunggu kedua HP"
        status_game = "MENUNGGU"


def main():
    global permainan_aktif, event_game
    global waktu_mulai, waktu_countdown, status_game

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.tls_set()
    client.on_message = saat_pesan

    try:
        client.connect(BROKER, PORT, 60)
        client.subscribe([(TOPIC_A, 1), (TOPIC_B, 1)])
        client.loop_start()

        # Reset semua data permainan saat program dimulai.
        reset_permainan()

        print("=== BOM-BANANA ===")
        print("Project ID:", PROJECT_ID)
        print("Durasi permainan:", DURASI_GAME, "detik")
        print("Durasi countdown:", DURASI_COUNTDOWN, "detik")
        print("Batas guncangan:", BATAS_GUNCANG)
        print("Batas putaran:", BATAS_PUTAR)
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
                    lama_countdown = sekarang - waktu_countdown

                    if lama_countdown >= DURASI_COUNTDOWN:
                        # Reset data sebelum memulai ronde baru.
                        skor = 0
                        DURASI_TAMBAHAN = 0
                        aksi_terakhir = {"A": 0, "B": 0}
                        bom_di_hp = random.choice(["A", "B"])

                        waktu_mulai = sekarang
                        status_game = "PLAYING"
                        event_game = "START! Game dimulai"

                        status = "PLAYING"
                        sisa_waktu = DURASI_GAME

                        print("\nSTART! Game dimulai!")
                        print("Bom awal di Player", bom_di_hp)

                    else:
                        hitungan = DURASI_COUNTDOWN - int(lama_countdown)

                        status = "COUNTDOWN"
                        sisa_waktu = DURASI_GAME
                        event_game = (
                            "Game dimulai dalam " + str(hitungan)
                        )

                elif status_game == "PLAYING":
                    durasi_total = DURASI_GAME + DURASI_TAMBAHAN
                    sudah_berjalan = sekarang - waktu_mulai

                    sisa_waktu = max(
                        0, int(durasi_total - sudah_berjalan)
                    )

                    if sisa_waktu <= 0:
                        status_game = "FINISHED"
                        status = "FINISHED"
                        sisa_waktu = 0

                        event_game = (
                            "Waktu habis! Skor akhir: " + str(skor)
                        )

                        print(
                            "\n\nWaktu habis! Skor akhir:", skor
                        )
                    else:
                        status = "PLAYING"

                else:
                    status = status_game
                    sisa_waktu = 0

            kirim_status(client, status, sisa_waktu)

            if status == "PLAYING":
                print(
                    "\rBom: Player " + bom_di_hp
                    + " | Skor: " + str(skor)
                    + " | Waktu: " + str(sisa_waktu)
                    + " detik   ",
                    end="",
                    flush=True
                )

            if status == "FINISHED":
                print("\nGame selesai. Jalankan ulang game.py untuk bermain lagi.")
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
