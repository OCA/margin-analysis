import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo9-addons-oca-margin-analysis",
    description="Meta package for oca-margin-analysis Odoo addons",
    version=version,
    install_requires=[
        'odoo9-addon-product_replenishment_cost',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
