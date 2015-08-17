.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Product Margin and Margin Rate
==============================

Add a field on the product form that compute the standard (or theorical)
margin based on the current values of sale and replenishment cost present in
the product form. We take care of taxe included or excluded.

It will just compute it as follow:
(Sale Price without tax - Replenishment Cost) / Sale Price without tax

Remember that this module can be used in conjonction with
product_cost_incl_bom to have the replenishment cost computed from the BOM when
a product has one.

  WARNING:

  1) As this module will base his simple computation on sale and cost prices,
  it suppose you have them both in the same currency (the price type must of
  the same currency for both of them). Remember this is the default OpenERP
  configuration (price type of all product price fields are set as the same as
  the company currency). We don't take care of it cause otherwise we should
  have added a dependency on sale module.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/web/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/margin-analysis/issues/new?body=module:%20product_standard_margin%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

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

