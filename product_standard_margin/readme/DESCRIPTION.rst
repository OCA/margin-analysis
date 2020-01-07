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
