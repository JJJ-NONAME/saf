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

import pytest

from ansys.saf.glow._hps_parametric_studies.serialization import (
    decode_data_from_hps,
    decode_string_from_hps,
    encode_data_for_hps,
    encode_string_for_hps,
)


def test_hps_data_serialization():
    data = list(range(64))
    encoded = encode_data_for_hps(data)
    decoded = decode_data_from_hps(encoded)
    assert decoded == data


@pytest.mark.parametrize("s", ["AZ123456", "AZ XY", "A......Z", "A-Z", "A_Z", "A/Z", 'A"Z', "A'Z", "©2025", "AäZ"])
def test_hps_string_serialization(s: str):
    encoded = encode_string_for_hps(s)
    for c in [".", "-", "/", '"', "'", "©", "ä"]:
        assert c not in encoded
    decoded = decode_string_from_hps(encoded)
    assert decoded == s


def test_helpful_exception_raised_when_encoding_object_not_supported_by_pickle():
    def f():
        return 1

    with pytest.raises(
        RuntimeError,
        match=r"The SAF HPS API does not support the serialization of \<class \'function\'\> objects\.  "
        r"In this case\: \<function "
        r"test_helpful_exception_raised_when_encoding_object_not_supported_by_pickle\.\<locals\>\.f at .*",
    ):
        encode_data_for_hps(f)
