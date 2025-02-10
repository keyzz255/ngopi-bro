import logging
import requests
import colorama
from colorama import Fore, Style
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, CallbackContext

# 🔹 Inisialisasi colorama untuk warna terminal
colorama.init(autoreset=True)

# 🔹 Konfigurasi Bot Telegram
TELEGRAM_BOT_TOKEN = "7862379874:AAFsKAsU5jIbWxQOj6ITvtyFL6_f16hp99Q"  # Ganti dengan Token Bot Anda

# 🔹 API Bank (Validasi Rekening)
API_BANK_URL = "https://cek-nomor-rekening-bank-indonesia1.p.rapidapi.com/cekRekening"
API_BANK_HEADERS = {
    "x-rapidapi-key": "347c3d28d8msh5b5bbb8fcfdf9eap1b3295jsn7f44586c582f",
    "x-rapidapi-host": "cek-nomor-rekening-bank-indonesia1.p.rapidapi.com"
}

# 🔹 Daftar kode bank di Indonesia
KODE_BANKS = {
    "bca": "014",
    "mandiri": "008",
    "bni": "009",
    "bri": "002",
    "cimb": "022",
    "danamon": "011",
    "maybank": "016",
    "permata": "013",
    "panin": "019",
    "btn": "200",
    "mega": "426",
    "bsi": "451",
    "btpn": "213",
    "jenius": "213",
    "ocbc": "028",
    "dbs": "046",
    "uob": "023",
    "hsbc": "041",
    "citibank": "031",
    "standard": "050",
    "muamalat": "147",
    "sea": "535",
    "bluebca": "88888",
    "sakuku": "99000"
}

# 🔹 Daftar e-Wallet yang didukung
EWALLET_SERVICES = {
    "dana": "dana",
    "ovo": "ovo",
    "gopay": "gopay",
    "shopeepay": "shopeepay",
    "linkaja": "linkaja",
    "sea": "sea",
    "bluebca": "bluebca",
    "sakuku": "sakuku"
}

# 🔹 Logging (Untuk Debugging)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# 🔹 Fungsi untuk mengecek rekening bank via API
def cek_rekening(kode_bank, nomor_rekening):
    params = {"kodeBank": kode_bank, "noRekening": nomor_rekening}
    try:
        response = requests.get(API_BANK_URL, headers=API_BANK_HEADERS, params=params)
        data = response.json()
        if response.status_code == 200 and "data" in data and "nama" in data["data"]:
            return data["data"]["nama"]
        else:
            return None  # Jika rekening tidak ditemukan
    except:
        return None  # Jika terjadi kesalahan

# 🔹 Fungsi untuk mengecek e-Wallet via API
def cek_ewallet(ewallet, nomor_hp):
    endpoint = f"/cek_ewallet/{nomor_hp}/{ewallet}"
    try:
        response = requests.get(API_EWALLET_URL + endpoint, headers=API_EWALLET_HEADERS, timeout=10)
        data = response.json()
        if response.status_code == 200 and "data" in data:
            return data["data"]["name"]
        else:
            return None
    except:
        return None

# 🔹 Fungsi saat pengguna mengetik /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "✅ Selamat datang di *BANK & E-WALLET CHECK BOT*!\n\n"
        "🔹 Ketik `<nama_bank> <nomor_rekening>` atau `<nomor_rekening> <nama_bank>` untuk validasi rekening.\n"
        "🔹 Ketik `<nama_ewallet> <nomor_hp>` atau `<nomor_hp> <nama_ewallet>` untuk validasi e-Wallet.\n"
        "🔹 Ketik `/list` untuk melihat daftar kode bank & e-Wallet.\n\n"
        "*Contoh:* `bca 8060127426` atau `8060127426 bca`\n"
        "*Contoh:* `shopeepay 081357645086` atau `081357645086 shopeepay`",
        parse_mode="Markdown"
    )

# 🔹 Fungsi untuk menangani semua pesan masuk
async def handle_message(update: Update, context: CallbackContext):
    try:
        text = update.message.text.strip().lower()  # Ambil teks dari pengguna
        words = text.split()  # Pecah pesan berdasarkan spasi

        # Memastikan format pesan valid (harus ada 2 kata: bank/eWallet + nomor)
        if len(words) != 2:
            return

        layanan_1, layanan_2 = words  # Ambil kedua kata input

        # **Menyesuaikan input dengan dua format**
        if layanan_1 in KODE_BANKS and layanan_2.isdigit():
            # **Format: bca 8060127426**
            kode_bank = KODE_BANKS[layanan_1]
            nomor = layanan_2
        elif layanan_2 in KODE_BANKS and layanan_1.isdigit():
            # **Format: 8060127426 bca**
            kode_bank = KODE_BANKS[layanan_2]
            nomor = layanan_1
        else:
            kode_bank = None

        if kode_bank:
            nama_pemilik = cek_rekening(kode_bank, nomor)
            if nama_pemilik:
                await update.message.reply_text(
                    f"✅ *BANK CHECK*\n\n"
                    f"🏦 Nama Bank: *{layanan_1.upper()}*\n"
                    f"🔢 Nomor Rekening: `{nomor}`\n"
                    f"👤 Nama Pemilik: *{nama_pemilik}*",
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text("⚠️ Rekening tidak ditemukan atau tidak valid.", parse_mode="Markdown")
            return

        # **Cek e-Wallet dengan dua format**
        if layanan_1 in EWALLET_SERVICES and layanan_2.isdigit():
            ewallet = EWALLET_SERVICES[layanan_1]
            nomor = layanan_2
        elif layanan_2 in EWALLET_SERVICES and layanan_1.isdigit():
            ewallet = EWALLET_SERVICES[layanan_2]
            nomor = layanan_1
        else:
            ewallet = None

        if ewallet:
            nama_pemilik = cek_ewallet(ewallet, nomor)
            if nama_pemilik:
                await update.message.reply_text(
                    f"✅ *E-WALLET CHECK*\n\n"
                    f"📱 Layanan: *{layanan_1.upper()}*\n"
                    f"📞 Nomor HP: `{nomor}`\n"
                    f"👤 Nama Pemilik: *{nama_pemilik}*",
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text("", parse_mode="Markdown")

    except:
        return

# 🔹 Menjalankan bot Telegram
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print(Fore.GREEN + "🚀 BOT TELEGRAM SEDANG BERJALAN...")
    app.run_polling()

# 🔹 Jalankan bot
if __name__ == "__main__":
    main()
