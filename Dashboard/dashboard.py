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




# Streamlit layout
st.title("Dashboard Analisis Penyewaan Sepeda")
st.sidebar.header("Filter")

# Filter interaktif berdasarkan tanggal dan musim
min_date, max_date = day_df["date"].min().date(), day_df["date"].max().date()
selected_date = st.sidebar.slider(
    "Pilih Rentang Tanggal:",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date)
)
day_filter_df = day_df[
    (day_df["date"] >= pd.to_datetime(selected_date[0])) & 
    (day_df["date"] <= pd.to_datetime(selected_date[1]))
]


season_opts = ["All Seasons", *day_df["season"].unique()]
selected_season = st.sidebar.selectbox("Pilih Musim:", season_opts)
day_filter_df = day_filter_df if selected_season == "All Seasons" else day_filter_df[day_filter_df["season"] == selected_season]

# Visualisasi: Total penyewaan sepeda berdasarkan musim dan tahun
st.subheader("Total Penyewaan Sepeda Berdasarkan Musim per Tahun")
seasonal_rentals = day_filter_df.groupby(["year", "season"], observed=False)["total_user"].sum().reset_index()
fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(x="season", y="total_user", hue="year", data=seasonal_rentals, palette="viridis", ax=ax)
ax.set_xlabel("Musim")
ax.set_ylabel("Total Penyewaan Sepeda")
ax.set_title("Total Penyewaan Sepeda Berdasarkan Musim per Tahun")
st.pyplot(fig)

# Visualisasi: Pengaruh Cuaca terhadap Penyewaan Sepeda
st.subheader("Pengaruh Cuaca terhadap Penyewaan Sepeda")
weather_rentals = day_filter_df.groupby("weather")["total_user"].mean().reset_index()
fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(x="weather", y="total_user", data=weather_rentals, palette="coolwarm", ax=ax)
ax.set_xlabel("Cuaca")
ax.set_ylabel("Rata-rata Penyewaan Sepeda")
ax.set_title("Pengaruh Cuaca terhadap Penyewaan Sepeda")
st.pyplot(fig)

# Analisis RFM
st.subheader("Analisis RFM (Recency, Frequency, Monetary)")
def calculate_rfm(day_df):
    recent_date = pd.Timestamp(day_df["date"].max())
    rfm_df = day_df.groupby("date", as_index=False).agg(
        frequency=("date", "count"),  # Seberapa sering penyewaan terjadi
        monetary=("total_user", "sum") # Total jumlah penyewaan sepeda per hari
    )
    rfm_df["recency"] = (recent_date - rfm_df["date"]).dt.days
    return rfm_df

rfm_result = calculate_rfm(day_filter_df)
st.dataframe(rfm_result.head())

# Visualisasi RFM
st.subheader("Visualisasi Analisis RFM")
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))
colors = ["#72BCD4"] * 5

# Recency
sns.barplot(y="recency", x="date", data=rfm_result.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Top 5 Hari dengan Penyewaan Terbaru (Recency)", loc="center", fontsize=18)
ax[0].tick_params(axis='x', rotation=45, labelsize=12)

# Frequency
sns.barplot(y="frequency", x="date", data=rfm_result.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("Top 5 Hari dengan Penyewaan Terbanyak (Frequency)", loc="center", fontsize=18)
ax[1].tick_params(axis='x', rotation=45, labelsize=12)

# Monetary
sns.barplot(y="monetary", x="date", data=rfm_result.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("Total jumlah penyewaan sepeda (Monetary)", loc="center", fontsize=18)
ax[2].tick_params(axis='x', rotation=45, labelsize=12)

plt.suptitle("Analisis RFM", fontsize=20)
st.pyplot(fig)

