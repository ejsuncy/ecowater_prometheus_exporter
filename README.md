> **Note**
> See the latest GitHub release and select the corresponding branch or tag above for applicable README instructions

# Ecowater Prometheus Exporter
![Current Version](https://img.shields.io/badge/Version-0.2.0a-brightgreen)

This is a prometheus exporter for the Ecowater API. OEMs such as Rheem use this API to provide Wi-Fi connectivity 
to their smart water softeners.

See [the sample metrics](data/metrics.txt) for a list of metrics you can query in prometheus.

Internally it uses the [py_ecowater python library](https://github.com/ejsuncy/py_ecowater).

The image can be found on
[GitHub Packages](https://github.com/ejsuncy/ecowater_prometheus_exporter/pkgs/container/ecowater_prometheus_exporter). 

## Usage
```shell
docker pull ghcr.io/ejsuncy/ecowater_prometheus_exporter:0.2.0a
```

### Environment Variables
The following environment variables are supported:

| Variable             | Description                                                                                                                                                                               | Options                             | Default                               |
|----------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------|---------------------------------------|
| `EXPORTER_LOG_LEVEL` | Controls verbosity of logs                                                                                                                                                                | `DEBUG`, `INFO`, `WARNING`, `ERROR` | `INFO`                                |
| `ACCOUNT_USERNAME`   | The username (email address) used to login.                                                                                                                                               |                                     |                                       |
| `ACCOUNT_PASSWORD`   | The password used to login to the account.                                                                                                                                                |                                     |                                       |
| `TZ`                 | The timezone to use for the container. Use the string in `TZ database name` column of the [List of TZ Database Time Zones](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones). |                                     | None (container defaults to UTC time) |
| `EXPORTER_PORT`      | The port to listen on                                                                                                                                                                     |                                     | `10003`                               |
| `EXPORTER_BIND_HOST` | The address to listen on                                                                                                                                                                  |                                     | `0.0.0.0`                             |
| `EXPORTER_NAMESPACE` | The prefix to use for prometheus metrics                                                                                                                                                  |                                     | `ecowater`                            |
| `CONFIG_FILE`        | The container filepath to the config file                                                                                                                                                 |                                     | `/etc/exporter/config.yaml`           |

### Running locally with docker or docker-compose
First export your username, password, timezone, and config directory path variables:
```shell
export ACCOUNT_USERNAME=''
export ACCOUNT_PASSWORD=''
export TZ='America/Denver'
export CONFIG_DIR="$(pwd)/volumes"
```

Run with docker:
```shell
docker run --rm \
-e ACCOUNT_USERNAME="$ACCOUNT_USERNAME" \
-e ACCOUNT_PASSWORD="$ACCOUNT_PASSWORD" \
-e TZ="$TZ" \
-p"10003:10003" \
--mount type=bind,source="$CONFIG_DIR"/volumes,target=/etc/exporter \
ghcr.io/ejsuncy/ecowater_prometheus_exporter:0.2.0a
```

Run via docker-compose:

```shell
docker-compose build && \
docker-compose up
```

Then visit in your browser:
```shell
http://0.0.0.0:10003/metrics
```

### Running on kubernetes
A sample manifest:
```yaml
# Service
apiVersion: v1
kind: Service
metadata:
  name: prometheus-exporters-ecowater
spec:
  type: LoadBalancer
  ports:
    - name: http
      port: 80
      targetPort: 10003
      protocol: TCP
  selector:
    app: prometheus-exporters-ecowater
---

# Secrets
apiVersion: v1
kind: Secret
metadata:
  name: secrets-ecowater
type: Opaque
data:
  # obtain b64 encoded password with `echo -n "<password>" | b64`
  ACCOUNT_PASSWORD: "<b64-encoded password here>"
---
# Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: prometheus-exporters-ecowater
  name: prometheus-exporters-ecowater
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus-exporters-ecowater
  template:
    metadata:
      labels:
        app: prometheus-exporters-ecowater
    spec:
      containers:
      - image: ghcr.io/ejsuncy/ecowater_prometheus_exporter:0.2.0a
        name: ecowater
        resources:
          limits:
            cpu: 200m
            memory: 300Mi
          requests:
            cpu: 100m
            memory: 150Mi
        ports:
          - name: http
            containerPort: 10003
            protocol: TCP
        env:
          - name: EXPORTER_LOG_LEVEL
            value: DEBUG
          - name: ACCOUNT_USERNAME
            value: myemail@test.com
          - name: TZ
            value: America/Denver
        envFrom:
          - secretRef:
              name: secrets-ecowater
```

Of course, you should fine-tune the memory and cpu requests and limits.
Also note that multiple replicas for High Availability (HA) may get you rate-limited or 
have your connections dropped since there's currently no built-in leader election.

You might configure your prometheus scrape settings in a configmap as such:
```yaml
apiVersion: v1
data:
  prometheus_config: |
    global:
      scrape_interval: 15s
      external_labels:
        monitor: 'k8s-prom-monitor'
    scrape_configs:
      - job_name: 'ecowater'
        metrics_path: /metrics
        scrape_interval: 3m
        scrape_timeout: 1m
        static_configs:
          - targets:
              - 'prometheus-exporters-ecowater'
kind: ConfigMap
metadata:
  name: prometheus-config
```


## Contributing and Development

### Update git-submod-lib submodule for current Makefile Targets
```shell
git submodule update --init --remote
```

### Make Python venv and install requirements
```shell
make -f git-submod-lib/makefile/Makefile venv
```

Make and commit changes, and then build and test the image locally as follows.

### Build Image Locally
```shell
make -f git-submod-lib/makefile/Makefile build-image
```

### Make a pull request to `main` with your changes
```shell
make -f git-submod-lib/makefile/Makefile pull-request-main
```

## Releasing

### Minor releases
```shell
make -f git-submod-lib/makefile/Makefile promotion-alpha
```

Once the PR is approved and merged:
```shell
make -f git-submod-lib/makefile/Makefile github-release
```

Once the Release is published:
```shell
make -f git-submod-lib/makefile/Makefile github-image
```

Now cut a version release branch:
```shell
make -f git-submod-lib/makefile/Makefile github-branch
```

Now move `main` to the next `alpha` version to capture future development
```shell
make -f git-submod-lib/makefile/Makefile version-alpha
```

### Patch releases
Start with the version branch to be patched (ie `0.0.x`)
```shell
make -f git-submod-lib/makefile/Makefile promotion-patch
```

Once the PR is approved and merged:
```shell
make -f git-submod-lib/makefile/Makefile github-release-patch
```

Once the Patch Release is published:
```shell
make -f git-submod-lib/makefile/Makefile github-image
```
