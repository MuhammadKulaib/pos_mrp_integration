{
    "name": "pos mrp integration",
    "summary": "Short (1 phrase/line) summary of the module's purpose",
    "description": """
Long description of module's purpose
    """,
    "author": "Mohammad Kulaib",
    "website": "https://www.yourcompany.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Uncategorized",
    "version": "0.1",
    # any module necessary for this one to work correctly
    "depends": ["product", "point_of_sale", "mrp"],
    # always loaded
    "data": [
        "views/product_template_views.xml",
        "views/mrp_production_views.xml",
        "views/pos_order_views.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_mrp_integration/static/src/js/pos_validate.js",
        ]
    },
    # only loaded in demonstration mode
    "demo": [],
    "auto_install": True,
}
