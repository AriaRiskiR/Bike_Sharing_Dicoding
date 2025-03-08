import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os


file_path = os.path.join(os.path.dirname(__file__), "clean_day_df.csv")

if not os.path.exists(file_path):
    st.error("File clean_day_df.csv tidak ditemukan. Pastikan file ada di direktori yang benar.")
    st.stop()


day_df = pd.read_csv(file_path)


if day_df.empty:
    st.error("Dataset kosong. Cek kembali file CSV Anda.")
    st.stop()

# ✅ Konversi tipe data
day_df["date"] = pd.to_datetime(day_df["date"], errors="coerce")  # Hindari error jika format salah

category_columns = ["season", "year", "month", "weekday", "holiday", "workingday", "weather"]
for col in category_columns:
    if col in day_df.columns:
        day_df[col] = day_df[col].astype("category")


day_df = day_df.dropna(subset=["year"])  

# 🎯 Judul Dashboard
st.title("Dashboard Analisis Penyewaan Sepeda")

# 🎯 Sidebar filter
st.sidebar.header("Filter Data")
selected_year = st.sidebar.selectbox("Pilih Tahun", day_df["year"].unique())

# ✅ Filter data berdasarkan tahun, tambahkan pengecekan jika data kosong
filtered_df = day_df[day_df["year"] == selected_year]

if filtered_df.empty:
    st.warning("Tidak ada data untuk tahun ini. Pilih tahun lain.")
    st.stop()

# 📌 **1. Statistik Penyewaan Berdasarkan Musim**
st.subheader("📊 Penyewaan Sepeda Berdasarkan Musim")

season_summary = filtered_df.groupby("season")["total_user"].agg(["sum", "mean"]).reset_index()

fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(x="season", y="sum", data=season_summary, palette="coolwarm", ax=ax)
ax.set_xlabel("Musim")
ax.set_ylabel("Total Penyewaan Sepeda")
ax.set_title("Total Penyewaan Sepeda Berdasarkan Musim")
st.pyplot(fig)

st.write(season_summary)

# 📌 **2. Pengaruh Cuaca terhadap Penyewaan Sepeda**
st.subheader("🌦️ Pengaruh Cuaca terhadap Penyewaan Sepeda")

weather_summary = filtered_df.groupby("weather")["total_user"].agg(["sum", "mean"]).reset_index()

fig2, ax2 = plt.subplots(figsize=(8, 5))
sns.barplot(x="weather", y="mean", data=weather_summary, palette="Blues", ax=ax2)
ax2.set_xlabel("Kondisi Cuaca")
ax2.set_ylabel("Rata-rata Penyewaan Sepeda")
ax2.set_title("Rata-rata Penyewaan Sepeda Berdasarkan Kondisi Cuaca")
st.pyplot(fig2)

st.write(weather_summary)

# 📌 **3. Tren Penyewaan Sepeda Sepanjang Tahun**
st.subheader("📅 Tren Penyewaan Sepeda Sepanjang Tahun")

fig3, ax3 = plt.subplots(figsize=(10, 5))
ax3.plot(filtered_df["date"], filtered_df["total_user"], marker="o", color="green", linestyle="-")
ax3.set_xlabel("Tanggal")
ax3.set_ylabel("Jumlah Penyewaan")
ax3.set_title("Tren Penyewaan Sepeda Sepanjang Tahun")
st.pyplot(fig3)

st.write("Aria Riski Ramadhan | Dicoding ")
