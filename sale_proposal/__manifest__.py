{
    "name": "Sale Proposal",
    "version": "16.0",
    "author": "Odoo india",
    "maintainer": "Odoo india",
    "depends": ['sale_management','purchase'],
    "website": "www.odoo.com",
    "summary": "Sale Proposal",
    "category": "apps",
    "data":[
        'data/ir_sequence.xml',
        'data/task_mail_template.xml',
        'security/ir.model.access.csv',
        'reports/report_proposal.xml',
        'reports/proposal_report.xml',
        'views/proposal_view.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            'sale_proposal/static/src/js/sale_order_portal.js',
        ],
    },
}