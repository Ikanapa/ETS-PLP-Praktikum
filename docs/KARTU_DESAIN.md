# Kartu Desain

Tuliskan lima keputusan desain penting dalam pekerjaan kalian. Untuk tiap keputusan, sebutkan
alternatif yang ditolak dan alasannya. Contoh topik (boleh memilih yang lain):

- bagaimana parser membedakan `*` sebagai "semua kolom" dan sebagai perkalian;
- di mana dan bagaimana presedensi `AND`/`OR` dinyatakan;
- mengapa error recovery berhenti di `;`, bukan di keyword `SELECT` berikutnya;
- urutan pencarian scope dan akibatnya pada shadowing serta correlated subquery;
- mengapa kolom tanpa qualifier hanya dilihat di scope terdalam, dan apa kelemahannya;
- bagaimana implementasi `INSERT ... SELECT` atau komentar blok kalian.

| No | Keputusan | Alternatif yang ditolak | Alasan |
| --- | --- | --- | --- |
| 1 | Presedensi `AND`/`OR` dinyatakan lewat tingkat grammar: `_or()` memanggil `_and()`, `_and()` memanggil `_not()`, dan masing-masing hanya punya satu operator di loopnya. | Tabel presedensi dengan Pratt parser (precedence climbing). | Seluruh parser memakai gaya satu method per tingkat (`_additive`, `_multiplicative`) dan SPESIFIKASI 3.1 menuliskan grammar per tingkat. Pemecahan method konsisten dengan gaya itu dan mudah dicocokkan baris demi baris dengan grammar. |
| 2 | Komentar blok `/* ... */` yang tidak ditutup melaporkan `LexError` di posisi awal komentar (baris dan kolom `/`). Karakter `*` pembuka dikonsumsi sebelum mencari penutup. | Melaporkan posisi akhir file (EOF). Alternatif lain: tidak mengonsumsi `*` pembuka lebih dulu. | Posisi awal menunjuk ke penyebab yang bisa diperbaiki penulis dan konsisten dengan `_string()` yang juga melaporkan posisi awal. EOF hanya menunjukkan akibatnya. Mengonsumsi `*` lebih dulu membuat `/*/` tidak dianggap tertutup. |
| 3 | Kolom tanpa qualifier hanya dicari di scope terdalam. Satu tabel: `resolved` diisi. Lebih dari satu tabel atau tidak ada tabel: warning dan `resolved` tetap `None`. | Menelusuri seluruh rantai scope sampai ada tabel yang cocok. | Tanpa skema database, resolver tidak tahu kolom milik tabel mana. Menelusuri rantai hanya menghasilkan tebakan yang bisa salah diam-diam. Kelemahannya: kolom dari query luar yang dipakai tanpa qualifier di subquery (correlated subquery) tidak ter-resolve. Penulis harus memakai qualifier, dan itu sejalan dengan warning yang muncul. |
| 4 | Scope dikelola sebagai stack: pencarian qualifier berjalan dari scope terdalam naik lewat `parent` dan berhenti di kecocokan pertama. Setiap `_push()` dipasangkan dengan `_pop()` di akhir method statement (`_select`, `_update`, `_delete`). | (a) Mengumpulkan rantai scope lalu membalik urutannya (kode lama). (b) Mengatur `self.scope = None` di tiap awal statement sebagai pengaman. | (a) membuat nama luar menutupi nama dalam, jadi shadowing tidak pernah terjadi. (b) menyembunyikan lupa `_pop()` di tempat lain, padahal scope subquery yang bocor di tengah statement tetap salah. Pasangan push/pop yang eksplisit membuat bug seperti pada `_delete()` mudah ditemukan. Wrapper `try/finally` atau context manager dicatat sebagai perbaikan lanjutan. |
| 5 | Di analyzer, operasi statement (`C`/`U`/`D`) hanya diberikan ke tabel targetnya. Tabel yang muncul di subquery, `WHERE`, atau nilai `SET` selalu `R`. | Meneruskan operasi statement induk ke semua tabel di dalamnya (perilaku lama pada `UPDATE`). Alternatif lain: menghapus parameter `op` dan memakai `"R"` di semua tempat. | Aturan SPESIFIKASI bagian 5 menyatakan tabel yang dibaca lewat subquery selalu `R`. Mewariskan `U` ke tabel subquery menghasilkan operasi tulis yang tidak pernah terjadi. Parameter `op` dipertahankan karena `_collect_select()` masih membutuhkannya untuk `SELECT`. |
