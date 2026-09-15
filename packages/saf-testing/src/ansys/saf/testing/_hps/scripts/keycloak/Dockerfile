# Start from the official Keycloak image (use a specific version)
FROM quay.io/keycloak/keycloak:26.3.5

# Copy your custom provider(s) JAR(s) into the providers directory
COPY job-action-token-1.2.0.jar /opt/keycloak/providers/

# Run the Keycloak build step to register your provider
RUN /opt/keycloak/bin/kc.sh build

# Expose the default Keycloak port
EXPOSE 8080

# Start Keycloak (use `start` for production, `start-dev` for dev)
ENTRYPOINT ["/opt/keycloak/bin/kc.sh", "start"]