from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MrpBom(models.Model):
    """Defines bills of material for a product or a product template"""

    _inherit = "mrp.bom"

    product_tmpl_id = fields.Many2one(
        "product.template",
        "Product",
        check_company=True,
        index=True,
        domain=[("type", "=", "consu"), ("manufacture_ok", "=", True)],
        required=True,
    )
    manufacture_ok = fields.Boolean(
        "Manufacture",
        related="product_tmpl_id.manufacture_ok",
    )

    @api.constrains("product_tmpl_id")
    def _check_valid_product_tmpl_id(self):
        if self.filtered(lambda i: not i.manufacture_ok):
            raise ValidationError(_("The product must be manufacture."))
