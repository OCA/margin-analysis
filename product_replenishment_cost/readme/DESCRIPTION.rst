Provides an overridable method on product which compute the Replenishment cost of a product. By default it just returns the value of "Cost price" field, but using the product_cost_incl_bom module, it will return the costing from the bom.

"Cost price" is the cost assigned for each product in the warehouse and the "Replenishment cost" is the cost it would cost to buy a new product. They are different costs because the cost price depends on your valuation method and the operations you have performed while the replenishment cost is determined by the current market conditions.

For example: The price of the product in the supplier's catalog is €15/piece. Therefore, if I want to buy a new unit, my replenishment cost would be €15. But if my stock comes from having bought it in a special offer that allowed me to buy it for €10, then my cost price is €10/piece.

As it is a generic module, you can also setup your own way of computing the replenishment_cost for your product.

All OCA modules to compute margins are based on it, so you'll be able to use them in your own way.
