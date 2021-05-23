# -*- coding: utf-8 -*-
# from odoo import http


# class VendorIdentifier(http.Controller):
#     @http.route('/vendor_identifier/vendor_identifier/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vendor_identifier/vendor_identifier/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('vendor_identifier.listing', {
#             'root': '/vendor_identifier/vendor_identifier',
#             'objects': http.request.env['vendor_identifier.vendor_identifier'].search([]),
#         })

#     @http.route('/vendor_identifier/vendor_identifier/objects/<model("vendor_identifier.vendor_identifier"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vendor_identifier.object', {
#             'object': obj
#         })
