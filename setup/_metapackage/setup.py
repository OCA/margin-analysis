import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-margin-analysis",
    description="Meta package for oca-margin-analysis Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-account_invoice_margin',
        'odoo12-addon-account_invoice_margin_sale',
        'odoo12-addon-product_replenishment_cost',
        'odoo12-addon-product_standard_margin',
        'odoo12-addon-sale_margin_delivered',
        'odoo12-addon-sale_margin_security',
        'odoo12-addon-sale_margin_sync',
        'odoo12-addon-sale_order_margin_percent',
        'odoo12-addon-sale_report_margin',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
