# Copyright (C) 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: Apache-2.0
#
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pathlib import Path

from ansys.bdm.api import EntityHandle, IAsyncStorageScope, IStorageScope, RecursiveDictionaryOfEntityHandles


def _compare_entity_dicts(
    dict1: RecursiveDictionaryOfEntityHandles,
    dict2: RecursiveDictionaryOfEntityHandles,
) -> bool:
    assert isinstance(dict1, dict)
    assert isinstance(dict2, dict)
    if dict1.keys() != dict2.keys():
        return False
    for key in dict1:
        val1 = dict1[key]
        val2 = dict2[key]
        if isinstance(val1, dict) and isinstance(val2, dict):
            if not _compare_entity_dicts(val1, val2):
                return False
        elif isinstance(val1, EntityHandle) and isinstance(val2, EntityHandle):
            assert val1.original_name == val2.original_name
        else:
            return False
    return True


def _verify_output_dir_against_source_dir(
    output_dir: Path,
    source_dir: Path,
):
    for path in output_dir.rglob("*"):
        matching_path_in_source = source_dir / path.relative_to(output_dir)
        assert matching_path_in_source.exists()
        if path.is_file():
            assert path.read_text() == matching_path_in_source.read_text()
        else:
            assert matching_path_in_source.is_dir()


def test_round_trip_store_to_dictionary_and_copy_from_dictionary(
    scope: IStorageScope,
    test_root: Path,
    tmp_path: Path,
):
    """Test round-trip: store directory to dictionary, then copy back to filesystem."""
    entity_dict = scope.store_to_dictionary(test_root)

    output_dir = tmp_path / "output"
    assert not output_dir.exists()
    scope.get_copy_from_dictionary(output_dir, entity_dict)

    _verify_output_dir_against_source_dir(output_dir, test_root)


async def test_round_trip_store_to_dictionary_and_copy_from_dictionary_async(
    async_scope: IAsyncStorageScope,
    async_test_root: Path,
    tmp_path: Path,
):
    """Test round-trip: store directory to dictionary, then copy back to filesystem."""
    entity_dict = await async_scope.store_to_dictionary(async_test_root)

    output_dir = tmp_path / "output"
    assert not output_dir.exists()
    await async_scope.get_copy_from_dictionary(output_dir, entity_dict)

    _verify_output_dir_against_source_dir(output_dir, async_test_root)


def test_round_trip_copy_from_dictionary_and_store_to_dictionary(
    scope: IStorageScope,
    source_dict: RecursiveDictionaryOfEntityHandles,
):
    """Test reverse round-trip: from dictionary to filesystem, and then create back a dictionary from it."""
    output_dir = scope.get_storage_root() / "output"
    assert not output_dir.exists()
    scope.get_copy_from_dictionary(output_dir, source_dict)

    dest_dict = scope.store_to_dictionary(output_dir)

    assert _compare_entity_dicts(source_dict, dest_dict)


async def test_round_trip_copy_from_dictionary_and_store_to_dictionary_async(
    async_scope: IAsyncStorageScope,
    async_source_dict: RecursiveDictionaryOfEntityHandles,
):
    """Test reverse round-trip: from dictionary to filesystem, and then create back a dictionary from it."""
    output_dir = await async_scope.get_storage_root() / "output"
    assert not output_dir.exists()
    await async_scope.get_copy_from_dictionary(output_dir, async_source_dict)

    dest_dict = await async_scope.store_to_dictionary(output_dir)

    assert _compare_entity_dicts(async_source_dict, dest_dict)


def _verify_output_dir_against_multiple_source_dir(
    output_dir: Path,
    source_dir: Path,
):
    for path in output_dir.rglob("*"):
        rel_path = path.relative_to(output_dir)
        if rel_path.parts[0] == "updated_level1":
            matching_path_in_root = source_dir / "level1" / Path(*rel_path.parts[1:])
        else:
            matching_path_in_root = source_dir / rel_path
        assert matching_path_in_root.exists()
        if path.is_file():
            assert path.read_text() == matching_path_in_root.read_text()
        else:
            assert matching_path_in_root.is_dir()


def test_round_trip_multiple_stores_and_single_copy(
    scope: IStorageScope,
    test_root: Path,
    tmp_path: Path,
):
    """Test that builds a dictionary from multiple calls and then a single copy."""
    my_entities = scope.store_to_dictionary(test_root)
    my_entities["updated_level1"] = scope.store_to_dictionary(test_root / "level1")

    output_dir = tmp_path / "output"
    output_dir.mkdir()
    scope.get_copy_from_dictionary(output_dir, my_entities)

    _verify_output_dir_against_multiple_source_dir(output_dir, test_root)


async def test_round_trip_multiple_stores_and_single_copy_async(
    async_scope: IAsyncStorageScope,
    async_test_root: Path,
    tmp_path: Path,
):
    """Test that builds a dictionary from multiple calls and then a single copy."""
    my_entities = await async_scope.store_to_dictionary(async_test_root)
    my_entities["updated_level1"] = await async_scope.store_to_dictionary(async_test_root / "level1")

    output_dir = tmp_path / "output"
    output_dir.mkdir()
    await async_scope.get_copy_from_dictionary(output_dir, my_entities)

    _verify_output_dir_against_multiple_source_dir(output_dir, async_test_root)
