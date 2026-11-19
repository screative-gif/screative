# Tim Konten {{BRAND}}

Buka folder ini di Claude Code, lalu cukup panggil **Naka**:

> Naka, riset tren minggu ini
> Naka, feeding minggu ini
> Naka, tulis C1
> Naka, siapkan visual C1
> Naka, render C1

| Agent | Peran |
|---|---|
| **Naka** | Koordinator (`CLAUDE.md`) |
| **Sera** | Pemburu Data (Apify) |
| **Lira** | Analis Tren |
| **Kala** | Perencana Feeding |
| **Diksa** | Penulis |
| **Rupa** | Desainer Visual (`render.py`) |
| **Tilik** | Pemeriksa Visual / QA (`check.py`) |

## Isi folder
- `CLAUDE.md`: instruksi Naka · `.claude/agents/`: anggota tim
- `riset/`: pengumpul & analisis data. Niche & keyword di `riset/config.json`, token Apify di `riset/.env` (rahasia)
- `konten/brand/brand.md`: profil brand · `konten/brand/visual.md` + `visual/brand.json`: identitas visual
- `konten/laporan`, `feed`, `draft`, `visual`: hasil kerja tim

## Kebutuhan
- macOS + Google Chrome (untuk render PNG) + Python 3 dengan Pillow (`pip3 install pillow`)
- Akun Apify gratis ($5 kredit/bulan; satu riset penuh sekitar $0.8)
- Akun ChatGPT untuk membuat ilustrasi
