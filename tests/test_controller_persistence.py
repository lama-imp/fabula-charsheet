import types

import pytest
import yaml

from data.models import Character


@pytest.fixture(autouse=True)
def isolated_save_directories(monkeypatch, tmp_path):
    chars_dir = tmp_path / "characters"
    img_dir = tmp_path / "characters" / "character_images"
    states_dir = tmp_path / "characters" / "states"
    chars_dir.mkdir(parents=True)
    img_dir.mkdir(parents=True)
    states_dir.mkdir(parents=True)
    monkeypatch.setattr("pages.controller.SAVED_CHARS_DIRECTORY", chars_dir)
    monkeypatch.setattr("pages.controller.SAVED_CHARS_IMG_DIRECTORY", img_dir)
    monkeypatch.setattr("pages.controller.SAVED_STATES_DIRECTORY", states_dir)
    return types.SimpleNamespace(chars=chars_dir, images=img_dir, states=states_dir)


def test_dump_character_writes_expected_file(controller, isolated_save_directories):
    controller.character.name = "Alice"
    controller.dump_character()
    expected = isolated_save_directories.chars / f"Alice.{controller.character.id}.character.yaml"
    assert expected.exists()


def test_dump_character_round_trips_via_yaml(controller, isolated_save_directories):
    controller.character.name = "Bob"
    controller.character.level = 12
    controller.dump_character()
    saved_path = isolated_save_directories.chars / f"Bob.{controller.character.id}.character.yaml"
    with saved_path.open(encoding="utf-8") as f:
        raw = yaml.load(f, Loader=yaml.UnsafeLoader)
    reloaded = Character(**raw)
    assert reloaded.name == "Bob"
    assert reloaded.level == 12
    assert reloaded.id == controller.character.id


def test_dump_character_removes_stale_files_for_same_id(controller, isolated_save_directories):
    controller.character.name = "Old Name"
    controller.dump_character()
    controller.character.name = "New Name"
    controller.dump_character()
    matches = list(isolated_save_directories.chars.glob(f"*.{controller.character.id}.character.yaml"))
    assert len(matches) == 1
    assert matches[0].name == f"New Name.{controller.character.id}.character.yaml"


def test_dump_state_writes_expected_file(controller, isolated_save_directories):
    controller.state.minus_hp = 7
    controller.dump_state()
    expected = isolated_save_directories.states / f"{controller.character.id}.yaml"
    assert expected.exists()


def test_load_state_round_trips(controller, isolated_save_directories):
    controller.state.minus_hp = 15
    controller.state.minus_mp = 3
    controller.dump_state()
    controller.state.minus_hp = 0
    controller.state.minus_mp = 0
    controller.load_state()
    assert controller.state.minus_hp == 15
    assert controller.state.minus_mp == 3


def test_load_state_missing_file_resets_state_and_raises(controller):
    controller.state.minus_hp = 99
    with pytest.raises(Exception):
        controller.load_state()
    assert controller.state.minus_hp == 0  # reset to a fresh CharState()


def test_dump_avatar_writes_image_bytes(controller, isolated_save_directories):
    controller.character.name = "Carol"
    image = types.SimpleNamespace(name="avatar.png", getbuffer=lambda: b"PNGDATA")
    controller.dump_avatar(image)
    expected = isolated_save_directories.images / f"Carol.{controller.character.id}.png"
    assert expected.read_bytes() == b"PNGDATA"


def test_dump_avatar_none_is_a_no_op(controller, isolated_save_directories):
    controller.dump_avatar(None)
    assert list(isolated_save_directories.images.iterdir()) == []


def test_dump_avatar_removes_stale_images_for_same_id(controller, isolated_save_directories):
    image_a = types.SimpleNamespace(name="a.png", getbuffer=lambda: b"A")
    image_b = types.SimpleNamespace(name="b.jpg", getbuffer=lambda: b"B")
    controller.character.name = "Dave"
    controller.dump_avatar(image_a)
    controller.dump_avatar(image_b)
    matches = list(isolated_save_directories.images.glob(f"*{controller.character.id}.*"))
    assert len(matches) == 1
    assert matches[0].suffix == ".jpg"
