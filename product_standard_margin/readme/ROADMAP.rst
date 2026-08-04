This module will not work properly if used in a multicompany context with "global" products
that are not related to any company.
This is due to current odoo limitation that compute field with a sudo user, and due to the field `standard_price`
that is weirdly company dependent, unlike the selling price.
