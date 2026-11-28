# Draft Carousel: Dolar tembus Rp18.300. Kenapa harga yang nggak ada urusannya sama dolar ikut naik? Fakta?

- **Kode:** C-DOLAR · **Jadwal posting:** Sabtu, 28 Nov 2026, 17.00 WIB (mode otomatis)
- **Platform:** Instagram Carousel (@seakun.id), 10 slide, 1080×1350
- **Pilar:** 2 · Fakta Unik (formula: `konten/pilar/fakta-unik/formula.md`, aturan: `konten/pilar/fakta-unik/aturan.md`)
- **Ide asal:** Radar topik `konten/laporan/2026-11-27_radar-topik.md` #1 (rumus 5: klaim + "Fakta?"). Pemicu: post @folkative soal rupiah di atas Rp18.300 (3.183 komentar). Tidak disebut di slide/caption.
- **Fakta:** hanya dari `konten/visual/2026-11-28_C-DOLAR/riset-fakta.md` (sudah dicek Naka). Tidak ada angka lain. Mekanisme (bahan/mesin/kemasan/ongkos kirim, pedagang jaga-jaga stok) ditulis tanpa angka.
- **Jembatan CTA:** tipe Uang/hemat (dari radar).
- **Gaya bahasa (feedback Silvia, Discord):** conversational, seperti teman ngobrol. Kalimat pendek, contoh warung (gorengan, mi instan, tahu tempe, obat warung). Tanpa "Pernahkah kamu…", "Yuk simak", "Bukan sekadar…, tapi…", daftar tiga kata berirama, em-dash, "fenomena", "krusial", "esensial".
- **Batasan:** tidak memprediksi kurs, tidak ada saran investasi/beli dolar, tidak menyalahkan pemerintah/pejabat/negara lain/pedagang, tidak menulis harga Seakun. Australia disebut hanya sebagai fakta asal impor.
- **Penyamaran nama:** tidak ada nama merek/layanan pihak ketiga di carousel ini ("mi instan", "obat warung" ditulis generik).
- **Gaya cover:** `poster` (giliran setelah `editorial` di C-JURUSAN; subjek di kanan, kiri kosong). Naka tetap cek dengan `python3 konten/brand/visual/gaya_cover.py`.

---

## Hook cover

**Utama (rumus 5, dipakai):**
```
DOLAR TEMBUS RP18.300.
KENAPA HARGA YANG NGGAK ADA
URUSANNYA SAMA DOLAR
__IKUT NAIK__? FAKTA?
```

**Alternatif 1 (contoh warung di depan):**
```
DOLARNYA DI BERITA,
NAIKNYA KERASA
DI __GEROBAK GORENGAN__.
KOK BISA?
```

**Alternatif 2 (kejutan tahu tempe):**
```
TAHU TEMPE ITU
MAKANAN PALING LOKAL.
KEDELAINYA?
__± 95% IMPOR__.
```

---

### Slide 1 · Cover
Kicker: FAKTA UNIK
Judul: DOLAR TEMBUS RP18.300.\nKENAPA HARGA YANG NGGAK ADA\nURUSANNYA SAMA DOLAR\n__IKUT NAIK__? FAKTA?
Subjudul: Gorengan depan gang juga kena. Ini jalurnya.
Gaya cover: **`poster`** (subjek di kanan, sisi kiri kosong untuk judul)
Gambar: **gambar umum (cover ElevenLabs oleh Naka, 4:5 · 2K · high)**. Tanpa teks, tanpa logo, tanpa wajah orang sungguhan.
- Deskripsi: gerobak gorengan di mulut gang Jakarta menjelang magrib, berada di sepertiga kanan frame. Tumpukan bakwan dan tahu goreng di etalase kaca berembun, lampu bohlam kuning, minyak mengepul. Tangan penjual (tanpa wajah) mengangkat gorengan pakai serok. Sisi kiri: tembok gang gelap dan bokeh lampu motor, kosong.
- Prompt (siap pakai):
  > Cinematic realistic photo, 4:5 vertical. A street fritter cart (gerobak gorengan) at the mouth of a narrow Jakarta alley at dusk, placed in the right third of the frame. Glass display case with piles of golden fried fritters and fried tofu, a warm hanging bulb, steam and oil smoke rising. Only the vendor's hands are visible, lifting fritters with a wire strainer, no face. The left half of the frame is calm and dark: a plain alley wall and soft blurred motorbike light bokeh, no important details there (reserved for a headline). Warm, slightly tense everyday mood, amber and deep teal tones, shallow depth of field, 35mm film look. No text, no letters, no logos, no price tags, no readable signs, no banknotes, no recognizable person, no faces.
- Cadangan (kalau gaya cover ternyata `lingkar`): close-up piring berisi gorengan, tahu, dan tempe goreng di meja warung kayu, subjek tengah-bawah, bagian atas kosong.
Alasan: gorengan langsung terbaca "harga sehari-hari", tanpa memakai simbol dolar atau uang yang terkesan ajakan beli valas.

### Slide 2 · Pembuka: angkanya dulu
Label: 01 · ANGKANYA
Judul: Rabu kemarin, 1 dolar\n__Rp18.303__.
Isi: Itu kurs resmi **JISDOR BI**, Rabu **25 Nov 2026**. Sehari sebelumnya masih **Rp18.204**. Jadi cuma dalam sehari naik **Rp99**. Kamis paginya di pasar spot malah sudah **Rp18.340**.
Visual data: **angka raksasa** “Rp18.303”, teks kecil di bawah: kurs JISDOR BI, 25 Nov 2026 (24 Nov: Rp18.204)
Penutup: **Kelihatannya cuma angka di berita. Tapi angka ini nyampe ke dapur.**
Sumber: Kontan, 26 Nov 2026 (kurs JISDOR BI 24–25 Nov & spot 26 Nov)
Gambar: **gambar umum** (Magnific stok): papan kurs digital di kantor penukaran uang, angka & tulisan buram/tidak terbaca. Jangan foto tumpukan dolar atau orang memegang dolar (biar nggak terbaca ajakan beli valas).

### Slide 3 · Puncak: dibanding setahun lalu
Label: 02 · SETAHUN LALU
Judul: Setahun lalu masih\n__Rp16.675__.
Isi: Akhir November 2025, rupiah ditutup **Rp16.675** per dolar. Sekarang **Rp18.303**. Selisihnya **sekitar Rp1.600**, kira-kira **10%**. Barang yang belinya pakai dolar, otomatis jadi segitu lebih mahal buat kita.
Visual data: **DULU vs SEKARANG** berdampingan
- DULU · 28 Nov 2025: Rp16.675
- SEKARANG · 25 Nov 2026: Rp18.303
- Pita kecil di tengah: “± Rp1.600 (± 10%)”
Keterangan kecil wajib di bawah: *2025 = penutupan pasar (Bloomberg), 2026 = JISDOR BI; selisih dibulatkan*
Penutup: **Harga di luar sana sama. Rupiahnya yang harus keluar lebih banyak.**
Sumber: Bisnis.com, 28 Nov 2025 (data Bloomberg); Kontan, 26 Nov 2026 (JISDOR BI). Selisih = hitungan Naka, dibulatkan.
Catatan untuk Rupa: tulis “sekitar/±”, jangan jadikan angka pasti (misalnya “Rp1.628” atau “9,8%”).
Gambar: **tanpa foto** (slide data di latar kertas brand).

### Slide 4 · Detail relate: gorengan & mi instan
Label: 03 · GORENGAN & MI INSTAN
Judul: Gorengan kamu\nawalnya __dari kapal__.
Isi: Terigu itu dari **gandum**, dan gandum bukan tanaman yang banyak ditanam di sini. Tahun **2025** kita impor **10,84 juta ton** biji gandum, nilainya **US$3,05 miliar**. Paling banyak dari Australia, sekitar **42%**.
Visual data: **angka raksasa** “10,84 juta ton”, teks kecil: impor biji gandum Indonesia 2025 (2024: 11,72 juta ton)
Penutup: **Jadi tiap gigit bakwan, ada dolar yang ikut kebayar.**
Sumber: GoodStats, 18 Sep 2026 (data BPS)
Gambar: **gambar umum** (Magnific stok): bakwan dan tahu goreng di etalase gerobak, atau semangkuk mi instan polos tanpa bungkus/merek. Tidak ada nama merek yang terbaca.

### Slide 5 · Detail relate: tahu tempe
Label: 04 · TAHU TEMPE
Judul: Paling lokal,\ntapi kedelainya __± 95% impor__.
Isi: Tahun ini kita butuh kedelai sekitar **2,7 juta ton**. Yang dipanen sendiri rata-rata cuma **± 227 ribu ton** setahun. Akhirnya sekitar **95%** kebutuhan harus diimpor. Pelemahan rupiah disebut jadi salah satu penyebab harga kedelai naik.
Visual data: **grafik batang** horizontal, 2 batang, judul kecil “Kedelai Indonesia”
- Kebutuhan 2026: ± 2,7 juta ton (batang panjang)
- Panen sendiri: ± 227 ribu ton/tahun (batang pendek, oranye)
Penutup: **Rupiah melemah, pengrajin tahu tempe yang duluan pusing.**
Sumber: CNBC Indonesia, 19 Jun 2026 (data Kementan; pengamat Khudori)
Gambar: **gambar umum** (Magnific stok): papan tempe dan potongan tahu di lapak pasar tradisional, atau karung kedelai di tempat produksi tahu. Tanpa wajah, tanpa merek.

### Slide 6 · Detail relate: obat warung
Label: 05 · OBAT WARUNG
Judul: Obat di warung pun,\nbahan bakunya __± 90% impor__.
Isi: Kata **Kepala BPOM**, sekitar **90%** bahan baku obat di Indonesia masih impor. Pabriknya boleh di sini. Tapi kalau bahannya dibeli pakai dolar, ongkos bikinnya ikut kena.
Visual data: **angka raksasa** “± 90%”, teks kecil: bahan baku obat di Indonesia yang masih impor (BPOM, Jul 2026)
Penutup: **Dibuat di sini belum tentu bahannya dari sini.**
Sumber: detikHealth, 6 Jul 2026 (pernyataan Kepala BPOM Taruna Ikrar)
Catatan isi: slide ini **tidak** menyebut obat tertentu, dosis, atau klaim harga obat sudah naik (tidak ada datanya). Hanya fakta bahan baku + mekanisme.
Gambar: **gambar umum** (Magnific stok): rak kecil obat strip/sachet di etalase warung, kemasan buram dan merek tidak terbaca. Catatan: BPOM disebut di slide, tapi **jangan pakai logo BPOM atau foto Kepala BPOM**; angkanya yang jadi pusat.

### Slide 7 · SLIDE KEJUTAN · Jalur yang nggak kelihatan
Label: 06 · YANG NGGAK KELIHATAN
Judul: Barangnya lokal,\n__ongkosnya belum tentu__.
Isi: Yang kebayar dolar nggak cuma bahannya. Sering ada mesin pabrik, plastik kemasan, sampai ongkos kirim yang ikut dihitung pakai dolar. Semuanya numpuk diam-diam di harga akhir.
Visual data: **mockup struk/nota warung jadul** (gaya beda dari slide lain: kertas struk termal agak kusut, huruf mesin kasir, tanpa nama toko/merek)
- BAHAN ............ $
- MESIN ............ $
- KEMASAN .......... $
- ONGKOS KIRIM ..... $
- TOTAL: “kok naik ya?”
Keterangan kecil wajib di slide: *ilustrasi, bukan data*
Penutup: **Kamu bayar pakai rupiah. Sebagian ongkosnya dibayar pakai dolar.**
Sumber: penjelasan mekanisme umum (tanpa angka), dari catatan `riset-fakta.md`.
Gambar: **tanpa foto** (mockup struk dibuat Rupa).

### Slide 8 · Analisis "kenapa": pedagang jaga-jaga
Label: 07 · JAGA-JAGA
Judul: Harga naik duluan,\nmikirin __stok minggu depan__.
Isi: Pedagang nggak cuma lihat modal hari ini. Kalau kulakan berikutnya bakal lebih mahal, harga di etalase ikut disesuaikan dari sekarang. Biar uang hasil jualan cukup buat belanja stok lagi.
Visual data: **garis waktu** 3 titik dengan panah
- Kurs naik → Modal kulakan naik → Harga di etalase ikut naik
Penutup: **Pedagang juga lagi jaga dapurnya sendiri.**
Sumber: penjelasan mekanisme umum (tanpa angka), dari catatan `riset-fakta.md`.
Catatan nada: tidak menyalahkan pedagang. Penutup sengaja berpihak ke pedagang kecil.
Gambar: **gambar umum** (Magnific stok): pedagang pasar tradisional menata dagangan (sayur/tahu/tempe), tampak samping atau belakang, tanpa wajah menghadap kamera.

### Slide 9 · Ringkasan + penutup reflektif
Label: 08 · RINGKASNYA
Judul: Dolarnya jauh,\n__efeknya sampai warung__.
Isi: Banyak barang yang kelihatan lokal ternyata bahannya dibeli dari luar. Begitu rupiah melemah, ongkosnya naik pelan-pelan sampai ke harga yang kita bayar.
Visual data: **tabel** 2 kolom
| KELIHATANNYA | ASLINYA |
|---|---|
| Gorengan & mi instan | Terigunya dari gandum impor (10,84 juta ton, 2025) |
| Tahu tempe | ± 95% kedelainya impor |
| Obat warung | ± 90% bahan baku obat impor |
| Harga naik duluan | Pedagang jaga-jaga stok berikutnya |
Penutup: **Kamu paling kerasa di mana: gorengan atau tahu tempe? Cerita di komentar.**
Sumber: rangkuman slide 4–8 (GoodStats/BPS 2026, CNBC Indonesia 2026, detikHealth 2026)
Gambar: **tanpa foto** (tabel di latar kertas brand).

### Slide 10 · CTA Seakun
Label: SEAKUN
Judul (kalimat jembatan, tebal): Kurs boleh naik-turun.\nLangganan kamu nggak harus ikut __bikin boncos__.
Manfaat: Patungan aja di seakun.id. Aman, legal, lebih hemat.
Visual data: **kotak harga baku** (otomatis dari `brand.json` `cta_harga` di layout `cta-seakun`; jangan menulis `layanan`/`judul_harga` di spec).
Label ajakan (satu saja): **Kunjungi seakun.id**
Sumber: (tidak ada)
Gambar: latar = foto cover yang di-blur (default `render.py`, aturan 1b). Tidak perlu foto baru. Tidak menulis `tombol`, `footer`, `bar_kanan`.
Catatan: tidak ada harga/daftar layanan yang ditulis manual. Kalimat jembatan sesuai permintaan Naka, dipecah 2 baris; "patungan aja di seakun.id" dipindah ke baris manfaat supaya judul tetap 2 baris.

---

## Caption

Kamu paling kerasa di mana: gorengan atau tahu tempe?

Dolar memang jauh dari dompet kita. Tapi terigu buat gorengan itu dari gandum impor, kedelai buat tahu tempe sekitar 95% juga dari luar. Jadi pas rupiah melemah, efeknya pelan-pelan nyampe ke warung depan rumah.

Ceritain harga apa yang paling bikin kamu kaget minggu ini.

---

## Sumber (untuk draft, footer slide, dan `foto/SUMBER.md`; bukan untuk caption)
1. Kontan, 26 Nov 2026 09.48 WIB, https://finansial.kontan.co.id/news/sentuh-level-rp18300-cek-kurs-dolar-as-rupiah-di-4-bank-besar-kamis-2611 : JISDOR BI 25 Nov 2026 Rp18.303 (melemah Rp99 dari 24 Nov Rp18.204); spot Kamis pagi 26 Nov Rp18.340 → slide 1, 2, 3
2. Bisnis.com, 28 Nov 2025, https://market.bisnis.com/read/20251128/93/1932547/rupiah-ditutup-lesu-ke-level-rp16675-per-dolar-as : rupiah ditutup Rp16.675 per dolar AS, 28 Nov 2025 (Bloomberg, penutupan pasar, bukan JISDOR). Selisih ± Rp1.600 (± 10%) = hitungan Naka, campuran spot vs JISDOR, ditulis "sekitar" → slide 3
3. GoodStats, 18 Sep 2026 (data BPS), https://goodstats.id/article/impor-gandum-indonesia-masih-tinggi-negara-mana-yang-jadi-pemasok-utama-6WGss : impor biji gandum 2025 10,84 juta ton (2024: 11,72 juta ton), US$3,05 miliar, Australia ± 42%; gandum bukan tanaman pangan yang dibudidayakan luas di Indonesia → slide 4, 9
4. CNBC Indonesia, 19 Jun 2026, https://www.cnbcindonesia.com/news/20260619105731-4-743998/ri-impor-90-kedelai-produksi-turun-terus-pemerintah-harus-apa : kebutuhan kedelai 2026 ± 2,7 juta ton, ± 95% impor (Kementan), produksi dalam negeri ± 227 ribu ton/tahun; pelemahan rupiah disebut salah satu penyebab harga kedelai naik → slide 5, 9
5. detikHealth, 6 Jul 2026, https://health.detik.com/berita-detikhealth/d-8561517/90-persen-bahan-baku-obat-ri-masih-impor-bpom-perkuat-pengujian-laboratorium : ± 90% bahan baku obat di Indonesia masih impor (Kepala BPOM Taruna Ikrar) → slide 6, 9
6. Mekanisme tanpa angka (slide 7 & 8): bahan/mesin/kemasan/ongkos kirim yang dibayar dolar; pedagang menaikkan harga untuk jaga-jaga stok berikutnya. Dari catatan `konten/visual/2026-11-28_C-DOLAR/riset-fakta.md`.

---

## Catatan untuk Naka, Rupa, Tilik & Sidik
- Semua angka dari `riset-fakta.md`. **Tidak ada `[CEK FAKTA]`.** Yang tidak terverifikasi (rekor terendah sepanjang sejarah, porsi impor BBM, layanan digital yang ditagih dolar) **sengaja tidak dipakai**, termasuk di slide CTA.
- **Keterangan wajib yang jangan hilang saat render (Tilik tolong cek):** slide 3 (*2025 = penutupan pasar Bloomberg, 2026 = JISDOR BI; selisih dibulatkan*), slide 7 (*ilustrasi, bukan data*). Selisih slide 3 selalu ditulis “±/sekitar”.
- **Arahan gambar per slide:**
  - **Cover:** ElevenLabs oleh Naka, gaya `poster` (gerobak gorengan di kanan, kiri kosong).
  - **Gambar umum → Magnific stok:** slide 2 (papan kurs buram, tanpa tumpukan dolar), slide 4 (gorengan/mi instan polos tanpa merek), slide 5 (tahu tempe di pasar/karung kedelai), slide 6 (obat strip di warung, merek buram, tanpa logo BPOM), slide 8 (pedagang pasar tampak samping/belakang).
  - **Nama spesifik → Sidik:** **tidak ada.** Nama yang muncul (BI/JISDOR, BPOM, Kementan, Australia) adalah lembaga/negara sebagai sumber data, bukan subjek gambar. Jangan pakai logo lembaga atau foto pejabat.
  - **Tanpa foto:** slide 3 (DULU vs SEKARANG), slide 7 (mockup struk, slide kejutan), slide 9 (tabel), slide 10 (latar = cover di-blur).
- **Batasan topik:** tidak ada prediksi kurs, tidak ada ajakan beli/simpan dolar, tidak menyalahkan pemerintah/pejabat/negara lain/pedagang, tidak menyebut berita bea masuk AS (gugur di radar). Tidak ada harga Seakun.
- Gaya bahasa sudah disesuaikan feedback Silvia: tanpa em-dash di teks slide/caption, tanpa pembuka "Pernahkah kamu", tanpa "Yuk simak", tanpa pola "Bukan sekadar…, tapi…", tanpa daftar tiga kata berirama, tanpa kata "fenomena/krusial/esensial".
- Tidak ada ajakan "geser/swipe". Slide CTA hanya 1 ajakan ("Kunjungi seakun.id"). Caption tanpa sumber, tanpa hashtag, tanpa baris CTA produk; pembukanya pertanyaan pilihan (usulan radar: pertanyaan pilihan lebih gampang dijawab). Tanda kutip melengkung “…” dipakai di semua kutipan.
