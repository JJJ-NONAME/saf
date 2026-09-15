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
from fastapi import FastAPI
import uvicorn

app = FastAPI()


@app.get("/")
def root():
    return {"Hello": "World"}


@app.get("/api/v1/health")
def health():
    return "OK"


def run_portal(host: str, port: int, ui_url: str, api_url: str, api_version: str):
    uvicorn.run(  # pyright: ignore
        app=app,
        host=host,
        port=port,
        log_level="error",
    )
