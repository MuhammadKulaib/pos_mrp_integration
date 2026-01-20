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
        for order in self:
            # Filter products that require manufacturing
            products = order.lines.mapped("product_id").filtered("manufacture_from_pos")
            if not products:
                continue

            # Check if a valid BoM exists for these products and the order's company
            # _bom_find returns a dict {product: bom}
            boms_by_product = self.env["mrp.bom"]._bom_find(
                products,
                picking_type=order.picking_type_id,
                company_id=order.company_id.id,
                bom_type="normal",
            )

            # Identify products for which no BoM was found
            products_missing_bom = products.filtered(
                lambda p: not boms_by_product.get(p)
            )

            if products_missing_bom:
                raise ValidationError(
                    _(
                        "The following products are marked for 'Manufacture from POS' but have no valid Bill of Materials available for company %(company)s:\n%(products)s",
                        company=order.company_id.name,
                        products=", ".join(products_missing_bom.mapped("display_name")),
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
                for line in order.lines.filtered(
                    lambda i: i.product_id.manufacture_from_pos
                )
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
