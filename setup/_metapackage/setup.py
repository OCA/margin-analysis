import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-margin-analysis",
    description="Meta package for oca-margin-analysis Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-account_invoice_margin>=16.0dev,<16.1dev',
        'odoo-addon-account_invoice_margin_sale>=16.0dev,<16.1dev',
        'odoo-addon-product_margin_classification>=16.0dev,<16.1dev',
        'odoo-addon-product_replenishment_cost>=16.0dev,<16.1dev',
        'odoo-addon-product_standard_margin>=16.0dev,<16.1dev',
        'odoo-addon-sale_margin_delivered>=16.0dev,<16.1dev',
        'odoo-addon-sale_margin_delivered_security>=16.0dev,<16.1dev',
        'odoo-addon-sale_margin_security>=16.0dev,<16.1dev',
        'odoo-addon-sale_margin_sync>=16.0dev,<16.1dev',
        'odoo-addon-sale_report_margin>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
