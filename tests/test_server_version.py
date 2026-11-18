"""計測したサーバの版を、起動ログから読んで照らす（EP001 設計審査3回目 K1）。"""
from lab.analyze import NG, NONE, OK, check_server_version
from lab.runner import read_server_version

LOG = """[10:00:00] [Server thread/INFO]: Starting minecraft server version 1.21.11
[10:00:05] [Server thread/INFO]: Done (4.2s)! For help, type "help"
[11:00:00] [Server thread/INFO]: Starting minecraft server version 26.3
[11:00:04] [Server thread/INFO]: Done (3.9s)! For help, type "help"
"""


def test_reads_last_start_line(tmp_path):
    p = tmp_path / "latest.log"
    p.write_text(LOG, encoding="utf-8")
    sv = read_server_version(p)
    assert sv["server_version"] == "26.3"
    assert "Starting minecraft server version 26.3" in sv["server_version_line"]


def test_missing_log_or_line_gives_no_version(tmp_path):
    assert read_server_version(tmp_path / "nothing.log")["server_version"] is None
    p = tmp_path / "latest.log"
    p.write_text("[10:00:00] [Server thread/INFO]: Done\n", encoding="utf-8")
    sv = read_server_version(p)
    assert sv["server_version"] is None and "版の行がない" in sv["server_version_source"]


def ctx(meta, mc_version="26.3"):
    return {"exp": {"mc_version": mc_version}, "meta": meta}


def test_check_compares_with_experiment():
    assert check_server_version(ctx({"server_version": "26.3", "server_version_line": "x"}), {})["status"] == OK
    assert check_server_version(ctx({"server_version": "1.21.11"}), {})["status"] == NG   # 違う jar で測った
    assert check_server_version(ctx({"server_version_source": "ない"}), {})["status"] == NG  # 証拠がない
    assert check_server_version(ctx({}), {})["status"] == NG                                 # 古い meta.json
    assert check_server_version(ctx({"server_version": "fake"}), {})["status"] == NONE       # 模擬サーバ
