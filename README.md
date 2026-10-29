# BomBanana
Proyek IoT game BomBanana menggunakan sensor HP dan MQTT.

Permainan menggunakan sensor accelerometer dan gyroscope untuk mendeteksi gerakan HP. Data sensor dikirim melalui MQTT ke laptop untuk diproses, sedangkan dashboard web menampilkan status permainan, timer, skor, dan notifikasi saat permainan berakhir.

## Tampilan dashboard
<img width="2844" height="1518" alt="image" src="https://github.com/user-attachments/assets/f042bca7-499e-4579-aa6d-5ebdaaf6b88c" />


## Cara bermain
- Siapkan dua HP Android yang menjalankan program sensor, yaitu HP A dan HP B.
- Jalankan program game.py pada laptop dan buka dashboard di browser.
- Setelah kedua HP terhubung, permainan dimulai dengan hitung mundur.
- Pemain yang sedang memegang bom dapat mengguncang HP untuk mengoper bom kepada pemain lainnya.
- Gerakan putaran HP yang memenuhi batas yang ditentukan dapat menambahkan waktu permainan.
- Permainan berakhir ketika waktu habis. Dashboard menampilkan notifikasi akhir permainan dan skor yang diperoleh.

---

## Fitur
- Dua HP Android sebagai edge device.
- Pembacaan sensor accelerometer dan gyroscope.
- Komunikasi data menggunakan MQTT melalui HiveMQ.
- Deteksi guncangan untuk memindahkan bom.
- Deteksi putaran untuk menambah waktu permainan.
- Dashboard web dengan timer, skor, countdown, dan popup akhir permainan.


## Cara menjalankan
### 1. Laptop
Install library yang tercantum pada `laptop/requirements.txt`, lalu jalankan
```
python laptop/game.py
```

### 2. HP Android
Install Termux, Termux:API, Python, dan library yang diperlukan sebagai berikut
```
pkg update
pkg install python termux-api
pip install paho-mqtt
```
Pastikan sensor accelerometer dan gyroscope tersedia serta izin Termux:API sudah diberikan.

Jalankan program sensor pada masing-masing HP menggunakan identitas A dan B

```
python phone_edge.py A
python phone_edge.py B
```
Perintah dijalankan dari folder tempat hone_edge.py berada.

### 3. Dashboard
Buka `dashboard/index.html` melalui browser dan pastikan koneksi MQTT menggunakan project ID yang sama dengan program Python.

Project id yang digunakan: `bombanana_kelompok16_4951`


## Teknologi yang digunakan
- Python
- HTML, CSS, dan JavaScript
- MQTT
- HiveMQ Public Broker
- Termux dan Termux:API


## MQTT Configuration
- Broker: `broker.hivemq.com`
- MQTT over TLS: port `8883`
- MQTT over WebSocket: `wss://broker.hivemq.com:8884/mqtt`
