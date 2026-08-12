# ⚡ Font & Image Upscaler Web App

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Framework-Flask_3.0-green.svg)
![OpenCV](https://img.shields.io/badge/Engine-OpenCV_4.8-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

Aplikasi web berarsitektur **Futuristik Tactical/Military HUD** yang dirancang khusus untuk melakukan **upscaling gambar** dan **mempertajam font/teks yang kabur (blur)** pada screenshot, dokumen scanned, atau foto teks. 

Menggunakan kombinasi algoritma Computer Vision tanpa beban GPU berat (*Lanczos-4 Interpolation, Multi-scale Laplacian Edge Boosting, CLAHE, Bilateral Filtering, dan Adaptive Thresholding*).

---

## 🌟 Fitur Utama

- **Font & Text Edge Boosting**: Mempertajam tepian karakter/huruf yang blur tanpa membuat noise di background.
- **Interactive Comparison Slider**: Visualisasi perbandingan gambar sebelum (*Original*) dan sesudah (*Upscaled*) secara *real-time* dengan slider interaktif.
- **Preset Pengolahan Siap Pakai**:
  - `Text Focus (Bagan / Screenshot Document)`: Untuk foto dokumen atau screenshot aplikasi.
  - `Hybrid Photo + Text`: Untuk gambar gabungan antara foto dan teks.
  - `High Contrast Binarized Text`: Mengubah teks kabur menjadi hitam-putih murni (*OCR ready*).
- **Kustomisasi Parameter Lanjutan**:
  - Scale Factor (1.5x - 4x)
  - Sharpness Level
  - Contrast Enhancement (CLAHE)
  - Edge Boost Strength
  - Denoising (Edge-preserving)
- **Tampilan Futuristic Tactical HUD UI**: Antarmuka bertema militer/cyberpunk yang responsif dan cepat.

---

## 📋 Prasyarat Sistem

Sebelum menginstal, pastikan sistem Anda sudah terpasang:
- **Python 3.8** atau versi lebih baru (`python3 --version`)
- **Python venv** module (`python3-venv`)
- **Git**

---

## 🚀 Panduan Instalasi & Menjalankan Aplikasi

### Cara 1: Menggunakan Script Otomatis (Direkomendasikan)

Script `run.sh` akan secara otomatis membuat Virtual Environment (`venv`), mengunduh dependencies, dan menjalankan server aplikasi.

1. **Clone repository ini**:
   ```bash
   git clone https://github.com/fahmiibrahimdevs/image-upscaler.git
   cd image-upscaler
   ```

2. **Berikan akses eksekusi ke `run.sh` & jalankan**:
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

3. **Buka aplikasi di browser**:
   Aplikasi dapat diakses melalui link: **`http://127.0.0.1:5000`**

---

### Cara 2: Instalasi Manual

Jika Anda ingin melakukan setup manual tanpa `run.sh`:

1. **Clone Repository**:
   ```bash
   git clone https://github.com/fahmiibrahimdevs/image-upscaler.git
   cd image-upscaler
   ```

2. **Buat & Aktifkan Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Jalankan Server Flask**:
   ```bash
   python3 app.py
   ```

5. **Akses Aplikasi**:
   Buka browser dan navigasi ke `http://127.0.0.1:5000`.

---

## 📁 Struktur Direktori Project

```text
image-upscaler/
├── app.py              # Server Flask REST API & Web Server
├── upscaler.py         # Engine OpenCV (Upscaling, Sharpening, CLAHE, Sobel)
├── requirements.txt    # Daftar dependencies Python
├── run.sh              # Launcher script otomatis
├── static/
│   ├── css/
│   │   └── style.css   # Tactical Military HUD Styling
│   └── js/
│       └── main.js     # Logika UI & Interactive Comparison Slider
└── templates/
    └── index.html      # Tampilan Web App utama
```

---

## 🛠️ Dependensi Utama

- **Flask**: Web Framework lightweight.
- **OpenCV (`opencv-python-headless`)**: Engine pengolahan citra & algoritma komputer vision.
- **Pillow & NumPy**: Manipulasi buffer gambar dan array matriks citra.

---

## 📄 Lisensi

Distributed under the **MIT License**. See `LICENSE` for more information.
