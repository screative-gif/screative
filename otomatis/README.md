# Workflow carousel otomatis (Discord)

Carousel pilar 2 (fakta / cerita unik / tren): **tayang Sabtu, Senin, Kamis 17.00 WIB** (keputusan user 26 Nov 2026, menggantikan jadwal harian).

| Kapan (WIB) | Yang terjadi |
|---|---|
| Senin & Jumat ± 07.00 | Bot kirim 10 topik radar + bobot ke Discord, dengan reaksi 1️⃣–🔟 |
| Radar Senin: sampai Senin 10.00 · Radar Jumat: sampai Sabtu 10.00 | Tim klik reaksi topik (boleh banyak) atau balas `usul: <topik lain>`. Hanya user di `config.json` yang dihitung |
| Senin 10.00 & Sabtu 10.00 | 2 topik teratas radar Senin → Senin + Kamis; 1 topik teratas radar Jumat → Sabtu. Suara kurang → bobot tertinggi. Jadwal dikirim ke Discord; balas `ganti <hari>: …` untuk tukar |
| Sen, Kam, Sab 10.00 | Carousel hari itu dikerjakan (slide + caption; PDF Canva hanya kalau diminta), dikirim ke Discord |
| Sen, Kam, Sab 15.00 (**1× sehari**) | Bot cek respon: balasan = feedback → direvisi & dikirim ulang (termasuk `ganti topik: …`); ✅ = approved. Feedback setelah 15.00 tidak dikerjakan untuk carousel hari itu |
| Sen, Kam, Sab 17.00 | Tayang otomatis di IG @seakun.id (`otomatis/instagram.py`), **walau belum ada ✅**. Link dikirim ke Discord |

Langkah detail untuk sesi terjadwal: `otomatis/ALUR.md`. Hasil otomatis di-commit ke branch `otomatis/carousel` lalu langsung di-merge ke `main`.

## Setup sekali saja

### 1. Bot Discord (Developer Portal → aplikasi bot kamu)
- **Bot → Privileged Gateway Intents → Message Content Intent: ON** (supaya bot bisa membaca isi balasan tim).
- Undang bot ke server dengan izin di channel: View Channel, Send Messages, Attach Files, Add Reactions, Read Message History.

### 2. Token & akses jaringan (Project settings → Cloud environment → ⚙️ environment Default)
Token **jangan** ditempel di chat atau di-commit. Simpan sebagai **Network secret** (header yang disisipkan otomatis ke host tertentu):

| Host | Header | Nilai |
|---|---|---|
| `discord.com` | `Authorization` | `Bot <token bot Discord>` |
| `api.apify.com` | `Authorization` | `Bearer <token Apify>` |
| `api.magnific.com` | `x-magnific-api-key` | `<API key Magnific>` |
| `graph.facebook.com` | `Authorization` | `Bearer <System-user token Meta>` |

Host yang perlu diizinkan: `discord.com`, `cdn.discordapp.com`, `media.discordapp.net`, `api.apify.com`, `trends.google.com`, `api.magnific.com` (+ host CDN unduhan Magnific), `commons.wikimedia.org`, `upload.wikimedia.org`.

Alternatif kalau Network secret tidak tersedia: environment variable `DISCORD_BOT_TOKEN` (dibaca `discord.py`) dan `APIFY_TOKEN`.

### 3. Tes
`python3 otomatis/discord.py cek` → harus menampilkan nama bot dan nama channel, tanpa mengirim pesan.
`python3 otomatis/instagram.py cek` → menampilkan akun @seakun.id + kuota posting, tanpa memposting.
`python3 otomatis/instagram.py posting --uji` → menyiapkan carousel di Meta tanpa menayangkannya.

## Perintah manual
```bash
python3 otomatis/discord.py status                 # siklus terakhir
python3 otomatis/discord.py baca-pilihan           # lihat suara/usulan tim
python3 otomatis/discord.py baca-feedback          # lihat ✅ & feedback
python3 otomatis/discord.py kirim "teks bebas"
```
