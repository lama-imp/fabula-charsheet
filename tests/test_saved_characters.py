from fabula_charsheet.data import saved_characters


def test_saved_characters_init(tmp_path):
    saved_characters.SAVED_CHARS = None
    (tmp_path / 'char.yaml').write_text('{"name": "Test"}')
    saved_characters.init(tmp_path)
    assert saved_characters.SAVED_CHARS is not None
    assert saved_characters.SAVED_CHARS.char_list
