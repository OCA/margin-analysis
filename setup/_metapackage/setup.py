import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-margin-analysis",
    description="Meta package for oca-margin-analysis Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-account_invoice_margin',
        'odoo14-addon-account_invoice_margin_sale',
        'odoo14-addon-product_standard_margin',
        'odoo14-addon-sale_margin_delivery_cost',
        'odoo14-addon-sale_margin_security',
        'odoo14-addon-sale_margin_sync',
        'odoo14-addon-sale_report_margin',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
