import pathlib
import fileez as fz

def test_write_and_read(tmp_path: pathlib.Path):
    file = tmp_path / "test.txt"
    fz.write(file, "Hello")
    assert fz.read(file) == "Hello"

def test_write_append_and_read(tmp_path: pathlib.Path):
    file = tmp_path / "append.txt"
    fz.write(file, "Hello")
    fz.write(file, " World", append=True)
    assert fz.read(file) == "Hello World"

def test_read_lines(tmp_path: pathlib.Path):
    file = tmp_path / "lines.txt"
    content = "Line1\nLine2\nLine3\n"
    fz.write(file, content)
    lines = fz.read_lines(file)
    assert lines == ["Line1\n", "Line2\n", "Line3\n"]

def test_make_and_list_dir(tmp_path: pathlib.Path):
    new_dir = tmp_path / "subdir"
    fz.make_dir(new_dir)
    assert new_dir.name in fz.list_dir(tmp_path)

def test_file_exists_and_delete(tmp_path: pathlib.Path):
    file = tmp_path / "file.txt"
    fz.write(file, "data")
    assert fz.exists(file)
    fz.delete(file)
    assert not fz.exists(file)

def test_delete_dir(tmp_path: pathlib.Path):
    dir_path = tmp_path / "todelete"
    fz.make_dir(dir_path)
    assert dir_path.exists()
    fz.delete_dir(dir_path)
    assert not dir_path.exists()

def test_copy_and_move_file(tmp_path: pathlib.Path):
    src = tmp_path / "src.txt"
    dst = tmp_path / "dst.txt"
    moved = tmp_path / "moved.txt"
    fz.write(src, "content")
    fz.copy_file(src, dst)
    assert fz.read(dst) == "content"
    fz.move_file(dst, moved)
    assert moved.exists()
    assert not dst.exists()

def test_json_read_write(tmp_path: pathlib.Path):
    data = {"name": "fileez", "version": 1}
    file = tmp_path / "data.json"
    fz.write_json(file, data)
    loaded = fz.read_json(file)
    assert loaded == data

def test_csv_read_write(tmp_path: pathlib.Path):
    rows = [["name", "age"], ["Alice", "30"], ["Bob", "25"]]
    file = tmp_path / "data.csv"
    fz.write_csv(file, rows)
    loaded = fz.read_csv(file)
    assert loaded == rows