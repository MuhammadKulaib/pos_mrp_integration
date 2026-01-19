from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    manufacture_ok = fields.Boolean(_("Manufacture"))

    @api.constrains("manufacture_ok", "available_in_pos", "is_kits", "bom_ids")
    def _check_valid_bom(self):
        """
        POS sale is blocked if no BoM exists
        """
        todo = self.filtered(lambda i: i.manufacture_ok and i.available_in_pos)
        for rec in todo:
            # check if product is kit
            if rec.is_kits:
                raise UserError(
                    _(
                        "This product is identified as a Kit. Please disable 'Manufacture' or change the Bill of Materials type to 'Manufacture this product'."
                    )
                )

            # check if product has valid bom
            if not (
                rec.bom_ids.mapped("bom_line_ids").filtered(
                    lambda i: i.product_id.type == "consu"
                )
                or rec.bom_ids.mapped("byproduct_ids").filtered(
                    lambda i: i.product_id.type == "consu"
                )
            ):
                raise UserError(
                    _(
                        "No valid Bill of Materials found. The product must containing at least one storable or consumable component or by-product."
                    )
                )

    @api.constrains("manufacture_ok", "type")
    def _check_valid_manufacture_type(self):
        """
        Check if the product type is valid for manufacture
        That Must equal consu
        """
        if self.filtered(lambda i: i.manufacture_ok and i.type != "consu"):
            raise UserError(_("The product type must be consumable for manufacture."))
