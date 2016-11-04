.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

================================
Product Cost including BOM costs
================================

Compute product cost price by recursively summing parts cost prices according to product BOM. It takes into
account the BoM costing (cost per cycle and so...). If no BOM define for a product, the cost_price is always
equal to the standard_price field of the product, so we always have a value to base our reporting on.

It makes a quite complex computation to include correct computation of such use case having
such a hierarchy of products:

            - Table A
                - 2x Plank 20.-
                - 4x Wood leg 10.-
            - Table B
                - 3x Plank 20.-
                - 4x Red wood leg
            - Red wood leg
                - 1x Wood leg 10.-
                - 1x Red paint pot 10.-
            - Chair
                - 1x Plank
                - 4x Wood leg
            - Table and Chair
                - 1x Table Z
                - 4x Chair Z
Changing the price of Wood leg will update the price of Table A, Table B, Red wood leg, 
Table & Chair products.

* Go to ...

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/132/8.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/margin-analysis/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/OCA/
margin-analysis/issues/new?body=module:%20
product_cost_incl_bom%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Alexandre Fayolle <alexandre.fayolle@camptocamp.com>
* Yannick Vaucher <yannick.vaucher@camptocamp.com>
* Guewen Baconnier <guewen.baconnier@camptocamp.com>
* Joël Grand-Guillaume <joel.grand-guillaume@camptocamp.com>
* Sodexis <dev@sodexis.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
