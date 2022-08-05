
from collections import namedtuple
from datetime import datetime
from dateutil import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.osv import expression

import logging

_logger = logging.getLogger(__name__)

class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'



    purchase_returns = fields.Many2one('stock.picking.type', 'Purchase Returns', check_company=True)
    sale_returns = fields.Many2one('stock.picking.type', 'Sale Returns', check_company=True)



    def _get_locations_values(self, vals, code=False):
        data = super(StockWarehouse, self)._get_locations_values( vals, code=False)
        def_values = self.default_get(['reception_steps', 'delivery_steps'])
        reception_steps = vals.get('reception_steps', def_values['reception_steps'])
        delivery_steps = vals.get('delivery_steps', def_values['delivery_steps'])
        code = vals.get('code') or code or ''
        code = code.replace(' ', '').upper()
        name = _(vals.get('name'))
        company_id = vals.get('company_id', self.default_get(['company_id'])['company_id'])
        data.update({
            'lot_stock_id': {
                'name': name ,
                'active': True,
                'usage': 'internal',
                'barcode': self._valid_barcode(name + '-STOCK', company_id)
            },
            'wh_input_stock_loc_id': {
                'name': _('Input'),
                'active': reception_steps != 'one_step',
                'usage': 'internal',
                'barcode': self._valid_barcode(name + '-INPUT', company_id)
            },
            'wh_qc_stock_loc_id': {
                'name': _('Quality Control'),
                'active': reception_steps == 'three_steps',
                'usage': 'internal',
                'barcode': self._valid_barcode(name + '-QUALITY', company_id)
            },
            'wh_output_stock_loc_id': {
                'name': _('Output'),
                'active': delivery_steps != 'ship_only',
                'usage': 'internal',
                'barcode': self._valid_barcode(name + '-OUTPUT', company_id)
            },
            'wh_pack_stock_loc_id': {
                'name': _('Packing Zone'),
                'active': delivery_steps == 'pick_pack_ship',
                'usage': 'internal',
                'barcode': self._valid_barcode(name + '-PACKING', company_id)
            },
            },
        )
        return data

    def _update_name_and_code(self, new_name=False, new_code=False):
        res = super(StockWarehouse, self)._update_name_and_code(new_name, new_code)
        if not new_name:
            return res
        if new_name:
            for warehouse in self:
                routes = warehouse.route_ids
                for route in routes:
                    route.write({'name': route.name.replace(warehouse.name, new_name, 1)})
                    for pull in route.rule_ids:
                        pull.write({'name': pull.name.replace(warehouse.name, new_name, 1)})
                if warehouse.mto_pull_id:
                    warehouse.mto_pull_id.write({'name': warehouse.mto_pull_id.name.replace(warehouse.name, new_name, 1)})
        if new_code:
            self.mapped('lot_stock_id').mapped('location_id').write({'name': new_name})
        return res

    def _get_picking_type_update_values(self):
        data = super(StockWarehouse, self)._get_picking_type_update_values()
        input_loc, output_loc = self._get_input_output_locations(self.reception_steps, self.delivery_steps)
        data.update({
            'sale_returns': {'default_location_dest_id': input_loc.id},
            'purchase_returns': {'default_location_src_id': output_loc.id},
            },
        )
        return data


    def _get_picking_type_create_values(self, max_sequence):
        data, next_sequence = super(StockWarehouse, self)._get_picking_type_create_values(max_sequence)
        input_loc, output_loc = self._get_input_output_locations(self.reception_steps, self.delivery_steps)
        Location = self.env['stock.location']
        customer_loc = self.env.ref('stock.stock_location_customers', raise_if_not_found=False)
        supplier_loc = self.env.ref('stock.stock_location_suppliers', raise_if_not_found=False)
        data.update({
            'in_type_id': {
                'name': self.name + ' ' + _('Purchase Receipt'),
                'code': 'incoming',
                'use_create_lots': True,
                'use_existing_lots': False,
                'default_location_src_id': supplier_loc.id,
                'sequence': max_sequence + 1,
                'barcode': self.name + ' ' + _('Purchase Receipt'),
                'show_reserved': False,
                'sequence_code':self.name + ' ' + _('Purchase Receipt'),
                'company_id': self.company_id.id,
            },
             'out_type_id': {
                'name': self.name + ' ' + _('Sale Delivery'),
                'code': 'outgoing',
                'use_create_lots': False,
                'use_existing_lots': True,
                'default_location_dest_id': customer_loc.id,
                'sequence': max_sequence + 1,
                'barcode': self.name + ' ' + _('Sale Delivery'),
                'sequence_code': self.name + ' ' + _('Sale Delivery'), 
                'company_id': self.company_id.id,
            },
             'pack_type_id': {
                'name': self.name + ' ' + _('Pack'),
                'code': 'internal',
                'use_create_lots': False,
                'use_existing_lots': True,
                'default_location_src_id': self.wh_pack_stock_loc_id.id,
                'default_location_dest_id': output_loc.id,
                'sequence': max_sequence + 4,
                'barcode':self.name + ' ' + _('Pack'),
                'sequence_code':self.name + ' ' + _('Pack'),
                'company_id': self.company_id.id,
            },
             'pick_type_id': {
                'name':self.name + ' ' + _('Pack'),
                'code': 'internal',
                'use_create_lots': False,
                'use_existing_lots': True,
                'default_location_src_id': self.lot_stock_id.id,
                'sequence': max_sequence + 3,
                'barcode':self.name + ' ' + _('Pack'),
                'sequence_code':self.name + ' ' + _('Pack'),
                'company_id': self.company_id.id,
            },
             'int_type_id': {
                'name':self.name + ' ' + _('Internal Transfers'),
                'code': 'internal',
                'use_create_lots': False,
                'use_existing_lots': True,
                'default_location_src_id': self.lot_stock_id.id,
                'default_location_dest_id': self.lot_stock_id.id,
                'active': self.reception_steps != 'one_step' or self.delivery_steps != 'ship_only' or self.user_has_groups('stock.group_stock_multi_locations'),
                'sequence': max_sequence + 2,
                'barcode':self.name + ' ' + _('Internal Transfers'),
                'sequence_code':self.name + ' ' + _('Internal Transfers'),
                'company_id': self.company_id.id,
            },
             'purchase_returns': {
                'name': self.name + ' ' + _('Purchase Returns'),
                'code': 'outgoing',
                'use_create_lots': False,
                'use_existing_lots': True,
                'default_location_dest_id': supplier_loc.id,
                'sequence': max_sequence + 1,
                'barcode': self.name + ' ' + _('Purchase Returns'),
                'sequence_code': self.name + ' ' + _('Purchase Returns'), 
                'company_id': self.company_id.id,
            },
            'sale_returns': {
                'name': self.name + ' ' + _('Sale Returns'),
                'code': 'incoming',
                'use_create_lots': True,
                'use_existing_lots': False,
                'default_location_src_id': customer_loc.id,
                'sequence': max_sequence + 1,
                'barcode': self.name + ' ' + _('Sale Returns'),
                'show_reserved': False,
                'sequence_code':self.name + ' ' + _('Sale Returns'),
                'company_id': self.company_id.id,
            },
        })
        return data, max_sequence + 6

    def _get_sequence_values(self):
        values = super(StockWarehouse, self)._get_sequence_values()
        values.update({
            'in_type_id': {
                'name': self.name + ' ' + _('Purchase Receipt'),
                'prefix':self.name + ' ' + _('Purchase Receipt/%(range_year)s/'),
                'range_reset' : 'yearly',
                'padding': 5,
                'use_date_range': True,
                'company_id': self.company_id.id,
            },
            'out_type_id': {
                'name': self.name + ' ' + _('Sale Delivery'),
                'prefix':self.name + ' ' + _('Sale Delivery/%(range_year)s/'),
                'range_reset' : 'yearly',
                'use_date_range': True,
                'padding': 5,
                'company_id': self.company_id.id,
            },
            'pack_type_id': {
                'name': self.name + ' ' + _('PACK'),
                'prefix':self.name + ' ' + _('PACK/%(range_year)s/'),
                'range_reset' : 'yearly',
                'use_date_range': True,
                'padding': 5,
                'company_id': self.company_id.id,
            },
            'pick_type_id': {
                'name': self.name + ' ' + _('PICK'),
                'prefix':self.name + ' ' + _('PICK/%(range_year)s/'),
                'range_reset' : 'yearly',
                'use_date_range': True,
                'padding': 5,
                'company_id': self.company_id.id,
            },
            'int_type_id': {
                'name': self.name + ' ' + _('Internal Transfers'),
                'prefix':self.name + ' ' + _('Internal Transfers/%(range_year)s/'),
                'range_reset' : 'yearly',
                'use_date_range': True,
                'padding': 5,
                'company_id': self.company_id.id,
            },
            'sale_returns': {
                'name': self.name + ' ' + _('Sale Returns'),
                'prefix':self.name + ' ' + _('Sale Returns/%(range_year)s/'),
                'range_reset' : 'yearly',
                'use_date_range': True,
                'padding': 5,
                'company_id': self.company_id.id,
            },
            'purchase_returns': {
                'name': self.name + ' ' + _('Purchase Returns'),
                'prefix':self.name + ' ' + _('Purchase Returns/%(range_year)s/'),
                'range_reset' : 'yearly',
                'use_date_range': True,
                'padding': 5,
                'company_id': self.company_id.id,
            },
        })
        return values

    def _create_or_update_sequences_and_picking_types(self):
        data = super()._create_or_update_sequences_and_picking_types()
        PickingType = self.env["stock.picking.type"]
        if 'out_type_id' in data:
            PickingType.browse(data['out_type_id']).write({'return_picking_type_id': data.get('sale_returns', False)})
        if 'in_type_id' in data:
            PickingType.browse(data['in_type_id']).write({'return_picking_type_id': data.get('purchase_returns', False)})
        return data
