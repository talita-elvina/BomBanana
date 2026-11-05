import pandas as pd

FILE_DATASET = "dataset/data_sensor.csv"

data = pd.read_csv(FILE_DATASET)

print("=== PEMERIKSAAN DATASET BOM-BANANA ===")

print("\n1. Jumlah seluruh data:")
print(len(data))

print("\n2. Jumlah data berdasarkan HP:")
print(data["hp"].value_counts())

print("\n3. Jumlah data berdasarkan label:")
print(data["label"].value_counts())

print("\n4. Jumlah data berdasarkan HP dan label:")
print(pd.crosstab(data["hp"], data["label"]))

print("\n5. Pemeriksaan data kosong:")
print(data.isnull().sum())

print("\n6. Pemeriksaan data duplikat:")
print(data.duplicated().sum())

print("\n7. Statistik data sensor:")
print(data[["ax", "ay", "az", "gx", "gy", "gz"]].describe())