# Solution Examples

<p align="left">
    <br />
    <img src="https://img.shields.io/badge/Python-3.11–3.14-blue.svg" alt="Supported Python versions" />
</p>

# Prerequisites

Visit the SAF documentation and ensure the [prerequisites](https://upgraded-carnival-wn6lkym.pages.github.io/version/stable/getting_started/prerequisites/index.html) are fulfilled.

## Beam Bending Requirements (Optional)

The beam bending example can optionally run a MAPDL simulation and generate a report using Ansys Dynamic Reporting (ADR). To enable these capabilities, install the following components.

### Ansys Mechanical APDL 2025 R2

To install MAPDL:

1. Download the Ansys 2025 R2 automated installer from: https://download.ansys.com/currentReleases

2. Run the installer and select Mechanical APDL as one of the installed products.

3. Ensure the MAPDL executable is accessible to the application via the `AWP_ROOT252` environment variable, which typically points to: `C:\Program Files\ANSYS Inc\v252`

### Ansys Dynamic Reporting 2026 R1

1. Download the Ansys 2026 R1 automated installer from: https://download.ansys.com/currentReleases

2. Run the installer and select Dynamic Reporting under Platform and install the package.

3. Set the ``ADR_INSTALLATION_DIRECTORY`` environment variable in your ``.env`` file to the absolute path of the Dynamic Reporting ``CEI`` directory installed.

Example:
```bash
ADR_INSTALLATION_DIRECTORY=C:\Program Files\ANSYS Inc\v261\CEI
```

# Install the example solution

It is assumed that SAF CLI is installed.

1. Move to the examples folder

```bash
cd examples
```

2. Install

```bash
saf install -f
```

# Run the example solution

From within the examples folder:

```bash
saf run
```

# License

Copyright (c) ANSYS Inc. All rights reserved.

