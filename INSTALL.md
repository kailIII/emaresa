GUIA DE INSTALACIÓN EN UBUNTU
=============================

Instalación de librerías Python

    $ sudo apt-get install python-docutils python-gdata python-mako python-dateutil python-feedparser python-lxml python-tz python-vatnumber python-webdav python-xlwt python-werkzeug python-yaml python-zsi python-unittest2 python-mock python-libxslt1 python-ldap python-reportlab python-pybabel python-pychart python-simplejson python-psycopg2 python-vobject python-openid python-setuptools bzr postgresql unixodbc unixodbc-dev python-pyodbc python-psutil nginx
    $ sudo easy_install jinja2
    $ sudo easy_install Geraldo
    $ sudo easy_install openerp-client-lib
    $ sudo easy_install openerp-client-etl
    $ sudo easy_install gunicorn


Creación del usuario de base de datos

    $ sudo su - postgres
    $ createuser -d -R -S cubicerp
    $ exit


Creación de usuario que contendrá al branch sincronizado

    $ sudo useradd cubicerp -m -s /bin/bash
    $ sudo su - cubicerp


Descarga de repositorios, preguntar el nombre se le puso a su repositorio privado (<tu_empresa>)

    $ git clone https://github.com/CubicERP/<tu_empresa>.git src
    $ cd src
    $ git submodule init
    $ git submodule update


Para actualizar los repositorios poner los siguientes comandos:

    ## Actualiza el directorio actual de su repositorio privado, es decir "src" ##
    $ git pull 
    ## Actualiza los submodulos, es decir los directorios odoo y branch ##
    $ git submodule update
    ## Para abrir la versión 7.0 del repositorio ##
    $ git checkout 7.0
    $ git submodule foreach git checkout 7.0


Modificación del archivo de configuración (asignación de puertos)

    $ vi .openerp_serverrc


Los comandos para iniciar y parar el servicio del OpenERP en desarrollo con Werkzeugh

    $ ./stop.sh
    $ ./start.sh


Los comandos para iniciar y reiniciar el servicio del OpenERP en producción con gunicorn

    $ ./gstart.sh
    $ ./grestart.sh


Agregando inicio automatico del servicio

    $ sudo vi /etc/rc.local
    -------------------------------------------
    sudo su - cubicerp -c "cd src;./start.sh"
    sudo su - cubicerp -c "cd src;./gstart.sh"
    -------------------------------------------

Una vez iniciado el servicio para probar la instalación utilizar el siguiente url:

    http://<tu-ip>:18069 


Comandos para actualización  de la base de datos

    $ cd src
    $ odoo/openerp-server -c .openerp_serverrc -d <base_de_datos> -u all


Instalación del Gunicorn + NGINX
--------------------------------

Debe conectarse con un usuario con permisos de ejecutar sudo

Generación de certificado SSL

    $ cd /etc/nginx/
    $ sudo mkdir ssl
    $ cd /etc/nginx/ssl
    $ sudo openssl genrsa -des3 -out openerp.pkey 1024

Elimina la clave del certificado ssl
  
    $ sudo openssl rsa -in openerp.pkey -out openerp.key

Firmando el certificado ssl

    $ sudo openssl req -new -key openerp.key -out openerp.csr
    $ sudo openssl x509 -req -days 730 -in openerp.csr -signkey openerp.key -out openerp.crt
    $ cd ..

Configurando NGINX

    $ sudo vi /etc/nginx/sites-available/openerp
    ---------------------------------------------
    server {
          listen   443;
          server_name 0.0.0.0;
  
          access_log  /var/log/nginx/openerp-access.log;
          error_log   /var/log/nginx/openerp-error.log;
  
          ssl on;
          ssl_certificate     /etc/nginx/ssl/openerp.crt;
          ssl_certificate_key /etc/nginx/ssl/openerp.key;
  
          location / {
                  proxy_pass http://127.0.0.1:8078;
          }
  
    }
    server {
          listen   80;
          server_name 0.0.0.0;
  
          access_log  /var/log/nginx/openerp-access.log;
          error_log   /var/log/nginx/openerp-error.log;
  
          location / {
                  proxy_pass http://127.0.0.1:8078;
          }
  
    }
    ---------------------------------------------
    $ sudo ln -s /etc/nginx/sites-available/openerp /etc/nginx/sites-enabled/openerp

Reiniciando NGINX

    $ sudo service nginx restart

Agregando PYTHONPATH

    $ sudo vi /etc/environment
    ---------------------------------------------
    ...
    PYTHONPATH=.
    ---------------------------------------------

Actualizar los parámetros del OpenERP

    $ sudo su - cubicerp
    $ cd src/odoo
    $ vi openerp-wsgi.py
    ---------------------------------------------
    ...
    conf['addons_path'] = './addons,../branch,../trunk'
    ...
    bind = '127.0.0.1:8078'
    pidfile = '.gunicorn.pid'
    workers = 7
    timeout = 240
    max_requests = 2000
    ---------------------------------------------

Iniciando el Gunicorn

    $ gunicorn openerp:service.wsgi_server.application -c openerp-wsgi.py
