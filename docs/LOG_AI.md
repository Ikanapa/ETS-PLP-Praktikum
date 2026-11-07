# Log Penggunaan AI

Catat setiap penggunaan AI atau coding agent yang memengaruhi kode atau laporan.

| No | Siapa | Prompt / tugas (ringkas) | Hasil: diterima, diubah, atau ditolak | Alasan | Cara verifikasi |
| --- | --- | --- | --- | --- | --- |
| 1 | Lexy | Meminta ringkasan catatan ETS dan urutan kerja | Diterima sebagai urutan kerja | Cocok dengan daftar deliverable di soal | Dicocokkan dengan soal |
| 2 | Iyan | Memeriksa `crud/analyzer.py` | Diterima: cabang `Update` meneruskan `"U"` ke subquery, diganti `"R"` | Aturan SPESIFIKASI bagian 5: tabel di subquery selalu `R` | Test `test_update_subquery_dibaca_bukan_diubah`; `python evaluate.py` |
| 3 | Iyan | Meminta entri `LAPORAN_BUG.md` sesuai template | **Diubah**: nama, nomor baris, dan bagian "Peran AI" diisi sendiri | AI tidak tahu siapa menemukan dan memperbaiki | Dicocokkan dengan kode, `--ast`, dan SPESIFIKASI.md |
| 4 | Iyan | Meminta draf `KARTU_DESAIN.md` | (isi: diterima / diubah / diganti) | Keputusan diambil dari perbaikan yang kami kerjakan | Dicocokkan dengan kode dan spesifikasi |
| 5 | Iyan | Meminta dugaan penyebab kesalahan regex | **Belum diterima**: masih dugaan | AI belum melihat `regex_extractor.py` dan isi sebagian file SQL | (isi setelah dicek ke kode regex) |
| 6 | Lexy | Gemini: pendekatan mengubah SQL kompleks menjadi token lalu AST tanpa library eksternal | Diterima sebagai gambaran struktur node AST; logika `lexer.py` dan `parser.py` diimplementasikan sendiri oleh Lexy | Regex baseline (F1 0.64) tidak menangani `WHERE` kompleks, subquery, dan alias | (isi: pytest / `--ast`) |
| 7 | Lexy | Gemini: cara `resolver.py` memetakan alias ke nama tabel pada kasus test 12 dan 15 | Diterima: saran mapping dictionary alias saat memproses klausa `FROM`; berhasil diimplementasikan | Alias tidak dikenali sehingga tabel tidak terdeteksi | (isi: test mana yang berubah dari gagal ke lulus) |
| 8 | Lexy | Gemini: aturan pemetaan node AST ke C/R/U/D agar tidak ada false positive pada `JOIN` | Diterima: merapikan logika kondisional `analyzer.py`; tabel di `WHERE`/`JOIN` dihitung `R` | Sesuai aturan operasi di SPESIFIKASI bagian 5 | (isi: `python evaluate.py` sebelum dan sesudah) |
| 9 | Lexy | Gemini: error `refusing to merge unrelated histories` dan konflik `.gitignore` | Diterima: `--allow-unrelated-histories` dan `git checkout --ours`; PR berhasil di-merge | Konflik berasal dari dua riwayat Git yang terpisah | `git log` dan `git status` setelah merge; (isi: `__MACOSX` tidak ikut) |

**Refleksi (3-5 kalimat).** Di bagian mana AI paling membantu? Di mana AI keliru atau
menyesatkan, dan bagaimana kalian mengetahuinya?
AI paling membantu menyusun kerangka laporan dan test regresi. AI keliru ketika menebak hal yang belum dilihatnya. Karena itu semua klaim AI kami verifikasi dengan pytest, `evaluate.py`, SPESIFIKASI.md, dan buku acuan, bukan diterima begitu saja.
