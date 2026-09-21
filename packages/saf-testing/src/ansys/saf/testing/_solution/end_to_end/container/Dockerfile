# Dockerfile that focuses on fast iterations for GLOW E2E testing.
FROM python:3.11-slim AS e2e_solution

RUN apt-get update

# MAPDL brings pyvista as a dependency. For running pyvista in headless mode
# https://docs.pyvista.org/version/stable/getting-started/installation.html#running-on-remote-servers
RUN apt-get install --no-install-recommends -y libglx-mesa0 libgl1 xvfb
RUN export DISPLAY=:99.0
RUN export PYVISTA_OFF_SCREEN=true
RUN Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &

# For AEDT
RUN apt-get install --no-install-recommends -y curl
RUN curl http://security.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1-1ubuntu2.1~18.04.23_amd64.deb -o libssl1.1.deb
RUN dpkg -i libssl1.1.deb

# Directory required by pymechanical
RUN mkdir -p /.local/share
RUN chmod -R 777 /.local

# Directory required by pymapdl
RUN mkdir -p /.config
RUN chmod -R 777 /.config

# Directory required by pyfluent
RUN mkdir -p /Downloads

# Directory required by Visor
RUN mkdir -p /logs
RUN chmod -R 777 /logs

# Directory required by pyHPS
RUN mkdir -p /.ansys/hps
RUN chmod -R 777 /.ansys

# For the healtcheck
RUN apt-get install --no-install-recommends -y curl

# Directories for mounting solution, local library and rest of dependencies
RUN mkdir -p /site-packages/
RUN mkdir -p /app/src/
RUN mkdir -p /library/src/

# Provide access to required libraries, included GLOW.
ENV PYTHONPATH="/site-packages/:/app/src/:/library/src/:${PYTHONPATH}"

# Launch API server directly with uvicorn
# we are assuming that the database and API server can support multiple workers
# this is not the case if the sqlite is being used here we are assuming that
# postgres or similar are being used
ENTRYPOINT ["python", "-m", "uvicorn", "ansys.saf.glow.api:app", "--workers", "${GLOW_API_NUMBER_OF_WORKERS}"]
