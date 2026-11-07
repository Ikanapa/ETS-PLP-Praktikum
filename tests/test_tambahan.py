"""Test tambahan buatan kelompok.

Isi dengan:
1. Satu test regresi untuk setiap bug yang kalian perbaiki (gagal sebelum perbaikan,
   lulus sesudahnya). Beri nama yang menjelaskan bug-nya.
2. Lima test kasus tepi, masing-masing dengan komentar singkat mengapa kasus itu berisiko.
"""

import pytest
from crud.lexer import tokenize, LexError, TokenType as T
from crud.parser import parse_sql
from crud import ast_nodes as ast
from crud.parser import parse_sql
from crud.resolver import Resolver

# test lexer
# def vals(s):
#     return [(t.type, t.value) for t in tokenize(s)[:-1]]

# def test_keyword_campuran_huruf():
#     assert vals("Select selection")[0] == (T.KEYWORD, "SELECT")
#     assert vals("Select selection")[1] == (T.IDENT, "selection")

# def test_operator_terpanjang():
#     assert vals("a <> b")[1] == (T.OP, "<>")
#     assert vals("a <= b")[1] == (T.OP, "<=")
#     assert len(vals("a <> b")) == 3

# def test_string_kutip_kembar():
#     assert vals("'O''Brien'") == [(T.STRING, "O'Brien")]
#     assert vals("''") == [(T.STRING, "")]
#     assert vals("''''") == [(T.STRING, "'")]

# def test_komentar_blok_kasus_tepi():
#     assert vals("/**/ a") == [(T.IDENT, "a")]
#     assert vals("/* a * b */ a") == [(T.IDENT, "a")]
#     with pytest.raises(LexError):
#         tokenize("/*/")
#     with pytest.raises(LexError):
#         tokenize("/* tak ditutup")

# def test_posisi_setelah_komentar_lintas_baris():
#     t = tokenize("/* a\n b */ x")[0]
#     assert (t.line, t.col) == (2, 7)

# test parser
# def test_or_lebih_rendah_dari_and():
#     s = parse_sql("SELECT a FROM t WHERE a=1 OR b=2 AND c=3")
#     assert s.errors == []
#     w = s.statements[0].where
#     assert w.op == "OR" and w.right.op == "AND"

# def test_and_lalu_or():
#     s = parse_sql("SELECT a FROM t WHERE a=1 AND b=2 OR c=3")
#     w = s.statements[0].where
#     assert w.op == "OR" and w.left.op == "AND"

# def test_left_outer_join():
#     s = parse_sql("SELECT a FROM t LEFT OUTER JOIN u ON t.x = u.x")
#     assert s.errors == []

# def test_insert_select():
#     s = parse_sql("INSERT INTO arsip (id) SELECT id FROM pesanan")
#     assert s.errors == []

# def test_recovery_satu_error_per_statement():
#     s = parse_sql("SELECT FROM t;\nSELECT a FROM u;")
#     assert len(s.errors) == 1 and len(s.statements) == 1

# def test_recovery_error_tepat_di_titik_koma():
#     s = parse_sql("SELECT a FROM ; SELECT b FROM u;")
#     assert len(s.errors) == 1 and len(s.statements) == 1

# test resolver
# def _resolve(sql):
#     script = parse_sql(sql)
#     diagnostics = Resolver().resolve_script(script)
#     return script, diagnostics


# def _column_refs(node):
#     """Kumpulkan semua ColumnRef di dalam node AST secara rekursif."""
#     found = []
#     if isinstance(node, ast.ColumnRef):
#         found.append(node)
#     elif isinstance(node, (list, tuple)):
#         for item in node:
#             found.extend(_column_refs(item))
#     elif hasattr(node, "__dict__"):
#         for value in vars(node).values():
#             found.extend(_column_refs(value))
#     return found


# def test_qualifier_dicari_dari_terdalam():
#     sql = ("SELECT 1 FROM pelanggan x WHERE EXISTS "
#            "(SELECT 1 FROM pesanan x WHERE x.total > 0);")
#     script, _ = _resolve(sql)
#     refs = [c for c in _column_refs(script) if c.qualifier == "x"]
#     assert refs and all(c.resolved == "pesanan" for c in refs)


# def test_scope_tidak_bocor_setelah_delete():
#     sql = "DELETE FROM sesi s WHERE s.id = 1; SELECT s.id FROM pesanan p;"
#     _, diagnostics = _resolve(sql)
#     assert any(d.level == "error" and "'s'" in d.message for d in diagnostics)


# def test_kolom_ambigu_dua_tabel():
#     script, diagnostics = _resolve("SELECT id FROM a, b;")
#     assert any(d.level == "warning" for d in diagnostics)
#     assert all(c.resolved is None for c in _column_refs(script))

# test analyzer
from crud.analyzer import analyze_statement

def test_update_subquery_dibaca_bukan_diubah():
    script = parse_sql(
        "UPDATE pesanan SET total = (SELECT MAX(n) FROM diskon) "
        "WHERE id IN (SELECT id FROM batal);")
    usage = analyze_statement(script.statements[0])
    assert usage["pesanan"] == {"U"}
    assert usage["diskon"] == {"R"}
    assert usage["batal"] == {"R"}