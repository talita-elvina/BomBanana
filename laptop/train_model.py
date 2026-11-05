import pandas as pd
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

FILE_DATASET = "dataset/data_sensor.csv"
FOLDER_MODEL = "model"
FILE_MODEL = "model/movement_model.pkl"

# membaca dataset
data =pd.read_csv(FILE_DATASET)

# memilih kolom sensor sebagai input AI
kolom_input = [
    "ax", "ay", "az",
    "gx", "gy", "gz"
]

X = data[kolom_input]
y = data["label"]

# Untuk memastikan data tidak kosong
if X.isnull().values.any() or y.isnull().values.any():
    raise ValueError("Dataset masih memiliki data kosong.")

# membagi data menjadi training dan testing
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("=== PROSES TRAINING BOM-BANANA ===")

print("\nJumlah data training:", len(X_train))
print("Jumlah data testing:", len(X_test))

# membuat model random forest
model =RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    class_weight="balanced"
)

# melatih model
model.fit(X_train, y_train)

# melakukan prediksi
prediksi = model.predict(X_test)

# menghitung akurasi
akurasi = accuracy_score(y_test, prediksi)

print("\n=== HASIL EVALUASI MODEL ===")

print("Akurasi:", round(akurasi * 100, 2), "%")

print("\nClassification Report:")
print(classification_report(y_test, prediksi))

print("\nConfusion Matrix:")
print(confusion_matrix(
    y_test,
    prediksi,
    labels=["DIAM", "GUNCANG", "PUTAR"]
))

# menyimpan model
os.makedirs(FOLDER_MODEL, exist_ok=True)

joblib.dump(model, FILE_MODEL)

print("\nModel berhasil disimpan!")
print("Lokasi:", FILE_MODEL)