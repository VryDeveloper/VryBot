import pytest

from vrybot.memory import InMemoryBackend, SQLiteBackend


@pytest.fixture(params=["memory", "sqlite"])
async def backend(request, tmp_path):
    b = InMemoryBackend(3) if request.param == "memory" else SQLiteBackend(3, tmp_path / "m.db")
    yield b
    await b.close()


async def test_keeps_only_last_n(backend):
    for i in range(5):
        await backend.add(1, "user", f"msg {i}")
    assert [m["content"] for m in await backend.history(1)] == ["msg 2", "msg 3", "msg 4"]


async def test_channels_are_isolated_and_clear_works(backend):
    await backend.add(1, "user", "a")
    await backend.add(2, "assistant", "b")
    await backend.clear(1)
    assert await backend.history(1) == []
    assert await backend.history(2) == [{"role": "assistant", "content": "b"}]
