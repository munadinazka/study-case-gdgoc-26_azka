# FilmLog — Movie Watchlist & Review Platform

FilmLog adalah aplikasi berbasis web untuk mengelola daftar film yang ingin ditonton (*watchlist*), mencatat film yang sudah ditonton, memberikan rating dan ulasan, serta mendapatkan rekomendasi film menggunakan Google Gemini AI.

Proyek ini dikembangkan sebagai bagian dari **Backend Recruitment Task GDGoC UGM 2026/2027**.

## Fitur Utama

- **Autentikasi pengguna:** Registrasi dan login menggunakan JWT.
- **Daftar film:** Menampilkan seluruh film dan detail informasi setiap film.
- **Watchlist:** Menambahkan, melihat, dan menghapus film dari daftar film yang ingin ditonton.
- **Watched & Reviews:** Mencatat film yang sudah ditonton, memberikan rating 1–5, dan menulis ulasan.
- **Rekomendasi AI:** Mendapatkan rekomendasi film berdasarkan preferensi pengguna menggunakan Google Gemini.
- **Validasi dan penanganan error:** Memvalidasi input serta menangani berbagai kondisi error API.

## Teknologi yang Digunakan

### Backend
- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- PyJWT
- pwdlib (Argon2)
- Google Gemini API

### Frontend
- HTML
- CSS
- JavaScript
- Tailwind CSS

### Pengujian
- Pytest
- HTTPX

## Struktur Proyek

```text
study-case-gdgoc-26_azka/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   ├── middleware/
│   │   ├── models/
│   │   ├── routers/
│   │   ├── schemas/
│   │   └── services/
│   ├── tests/
│   ├── .env.example
│   ├── main.py
│   └── requirements.txt
├── data/
│   ├── movies.json
│   └── seed.sql
├── frontend/
│   ├── app.js
│   ├── index.html
│   ├── style.css
│   └── README.md
├── .gitignore
└── README.md
```

## Database

FilmLog menggunakan PostgreSQL sebagai database relasional.

Database terdiri atas delapan tabel:

| Tabel | Fungsi |
|---|---|
| `users` | Menyimpan informasi akun pengguna |
| `movies` | Menyimpan informasi film |
| `genres` | Menyimpan kategori genre film |
| `movie_genre` | Menghubungkan film dengan genre |
| `people` | Menyimpan informasi orang yang terlibat dalam film |
| `movie_people` | Menghubungkan film dengan pemeran dan sutradara |
| `watchlists` | Menyimpan daftar film yang ingin ditonton |
| `user_ratings` | Menyimpan rating dan ulasan pengguna |

Data awal film disediakan melalui direktori `data/`.

## Persiapan dan Instalasi

### 1. Clone Repository

```bash
git clone https://github.com/munadinazka/study-case-gdgoc-26_azka.git
cd study-case-gdgoc-26_azka
```

### 2. Persiapan Database

Pastikan PostgreSQL sudah berjalan.

Buat database sesuai konfigurasi yang akan digunakan pada file `.env`, kemudian jalankan SQL schema dan seed data yang tersedia di direktori `data/`.

### 3. Persiapan Backend

Masuk ke direktori backend:

```bash
cd backend
```

Buat virtual environment:

```bash
python -m venv .venv
```

Aktifkan virtual environment di Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Instal dependensi:

```bash
pip install -r requirements.txt
```

Buat file `.env` berdasarkan `.env.example`, kemudian sesuaikan konfigurasi database dan API key milik masing-masing pengguna.

Jangan membagikan file `.env` karena berisi informasi rahasia.

### 4. Menjalankan Backend

Dari direktori `backend`, jalankan:

```bash
uvicorn main:app --reload
```

Backend berjalan pada:

```text
http://localhost:8000
```

Dokumentasi API Swagger tersedia di:

```text
http://localhost:8000/docs
```

### 5. Menjalankan Frontend

Buka terminal baru, kemudian masuk ke direktori frontend:

```bash
cd frontend
```

Jalankan server lokal:

```bash
python -m http.server 3000
```

Buka aplikasi melalui:

```text
http://localhost:3000
```

Pastikan backend dan frontend berjalan bersamaan agar aplikasi dapat berkomunikasi dengan API.

## Dokumentasi API

Seluruh endpoint API menggunakan prefix `/api`.

### Authentication

| Method | Endpoint | Keterangan |
|---|---|---|
| POST | `/api/auth/register` | Registrasi pengguna |
| POST | `/api/auth/login` | Login pengguna dan memperoleh JWT |

### Movies

| Method | Endpoint | Keterangan |
|---|---|---|
| GET | `/api/movies` | Menampilkan daftar film |
| GET | `/api/movies/{movie_id}` | Menampilkan detail film |
| POST | `/api/movies/recommend` | Meminta rekomendasi film dari Gemini AI |

### Watchlist

Endpoint berikut memerlukan autentikasi JWT.

| Method | Endpoint | Keterangan |
|---|---|---|
| GET | `/api/watchlist` | Melihat watchlist pengguna |
| POST | `/api/watchlist` | Menambahkan film ke watchlist |
| DELETE | `/api/watchlist/{movie_id}` | Menghapus film dari watchlist |

### Watched & Reviews

Endpoint berikut memerlukan autentikasi JWT.

| Method | Endpoint | Keterangan |
|---|---|---|
| GET | `/api/watched` | Melihat film yang sudah ditonton |
| POST | `/api/watched` | Menambahkan film yang sudah ditonton beserta rating dan ulasan |

## Keamanan dan Validasi

Beberapa mekanisme keamanan yang diterapkan:

- Password pengguna disimpan dalam bentuk hash menggunakan Argon2.
- Autentikasi menggunakan JSON Web Token (JWT).
- Endpoint watchlist dan watched dilindungi autentikasi.
- Rating dibatasi pada rentang 1–5.
- Input ulasan divalidasi agar tidak kosong.
- Duplikasi film pada watchlist dan catatan film yang sudah ditonton ditangani melalui validasi dan constraint database.
- File `.env` tidak disertakan dalam repository.

## Integrasi Google Gemini AI

FilmLog menggunakan Google Gemini API untuk menghasilkan rekomendasi film.

Rekomendasi tidak langsung diterima sebagai data film baru. Backend menyediakan katalog film dari database kepada layanan AI, kemudian memvalidasi hasil rekomendasi agar film yang dikembalikan benar-benar tersedia dalam database lokal.

Dengan demikian, rekomendasi AI tetap mengacu pada koleksi film yang dimiliki aplikasi.

## Pengujian

Pengujian backend menggunakan Pytest.

Jalankan seluruh pengujian dari direktori `backend`:

```bash
python -m pytest -q
```

Pengujian mencakup autentikasi, daftar film, watchlist, watched, validasi input, autentikasi endpoint terlindungi, serta integrasi rekomendasi AI.

## Dokumentasi Tambahan

- Dokumentasi API: `http://localhost:8000/docs`
- Panduan frontend: `frontend/README.md`

---

**FilmLog — Movie Watchlist & Review Platform**

Dikembangkan untuk Hacker Backend Assignment Specification Recruitment GDGoC UGM 2026/2027.