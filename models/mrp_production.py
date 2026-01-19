from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    """Manufacturing Orders"""

    _inherit = "mrp.production"

    product_id = fields.Many2one(
        "product.product",
        "Product",
        domain=[("type", "=", "consu"), ("manufacture_ok", "=", True)],
        compute="_compute_product_id",
        store=True,
        copy=True,
        precompute=True,
        readonly=False,
        required=True,
        check_company=True,
    )
    manufacture_ok = fields.Boolean(
        "Manufacture",
        related="product_id.manufacture_ok",
    )

    @api.constrains("product_id")
    def _check_valid_product_id(self):
        if self.filtered(lambda i: not i.manufacture_ok):
            raise ValidationError(_("The product must be manufacture."))
