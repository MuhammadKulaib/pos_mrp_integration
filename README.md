# Odoo POS - MRP Integration

## Overview
This module bridges the gap between Point of Sale (POS) and Manufacturing (MRP) by automating the creation of Manufacturing Orders for products sold at the POS. It is designed for businesses that require "Make to Order" workflows directly from the checkout counter, ensuring inventory accuracy and immediate production tracking.

## Integration Flow

### 1. Configuration & Setup
Products intended for immediate manufacturing must be configured with:
- **Manufacture from POS**: A dedicated boolean flag on the Product Template.
- **Bill of Materials (BoM)**: A valid "Manufacture this product" (Normal) BoM.

### 2. Point of Sale (Frontend Request)
When a cashier selects a product:
- **Real-time Validation**: The system checks if the product is marked for manufacturing and possesses a valid BoM.
- **Error Handling**: If the BoM is missing, the system intercepts the action, removes the line from the cart, and displays a "Missing BoM" alert to prevent invalid orders.

### 3. Order Processing (Backend Execution)
Upon validating payment (`action_pos_order_paid`):
- The system identifies all order lines marked for POS Manufacturing.
- A **Manufacturing Order (MO)** is generated for each specific line item.

### 4. Manufacturing Workflow
The generated MOs undergo an automated lifecycle:
1.  **Draft to Confirmed**: The MO is created and immediately confirmed to reserve components.
2.  **Availability Check**: The system checks component availability.
3.  **Auto-Completion**: If components are available (`components_availability_state != 'unavailable'`), the MO is automatically marked as **Done**, decrementing component stock and incrementing finished product stock instantly.
4.  **Exception Handling**: If components are unavailable, the MO remains in `Confirmed` state for manual production or replenishment.

---

## Key Design Decisions

### Dual-Layer Validation
To prevent "stuck" orders and ensure data consistency, validation is enforced at two levels:
- **Frontend (JS)**: Provides immediate feedback to the cashier, ensuring a smooth UX and preventing "bad data" from entering the cart.
- **Backend (Python)**: A secondary safety net during order creation ensures that no MO is attempted without a valid BoM, protecting the database from incomplete records.

### Atomic Manufacturing (One-to-One)
The module creates **one Manufacturing Order per POS Order Line**.
- **Reasoning**: This granular approach allows for precise cost tracking and better handling of potential future customizations (e.g., "Burger without onions") where each sold item might legally constitute a unique production run.

### "Best Effort" Automation
The system is designed for speed. It attempts to close the manufacturing loop (Produce & Done) immediately. However, it respects inventory constraints by pausing at the "Confirmed" state if stock is insufficient, preventing negative stock inconsistencies (depending on configuration) and alerting warehouse staff via the open MO.

---

## Assumptions & Limitations

1.  **Product Type**: The module enforces strict type checking. Products must be **Storable** (or Consumable, depending on version context) to track stock moves correctly. Service products are ignored.
2.  **BoM Type**: Only **Normal** (Manufacture this product) BoMs are supported. Kits (Phantom) are handled by standard Odoo logic and are not processed by this module.
3.  **Stock Availability**: The "Auto-Done" feature assumes that if Odoo says stock is available, it physically is. If stock records are inaccurate, the MO will halt at "Confirmed".
4.  **Performance**: Real-time MO creation adds a slight overhead to the "Validate" payment action. For high-volume retail with complex BoMs, this may introduce localized latency at the register.
