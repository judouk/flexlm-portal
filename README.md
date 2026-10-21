# flexlm-portal
A management portal for FlexLM

Designed almost entirely by Q&A with ChatGPT


What this provides
==================
I wanted a method for managing FlexLM updates. I was growing tired of the number of errors that were manually introduced by administrators who would seemingly take the license file, 'install' it and wait for the end-users to complain when things went wrong.

The model presented here has the premise of a user, a manager, or an admin


Setup Instructions
==================
The assumption here is that you have a linux enviroment with access to setup a python environment
This has been tested on a Rocky 8.10 environment with Python 3.12.8
A compiler (gcc) and python-development (python-devel) libraries are required.


These assumptions may change as development of this continues

1. Create a FastAPI environment
cd /var/www
mkdir backend
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip3 install alembic fastapi ldap3 passlib pydantic python-jose python-multipart pyyaml sqlalchemy uvicorn

2. Checkout Code
cd ~
git clone https://github.com/judouk/flexlm-portal.git flexlm-portal

3. Build a distribution
cd flexlm-portal/frontend
npm run build

4. Copy distribution to webserver
mkdir /var/www/flexlm
cp -a ~/flexlm-portal/dist/* /var/www/flexlm/.

5. Configure your settings
edit config/portal.yaml as required

  provider: local
   This may be the quickest option to get you going.
   scripts/create_admin.py is useful to create a basic admin/admin user

6. Configure selinux
setsebool -P httpd_can_network_connect on

7. Configure apache vhost
  Add
        LoadModule		proxy_module		modules/mod_proxy.so
        LoadModule		proxy_http_module	modules/mod_proxy_http.so

        ProxyPass		/api			http://127.0.0.1:8000
        ProxyPassReverse	/api			http://127.0.0.1:8000

8. Start uvicorn
uvicorn app.main:app --reload

9. Configure servers
Connect to the webserver and login
You should be in the admin group

10. Upload FlexLM files
These files will be automatically parsed

11. Public licence summary
The frontend exposes `/licences` without requiring a portal login. It groups
current uploaded licence rights by licence server, feature or product name,
quantity, and expiry date. Cadence `Product Name` / `Licensed Rights` comment
blocks and conventional FlexLM `FEATURE` / `INCREMENT` lines are supported.
When multiple uploads define the same product or feature for a server, the
newest definition replaces the historical definitions rather than adding them
to the current total.

12. Options files
Configure the options file path on the appropriate vendor daemon first. The
Options Files page then asks for that daemon and writes the managed content to
the configured path, ensuring the path in the generated `DAEMON` line and the
managed file refer to the same artifact.

Optional modern interface
=========================
The existing React interface remains the default. To select the modern,
ETX-inspired presentation, set this top-level value in your production
`config/portal.yaml`:

```yaml
ux_version: 2
```

Omitting this setting, or setting `ux_version: 1`, selects the original UI.
Only the integers `1` and `2` are accepted; invalid values fail backend startup.
Create the production configuration from `config/portal.yaml.example` and
configure it for your installation as described above. The example is not a
production configuration.

Build and deploy the frontend once with both interfaces included. Restart
FastAPI after changing `ux_version`, then reload the browser. No frontend
rebuild, database migration, or authentication changes are needed to switch.
To roll back the presentation, set `ux_version: 1`, restart FastAPI and reload.

Both versions use the same URLs, API endpoints, AD/LDAP authentication,
role checks, licence processing, storage and publishing services. ETX supplies
visual inspiration only; its Google/Microsoft OAuth sign-in is not included.
The existing local and trusted-header authentication providers remain supported.
The public `/licences` page remains available without authentication.

FastAPI exposes only `{"ux_version": 1}` or `{"ux_version": 2}` at `/ui-config`
(`/api/ui-config` through the documented Apache proxy). This endpoint must be
reachable before login and must not be cached by the reverse proxy. It never
returns credentials or other portal settings. An older backend returning 404
selects UI 1; other configuration failures show a retry screen. Keep the existing
SPA fallback for direct links such as `/servers` and `/licences`, and preserve
the `/api` proxy ahead of that fallback.

The modern stylesheet is loaded only for UI 2 and scoped to that version.
Functional pages, API helpers, login handling and authentication are shared.
UI 2 waits for `/me` before redirecting a protected route; UI 1 retains its
existing session-initialization behavior.

Validation: `python -m unittest discover -s tests` (with the backend dependencies
installed), and `cd frontend && npm test && npm run build`. UI configuration tests use
isolated temporary configurations/databases and mock AD authentication; a live
AD sign-in should also be checked in your deployment environment.
