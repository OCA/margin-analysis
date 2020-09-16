def migrate(cr, version):
    """ From 10.0, to 12.0, margin_classification_id,
    theoretical_price, theoretical_difference, margin_state
    moved from product.template to product.product
    """
    cr.execute("""
        ALTER TABLE product_product
        ADD COLUMN margin_classification_id integer;
    """)
    cr.execute("""
        UPDATE product_product pp
        SET margin_classification_id = pt.margin_classification_id
        FROM product_template pt
        WHERE pt.id = pp.product_tmpl_id
        AND pt.margin_classification_id is not null;
    """)

    cr.execute("""
        ALTER TABLE product_product
        ADD COLUMN theoretical_price float;
    """)
    cr.execute("""
        ALTER TABLE product_product
        ADD COLUMN theoretical_difference float;
    """)
    cr.execute("""
        ALTER TABLE product_product
        ADD COLUMN margin_state varchar;
    """)

    cr.execute("""
        UPDATE product_product pp
        SET theoretical_price = pt.theoretical_price,
        theoretical_difference = pt.theoretical_difference,
        margin_state = pt.margin_state
        FROM product_template pt
        WHERE pt.id = pp.product_tmpl_id;
    """)
