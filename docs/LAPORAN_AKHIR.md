# Laporan Akhir

## 1. Hasil evaluasi

Tempel keluaran `python evaluate.py` setelah `data/ground_truth.csv` dilengkapi.

```text
Dievaluasi: audit.sql, campuran_error.sql, laporan_penjualan.sql, pemeliharaan.sql (27 triple)

Metode   Precision  Recall     F1
parser        1.00    1.00   1.00
regex         0.65    0.81   0.72

[regex]
  salah ditemukan (FP): ('audit.sql', 16, 'sesi', 'R')
  salah ditemukan (FP): ('campuran_error.sql', 4, 'pesanan', 'R')
  salah ditemukan (FP): ('campuran_error.sql', 8, 'keranjang', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'pelanggan', 'D')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'pelanggan', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'pesanan', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'rahasia', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 15, 'pesanan', 'R')
  salah ditemukan (FP): ('pemeliharaan.sql', 2, 'crm.alamat', 'R')
  salah ditemukan (FP): ('pemeliharaan.sql', 2, 'crm.pelanggan', 'R')
  salah ditemukan (FP): ('pemeliharaan.sql', 2, 'pelanggan_lama', 'U')
  salah ditemukan (FP): ('pemeliharaan.sql', 15, 'crm.alamat', 'R')
  terlewat (FN):       ('audit.sql', 2, 'pesanan', 'R')
  terlewat (FN):       ('laporan_penjualan.sql', 3, 'pelanggan', 'R')
  terlewat (FN):       ('laporan_penjualan.sql', 3, 'pesanan', 'R')
  terlewat (FN):       ('pemeliharaan.sql', 3, 'crm.alamat', 'R')
  terlewat (FN):       ('pemeliharaan.sql', 3, 'crm.pelanggan', 'R')
```

## 2. Tiga kasus di mana regex salah

Untuk tiap kasus: SQL-nya, kesalahan regex, dan mengapa parser benar (kaitkan dengan konsep
lexing, parsing, atau resolusi).

1. Tabel target `DELETE` dihitung sebagai `R` (`audit.sql` baris 16).
```sql
DELETE FROM sesi s WHERE s.kedaluwarsa < :sekarang;
```
Regex melaporkan `sesi` sebagai `R` (FP) selain `D`. Dugaan penyebab: pola `FROM <nama>` cocok
dengan `FROM` milik `DELETE`, karena regex tidak tahu `FROM` itu bagian dari statement apa. Pola yang
sama muncul pada `campuran_error.sql` baris 8, `laporan_penjualan.sql` baris 15, dan
`pemeliharaan.sql` baris 15. Parser benar karena ia membangun node `Delete` dengan satu tabel target,
dan analyzer memberi `D` hanya pada tabel itu. Konsepnya adalah parsing: struktur statement
menentukan peran `FROM`, bukan teks di sekitarnya (grammar, Bab 5-6).

2. Teks di dalam komentar dianggap statement (`pemeliharaan.sql` baris 1-2).
```sql
/* Skrip pemeliharaan data pelanggan.
   Catatan lama: UPDATE pelanggan_lama sudah tidak dipakai. */
select c.id, c.nama, a.kota
from crm.pelanggan c
left outer join crm.alamat a on a.pelanggan_id = c.id
```
Regex melaporkan `pelanggan_lama` sebagai `U` (FP). Tabel `crm.pelanggan` dan `crm.alamat` juga
dilaporkan di baris 2 (FP) dan hilang di baris 3 (FN): tabelnya benar tetapi nomor baris statement
salah. Dugaan penyebab: regex tidak membuang komentar, sehingga kata `UPDATE` di dalam komentar
dianggap awal statement dan baris awal statement bergeser ke baris komentar. Parser benar karena
lexer membuang komentar blok sebelum token sampai ke parser, jadi `UPDATE` di komentar tidak pernah
menjadi token `KEYWORD`. Konsepnya adalah lexing: komentar adalah lexeme yang dibuang (Bab 4).
Contoh serupa untuk string: pada `laporan_penjualan.sql` regex melaporkan `rahasia` sebagai tabel,
yang menurut catatan kami berasal dari teks di komentar atau string (cocokkan dengan isi file).

3. Tabel kedua pada `FROM` dengan koma terlewat (`audit.sql` baris 2).
```sql
SELECT p.id, p.nama
FROM pelanggan p, pesanan o
WHERE o.pelanggan_id = p.id
```
Regex melewatkan `pesanan` (FN). Dugaan penyebab: regex hanya mengambil satu nama setelah `FROM`
dan tidak mengenali daftar sumber yang dipisah koma. Parser benar karena `sources` di node `Select`
adalah daftar, dan analyzer menandai tiap sumber sebagai `R`. Konsepnya adalah parsing: daftar
dipisah koma adalah bagian dari grammar, bukan pola teks tunggal.

## 3. Batas pendekatan kami

Minimal tiga hal yang **tidak bisa** ditangani dengan benar oleh tool ini meskipun semua bug
sudah diperbaiki. Untuk tiap batas: contoh SQL atau situasinya, akibatnya pada CRUD matrix,
dan informasi apa yang dibutuhkan untuk mengatasinya.

1. Kolom tanpa qualifier pada lebih dari satu tabel (resolusi tanpa skema).
2. Correlated subquery dengan kolom tanpa qualifier.
3. SQL dinamis dan operasi di luar subset.

## 4. Pembagian kerja

Siapa mengerjakan apa, dan bagaimana kalian memastikan keduanya memahami seluruh kode.
Lexy mengerjakan perbaikan kode
Iyan mengidentifikasi bug dan menyusun file .md

Kami berdua berusaha memahami kode dengan mengerjakan di satu waktu dengan bantuan AI untuk menjelaskan apa yang tidak kami mengerti.