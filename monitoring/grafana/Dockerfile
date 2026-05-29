FROM grafana/grafana:10.2.0

LABEL maintainer="Smart Factory IoT Team"
LABEL description="Grafana — pre-provisioned dashboards for Smart Factory monitoring"

# Copy provisioning configurations
COPY provisioning/datasources/ /etc/grafana/provisioning/datasources/
COPY provisioning/dashboards/ /etc/grafana/provisioning/dashboards/

# Default environment
ENV GF_SECURITY_ADMIN_USER=admin \
    GF_SECURITY_ADMIN_PASSWORD=admin \
    GF_USERS_ALLOW_SIGN_UP=false \
    GF_SERVER_ROOT_URL=http://localhost:3001 \
    GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource

EXPOSE 3000

HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=3 \
    CMD wget -qO- http://localhost:3000/api/health || exit 1
