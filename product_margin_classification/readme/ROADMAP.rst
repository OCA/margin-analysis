* This module will not work for variants that have a not null ``price_extra`` value,
  due to the poor design of Odoo product module.
  This issue can be maybe fixed in new version of Odoo.

* This module will not work for products that available in several
  companies, because this module introduces stored fields, that can
  not be company dependant, and the fields depends on ``standard_price``
  that is company dependent.
