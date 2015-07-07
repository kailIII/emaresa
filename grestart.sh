# Script para recargar el servidor Gunicorn con OpenERP

#kill -HUP `cat odoo/.gunicorn.pid`
killall -9 gunicorn
sh ./gstart.sh
