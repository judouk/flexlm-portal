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


