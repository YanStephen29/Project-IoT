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
Pengendara akan mendekati gerbang parkir dapat melihat total pengunjung dan sisa slot parkir yang tersedia lalu pengendara men-tap kartu di MFRC522, setelah kartu terdeteksi maka servo akan terbuka dan pengendara dapat masuk lalu servo akan menutup apabila kendaraan telah terdeteksi sensor yang menggunakan sensor (HC-SR04). Pengendara akan menuju area parkir yang sudah ada sensor infra red yang sudah di lengkapi RGB sebagai indikator. Apabila kendaraan sudah terdeteksi sensor infra red sesuai dengan jarak yang ditentukan maka lampu RGB akan berubah. Sistem juga akan menampilkan dan mengupdate sisa slot parkir menggunakan LCD. RGB LED akan digunakan untuk menandai slot yang kosong atau terisi.

---

## 🧩 Komponen yang Digunakan  

| Komponen                     | Jumlah | Fungsi                                                           |
|------------------------------|--------|------------------------------------------------------------------|
| *Ultrasonic HC-SR04*      | 1      | Mendeteksi jarak kendaraan (mobil/motor) di jalur masuk         |
| *Infra Red*               | 1      | Mendeteksi keberadaan kendaraan pada slot parkir                |
| *Servo Motor*             | 2      | Membuka/Tutup palang otomatis                                   |
| *RGB LED*                 | 2      | Menunjukkan status slot parkir (hijau = kosong, merah = penuh)  |
| *OLED I2C Display (0.96”)*| 1      | Menampilkan jumlah slot yang tersedia                           |
| *RFID MFRC522*            | 1      | Mengendalikan sistem dan koneksi ke WiFi                        |
| *ESP32 / Microcontroller* | 1      | Mengendalikan sistem dan koneksi ke WiFi                        |

---

## 🛠 Tools Tambahan
- MicroPython (untuk ESP32)
- Thonny IDE atau uPyCraft
- Wokwi (untuk simulasi)
- Firebase (untuk mencatat data pengunjung)
- WiFi (untuk komunikasi antar perangkat)
- Web (untuk monitoring pengelola parkir)

---

## 🚦 Alur Sistem  
1. Pengendara mendekati gerbang parkir  
2. Pengendara tap kartu pada RFID
3. Jumlah pengunjung diperbaharui
4. Servo membuka palang masuk
5. HC-SR04 mendeteksi kendaraan lewat
6. Servo menutup
7. Pengendara mendekati area parkir
8. Infrared mendeteksi kendaraan yang masuk
9. RGB LED dan OLED diperbarui sesuai status slot 
10. Slot kosong → LED berubah warna ke hijau kembali  
11. Saat kendaraan keluar → sensor mendeteksi, data diperbarui

---
