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

    pos_order_id = fields.Many2one(
        "pos.order",
        "POS Order",
        related="pos_order_line_id.order_id",
        readonly=True,
        store=True,
        copy=False,
        help="The POS Order that generated this Manufacturing Order",
    )
    pos_order_line_id = fields.Many2one(
        "pos.order.line",
        "POS Order Line",
        readonly=True,
        copy=False,
        help="The POS Order Line that generated this Manufacturing Order",
    )

    @api.constrains("product_id")
    def _check_valid_product_id(self):
        if self.filtered(lambda i: not i.manufacture_ok):
            raise ValidationError(_("The product must be manufacture."))

    def action_open_pos_order(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "pos.order",
            "res_id": self.pos_order_id.id,
            "view_mode": "form",
            "target": "current",
        }
