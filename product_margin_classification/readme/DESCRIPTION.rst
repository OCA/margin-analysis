This module is designed to extend Sale Price computation in Odoo.

This module add a new model 'Margin Classifications' linked to Product variants.

A margin classification has a 'Profit Margin' field and extra fields to manage
computation method, like in Pricelist Item model (Markup Rate, Rounding and Surcharge fields)

This module use both [Markup](https://en.wikipedia.org/wiki/Markup_(business))
and [Profit Margin](https://en.wikipedia.org/wiki/Profit_margin) concepts.

You could be interested by native Pricelist functionalities, setting sale
prices based on Cost prices. The main problem of this design is that sale price
change automaticaly when cost price changes, that is not desired in some user
cases. For exemple, if you have a shop, you want to changes sale prices when
customers is not in the shop, and after having changed labels in the shop.
