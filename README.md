# Bom-Banana
Bom-Banana merupakan proyek permainan berbasis Internet of Things (IoT) yang memanfaatkan sensor smartphone dan komunikasi MQTT. Permainan ini menggunakan dua HP Android sebagai perangkat pemain dan sebuah laptop untuk memproses data serta menjalankan sistem permainan.

Sistem menggunakan sensor accelerometer dan gyroscope untuk membaca pergerakan HP. Data sensor dikirim melalui MQTT ke laptop, kemudian diproses menggunakan model Artificial Intelligence (AI) untuk mengenali gerakan pemain. Dashboard web digunakan untuk menampilkan status permainan, skor, timer, dan notifikasi selama permainan berlangsung.


## Tampilan Dashboard
<img width="2844" height="1518" alt="Dashboard Bom-Banana" src="https://github.com/user-attachments/assets/f042bca7-499e-4579-aa6d-5ebdaaf6b88c" />

## Fitur
- Dua HP Android sebagai edge device untuk membaca pergerakan pemain.
- Pembacaan sensor accelerometer dan gyroscope.
- Pengiriman data sensor menggunakan protokol MQTT melalui HiveMQ.
- Penerapan AI menggunakan algoritma Random Forest untuk mengenali gerakan pemain.
- Pengenalan tiga jenis gerakan, yaitu DIAM, GUNCANG, dan PUTAR.
- Gerakan GUNCANG digunakan untuk memindahkan bom kepada pemain lain dan menambah skor.
- Gerakan PUTAR digunakan untuk menambahkan waktu permainan selama 3 detik.
- Dashboard web untuk menampilkan timer, skor, status pemain, countdown, dan notifikasi akhir permainan.


## Penerapan Artificial Intelligence (AI)
Bom-Banana menggunakan algoritma Random Forest untuk mengenali pola gerakan berdasarkan data sensor smartphone.

Tahapan penerapan AI:
1. Input: Sistem memperoleh data pergerakan pemain dari sensor accelerometer dan gyroscope pada dua smartphone yang terdiri dari enam nilai sensor, yaitu ax, ay, az, gx, gy, dan gz.
2. Pengumpulan Data: Data sensor dikumpulkan dan diberi label berdasarkan tiga jenis gerakan yaitu DIAM, GUNCANG, dan PUTAR.
3. Dataset: Data yang telah diberi label disimpan dalam file data_sensor.csv dan digunakan sebagai dataset untuk melatih model AI.
4. Pelatihan Model: Model dilatih menggunakan algoritma Random Forest untuk mengenali pola dari data gerakan.
5. Penyimpanan Model: Hasil pelatihan disimpan dalam file movement_model.pkl.
6. Prediksi: Saat permainan berlangsung, model membaca data sensor dan memprediksi gerakan pemain berdasarkan enam nilai sensor.
7. Output: Hasil prediksi digunakan untuk menentukan tindakan dalam permainan. GUNCANG digunakan untuk memindahkan bom dan menambah skor, sedangkan PUTAR digunakan untuk menambah waktu permainan selama 3 detik.
8. Deteksi Ulang: Prediksi DIAM digunakan untuk mengaktifkan kembali deteksi gerakan supaya aksi berikutnya dihitung.


## Teknologi yang Digunakan
- Python
- HTML, CSS, dan JavaScript
- MQTT
- HiveMQ Public Broker
- Termux dan Termux:API
- Pandas
- Scikit-learn
- Joblib


## Cara Menjalankan Program

### 1. Persiapan Laptop

Pastikan Python sudah terpasang. Buka terminal pada folder utama proyek, kemudian install library yang diperlukan:

```bash
pip install -r laptop/requirements.txt
```

### 2. Pengumpulan Dataset

Sebelum menjalankan permainan, dataset perlu disiapkan untuk melatih model AI.

Masuk ke folder `laptop`, kemudian jalankan:

```bash
python collect_data.py
```

Setelah pengumpulan data selesai, periksa dataset:

```bash
python check_dataset.py
```

Kemudian lakukan pelatihan model:

```bash
python train_model.py
```

Setelah model selesai dilatih, lakukan pengujian:

```bash
python test_model.py
```

Model hasil pelatihan disimpan dalam file `model/movement_model.pkl`.

Tahapan pengumpulan dan pelatihan ini dilakukan ketika membuat atau memperbarui dataset dan model. Jika model sudah tersedia dan tidak ingin dilatih ulang, tahapan tersebut dapat dilewati.

### 3. Menjalankan HP Android

Siapkan dua HP Android dengan aplikasi Termux dan Termux:API.

Install kebutuhan melalui Termux:

```bash
pkg update
pkg install python termux-api
pip install paho-mqtt
```

Pastikan izin Termux:API sudah diberikan dan sensor smartphone dapat dibaca.

Masuk ke folder `hp` yang berisi `phone_edge.py`, kemudian jalankan program pada masing-masing HP.

HP A:

```bash
python phone_edge.py A
```

HP B:

```bash
python phone_edge.py B
```

### 4. Menjalankan Permainan di Laptop

Setelah kedua HP menjalankan program sensor, buka terminal pada folder `laptop`, kemudian jalankan:

```bash
python game.py
```

Program akan menerima data sensor dari kedua HP melalui MQTT dan memprosesnya menggunakan model AI.

### 5. Menjalankan Dashboard

Buka file berikut melalui browser:

```text
dashboard/index.html
```

Pastikan dashboard dan program Python menggunakan Project ID yang sama.

Project ID:

```text
bombanana_kelompok16_4951
```


## Cara Bermain
- Siapkan dua HP Android yang menjalankan program sensor sebagai pemain A dan pemain B.
- Jalankan `game.py` pada laptop dan buka dashboard melalui browser.
- Setelah kedua HP terhubung, permainan dimulai dengan hitung mundur.
- Pemain yang sedang memegang bom dapat mengguncang HP untuk mengoper bom kepada pemain lainnya.
- Pemain dapat melakukan gerakan putaran untuk menambahkan waktu permainan selama 3 detik.
- Setiap perpindahan bom yang berhasil menambah skor sebanyak 1 poin.
- Permainan berakhir ketika waktu habis. Dashboard menampilkan notifikasi akhir permainan dan skor yang diperoleh.


## MQTT Configuration

- Broker: `broker.hivemq.com`
- MQTT over TLS: Port `8883`
- MQTT over WebSocket: `wss://broker.hivemq.com:8884/mqtt`
- Project ID: `bombanana_kelompok16_4951`

kelompok 16
