/** @odoo-module **/

import { PosStore } from "@point_of_sale/app/services/pos_store";
import { patch } from "@web/core/utils/patch";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

patch(PosStore.prototype, {
    async addLineToOrder(vals, order, opts = {}, configure = true) {
        const line = await super.addLineToOrder(vals, order, opts, configure);

        if (line) {
            const product = line.product_id;
            if (product.manufacture_ok && !product.bom_count) {
                this.dialog.add(AlertDialog, {
                    title: 'Missing BoM',
                    body: `Product ${product.display_name} has no Bill of Materials`
                });
                order.removeOrderline(line);
                return;
            }
        }
        return line;
    }
});
