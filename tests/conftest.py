import os
import shutil
import sys
import tempfile

from django.conf import settings
import pytest


BASE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"
)
sys.path.append(BASE_DIR)

PROJECT_DIR_NAME = "wallet"

MANAGE_PATH = BASE_DIR
if "manage.py" not in os.listdir(MANAGE_PATH):
    assert False, (
        f"В директории `{MANAGE_PATH}` не найден файл `manage.py`. "
        "Убедитесь, что у вас верная структура проекта."
    )

pytest_plugins = [
    "tests.fixtures.fixture_user",
    "tests.fixtures.fixture_data",
]


@pytest.fixture
def fixture_name(request):
    return request.getfixturevalue(request.param)


@pytest.fixture(autouse=True)
def temp_media_root():
    temp_dir = tempfile.mkdtemp()
    settings.MEDIA_ROOT = temp_dir
    yield
    shutil.rmtree(temp_dir)
