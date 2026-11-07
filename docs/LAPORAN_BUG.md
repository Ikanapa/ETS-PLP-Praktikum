# Laporan Bug

Salin blok di bawah untuk setiap bug. Bagian **Akar masalah** wajib ditulis dengan kata-kata
sendiri dan memakai konsep dari *Crafting Interpreters* (sebutkan bab). Bagian ini diuji lisan.

---

## Bug 1: Keyword huruf kecil dikenali sebagai IDENT

**Ditemukan oleh:** Iyan · **Diperbaiki oleh:** Lexy

**Gejala.** tokenize("select id from t") menghasilkan Token(IDENT, 'select', 1:1). Menurut SPESIFIKASI.md bagian 2.2, keyword tidak peka huruf besar/kecil dan nilai tokennya dinormalisasi ke huruf besar, sehingga seharusnya Token(KEYWORD, 'SELECT', 1:1). Test terlihat test_keyword_huruf_kecil gagal.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
select 1 from t
```

**Akar masalah.** _word() membandingkan teks asli (text in KEYWORDS) dengan KEYWORDS yang  hurufnya besar semua, jadi select tidak bisa cocok. Konsepnya dari 4.7 Reserved Words and Identifiers

**Perbaikan.** crud/lexer.py, fungsi _word() : teks diubah ke huruf besar (text.upper()) sebelum dicek ke KEYWORDS, dan token keyword menyimpan versi huruf besar. IDENT tetap memakai teks asli karena normalisasi huruf kecil menjadi tugas parser (spec 2.2). Alternatif yang dipertimbangkan: (a) mengisi KEYWORDS dengan semua variasi huruf, ditolak karena tidak mungkin mencakup sElEcT dan melanggar syarat bahwa nilai token ternormalisasi; (b) menormalisasi di parser, ditolak karena membuat tipe token (KEYWORD vs IDENT) salah sejak lexer.

**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.
Output sebelum perbaikan test_keyword_campuran_huruf :
FAILED tests/test_tambahan.py::test_keyword_campuran_huruf - AssertionError: assert (<TokenType.I... 2>, 'Select') == (<TokenType.K... 1>, 'SELECT')

Sesudah : tests/test_tambahan.py::test_keyword_campuran_huruf PASSED    


**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?
ya, sesuai yang dilampirkan di file LOG_AI.md

---


## Bug 2: Operator <> terpecah menjadi < dan >

**Ditemukan oleh:** Iyan · **Diperbaiki oleh:** Lexy

**Gejala.** Di laporan_penjualan.sql, parser melaporkan Baris 6, kolom 41 : diharapkan ekspresi, ditemukan '>', dan test test_matrix_laporan_penjualan gagal, nah saya menduga penyebabnya di bagian <> di baris tsb, karena menurut spec 2.5, lexer selalu mengambil operator terpanjang yang cocok, jadi <> harus satu token OP.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
SELECT a FROM t WHERE a <> 1
```

**Akar masalah.** Cabang < di _scan_token() cuma mengecek = setelahnya (<=), tidak mengecek >. Karena itu < berdiri sendiri, lalu > malahan dibaca sebagai token terpisah, dan parser menemukan > di tempat yang harusnya mengharapkan ekspresi. Mekanismenya adalah match() dari 4.6, yaitu melihat satu karakter berikutnya dan memakannya hanya jika cocok.

**Perbaikan.** crud/lexer.py, _scan_token(), cabang <: cek > lebih dulu, lalu =, baru fallback ke <, dan hanya satu _add yang dipanggil per cabang. Alternatif: membiarkan lexer menghasilkan < dan > lalu menggabungkannya di parser. Ditolak karena menggeser tanggung jawab lexical ke parser dan melanggar spec 2.5.

**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.
Output sebelum perbaikan test_operator_terpanjang :
FAILED tests/test_tambahan.py::test_operator_terpanjang - AssertionError: assert (<TokenType.OP: 6>, '<') == (<TokenType.OP: 6>, '<>')

Sesudah : tests/test_tambahan.py::test_operator_terpanjang PASSED  

**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?
ya, bisa diverifikasi di file LOG_AI.md

---


## Bug 3: Kutip kembar '' di dalam string tidak ditangani

**Ditemukan oleh:** Iyan · **Diperbaiki oleh:** Lexy

**Gejala.** Pada kode lama, 'O''Brien' dibaca sebagai dua token string (O dan Brien) karena string berhenti di kutip pertama (hasil penelusuran kode _string()). Menurut spec 2.4, '' mewakili satu kutip, jadi hasil yang benar adalah satu token STRING bernilai O'Brien.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
SELECT 'O''Brien' FROM t
```

**Akar masalah.** _string() menganggap kutip tunggal pertama yang ditemui sebagai penutup, tanpa melihat karakter setelahnya. Konsepnya dari 4.6.1 String literals : lexeme panjang dibaca terus oleh kode khusus sampai akhir yang sebenarnya, dan menentukan akhir itu membutuhkan lookahead.

**Perbaikan.** crud/lexer.py, _string() : setelah membaca ', jika _peek() juga ', konsumsi dan tambahkan satu kutip ke isi lalu lanjutkan. Jika bukan, itu penutup dan loop berhenti. Alternatif : membaca string mentah lalu mengganti '' dengan ' setelahnya. Ditolak karena tidak bisa membedakan penutup string dari kutip kembar ('' string kosong dengan awal kutip kembar).

**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.
Output sebelum perbaikan test_string_kutip_kembar :
FAILED tests/test_tambahan.py::test_string_kutip_kembar - assert [(<TokenType.... 4>, 'Brien')] == [(<TokenType....>, "O'Brien")]

Sesudah : tests/test_tambahan.py::test_string_kutip_kembar PASSED 

**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?
ya, bisa diverifikasi di file LOG_AI.md

---


## Bug 4: Komentar blok /* ... */ belum didukung (TODO T3)

**Ditemukan oleh:** Iyan · **Diperbaiki oleh:** Lexy

**Gejala.** tokenize("/* komentar\n dua baris */ SELECT") melempar LexError : Baris 1, kolom 1 : komentar blok belum didukung. Akibatnya pemeliharaan.sql gagal dengan LEX ERROR dan test test_komentar_blok gagal. Spec 2.3 meminta komentar blok boleh lintas baris, boleh berisi *, tidak bersarang, tidak menghasilkan token, dan yang tidak ditutup adalah LexError.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
/* c */ SELECT 1 FROM t
```

**Akar masalah.** Cabang / + * di _scan_token() langsung raise LexError, jadi komentar blok tidak pernah dipindai. Konsepnya dari 4.6 Longer lexemes : setelah awal lexeme ketahuan, kode khusus memakan karakter sampai penutupnya, dan komentar dibuang dengan tidak memanggil addToken().

**Perbaikan.** crud/lexer.py, _scan_token() : setelah melewati * pembuka, loop dengan _advance() sampai menemukan pasangan * dan /, lalu return tanpa token. Jika input habis sebelum penutup, lempar LexError("komentar blok tidak ditutup", line, col) di posisi awal komentar. Memakai _advance() menjaga nomor baris dan kolom tetap benar setelah komentar lintas baris. Alternatif yang ditolak : (a) menghapus komentar dengan regex sebelum lexing, karena merusak nomor baris dan kolom serta salah mengenali /* */ di dalam string, (b) mendukung nesting, karena spec bagian 9 menyatakan di luar lingkup.

**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.
Output sebelum perbaikan test_komentar_blok_kasus_tepi dan test_posisi_setelah_komentar_lintas_baris:
FAILED tests/test_tambahan.py::test_komentar_blok_kasus_tepi - crud.lexer.LexError: Baris 1, kolom 1: komentar blok belum didukung
FAILED tests/test_tambahan.py::test_posisi_setelah_komentar_lintas_baris - crud.lexer.LexError: Baris 1, kolom 1: komentar blok belum didukung

Sesudah : 
tests/test_tambahan.py::test_komentar_blok_kasus_tepi PASSED
tests/test_tambahan.py::test_posisi_setelah_komentar_lintas_baris PASSED


**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?
ya, bisa diverifikasi di file LOG_AI.md

---

<!-- Bug yang ada di parser -->
## Bug 5: Presedensi AND dan OR disamakan

**Ditemukan oleh:** Iyan · **Diperbaiki oleh:** Lexy

**Gejala.** Pada python -m crud.cli data/sample/audit.sql --ast, kondisi WHERE berbentuk AND(OR(AND(A,B), C), D). Dari pohonnya, kondisi aslinya berpola A AND B OR C AND D. Menurut SPESIFIKASI.md bagian 3.1, OR berpresedensi lebih rendah dari AND, sehingga pohon yang benar adalah OR(AND(A,B), AND(C,D)).

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
SELECT a FROM t WHERE a = 1 OR b = 2 AND c = 3
```

**Akar masalah.** Method _logical() memproses AND dan OR dalam satu loop (while self._check_kw("AND", "OR")), sehingga keduanya berada di satu tingkat presedensi dan digabung dari kiri ke kanan. Konsep yang dilanggar ada di 6.1 : grammar harus dibuat bertingkat, satu rule per tingkat presedensi, dan tiap rule hanya mencocokkan ekspresi pada tingkatnya atau yang lebih tinggi. Dua operator berbeda presedensi tidak boleh berbagi satu rule. Method lain di parser (_additive, _multiplicative) sudah mengikuti pola itu, hanya _logical yang menyimpang.

**Perbaikan.** crud/parser.py: _logical() dipecah menjadi _or() (loop atas OR, operand dari _and()) dan _and() (loop atas AND, operand dari _not()). _expr() sekarang memanggil _or(). Alternatif yang dipertimbangkan : tabel presedensi dengan Pratt parser / precedence climbing, ditolak karena seluruh parser memakai gaya satu method per tingkat dan spesifikasi menuliskan grammar per tingkat, jadi pemecahan method lebih konsisten dan lebih mudah dicocokkan dengan grammar (6.2).

**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.
Output sebelum perbaikan test_or_lebih_rendah_dari_and dan test_and_lalu_or :
tests/test_tambahan.py::test_or_lebih_rendah_dari_and FAILED  
tests/test_tambahan.py::test_and_lalu_or PASSED  

Sesudah : 
tests/test_tambahan.py::test_or_lebih_rendah_dari_and PASSED
tests/test_tambahan.py::test_and_lalu_or PASSED 

**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?
ya, bisa diverifikasi di file LOG_AI.md

---

## Bug 6: Error recovery

**Ditemukan oleh:** Iyan · **Diperbaiki oleh:** Lexy

**Gejala.** laporan_penjualan.sql hanya ada satu parse error, tetapi FileResult.statements kosong, SPESIFIKASI.md bagian 6 menyatakan bahwa setelah error, token dibuang sampai dan termasuk ; berikutnya, dan statement valid sesudahnya tetap diproses.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
SELECT FROM t;
SELECT a FROM u;
```

**Akar masalah.** _synchronize() lama hanya berisi while not self._at_end(): self._advance(), tanpa kondisi berhenti, jadi semua token sampai EOF dibuang. Konsep yang dilanggar ada di 6.3.1 dan 6.3.3 : setelah error, parser harus bersinkronisasi ke sebuah titik yang ditentukan, yaitu membuang token hanya sampai batas statement.

**Perbaikan.** crud/parser.py, _synchronize(): loop memanggil _advance() lalu berhenti begitu token yang dikonsumsi adalah ;. Kasus tepi yang dicek : jika token pemicu error adalah ; itu sendiri (SELECT a FROM ;), ; tersebut yang dikonsumsi dan loop berhenti, sehingga statement berikutnya tidak ikut terbuang.

**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.
Output sebelum perbaikan test_recovery_satu_error_per_statement dan test_recovery_error_tepat_di_titik_koma. :
tests/test_tambahan.py::test_recovery_satu_error_per_statement FAILED  
tests/test_tambahan.py::test_recovery_error_tepat_di_titik_koma FAILED 

Sesudah : 
tests/test_tambahan.py::test_recovery_satu_error_per_statement PASSED
tests/test_tambahan.py::test_recovery_error_tepat_di_titik_koma PASSED  

**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?
ya, bisa diverifikasi di file LOG_AI.md

---

## Bug 7: LEFT OUTER JOIN ditolak

**Ditemukan oleh:** Iyan · **Diperbaiki oleh:** Lexy

**Gejala.** LEFT OUTER JOIN menghasilkan error diharapkan JOIN, ditemukan 'OUTER'. Grammar di SPESIFIKASI.md bagian 3 menulis join = [ "INNER" | "LEFT" [ "OUTER" ] ] "JOIN" ..., jadi bentuk ini valid.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
SELECT a FROM t LEFT OUTER JOIN u ON t.x = u.x
```

**Akar masalah.** _join() mencocokkan LEFT lalu langsung mengharuskan JOIN, sehingga elemen opsional OUTER tidak pernah ditangani. Konsep dari 6.2 (recursive descent) : setiap method harus menerima tepat apa yang diterima rule grammarnya. Elemen opsional di grammar berarti ada cabang if match(...) di kode.

**Perbaikan.** crud/parser.py, _join(): di dalam cabang LEFT ditambahkan self._match_kw("OUTER") sebelum _expect_kw("JOIN"). kind tetap "LEFT" sesuai komentar field di ast_nodes.py, dan OUTER tanpa LEFT tetap error sesuai grammar. Alternatif yang dipertimbangkan: menerima OUTER di mana pun sebelum JOIN. Ditolak karena akan menerima OUTER JOIN dan INNER OUTER JOIN yang bukan bagian grammar.

**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.
Output sebelum perbaikan test_left_outer_join :
tests/test_tambahan.py::test_left_outer_join FAILED  

Sesudah : 
tests/test_tambahan.py::test_left_outer_join PASSED 

**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?
ya, bisa diverifikasi di file LOG_AI.md

---

<!-- Bug resolver -->
## Bug 8: Qualifier dicari dari scope terluar, bukan terdalam

**Ditemukan oleh:** Iyan · **Diperbaiki oleh:** Lexy

**Gejala.** Pada python -m crud.cli data/sample/audit.sql --ast, x.total di dalam subquery ter-resolve ke pelanggan (scope luar), padahal x juga dideklarasikan di subquery sebagai pesanan. Menurut SPESIFIKASI.md bagian 4.3, qualifier dicari dari scope terdalam ke luar.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
SELECT 1 FROM pelanggan x
WHERE EXISTS (SELECT 1 FROM pesanan x WHERE x.total > 0);
```

**Akar masalah.** _lookup() mengumpulkan rantai scope dari terdalam ke terluar, lalu membalikkannya dengan reversed(chain), sehingga scope terluar dicek lebih dulu dan menang. Menurut Bab 11, scope berbentuk stack dan pencarian nama berjalan dari scope terdalam ke luar, berhenti di kecocokan pertama. Itulah yang membuat deklarasi dalam menutupi (shadow) deklarasi luar. Dengan urutan terbalik, nama luar mengalahkan nama dalam, sehingga shadowing tidak pernah terjadi.

**Perbaikan.** crud/resolver.py, _lookup(): list chain dan reversed(chain) dihapus. Sebagai gantinya, loop while scope is not None memeriksa scope.entries mulai dari scope saat ini, lalu naik ke parent, dan mengembalikan kecocokan pertama. Alternatif yang ditolak: mempertahankan chain dan hanya mengganti urutan iterasi, karena list tambahan itu tidak punya fungsi lain dan hanya membuka peluang salah urut.

**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.
Output sebelum perbaikan test_qualifier_dicari_dari_terdalam :
tests/test_tambahan.py::test_qualifier_dicari_dari_terdalam FAILED 

Sesudah : 
tests/test_tambahan.py::test_qualifier_dicari_dari_terdalam PASSED  

**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?
ya, bisa diverifikasi di file LOG_AI.md

---

## Bug 9: Scope tidak di-pop setelah DELETE

**Ditemukan oleh:** Iyan · **Diperbaiki oleh:** Lexy

**Gejala.** Pada audit.sql (baris 18), s.id ter-resolve ke sesi dari statement DELETE sebelumnya, padahal seharusnya error “alias tidak terdefinisi”. Menurut SPESIFIKASI.md bagian 4.5, setiap statement berdiri sendiri dan tidak ada scope yang tersisa.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
DELETE FROM sesi s WHERE s.id = 1;
SELECT s.id FROM pesanan p;
```

**Akar masalah.** _delete() memanggil _push() tetapi tidak pernah _pop(), sedangkan _select() dan _update() berpasangan dengan benar. Menurut Bab 11, scope dibuka saat masuk blok dan harus ditutup saat keluar. Kalau tidak, stack terus bertambah dan isi scope lama terlihat oleh kode sesudahnya. Di sini entri s tertinggal di self.scope saat statement berikutnya diproses.

**Perbaikan.** crud/resolver.py, _delete(): ditambahkan self._pop() di akhir method.  Pasangan push/pop bisa dibungkus try/finally atau context manager supaya lupa pop tidak mungkin terjadi.

**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.
Output sebelum perbaikan test_scope_tidak_bocor_setelah_delete :
tests/test_tambahan.py::test_scope_tidak_bocor_setelah_delete FAILED 

Sesudah : 
tests/test_tambahan.py::test_scope_tidak_bocor_setelah_delete PASSED 

**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?
ya, bisa diverifikasi di file LOG_AI.md

---

## Bug 10: Tabel di subquery UPDATE dicatat sebagai U, bukan R

**Ditemukan oleh:** Iyan · **Diperbaiki oleh:** Lexy

**Gejala.** Pada UPDATE yang memiliki subquery di SET atau WHERE, tabel yang hanya dibaca muncul dengan operasi U di CRUD matrix. Menurut SPESIFIKASI.md bagian 5, tabel yang dibaca lewat subquery selalu R. Akibatnya matrix berisi operasi tulis yang tidak pernah terjadi, dan skor evaluate.py turun karena operasi yang diprediksi tidak cocok dengan label.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
UPDATE pesanan SET total = 0 WHERE id IN (SELECT id FROM batal);
```

**Akar masalah.** Cabang Update di analyze_statement() meneruskan "U" sebagai argumen op ke _collect(). Fungsi itu menerapkan op ke semua tabel yang ditemukan di dalam subquery, sehingga operasi milik tabel target (pesanan) ikut menempel pada tabel lain (batal). Aturannya, U hanya berlaku untuk tabel yang diubah oleh statement itu sendiri, sedangkan tabel yang muncul di dalam subquery hanya dibaca. Cabang Delete sudah benar karena memakai "R", jadi cabang Update tidak konsisten dengan Delete untuk aturan yang sama.

**Perbaikan.** crud/analyzer.py, cabang Update: argumen op untuk _collect() pada assignments dan where diubah dari "U" menjadi "R". Tabel target tetap ditandai U lewat usage[stmt.table.name].add("U"). Alternatif yang ditolak: menghapus parameter op dari _collect() dan selalu memakai "R". Cara itu lebih sederhana, tetapi mengubah signature helper yang masih dipakai _collect_select() untuk SELECT dengan op dari pemanggilnya.

**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.
Output sebelum perbaikan test_update_subquery_dibaca_bukan_diubah :
tests/test_tambahan.py::test_update_subquery_dibaca_bukan_diubah FAILED  

Sesudah : 
tests/test_tambahan.py::test_update_subquery_dibaca_bukan_diubah PASSED  

**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?
ya, bisa diverifikasi di file LOG_AI.md

---