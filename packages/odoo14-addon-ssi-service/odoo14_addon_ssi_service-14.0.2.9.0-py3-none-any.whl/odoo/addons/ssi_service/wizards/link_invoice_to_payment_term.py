# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class LinkInvoiceToPaymentTerm(models.TransientModel):
    _name = "link_invoice_to_payment_term"
    _description = "Link Invoice To Service Contract Payment Term"

    @api.model
    def _default_contract_id(self):
        return self.env.context.get("active_id", False)

    term_id = fields.Many2one(
        string="Contract Term",
        comodel_name="service.contract_fix_item_payment_term",
        default=lambda self: self._default_contract_id(),
    )
    allowed_invoice_ids = fields.Many2many(
        string="Allowed Invoices",
        comodel_name="account.move",
        compute="_compute_allowed_invoice_ids",
        store=False,
        compute_sudo=True,
    )
    invoice_id = fields.Many2one(
        string="# Invoice",
        comodel_name="account.move",
    )

    @api.depends(
        "term_id",
    )
    def _compute_allowed_invoice_ids(self):
        AM = self.env["account.move"]
        for record in self:
            criteria = [
                ("move_type", "=", "out_invoice"),
                ("partner_id", "=", record.term_id.service_id.partner_id.id),
                ("state", "=", "posted"),
            ]
            result = AM.search(criteria).ids
            record.allowed_invoice_ids = result

    def action_confirm(self):
        for record in self.sudo():
            record._confirm()

    def _confirm(self):
        self.ensure_one()
        self.term_id.write(
            {
                "invoice_id": self.invoice_id.id,
            }
        )
