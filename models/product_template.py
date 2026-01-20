from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    manufacture_from_pos = fields.Boolean(
        string="Manufacture from POS",
        help="If enabled, a Manufacturing Order is automatically created when sold via POS.",
    )

    @api.constrains("manufacture_from_pos", "is_kits", "bom_ids")
    def _check_valid_bom(self):
        """
        Product Must Have a valid Bill of Materials (BoM)
        """
        for tmpl in self.filtered("manufacture_from_pos"):
            # Use _bom_find to correctly handle company and variant fallback logic
            boms = (
                self.env["mrp.bom"]
                ._bom_find(
                    tmpl.product_variant_ids,
                    company_id=tmpl.company_id.id,
                    bom_type="normal",
                )
                .values()
            )

            # Ensure at least one valid BoM exists
            if not boms:
                raise UserError(
                    _(
                        "Product '%(name)s' must have a valid 'Manufacture this product' BoM (Company: %(company)s).",
                        name=tmpl.display_name,
                        company=tmpl.company_id.name or "All",
                    )
                )

    @api.constrains("manufacture_from_pos", "type")
    def _check_manufacture_product_type(self):
        """
        Validate that the product type allows 'Manufacture from POS'.
        Currently restricted to consumable products.
        """
        if self.filtered(lambda i: i.manufacture_from_pos and i.type != "consu"):
            raise UserError(
                _(
                    "Manufacturing from POS is currently only supported for Consumable products.",
                ),
            )
