// Copyright (C) 2026 ANSYS, Inc. and/or its affiliates.
// SPDX-License-Identifier: Apache-2.0
//
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/**
 * GLOW Authentication Refresh Handler
 *
 * Automatically detects 401 Unauthorized responses from the GLOW API and triggers
 * re-authentication by reloading the page. After successful authentication, the user
 * is redirected back to their original page.
 *
 * This handler is automatically loaded by Dash and requires no configuration.
 * It intercepts all fetch requests and monitors for 401 responses that indicate
 * an expired OAuth session.
 */

(function() {
    'use strict';

    // Store the original fetch function before overriding it
    const originalFetch = window.fetch;

    // Track if we're currently handling a 401 to prevent redirect loops
    let handling401 = false;

    /**
     * Override the global fetch function to intercept 401 Unauthorized responses.
     * This allows us to detect session expiration without modifying solution code.
     */
    window.fetch = async function(...args) {
        try {
            const response = await originalFetch.apply(this, args);

            // Check for 401 Unauthorized response indicating session expiration
            if (response.status === 401 && !handling401) {
                handling401 = true;

                console.warn(
                    '[GLOW] Session expired (401 Unauthorized). ' +
                    'Triggering re-authentication flow...'
                );
                // Reload the page after a short delay to trigger authentication
                // The authentication middleware will intercept and redirect to login
                setTimeout(() => {
                    window.location.reload();
                }, 100);
            }

            // Reset the handling flag when we get a successful response
            if (response.ok && handling401) {
                handling401 = false;
            }

            return response;
        } catch (error) {
            console.error('[GLOW] Fetch request failed:', error);
            throw error;
        }
    };
    console.info('[GLOW] Authentication refresh handler initialized successfully');
})();
