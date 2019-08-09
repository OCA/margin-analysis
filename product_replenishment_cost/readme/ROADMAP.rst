Due to framework limitation, the field ``replenishment_cost`` is not
company dependent, while ``standard_price`` is. (in the recent Odoo versions)

It is due to the current impossibility to make working computed field between
two field ``company_dependent=True``.
