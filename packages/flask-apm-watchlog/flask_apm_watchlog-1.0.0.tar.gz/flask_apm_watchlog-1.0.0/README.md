# flask_watchlog_apm

🔗 **Website**: [https://watchlog.io](https://watchlog.io)

**flask_watchlog_apm** is a lightweight APM integration for Flask, built on OpenTelemetry. It provides:

- **Auto-instrumentation** for Flask routes and underlying HTTP calls  
- **Manual custom spans** via the OpenTelemetry API  
- **JSON-over-HTTP exporter** (OTLP) compatible with Watchlog Agent  
- **Environment detection** (local vs in-cluster Kubernetes)  
- **Configurable sampling**, error-only and slow-only span export  

---

## Installation

Install from PyPI:

```bash
pip install flask_watchlog_apm
```

Or directly from GitHub:

```bash
pip install git+https://github.com/Watchlog-monitoring/flask_watchlog_apm.git
```

---

## Quick Start

Initialize the APM **before** registering any routes:

```python
# main.py
from flask import Flask
from flask_watchlog_apm.instrument import instrument_app

app = Flask(__name__)

# 1) Initialize Watchlog APM
instrument_app(
    app,
    service_name="my-flask-service",   # your service name
    otlp_endpoint="http://localhost:3774/apm",
    headers={"Authorization": "Bearer <token>"},
    sample_rate=0.5,                   # random sample rate (0.0–1.0, capped at 0.3)
    send_error_spans=True,             # always export error spans
    error_tps=10,                      # max 10 error spans per second
    slow_threshold_ms=100              # always export spans >100ms
)

# 2) Define your routes
@app.route("/")
def hello():
    return "Hello, Watchlog APM!"

# 3) Run your app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000, debug=True)
```

What happens?

1. Flask endpoints and outbound HTTP calls (via `requests`) are auto-instrumented.  
2. Spans are batched and sent as JSON to your Watchlog Agent (local or in-cluster).  
3. Configurable filters—sampling, error-only, slow-only—are applied.

---

## Configuration Options

| Parameter           | Type    | Default                     | Description                                                      |
| ------------------- | ------- | --------------------------- | ---------------------------------------------------------------- |
| `service_name`      | `str`   | **required**                | Name of your Flask service                                       |
| `otlp_endpoint`     | `str`   | `http://localhost:3774/apm` | Base OTLP URL (appends `/<service>/v1/traces`)                   |
| `headers`           | `dict`  | `{}`                        | Additional HTTP headers for OTLP requests                        |
| `batch_max_size`    | `int`   | `200`                       | Maximum spans per batch                                          |
| `batch_delay_ms`    | `int`   | `5000`                      | Delay in milliseconds between batch exports                      |
| `sample_rate`       | `float` | `1.0`                       | Random sampling rate (0.0–1.0, internal cap at 0.3)             |
| `send_error_spans`  | `bool`  | `False`                     | If `True`, always export spans with non-OK status                |
| `error_tps`         | `int`   | `None`                      | Max error spans to export per second (`None` = unlimited)        |
| `slow_threshold_ms` | `int`   | `0`                         | If >0, always export spans slower than this threshold (ms)       |
| `export_timeout`    | `float` | `10.0`                      | HTTP request timeout (seconds) for exporter POSTs                |

---

## Manual Custom Spans

Use the OpenTelemetry API to create custom spans:

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

@app.route("/db")
def fetch_db():
    with tracer.start_as_current_span("db.query", attributes={"db.system":"postgresql"}):
        # your DB logic here
        return "db query done"
```

---

## Environment Detection

- **Local (non-K8s)**: sends to `http://127.0.0.1:3774/apm`  
- **Kubernetes (in-cluster)**: sends to `http://watchlog-python-agent.monitoring.svc.cluster.local:3774/apm`

Detection checks in order:

1. Existence of `/var/run/secrets/kubernetes.io/serviceaccount/token`  
2. Presence of `kubepods` in `/proc/1/cgroup`  
3. DNS lookup of `kubernetes.default.svc.cluster.local`

---

## License

MIT © Mohammadreza

Built for [Watchlog.io](https://watchlog.io)
