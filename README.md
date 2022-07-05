
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/margin-analysis&target_branch=13.0)
[![Pre-commit Status](https://github.com/OCA/margin-analysis/actions/workflows/pre-commit.yml/badge.svg?branch=13.0)](https://github.com/OCA/margin-analysis/actions/workflows/pre-commit.yml?query=branch%3A13.0)
[![Build Status](https://github.com/OCA/margin-analysis/actions/workflows/test.yml/badge.svg?branch=13.0)](https://github.com/OCA/margin-analysis/actions/workflows/test.yml?query=branch%3A13.0)
[![codecov](https://codecov.io/gh/OCA/margin-analysis/branch/13.0/graph/badge.svg)](https://codecov.io/gh/OCA/margin-analysis)
[![Translation Status](https://translation.odoo-community.org/widgets/margin-analysis-13-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/margin-analysis-13-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# Margin Analysis

This project aim to deal with modules related to manage Financial controlling and costing in a generic way. You'll find modules that:

 - Compute cost based on BoM
 - Compute standard and historical margin
 - ...

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[account_invoice_margin](account_invoice_margin/) | 13.0.1.2.2 | [![sergio-teruel](https://github.com/sergio-teruel.png?size=30px)](https://github.com/sergio-teruel) | Show margin in invoices
[account_invoice_margin_sale](account_invoice_margin_sale/) | 13.0.1.0.2 | [![sergio-teruel](https://github.com/sergio-teruel.png?size=30px)](https://github.com/sergio-teruel) [![carlosdauden](https://github.com/carlosdauden.png?size=30px)](https://github.com/carlosdauden) | Set margin in invoices from sale orders
[account_invoice_margin_sale_delivered_sync](account_invoice_margin_sale_delivered_sync/) | 13.0.1.1.0 | [![sergio-teruel](https://github.com/sergio-teruel.png?size=30px)](https://github.com/sergio-teruel) | Sync invoice margin between invoices and sale orders
[sale_elaboration_margin](sale_elaboration_margin/) | 13.0.1.0.0 |  | Compute elaboration margins in sale orders lines
[sale_margin_delivered](sale_margin_delivered/) | 13.0.1.0.2 | [![sergio-teruel](https://github.com/sergio-teruel.png?size=30px)](https://github.com/sergio-teruel) | Sale Margin Delivered
[sale_margin_security](sale_margin_security/) | 13.0.1.0.1 | [![sergio-teruel](https://github.com/sergio-teruel.png?size=30px)](https://github.com/sergio-teruel) | Sale Margin Security
[sale_margin_sync](sale_margin_sync/) | 13.0.1.0.1 |  | Recompute sale margin when stock move cost price is changed
[sale_order_margin_percent](sale_order_margin_percent/) | 13.0.1.1.0 |  | Show Percent in sale order
[sale_report_margin](sale_report_margin/) | 13.0.1.0.0 | [![sergio-teruel](https://github.com/sergio-teruel.png?size=30px)](https://github.com/sergio-teruel) | Sale Report Margin

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to Odoo Community Association (OCA)
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----
OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
