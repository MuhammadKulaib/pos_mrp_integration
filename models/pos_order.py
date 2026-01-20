from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PosOrder(models.Model):
    _inherit = "pos.order"

    mrp_production_ids = fields.One2many(
        "mrp.production",
        "pos_order_id",
        string="MRP Productions",
        readonly=True,
    )
    mrp_production_count = fields.Integer(
        string="MRP Production Count",
        compute="_compute_mrp_production_count",
    )

    @api.depends("mrp_production_ids")
    def _compute_mrp_production_count(self):
        for rec in self:
            rec.mrp_production_count = len(rec.mrp_production_ids)

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

    def action_pos_order_paid(self):
        res = super().action_pos_order_paid()
        self._create_mrp_orders()
        return res

    def _create_mrp_orders(self):
        for order in self.filtered(lambda o: not o.is_refund):
            company = order.company_id
            picking_type_id = order.picking_type_id.warehouse_id.manu_type_id.id
            mrp_orders_to_create = [
                {
                    "product_id": line.product_id.id,
                    "product_qty": line.qty,
                    "product_uom_id": line.product_uom_id.id,
                    "pos_order_id": order.id,
                    "pos_order_line_id": line.id,
                    "origin": order.name,
                    "company_id": company.id,
                    "picking_type_id": picking_type_id,
                }
                for line in order.lines.filtered(lambda i: i.product_id.manufacture_ok)
            ]
            production_orders = (
                self.env["mrp.production"]
                .with_company(company)
                .sudo()
                .create(mrp_orders_to_create)
            )
            production_orders.action_confirm()
            production_orders.button_mark_done()

    def action_open_mrp_production(self):
        self.ensure_one()
        return {
            "name": _("MRP Productions"),
            "type": "ir.actions.act_window",
            "res_model": "mrp.production",
            "view_mode": "list,kanban,form,calendar,pivot,graph,activity",
            "domain": [("pos_order_id", "=", self.id)],
            "context": {"create": False},
        }
