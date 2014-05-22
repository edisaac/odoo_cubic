Acerca de este Fork de Odoo
===========================

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

Odoo is a suite of open source Business apps. More info at http://www.odoo.com

Installation
============

[Setup/migration guide for employees](https://github.com/odoo/odoo/blob/master/doc/git.rst)


Migration from bazaar
=====================

If you have existing bazaar branches and want to move them to a git repository,
there are several options:

* download http://nightly.openerp.com/move-branch.zip and run it with
  `python move-branch.zip -h` (for the help). It should be able to convert
  simple-enough branches for you (even if they have merge commits &al)
* Extract the branch contents as patches and use `git apply` or `git am` to
  rebuild a branch from them
* Replay the branch by hand

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


System Requirements
-------------------

The dependencies are listed in setup.py


Debian/Ubuntu
-------------

Add the apt repository

    deb http://nightly.openerp.com/7.0/deb/ ./

in your source.list and type:

    $ sudo apt-get update
    $ sudo apt-get install openerp

Or download the deb file and type:

    $ sudo dpkg -i <openerp-deb-filename>
    $ sudo apt-get install -f

RedHat, Fedora, CentOS
----------------------

Install the required dependencies:

    $ yum install python
    $ easy_install pip
    $ pip install .....

Install the openerp rpm

    $ rpm -i openerp-VERSION.rpm

Windows
-------

Check the notes in setup.py


Setting up your database
------------------------

Point your browser to http://localhost:8069/ and click "Manage Databases", the
default master password is "admin".

