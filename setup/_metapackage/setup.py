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
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
