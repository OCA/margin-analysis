Provides an overridable method on product which compute the Replenishment cost of a product. By default it just returns the value of "Cost price" field, but using the product_cost_incl_bom module, it will return the costing from the bom.

As it is a generic module, you can also setup your own way of computing the replenishment_cost for your product.

All OCA modules to compute margins are based on it, so you'll be able to use them in your own way.