odoo.define('sale_proposal.report_proposal', function (require) {

    var publicWidget = require('web.public.widget');

    publicWidget.registry.ProposalPortal = publicWidget.Widget.extend({
        selector: '.o_portal_proposal_sidebar',
        events: {
            'click #accept_proposal': '_onAcceptProposal',
            'click #refuse_proposal': '_onRefuseProposal',
            'change .qty-accepted': '_onQtyAcceptedChange',
            'change .price-accepted': '_onPriceAcceptedChange',
        },

        _onAcceptProposal: function (ev) {
            ev.preventDefault();
            var recId = $(ev.currentTarget).data('proposal-id');
            this._rpc({
                route: '/my/proposal/accept/' + recId,
                params: {},
            }).then(function (result) {
                if (result.success) {
                    window.location.reload();
                }
            });
        },


        _onRefuseProposal: function (ev) {
            ev.preventDefault();
            var recId = $(ev.currentTarget).data('proposal-id');
            this._rpc({
                route: '/my/proposal/refuse/' + recId,
                params: {},
            }).then(function (result) {
                if (result.success) {
                    window.location.reload();
                }
            });
        },

        _onQtyAcceptedChange: function (ev) {
            var lineId = $(ev.currentTarget).data('line-id');
            var newQty = $(ev.currentTarget).val();
            this._updateProposalLine(lineId, {qty_accepted: newQty});
        },

        _onPriceAcceptedChange: function (ev) {
            var lineId = $(ev.currentTarget).data('line-id');
            var newPrice = $(ev.currentTarget).val();
            this._updateProposalLine(lineId, {price_accepted: newPrice});
        },

        _updateProposalLine: function (lineId, data) {
            this._rpc({
                model: 'proposal.lines',
                method: 'write',
                args: [[lineId], data],
            }).then(function () {
                window.location.reload();
            });
        },
    });
});