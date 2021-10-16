import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-margin-analysis",
    description="Meta package for oca-margin-analysis Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-account_invoice_margin',
        'odoo11-addon-account_invoice_margin_sale',
        'odoo11-addon-sale_margin_delivered',
        'odoo11-addon-sale_margin_security',
        'odoo11-addon-sale_margin_sync',
        'odoo11-addon-sale_order_margin_percent',
        'odoo11-addon-sale_report_margin',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 11.0',
    ]
)
