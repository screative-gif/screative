# Agent Riset Tren: Pengumpul Data

Mengumpulkan post populer dari **Threads, X, Instagram, dan TikTok** berdasarkan keyword dan hashtag niche kamu, lewat Apify (paket gratis, kredit $5/bulan).

## Setup (sekali saja)

1. Daftar gratis di https://console.apify.com/sign-up (tidak perlu kartu kredit).
2. Buka **Settings → API & Integrations**, lalu salin *Personal API token*.
3. Di folder ini, salin `.env.example` jadi `.env`, lalu tempel token-nya:
   ```
   APIFY_TOKEN=apify_api_xxxxxxxx
   ```
   Token ini rahasia. Jangan dibagikan atau di-upload ke mana pun.
4. Edit `config.json`: isi `niche`, `keywords`, dan `hashtags` kamu.

## Alur lengkap

1. `python3 collect.py`: ambil data
2. `python3 analyze.py`: hitung statistik → `data/<run>/summary.md`
3. Di Claude Code (folder utama), bilang **"Naka, riset tren"**. Lira akan menulis laporan ke `konten/laporan/`

## Menjalankan

```bash
python3 collect.py --dry-run        # tes pakai data contoh, gratis
python3 collect.py --limit 3        # tes murah: 3 post per keyword
python3 collect.py                  # semua platform
```

Hasilnya ada di `data/<tanggal_jam>/`:
- `posts.csv`: semua post, diurutkan dari engagement tertinggi (bisa dibuka di Excel atau Google Sheets)
- `posts.json`: data yang sama, untuk tahap analisis berikutnya
- `raw/`: data asli dari tiap actor, untuk mengecek atau memperbaiki mapping kolom

Skor `engagement` = likes + 2×komentar + 3×share/repost.

## Biaya (perkiraan, paket gratis)

| Platform | Actor | Harga per post | Sekali jalan (config default) |
|---|---|---|---|
| Threads | scrapesage/threads-search-scraper | ~$0.003 | ≤ $0.30 |
| X | xquik/x-tweet-scraper | ~$0.00015 | ≤ $0.10 (biasanya ~$0.02) |
| Instagram | apify/instagram-hashtag-scraper | ~$0.0026 | ≤ $0.30 |
| TikTok | clockworks/tiktok-scraper | ~$0.0037 | ≤ $0.50 (minimum dari actor-nya) |

Total sekitar **$0.80–0.90 per sekali jalan**. Kalau dijalankan seminggu sekali, sekitar $3.2 per bulan, masih di bawah kredit gratis $5. `max_usd_per_run` di config adalah batas keras: kalau tercapai, actor berhenti, jadi hasilnya bisa lebih sedikit dari target. Selain itu ada biaya pemakaian platform Apify (compute) yang kecil; pantau di Apify Console → Billing.

Untuk menghemat, kurangi `results_per_query` atau jumlah keyword, atau matikan platform dengan `"enabled": false`.

## Catatan

- Actor X paling populer (apidojo/tweet-scraper) **tidak bisa dipakai lewat API di paket gratis**, jadi dipakai xquik.
- Actor bisa diganti di `config.json` → `actor`. Kalau inputnya beda, sesuaikan fungsi `build_input()` di `collect.py`.
- Instagram dicari lewat hashtag. Kalau `hashtags` kosong, keyword yang dipakai.
