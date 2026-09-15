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

import logging

from ansys.saf.glow._config.settings import Settings
from ansys.saf.glow._ui.server import create_app

logger = logging.getLogger(__name__)

# Exposing server as a convenient way to start the solution UI using a production server:
# 'waitress-serve --host 127.0.0.1 --port 5433 ansys.saf.glow.ui:app'
settings = Settings.model_validate({})
ui_app = create_app(settings)
app = ui_app.server
logger.info(f"Running GLOW UI server on http://{settings.glow_ui_host}:{settings.glow_ui_port}")
