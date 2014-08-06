[![Build Status](http://runbot.odoo.com/runbot/badge/default/1/8.0.svg)](http://runbot.odoo.com/runbot)

Este clon de Odoo fue creado para satisfacer los requerimientos de localización de nuestros clientes ubicados en sudamerica de habla hispana. Por lo tanto consideramos que si te encuentras en Panamá, Colombia, Ecuador, Perú, Chile, Argentina, Bolivia, Paraguay o Uruguay, entonces este clon puede ser de mucha utilidad para tu proyecto de implementación.

Nosotros mantenemos y utilizamos este clon como base de los módulos que desarrollamos para nuestros clientes de consultoría y nube. Además hemos incluido un directorio "extra-addons" con los módulos que hacemos públicos para el beneficio de toda la comunidad.

Branch Público de Cubic ERP
---------------------------

El "Branch Público CubicERP" esta ahora localizado en el directorio "extra-addons" de este clon, hemos decidido integrarlo con este clon para la facilidad de instalación y punto centralizado de atención de preguntas e incidencias.

¿Por qué creamos un clon separado de odoo/odoo?
-----------------------------------------------

La respuesta es muy sencilla, cuando nosotros remitimos estos parches a OpenERP (ahora Odoo) no los consideraron o no los atendieron, asi como los cientos de parches no atendidos que ha enviado la comunidad a OpenERP (https://code.launchpad.net/~openerp/openobject-addons/trunk ver en Branch Merges).

En esta nueva plataforma github.com estamos enviando ya, algunas contribuciones y si nos atienden, iremos enviando todos los parches para asi contar con una única copia del nuevo odoo.

Soporte Comunitario Gratuito en Español
=======================================

Nos complace en anunciar, que mediante este repositorío estaremos atendiendo las consultas y soporte requerido por la comunidad de habla hispana que hubera llevado alguno de los cursos que dictamos en los diferentes países (http://cubicerp.eventbrite.com). 

Este servicio de soporte no tiene SLA, es decir no tiene tiempo máximo de atención. Si usted requiere un soporte profesional en OpenERP, con nivel de servicio y atención personalizada, por favor contrate nuestro servicio de branch o nube.

En caso deseen remitir código fuente para el soporte en español, este debe ser enviado mediante un "pull request" dentro del directorio "sandbox", este directorio sandbox es para almacenar todos el código fuente sobre el cual desean soporte técnico y por ningún motivo deben de incluirlo en el addons de su archivo de configuración, usualmente .openerp_serverrc

Para el soporte funcional, deben remitirnos capturas de pantalla y alguna forma de ingresar a su servidor o sinó utilizar nuestras demos de openerp ubicadas en el home de nuestro website (http://cubicERP.com)

Esperamos poder atenderlos con la calidad y cordialidad que nos caracteriza.

Acerca de Cubic ERP
===================

Cubic ERP le ofrece consultoría y educación en Odoo (antes OpenERP) desde 2009, nuestros principales logros:
- Partner oficial de Odoo (antes OpenERP) desde 2010
- Certificación FEC-V7 "Expertos en OpenERP", según PearsonVUE y OpenERP SA
- Partner de Entrenamiento y Certificación en OpenERP
- Top Author en apps.openerp.com con más de 75 módulos publicados
- Pertenecemos al histórico "OpenERP Commiters Team"
- Cinco módulos desarrollados por Cubic ERP estan incluidos en el release oficial de OpenERP
- Consultores Expertos en OpenERP con clientes en Perú, Colombia, Chile, Ecuador, Argentina, Paraguay, Panama y Bolivia

Nuestros Servicios
------------------
- Cubic ERP Cloud - SaaS Virtual en la Nube (http://cubicerp.com/nube)
- Consultoría Funcional y Técnica en OpenERP (http://cubicerp.com/consultoria)
- Cursos de OpenERP, Cursos de 5 dias, Workshops de 2 dias (http://cubicerp.com/cursos)
- Branch Privado Cubic ERP con Soporte funcional y técnico, además descuentos en horas de Consultoría  (http://cubicerp.com/branch)


About Odoo
==========

Odoo is a suite of web based open source business apps.  More info at http://www.odoo.com

The easiest way to play with it is the <a href="https://www.odoo.com/page/start">Odoo free trial</a>, email registration is NOT required, use the "skip this step" link on the registration page to skip it.


Getting started with Odoo development
--------------------------------------

If you are a developer type the following command at your terminal [1]:

    wget -O- https://raw.githubusercontent.com/odoo/odoo/master/odoo.py | python

Then follow <a href="https://doc.openerp.com/trunk/server/howto/howto_website/">the developer tutorial</a>

Other way to migrate your repository is:

1) Install bzr-fastimport

    $ sudo apt-get install bzr-fastimport

2) Move into your bazzar branch local directory

3) Initialice your local branch directory with git

    $ git init

4) Run the next command to migrate your bzr to git

    $ bzr fast-export --git-branch=master . | git fast-import

5) Check your logs on git

    $ git log

6) Push your new git branch to github or other

    $ git push https://...



Packages, tarballs and installers
---------------------------------

* Debian packages

    Add this apt repository to your /etc/apt/sources.list file

        deb http://nightly.openerp.com/8.0/deb/ ./

    Then type:

        $ sudo apt-get update
        $ sudo apt-get install odoo

* <a href="http://nightly.openerp.com/">Source tarballs</a>

* <a href="http://nightly.openerp.com/">Windows installer</a>

* <a href="http://nightly.openerp.com/">RPM package</a>


For Odoo employees
------------------

To add the odoo-dev remote use this command:

    $ ./odoo.py setup_git_dev

To fetch odoo merge pull requests refs use this command:

    $ ./odoo.py setup_git_review

