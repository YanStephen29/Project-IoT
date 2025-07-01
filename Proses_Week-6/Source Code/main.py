from machine import Pin, PWM, I2C
from time import sleep
from servo_lib import Servo
from mfrc522 import MFRC522
from hcsr04 import HCSR04
from i2c_lcd import I2cLcd
from aes_lib import encrypt_uid, decrypt_uid
import socket
import _thread
import network
import time
import urequests

# --- Inisialisasi I2C dan LCD (DIPINDAHKAN KE SINI) ---
# Pastikan pin SCL dan SDA sesuai dengan koneksi fisik Anda
# Contoh untuk ESP32: I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
# Atau I2C(1, scl=Pin(X), sda=Pin(Y), freq=400000) tergantung pin yang digunakan
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000) 
# Alamat I2C umum untuk LCD (0x27 atau 0x3F)
LCD_I2C_ADDR = 0x27 # Menggunakan variabel untuk alamat I2C
LCD_ROWS = 4
LCD_COLS = 20
lcd = I2cLcd(i2c, LCD_I2C_ADDR, LCD_ROWS, LCD_COLS)
lcd_pesan_terakhir = "" # Variabel ini juga perlu didefinisikan setelah lcd

# --- Fungsi untuk mengirim data ke Firebase ---
def kirim_ke_firebase(uid, masuk, keluar, durasi):
    url = "https://iottubes-f6958-default-rtdb.asia-southeast1.firebasedatabase.app/riwayat.json"
    data = {"uid": uid, "masuk": masuk, "keluar": keluar, "durasi": durasi}
    try:
        res = urequests.post(url, json=data)
        print("Data terkirim ke Firebase:", res.text)
        res.close()
    except Exception as e:
        print("Gagal kirim ke Firebase:", e)

# --- WiFi setup ---
ssid = 'Not4Public'
password = 'password'
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
if not wifi.isconnected():
    print('Menghubungkan ke jaringan Wi-Fi...')
    lcd.clear() # Sekarang 'lcd' sudah terdefinisi
    lcd.putstr("Connecting WiFi...")
    wifi.connect(ssid, password)
    while not wifi.isconnected():
        pass
print('Terhubung ke Wi-Fi. IP:', wifi.ifconfig()[0])
lcd.clear()
lcd.putstr("WiFi Connected!")
lcd.move_to(0, 1)
lcd.putstr(wifi.ifconfig()[0])
sleep(2) # Tampilkan sebentar IP di LCD

# --- Inisialisasi Komponen Hardware (sisanya) ---
servo_masuk = Servo(pin_number=13)
servo_keluar = Servo(pin_number=27)
servo_counter = 0 # Jumlah kendaraan yang masuk
rfid = MFRC522(sck=18, mosi=23, miso=19, rst=4, cs=5)
ultrasonic = HCSR04(trigger_pin=12, echo_pin=14)
ir1 = Pin(32, Pin.IN) # Sensor IR untuk slot parkir 1
ir2 = Pin(33, Pin.IN) # Sensor IR untuk slot parkir 2
rgb1_red = Pin(15, Pin.OUT)
rgb1_green = Pin(2, Pin.OUT)
rgb_red = Pin(25, Pin.OUT)
rgb_green = Pin(26, Pin.OUT)


# --- Variabel Status Pengguna dan Riwayat ---
user_status = {} # Status parkir user: 'masuk' atau 'keluar'
user_time = {}   # Waktu masuk user
histories = []   # Riwayat parkir

# --- Fungsi untuk memperbarui tampilan parkiran di LCD dan LED RGB ---
def update_parkiran():
    global lcd_pesan_terakhir, ir1_status, ir2_status
    status1 = not ir1.value() # Asumsi active LOW
    status2 = not ir2.value() # Asumsi active LOW
    ir1_status, ir2_status = status1, status2 # Update status global untuk webserver

    # Kontrol LED RGB
    rgb1_red.value(status1)
    rgb1_green.value(not status1)
    rgb_red.value(status2)
    rgb_green.value(not status2)

    total_terisi = int(status1) + int(status2)
    pesan_baris1 = ""
    pesan_baris2 = ""

    if total_terisi == 2:
        pesan_baris1 = "Parkir Penuh!"
        pesan_baris2 = "Maaf, Tidak Ada Slot"
    else:
        pesan_baris1 = f"Slot Tersedia: {2 - total_terisi}"
        pesan_baris2 = f"Total Pengunjung: {servo_counter}"

    # Hanya update LCD jika pesan berubah untuk menghindari kedip
    pesan_baru_lengkap = pesan_baris1 + "\n" + pesan_baris2
    if pesan_baru_lengkap != lcd_pesan_terakhir:
        lcd.clear()
        lcd.putstr(pesan_baris1)
        lcd.move_to(0, 1)
        lcd.putstr(pesan_baris2)
        lcd_pesan_terakhir = pesan_baru_lengkap

# --- Template HTML untuk Web Server ---
html_template = """
<html>
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="5">
  <title>Monitoring Parkiran</title>
  <style>
    body { font-family: Arial; background: #1c1c1c; color: white; text-align: center; }
    .slot-container { display: flex; justify-content: center; margin-top: 20px; }
    .slot {
      width: 100px; height: 150px; margin: 10px;
      border: 2px solid #555; border-radius: 10px;
      display: flex; align-items: center; justify-content: center;
      position: relative; font-size: 20px; font-weight: bold;
    }
    .terisi { background-color: #aa2e2e; }
    .kosong { background-color: #2eaa5c; color: black; }
    .label { position: absolute; bottom: 5px; width: 100%; color: #fff; }
    .status { margin-top: 20px; font-size: 20px; color: #00ffaa; }
    table { width: 90%; margin: 20px auto; border-collapse: collapse; }
    th, td { border: 1px solid #ddd; padding: 8px; }
    th { background-color: #333; }
  </style>
</head>
<body>
  <h1>Monitoring Slot Parkir</h1>
  <div class="slot-container">
    <div class="slot {slot1_class}">{slot1_text}<div class="label">P1</div></div>
    <div class="slot {slot2_class}">{slot2_text}<div class="label">P2</div></div>
  </div>
  <div class="status">Sisa Slot: {sisa}</div>
  <div class="status">Total Pengunjung: {pengunjung}</div>
  <h2>Riwayat Masuk/Keluar</h2>
  <table>
    <tr><th>No</th><th>UID</th><th>Masuk</th><th>Keluar</th><th>Durasi</th></tr>
    {history_rows}
  </table>
  <form action="/data"><button type="submit">Lihat Data Statistik</button></form>
</body>
</html>
"""

# --- Fungsi untuk memformat riwayat untuk tampilan web ---
def format_histories():
    return "".join([
        f"<tr><td>{i+1}</td><td>{decrypt_uid(h['uid'])}</td><td>{h['masuk']}</td><td>{h['keluar']}</td><td>{h['durasi']}</td></tr>"
        for i, h in enumerate(histories)
    ])

# --- Fungsi Web Server ---
def start_webserver():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)
    print("Web server listening on http://0.0.0.0:80")

    while True:
        cl, addr = s.accept()
        request = cl.recv(1024).decode()

        if "GET /data" in request:
            rows = ""
            labels, durations = [], []
            for i, h in enumerate(histories):
                rows += f"<tr><td>{i+1}</td><td>{decrypt_uid(h['uid'])}</td><td>{h['masuk']}</td><td>{h['keluar']}</td><td>{h['durasi']}</td></tr>"
                labels.append(f"'{decrypt_uid(h['uid'])}'")

                durasi_str = h['durasi']
                menit = detik = 0
                if "m" in durasi_str and "s" in durasi_str:
                    parts = durasi_str.split()
                    menit = int(parts[0][:-1])
                    detik = int(parts[1][:-1])
                elif "m" in durasi_str:
                    menit = int(durasi_str[:-1])
                elif "s" in durasi_str:
                    detik = int(durasi_str[:-1])
                total_menit = menit + detik / 60
                durations.append(str(round(total_menit, 2)))

            response = f"""
            <html><head><title>Statistik</title>
            <meta http-equiv="refresh" content="5">
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body {{ background: #121212; color: #fff; text-align: center; }}
                table {{ width: 90%; margin: auto; border-collapse: collapse; margin-top: 30px; }}
                th, td {{ padding: 12px; border: 1px solid #444; }}
                th {{ background-color: #222; }}
                tr:nth-child(even) {{ background-color: #1e1e1e; }}
                canvas {{ background-color: #fff; border-radius: 10px; }}
            </style></head><body>
            <h1>Statistik Pengunjung</h1>
            <canvas id="durasiChart" width="400" height="200"></canvas>
            <script>
                const ctx = document.getElementById('durasiChart').getContext('2d');
                new Chart(ctx, {{
                    type: 'bar',
                    data: {{
                        labels: [{','.join(labels)}],
                        datasets: [{{
                            label: 'Durasi Parkir (menit)',
                            data: [{','.join(durations)}],
                            backgroundColor: 'rgba(0, 255, 170, 0.6)',
                            borderColor: 'rgba(0, 255, 170, 1)',
                            borderWidth: 1
                        }}]
                    }},
                    options: {{ scales: {{ y: {{ beginAtZero: true }} }} }}
                }});
            </script>
            <table><thead><tr><th>No</th><th>UID</th><th>Masuk</th><th>Keluar</th><th>Durasi</th></tr></thead>
            <tbody>{rows}</tbody></table>
            <form action="/" method="get">
              <button type="submit">Kembali ke Monitoring</button>
            </form>
            </body></html>
            """

            cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            cl.send(response)
            cl.close()
            continue

        slot1_class = 'terisi' if ir1_status else 'kosong'
        slot2_class = 'terisi' if ir2_status else 'kosong'
        slot1_text = 'TERISI' if ir1_status else 'KOSONG'
        slot2_text = 'TERISI' if ir2_status else 'KOSONG'
        sisa = 2 - int(ir1_status) - int(ir2_status)

        response = html_template.format(
            slot1_class=slot1_class,
            slot2_class=slot2_class,
            slot1_text=slot1_text,
            slot2_text=slot2_text,
            sisa=sisa,
            pengunjung=servo_counter,
            history_rows=format_histories()
        )
        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(response)
        cl.close()

# Mulai Web Server di thread terpisah
_thread.start_new_thread(start_webserver, ())

# Status awal IR (digunakan oleh webserver)
ir1_status = False
ir2_status = False

# --- Loop utama program ---
while True:
    # Memperbarui status parkiran di LCD dan LED RGB
    update_parkiran()

    # Membaca RFID
    (stat, tag_type) = rfid.request(rfid.REQIDL)

    if stat == rfid.OK:
        (stat, uid) = rfid.anticoll()
        if stat == rfid.OK:
            uid_plain = ''.join('{:02x}'.format(x) for x in uid)
            uid_encrypted = encrypt_uid(uid_plain)

            print(f"UID Terdeteksi: {uid_plain}")
            print(f"UID Terenkripsi: {uid_encrypted}")

            now = time.localtime()
            waktu_str = "{:02}:{:02}:{:02}".format(now[3], now[4], now[5])

            if uid_plain not in user_status or user_status[uid_plain] == 'keluar':
                # --- Proses Masuk ---
                print("UID ingin MASUK")
                lcd.clear()
                lcd.putstr("Selamat datang,")
                lcd.move_to(0, 1)
                lcd.putstr(f"{decrypt_uid(uid_encrypted)[:16]}!") # Tampilkan UID sebagian atau nama jika ada
                lcd.move_to(0, 2)
                lcd.putstr("Pintu masuk dibuka")

                servo_masuk.move_to_angle(90)
                servo_counter += 1 # Tambah counter pengunjung
                sleep(1) # Tunggu sebentar pintu terbuka

                # Cek sensor ultrasonik sampai mobil lewat
                lcd.move_to(0, 3)
                lcd.putstr("Mobil sedang masuk..")
                while True:
                    jarak = ultrasonic.distance_cm()
                    if jarak is not None and jarak < 30: # Jika ada objek dekat sensor
                        break
                    sleep(0.1) # Tunggu sebentar sebelum cek lagi
                
                lcd.move_to(0, 3)
                lcd.putstr("Pintu masuk ditutup")
                servo_masuk.move_to_angle(0) # Tutup pintu
                
                user_status[uid_plain] = 'masuk'
                user_time[uid_plain] = waktu_str
                
                sleep(2) # Tampilkan pesan "mobil masuk" sebentar
                # LCD akan kembali menampilkan status parkiran di iterasi loop berikutnya

            elif user_status[uid_plain] == 'masuk':
                # --- Proses Keluar ---
                print("UID ingin KELUAR")
                lcd.clear()
                lcd.putstr("Terima kasih,")
                lcd.move_to(0, 1)
                lcd.putstr(f"{decrypt_uid(uid_encrypted)[:16]}!")
                lcd.move_to(0, 2)
                lcd.putstr("Pintu keluar dibuka")

                servo_keluar.move_to_angle(90)
                sleep(3) # Tunggu sebentar pintu terbuka dan mobil lewat
                servo_keluar.move_to_angle(0) # Tutup pintu

                user_status[uid_plain] = 'keluar'

                waktu_masuk = user_time.get(uid_plain, "--:--:--")
                waktu_keluar = waktu_str

                durasi = "-"
                try:
                    # Konversi waktu ke detik untuk menghitung durasi
                    jm = int(waktu_masuk[:2]) * 3600 + int(waktu_masuk[3:5]) * 60 + int(waktu_masuk[6:])
                    jk = int(waktu_keluar[:2]) * 3600 + int(waktu_keluar[3:5]) * 60 + int(waktu_keluar[6:])
                    detik = jk - jm
                    durasi = f"{detik // 60}m {detik % 60}s"
                except:
                    pass
                
                # Tambahkan durasi ke LCD
                lcd.move_to(0, 3)
                lcd.putstr(f"Durasi: {durasi}")

                data_entry = {
                    'uid': uid_encrypted,
                    'masuk': waktu_masuk,
                    'keluar': waktu_keluar,
                    'durasi': durasi
                }
                histories.append(data_entry)
                kirim_ke_firebase(**data_entry)
                sleep(2) # Tampilkan pesan "Terima kasih" dan durasi sebentar
                # LCD akan kembali menampilkan status parkiran di iterasi loop berikutnya
    
    # Jeda singkat sebelum loop berikutnya untuk mencegah pemindaian RFID terlalu cepat
    sleep(0.1)

