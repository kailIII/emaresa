# Script para iniciar el servidor OpenERP
cd odoo
gunicorn openerp:service.wsgi_server.application -D --log-file ../log/gunicorn.log  -c openerp-wsgi.py
cd ..
