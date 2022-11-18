import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-margin-analysis",
    description="Meta package for oca-margin-analysis Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-account_invoice_margin>=15.0dev,<15.1dev',
        'odoo-addon-account_invoice_margin_sale>=15.0dev,<15.1dev',
        'odoo-addon-sale_margin_delivered>=15.0dev,<15.1dev',
        'odoo-addon-sale_margin_security>=15.0dev,<15.1dev',
        'odoo-addon-sale_report_margin>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
