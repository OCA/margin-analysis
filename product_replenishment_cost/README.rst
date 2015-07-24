.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Product Replenishment Cost
==========================

Provides an overridable method on product which compute the Replenishment cost
of a product. By default it just returns the value of "Cost price" field, but
using the product_cost_incl_bom module, it will return the costing from the
bom.

As it is a generic module, you can also setup your own way of computing the
replenishment_cost for your product.

All OCA modules to compute margins are based on it, so you'll be able to use
them in your own way.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/web/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/margin-analysis/issues/new?body=module:%20product_replenishment_cost%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Alexandre Fayolle <alexandre.fayolle@camptocamp.com>
* Yannick Vaucher <yannick.vaucher@camptocamp.com>
* Joël Grand-Guillaume <joel.grand-guillaume@camptocamp.com>
* Sylvain Le Gal (https://twitter.com/legalsylvain)

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
    :alt: Odoo Community Association
    :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.

