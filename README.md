# 🚗 IoT Smart Parking Detector

## 👥 Kelompok 14  
- *Yan Stephen Christian Immanuel Hutagalung* - 105222010  
- *Nurul Humam Mutarobbi* - 105222020

---

## 📌 Judul  
*IoT Smart Parking Detector*

---

## 📝 Deskripsi Singkat  
Proyek ini bertujuan untuk menciptakan sistem parkir pintar berbasis Internet of Things (IoT) yang mampu memantau ketersediaan slot parkir secara real-time. Sistem ini dirancang untuk mengoptimalkan efisiensi parkir dengan memberikan informasi langsung kepada pengguna mengenai slot yang tersedia dan mengatur akses kendaraan melalui sensor dan aktuator otomatis.

---

## 🎯 Tujuan  
- Mengatur dan memonitor ruang parkir secara otomatis dan real-time  
- Mengurangi kemacetan akibat pencarian slot parkir  
- Menyediakan informasi sisa slot parkir melalui display OLED  
- Meningkatkan efisiensi dan keamanan area parkir

---

## 🌍 Target SDGs  
- *SDG 9 - Industry, Innovation, and Infrastructure*  
Mendorong inovasi dalam pengelolaan infrastruktur perkotaan, khususnya transportasi dan parkir cerdas melalui teknologi digital dan sistem otomatisasi.

---

## ⚙ Skema  
*Skema 1:*  
Pengendara akan melewati gerbang parkir dan mendeteksi kendaraan menggunakan sensor (Ultrasonik atau IR Breakbeam). Jika terdapat slot kosong, servo motor akan membuka palang otomatis. Sistem juga akan menampilkan sisa slot parkir menggunakan OLED. RGB LED akan digunakan untuk menandai slot yang kosong atau terisi.

---

## 🧩 Komponen yang Digunakan  

| Komponen                     | Jumlah | Fungsi                                                           |
|------------------------------|--------|------------------------------------------------------------------|
| *Ultrasonic HC-SR04*      | 1      | Mendeteksi jarak kendaraan (mobil/motor) di jalur masuk         |
| *Ultrasonic Pendek*       | 1      | Mendeteksi keberadaan kendaraan pada slot parkir                |
| *IR Breakbeam / IR Get*   | 1      | Mendeteksi objek saat masuk ke area tertentu                    |
| *Servo Motor*             | 1      | Membuka/Tutup palang otomatis                                   |
| *RGB LED*                 | 5      | Menunjukkan status slot parkir (hijau = kosong, merah = penuh)  |
| *OLED I2C Display (0.96”)*| 1      | Menampilkan jumlah slot yang tersedia                           |
| *ESP32 / Microcontroller* | 1      | Mengendalikan sistem dan koneksi ke WiFi                        |

---

## 🛠 Tools Tambahan
- MicroPython (untuk ESP32)
- Thonny IDE atau uPyCraft
- Wokwi (untuk simulasi)
- Flask (untuk server data sederhana - opsional)
- WiFi (untuk komunikasi antar perangkat)

---

## 🚦 Alur Sistem  
1. Pengendara mendekati gerbang parkir  
2. Sensor mendeteksi kendaraan → sistem mengecek ketersediaan slot  
3. Jika ada slot kosong → servo membuka palang masuk  
4. RGB LED dan OLED diperbarui sesuai status slot  
5. Slot parkir terisi → sensor mendeteksi kendaraan  
6. Slot kosong → LED berubah warna ke hijau kembali  
7. Saat kendaraan keluar → sensor mendeteksi, data diperbarui

---
