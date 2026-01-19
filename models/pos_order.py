from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.constrains("lines")
    def _check_valid_order_lines(self):
        for rec in self:
            products = rec.lines.mapped("product_id").filtered(
                lambda p: p.manufacture_ok and not p.bom_count
            )
            if products:
                raise ValidationError(
                    _(
                        "Product %s has no Bill of Materials"
                        % str(", ".join(products.mapped("display_name")))
                    )
                )
