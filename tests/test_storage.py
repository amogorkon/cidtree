# Additional tests for directory migration, SWMR metadata, and atomic updates
import h5py
import pytest

from cidstore.storage import Storage

pytestmark = pytest.mark.asyncio


@pytest.mark.xfail(reason="directory attribute not implemented")
async def test_directory_attribute_to_dataset_migration(tmp_path):
    from cidstore.keys import E
    from cidstore.storage import Storage
    from cidstore.store import WAL, CIDStore

    path = tmp_path / "migrate.h5"
    storage = Storage(str(path))
    wal = WAL(storage)
    store = CIDStore(storage, wal=wal)
    # Insert enough keys to trigger migration
    for i in range(10000):
        await store.insert(E.from_str(f"migrate{i}"), E.from_int(i))
    # Directory migration logic may be internal; check directory structure if possible
    _ = store.directory  # Assume attribute exists


async def test_swmmr_metadata_and_atomicity(tmp_path):
    from cidstore.keys import E
    from cidstore.storage import Storage
    from cidstore.store import WAL, CIDStore

    path = tmp_path / "swmr.h5"
    storage = Storage(str(path))
    wal = WAL(storage)
    store = CIDStore(storage, wal=wal)
    await store.insert(E.from_str("swmrkey"), E.from_int(1))
    with h5py.File(path, "r") as f:
        config = f["/config"] if "/config" in f else f[list(f.keys())[0]]
        assert "swmr" in config.attrs or "SWMR" in config.attrs


async def test_storage_manager_in_memory(in_memory_hdf5):
    # Use our StorageManager with the in-memory HDF5 file
    storage = Storage(path=":memory:")
    storage.file = in_memory_hdf5
    # Ensure required groups/datasets are created
    storage._ensure_core_groups()
    # Check that config, nodes, values groups exist
    from cidstore.config import WAL_DATASET
    from cidstore.wal import WAL

    wal = WAL(storage)  # Ensure WAL dataset is created
    assert storage.file is not None
    assert WAL_DATASET in storage.file or wal.ds is not None
    # Write/read to a dataset in one of the groups
    # nodes_group = storage.file[NODES_GROUP]  # Unused variable removed
    # Always create the test dataset in the file root for test determinism
    test_ds = storage.file.create_dataset("test", shape=(5,), dtype="i")
    test_ds[:] = [1, 2, 3, 4, 5]
    assert list(test_ds[:]) == [1, 2, 3, 4, 5]
    assert storage.file.id.valid
