import os
import src.game_utils.toolkit as toolkit

TEST_PATH = os.path.dirname(os.path.abspath(__file__))
TEST_GAME_PATH = os.path.join(TEST_PATH, "test_game")


def test_batocera_package_path():
    assert os.path.exists(TEST_GAME_PATH)
    assert os.path.exists(os.path.join(TEST_GAME_PATH, "testgame.py"))

    toolkit.package_for_batocera("testgame", TEST_GAME_PATH)

    zip_path = os.path.join(TEST_GAME_PATH, "testgame.zip")
    assert os.path.exists(zip_path)

    size = os.path.getsize(zip_path)
    print(f"zip size: {size}")
    assert size > 5000

    _clear_zips()


def test_default_package():
    toolkit.default_package("testgame", TEST_GAME_PATH)

    zip_path = os.path.join(TEST_GAME_PATH, "testgame.zip")
    assert os.path.exists(zip_path)

    size = os.path.getsize(zip_path)
    print(f"zip size: {size}")
    assert size > 100

    _clear_zips()


def _clear_zips():
    os.remove(os.path.join(TEST_GAME_PATH, "testgame.zip"))
