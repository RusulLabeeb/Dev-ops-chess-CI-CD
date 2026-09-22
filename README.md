\# DevOps Chess CI/CD Deployment



A practical DevOps project for deploying a static Chess web application using \*\*Linux, Git, Podman/Docker, Caddy, Flask Webhooks, systemd, and CI/CD automation\*\*.



The project covers containerized deployment, reverse proxy configuration, HTTPS, GitHub webhook integration, and automated redeployment after a Git push.



\---



\## 🏗️ Project Architecture



```text

GitHub Repository

&#x20;      │

&#x20;      │ git push

&#x20;      ▼

GitHub Webhook

&#x20;      │

&#x20;      │ HTTPS / Webhook

&#x20;      ▼

Caddy :9000

&#x20;      │

&#x20;      ▼

Flask Webhook Receiver

&#x20;      │

&#x20;      │ HMAC validation

&#x20;      ▼

deploy.simple

&#x20;      │

&#x20;      ├── git fetch

&#x20;      ├── git reset

&#x20;      └── docker compose up -d --build

&#x20;      │

&#x20;      ▼

Chess Container :8081

&#x20;      │

&#x20;      ▼

Caddy :3000

&#x20;      │

&#x20;      ▼

HTTPS Chess Website

```



\---



\# 1. Technologies Used



\* Linux / RHEL

\* Bash

\* Git / GitHub

\* Podman

\* Docker CLI compatibility

\* Podman Compose

\* Caddy

\* Python

\* Flask

\* systemd

\* GitHub Webhooks

\* HMAC SHA-256

\* FirewallD

\* HTTPS / TLS



\---



\# 2. Clone the Repository



Clone the Chess project:



```bash

cd /home/student

git clone https://github.com/RaafatTurki/chess.git

cd chess

```



Check the files:



```bash

ls

```



\---



\# 3. Verify Docker / Podman



The lab environment uses Podman with Docker CLI compatibility.



```bash

docker --version

docker compose version

podman --version

podman-compose --version

```



Check running containers:



```bash

docker ps

```



\---



\# 4. Deploy the Chess Application



The application is deployed using:



```bash

docker compose -f compose.simple.yml up -d --build

```



Check the container:



```bash

docker ps

```



Test the application:



```bash

curl -i http://127.0.0.1:8081

```



Expected result:



```text

HTTP/1.1 200 OK

```



\---



\# 5. Deployment Script



Create:



```text

/home/student/chess/deploy.simple

```



Content:



```bash

\#!/bin/bash



set -euo pipefail



cd "$(dirname "$0")"



git fetch \&\& git reset --hard @{u}



docker compose -f compose.simple.yml up -d --build --force-recreate

```



Make it executable:



```bash

chmod +x /home/student/chess/deploy.simple

```



Run it manually:



```bash

/home/student/chess/deploy.simple

```



The script performs:



1\. Moves to the project directory.

2\. Fetches the latest Git changes.

3\. Resets the local repository to the remote branch.

4\. Rebuilds the container.

5\. Recreates the running container.



\---



\# 6. Caddy Reverse Proxy



Caddy is used as a reverse proxy.



Main application:



```text

Client

&#x20; ↓

Caddy :3000

&#x20; ↓

Chess Container :8081

```



Caddy configuration:



```caddy

{

&#x20;   default\_sni 178.18.249.160

}



https://178.18.249.160:3000 {

&#x20;   tls internal

&#x20;   reverse\_proxy localhost:8081

}



:9000 {

&#x20;   reverse\_proxy 127.0.0.1:5000

}

```



Validate the configuration:



```bash

sudo caddy validate --config /etc/caddy/Caddyfile

```



Restart Caddy:



```bash

sudo systemctl restart caddy

```



Check its status:



```bash

sudo systemctl status caddy

```



\---



\# 7. Firewall Configuration



Open the application and webhook ports:



```bash

sudo firewall-cmd --permanent --add-port=3000/tcp

sudo firewall-cmd --permanent --add-port=9000/tcp

sudo firewall-cmd --reload

```



Verify:



```bash

sudo firewall-cmd --list-ports

```



\---



\# 8. Flask Webhook Receiver



Create the CI/CD application:



```text

/opt/cicd/app.py

```



Python application:



```python

from flask import Flask, request, abort

import hashlib

import hmac

import subprocess



app = Flask(\_\_name\_\_)



SECRET = b"YOUR\_SECRET"





@app.post("/webhook")

def webhook():

&#x20;   signature = request.headers.get("X-Hub-Signature-256", "")



&#x20;   if not signature.startswith("sha256="):

&#x20;       abort(401)



&#x20;   body = request.get\_data()



&#x20;   expected = "sha256=" + hmac.new(

&#x20;       SECRET,

&#x20;       body,

&#x20;       hashlib.sha256

&#x20;   ).hexdigest()



&#x20;   if not hmac.compare\_digest(signature, expected):

&#x20;       abort(401)



&#x20;   subprocess.run(

&#x20;       \["/home/student/chess/deploy.simple"],

&#x20;       cwd="/home/student/chess",

&#x20;       check=True

&#x20;   )



&#x20;   return "Deployment triggered\\n", 200





app.run(host="127.0.0.1", port=5000)

```



The webhook receiver:



1\. Receives the GitHub webhook.

2\. Reads `X-Hub-Signature-256`.

3\. Calculates the expected HMAC SHA-256 signature.

4\. Compares the signatures securely.

5\. Rejects invalid requests with HTTP `401`.

6\. Runs the deployment script for valid requests.



\---



\# 9. Python Virtual Environment



Create the CI/CD environment:



```bash

sudo mkdir -p /opt/cicd

sudo chown -R student:student /opt/cicd

```



Create the virtual environment:



```bash

cd /opt/cicd

python3 -m venv venv

```



Activate it:



```bash

source /opt/cicd/venv/bin/activate

```



Install Flask:



```bash

pip install flask

```



Check Flask:



```bash

pip show flask

```



Deactivate:



```bash

deactivate

```



\---



\# 10. Test Python Syntax



Before starting the service:



```bash

/opt/cicd/venv/bin/python -m py\_compile /opt/cicd/app.py

```



No output means the syntax check passed.



\---



\# 11. CI/CD systemd Service



Create:



```text

/etc/systemd/system/cicd.service

```



Configuration:



```ini

\[Unit]

Description=CI/CD webhook receiver

After=network-online.target

Wants=network-online.target



\[Service]

Type=simple

User=student

Group=student

WorkingDirectory=/opt/cicd

Environment=PYTHONUNBUFFERED=1

ExecStart=/opt/cicd/venv/bin/python app.py

Restart=on-failure



\[Install]

WantedBy=multi-user.target

```



Reload systemd:



```bash

sudo systemctl daemon-reload

```



Enable the service:



```bash

sudo systemctl enable cicd

```



Start it:



```bash

sudo systemctl start cicd

```



Check:



```bash

sudo systemctl status cicd

```



\---



\# 12. Chess systemd Service



Create:



```text

/etc/systemd/system/chess.service

```



Configuration:



```ini

\[Unit]

Description=Chess app

After=network-online.target

Wants=network-online.target



\[Service]

Type=oneshot

RemainAfterExit=yes

User=student

Group=student

WorkingDirectory=/home/student/chess

ExecStart=/bin/bash /home/student/chess/deploy.simple

ExecStop=/usr/bin/podman-compose -f /home/student/chess/compose.simple.yml down



\[Install]

WantedBy=multi-user.target

```



Reload:



```bash

sudo systemctl daemon-reload

```



Enable:



```bash

sudo systemctl enable chess

```



Start:



```bash

sudo systemctl start chess

```



Check:



```bash

sudo systemctl status chess

```



\---



\# 13. Enable User Linger



This allows the user's systemd environment to continue running without an active login session.



```bash

sudo loginctl enable-linger student

```



Verify:



```bash

loginctl show-user student | grep Linger

```



Expected:



```text

Linger=yes

```



\---



\# 14. GitHub Webhook



In the GitHub repository:



```text

Settings

→ Webhooks

→ Add webhook

```



Payload URL:



```text

https://178.18.249.160:9000/webhook

```



Content type:



```text

application/json

```



Secret:



```text

YOUR\_SECRET

```



Select:



```text

Just the push event

```



\---



\# 15. Test Invalid Webhook



An unsigned request should be rejected:



```bash

curl -i -X POST http://127.0.0.1:9000/webhook \\

\-H "Content-Type: application/json" \\

\--data '{"zen":"test"}'

```



Expected:



```text

401

```



This confirms that the webhook requires a valid signature.



\---



\# 16. Test Signed Webhook



Example:



```bash

SECRET="YOUR\_SECRET"



PAYLOAD='{"zen":"test"}'



SIG="sha256=$(printf '%s' "$PAYLOAD" | \\

openssl dgst -sha256 -hmac "$SECRET" | \\

sed 's/^.\* //')"



curl -s -w "\\nstatus:%{http\_code}\\n" \\

\-X POST http://127.0.0.1:9000/webhook \\

\-H "Content-Type: application/json" \\

\-H "X-GitHub-Event: push" \\

\-H "X-Hub-Signature-256: $SIG" \\

\--data-raw "$PAYLOAD"

```



Expected:



```text

Deployment triggered



status:200

```



\---



\# 17. HTTPS Test



Because port `3000` is configured for HTTPS:



```bash

curl -k -I https://127.0.0.1:3000

```



Expected:



```text

HTTP/2 200

```



The `-k` option is used because the project uses Caddy's internal TLS certificate.



\---



\# 18. Verify Container



```bash

docker ps

```



Expected:



```text

chess

```



Check the application directly:



```bash

curl -i http://127.0.0.1:8081

```



Expected:



```text

HTTP/1.1 200 OK

```



\---



\# 19. Verify Services



Check both services:



```bash

sudo systemctl status chess

sudo systemctl status cicd

```



Check that they are enabled:



```bash

sudo systemctl is-enabled chess cicd

```



Expected:



```text

enabled

enabled

```



\---



\# 20. Reboot Test



Reboot the server:



```bash

sudo reboot

```



After reconnecting, verify:



```bash

sudo systemctl status chess

sudo systemctl status cicd

docker ps

```



Test HTTPS:



```bash

curl -k -I https://127.0.0.1:3000

```



Test webhook again.



Expected:



```text

HTTP/2 200

```



and:



```text

Deployment triggered

status:200

```



This confirms that the deployment survives a server reboot.



\---



\# 21. Problems Encountered \& Solutions



\## Problem 1 — Git repository not found



\### Error



```text

fatal: not a git repository

```



The deployment script was being executed from the wrong working directory.



\### Solution



Added:



```bash

cd "$(dirname "$0")"

```



This makes the script work from its own project directory regardless of where it is called from.



\---



\## Problem 2 — `dirname "$0"` was run directly in the terminal



The command:



```bash

cd "$(dirname "$0")"

```



belongs inside the deployment script.



It should not be executed directly in the terminal because `$0` refers to the current shell/script context.



\---



\## Problem 3 — Flask returned HTTP 500



The webhook receiver could reach the Flask application, but the deployment process failed.



\### Solution



The deployment script was corrected and the subprocess was given the correct working directory:



```python

subprocess.run(

&#x20;   \["/home/student/chess/deploy.simple"],

&#x20;   cwd="/home/student/chess",

&#x20;   check=True

)

```



\---



\## Problem 4 — Python `IndentationError`



The Flask application initially had incorrect indentation.



\### Solution



The Python file was rewritten with correct indentation and validated using:



```bash

/opt/cicd/venv/bin/python -m py\_compile /opt/cicd/app.py

```



\---



\## Problem 5 — Webhook returned HTTP 502



The reverse proxy was working, but the Flask backend was not running correctly.



\### Solution



The `cicd.service` was fixed and restarted:



```bash

sudo systemctl restart cicd

```



Then:



```bash

sudo systemctl status cicd

```



\---



\## Problem 6 — `chess.service` failed after reboot



The service initially returned:



```text

status=203/EXEC

Permission denied

```



Systemd could not directly execute the script from `/home/student`.



\### Solution



Changed:



```ini

ExecStart=/home/student/chess/deploy.simple

```



to:



```ini

ExecStart=/bin/bash /home/student/chess/deploy.simple

```



Then:



```bash

sudo systemctl daemon-reload

sudo systemctl restart chess

```



\---



\## Problem 7 — HTTP request returned 400 on port 3000



The request was:



```bash

curl -I http://127.0.0.1:3000

```



But port `3000` was configured for HTTPS.



\### Solution



Use:



```bash

curl -k -I https://127.0.0.1:3000

```



\---



\## Problem 8 — Caddy internal certificate warning



Caddy reported that it could not automatically install its internal root certificate because the required certificate utility was unavailable and the `caddy` user did not have sudo access.



However, HTTPS itself worked successfully.



Test:



```bash

curl -k -I https://127.0.0.1:3000

```



Result:



```text

HTTP/2 200

```



\---



\# 22. Final Verification



The final project was tested for:



\* \[x] Chess container running

\* \[x] Application accessible on port `8081`

\* \[x] Caddy reverse proxy

\* \[x] HTTPS on port `3000`

\* \[x] Flask webhook receiver

\* \[x] HMAC signature validation

\* \[x] Invalid webhook rejected with `401`

\* \[x] Valid webhook triggers deployment

\* \[x] systemd services enabled

\* \[x] Services survive reboot

\* \[x] Automated container rebuild/recreation

\* \[x] Git-based deployment



\---



\# 23. What I Learned



Through this project, I practiced:



\* Linux service management with systemd

\* Git-based deployment workflows

\* Bash scripting

\* Container deployment with Podman/Docker

\* Docker Compose / Podman Compose

\* Reverse proxy configuration with Caddy

\* HTTPS and TLS

\* Python Flask webhooks

\* HMAC SHA-256 authentication

\* Firewall configuration

\* Service troubleshooting using systemd logs

\* Automated deployment triggered by GitHub

\* Debugging integration problems between Git, containers, systemd, Caddy and Python



\---



\# 24. Result



The final setup provides an automated deployment flow:



```text

Git Push

&#x20;  ↓

GitHub Webhook

&#x20;  ↓

Flask

&#x20;  ↓

HMAC Validation

&#x20;  ↓

deploy.simple

&#x20;  ↓

Git Fetch / Reset

&#x20;  ↓

Container Rebuild

&#x20;  ↓

Chess Application

&#x20;  ↓

Caddy HTTPS

```



The application and CI/CD services are configured to start automatically after a server reboot.



