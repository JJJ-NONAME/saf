default testing solution. it should include:
- method_assets for testing encryption.
- build_assets for testing local dependencies.
    - ansys_solutions_custom_package_for_installer_test: dependency that has a subdependency that is defined by a wheel URL. this new subdependency must not be in the poetry.lock already.
    - custom-package-for-test-2: minimal local wheel package with different wheel files depending on OS.
- tqdm and pooch dependencies for testing custom Desktop and UI dependencies.
- doc/source for testing documentation build.
- without_portal_poetry_lock for testing support for solutions without portal
- .env file for testing support for env files