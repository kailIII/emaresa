{
  "name" : "reportes",
  "version" : "1.0",
  "author" : "Ingenieria OpenDrive Ltda",
  "website" : "http://opendrive.cl",
  "category" : "Localizacion Chilena",
  "description": """
reportes balance tributario, libro de compras, libro de ventas. 

Para openerp V6.1. en libro de compras y libro de ventas trae el rut del campo res_partner.rut y el numero del campo acount_invoice.number

 """,
  "depends" : ['base'],
  "init_xml" : [ ],
  "demo_xml" : [ ],
  "update_xml" : ['reportes_view.xml'],
  "installable": True,
  "application": True
}
