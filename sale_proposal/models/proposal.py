from odoo import fields, models, api, _


class ProposalProposal(models.Model):
    _name = 'proposal.proposal'
    _description = 'Proposal Proposal'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char('Sequence', default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', 'Customer')
    date_order = fields.Datetime(string="Order Date", default=fields.Datetime.now)
    salesman_id = fields.Many2one('res.users', 'Salesman')
    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('customer_accepted', 'Customer Accepted'),
        ('customer_refused', 'Customer Refused'),
        ('confirmed', 'Confirmed'),
        ('cancel', 'Cancelled')
    ], default='draft', string='Status', tracking=True)
    amount_total = fields.Float('Amount Total')
    amount_purposed = fields.Float('Amount Total')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    proposal_link = fields.Char('Proposal Link', compute='get_proposal_link')
    line_ids = fields.One2many('proposal.lines', 'proposal_id', 'Proposal Orders')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'proposal.proposal') or _("New")
        return super().create(vals_list)

    def action_customer_accept(self):
        self.write({'state': 'customer_accepted'})

    def action_customer_refused(self):
        self.write({'state': 'customer_refused'})

    def action_confirm(self):
        self.ensure_one()
        if self.state == 'customer_accepted':
            self.state = 'confirmed'
            sale_order = self.env['sale.order'].create({
                'partner_id': self.partner_id.id,
                'pricelist_id': self.pricelist_id.id,
                'user_id': self.salesman_id.id,
                'state':'sale',
                'date_order': fields.Datetime.now(),
            })
            for line in self.line_ids:
                self.env['sale.order.line'].create({
                    'order_id': sale_order.id,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.qty_accepted,
                    'price_unit': line.price_accepted,
                })
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'res_id': sale_order.id,
                'view_mode': 'form',
                'target': 'current',
            }

    def get_proposal_link(self):
        for rec in self:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            rec.proposal_link = f"{base_url}/my/proposal/{rec.id}"

    def action_move_to_sent(self):
        if self.partner_id:
            body_html = \
            self.env.ref('sale_proposal.task_email_template')._render_field('body_html', self.ids, compute_lang=True)[self.id]
            self.env['mail.thread'].message_notify(
                email_from= self.salesman_id.email_formatted or '',
                subject='Proposal Summery',
                body=body_html,
                partner_ids=self.partner_id.ids
            )
            self.message_post(body=body_html)
            self.state = 'sent'

    def _get_portal_return_action(self):
        """ Return the action used to display orders when returning from customer portal. """
        self.ensure_one()
        return self.env.ref('sale_proposal.proposal_proposal_view_action')

    def action_move_to_confirm(self):
        self.state = 'confirmed'


class ProposalLines(models.Model):
    _name = 'proposal.lines'
    _description = 'Proposal Proposal'

    proposal_id = fields.Many2one('proposal.proposal', 'Proposal')
    product_id = fields.Many2one('product.product', 'Product')
    name = fields.Char('Label', related='product_id.default_code')
    pricelist_item_id = fields.Many2one(
        comodel_name='product.pricelist.item',
        compute='_compute_pricelist_item_id', store=1)
    qty_proposed = fields.Float('Qty Proposed', default=1)
    qty_accepted = fields.Float('Qty Accepted')
    price_proposed = fields.Float('Price Proposed', compute='_get_price_proposed')
    price_accepted = fields.Float('Price Accepted')

    @api.depends('product_id')
    def _compute_pricelist_item_id(self):
        for line in self:
            if not line.product_id or not line.proposal_id.pricelist_id:
                line.pricelist_item_id = False
            else:
                line.pricelist_item_id = line.proposal_id.pricelist_id._get_product_rule(
                    line.product_id,
                    line.qty_proposed or 1.0,
                    uom=line.product_id.uom_id,
                    date=line.proposal_id.date_order,
                )

    @api.depends('product_id', 'qty_proposed')
    def _get_price_proposed(self):
        self.price_proposed = False
        for record in self:
            if not record.product_id:
                record.pricelist_item_id = False
            else:
                pricelist_rule = record.pricelist_item_id
                order_date = record.proposal_id.date_order or fields.Date.today()
                product = record.product_id
                qty = record.qty_proposed or 1.0
                uom = record.product_id.uom_id
                currency = record.proposal_id.company_id.currency_id
                price = pricelist_rule._compute_price(
                    product, qty, uom, order_date, currency=currency)

                record.price_proposed = price
