import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-margin-analysis",
    description="Meta package for oca-margin-analysis Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-account_invoice_margin',
        'odoo13-addon-account_invoice_margin_sale',
        'odoo13-addon-sale_margin_delivered',
        'odoo13-addon-sale_margin_security',
        'odoo13-addon-sale_report_margin',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
