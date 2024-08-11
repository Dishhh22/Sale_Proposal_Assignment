# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, http, SUPERUSER_ID, _
from odoo.addons.portal.controllers import portal
from odoo.http import request


class CustomerPortalProposal(portal.CustomerPortal):

    @http.route(['/my/proposal/<int:proposal_id>'], type='http', auth="public", website=True)
    def portal_order_page(self, proposal_id, access_token=None, report_type=None):
        order_sudo = self._document_check_access('proposal.proposal', proposal_id, access_token=access_token)
        values = {
            'docs': order_sudo,
            'proposal_proposal': order_sudo,
            'report_type': 'html',
        }
        return request.render("sale_proposal.report_proposal", values)

    @http.route(['/my/proposal/accept/<int:proposal_id>'], type='json', auth="public", website=True)
    def accept_proposal(self, proposal_id, access_token=None):
        order_sudo = self._document_check_access('proposal.proposal', proposal_id, access_token=access_token)
        order_sudo.action_customer_accept()
        return {'success': True}

    @http.route(['/my/proposal/refuse/<int:proposal_id>'], type='json', auth="public", website=True)
    def refuse_proposal(self, proposal_id, access_token=None):
        order_sudo = self._document_check_access('proposal.proposal', proposal_id, access_token=access_token)
        order_sudo.action_customer_refused()
        return {'success': True}
