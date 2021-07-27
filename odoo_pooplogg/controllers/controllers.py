# -*- coding: utf-8 -*-
# from odoo import http


# class OdooPooplogg(http.Controller):
#     @http.route('/odoo_pooplogg/odoo_pooplogg/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/odoo_pooplogg/odoo_pooplogg/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('odoo_pooplogg.listing', {
#             'root': '/odoo_pooplogg/odoo_pooplogg',
#             'objects': http.request.env['odoo_pooplogg.odoo_pooplogg'].search([]),
#         })

#     @http.route('/odoo_pooplogg/odoo_pooplogg/objects/<model("odoo_pooplogg.odoo_pooplogg"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('odoo_pooplogg.object', {
#             'object': obj
#         })
