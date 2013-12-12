# -*- coding: utf-8 -*-
##############################################################################
#
#    Author:  Joel Grand-Guillaume
#    Copyright 2013 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import tools
from openerp.osv import orm


class report_stock_move(orm.Model):
    _inherit = "report.stock.move"

    def init(self, cr):
        """
        Override the SQL view tpo replace standard_price by cost_price
        """
        tools.drop_view_if_exists(cr, 'report_stock_move')
        cr.execute("""
CREATE OR REPLACE view report_stock_move AS (
    SELECT
            min(sm.id) as id,
            date_trunc('day', sm.date) as date,
            to_char(date_trunc('day',sm.date), 'YYYY') as year,
            to_char(date_trunc('day',sm.date), 'MM') as month,
            to_char(date_trunc('day',sm.date), 'YYYY-MM-DD') as day,
            avg(date(sm.date)-date(sm.create_date)) as day_diff,
            avg(date(sm.date_expected)-date(sm.create_date)) as day_diff1,
            avg(date(sm.date)-date(sm.date_expected)) as day_diff2,
            sm.location_id as location_id,
            sm.picking_id as picking_id,
            sm.company_id as company_id,
            sm.location_dest_id as location_dest_id,
            sum(sm.product_qty) as product_qty,
            sum(
                (CASE WHEN sp.type in ('out') THEN
                         (sm.product_qty * pu.factor / pu2.factor)
                      ELSE 0.0
                END)
            ) as product_qty_out,
            sum(
                (CASE WHEN sp.type in ('in') THEN
                         (sm.product_qty * pu.factor / pu2.factor)
                      ELSE 0.0
                END)
            ) as product_qty_in,
            sm.partner_id as partner_id,
            sm.product_id as product_id,
            sm.state as state,
            sm.product_uom as product_uom,
            pt.categ_id as categ_id ,
            coalesce(sp.type, 'other') as type,
            sp.stock_journal_id AS stock_journal,

            -- *** BEGIN of changes ***
            sum(
                (CASE WHEN sp.type in ('in') THEN
                         (sm.product_qty * pu.factor / pu2.factor) * pp.cost_price
                      ELSE 0.0
                END)
                -
                (CASE WHEN sp.type in ('out') THEN
                         (sm.product_qty * pu.factor / pu2.factor) * pp.cost_price
                      ELSE 0.0
                END)
            ) as value
            -- *** END OF CHANGES ***
        FROM
            stock_move sm
            LEFT JOIN stock_picking sp ON (sm.picking_id=sp.id)
            LEFT JOIN product_product pp ON (sm.product_id=pp.id)
            LEFT JOIN product_uom pu ON (sm.product_uom=pu.id)
              LEFT JOIN product_uom pu2 ON (sm.product_uom=pu2.id)
            LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
        GROUP BY
            coalesce(sp.type, 'other'), date_trunc('day', sm.date),
            sm.partner_id, sm.state, sm.product_uom, sm.date_expected,
            -- *** BEGIN of changes ***
            sm.product_id, pp.cost_price, sm.picking_id,
            -- *** END OF CHANGES ***
            sm.company_id, sm.location_id, sm.location_dest_id, pu.factor,
            pt.categ_id, sp.stock_journal_id,
            year, month, day
               )
        """)


class report_stock_inventory(orm.Model):
    _inherit = "report.stock.inventory"

    def init(self, cr):
        """
        Override the SQL view tpo replace standard_price by cost_price
        """
        tools.drop_view_if_exists(cr, 'report_stock_inventory')
        cr.execute("""
CREATE OR REPLACE view report_stock_inventory AS (
    (SELECT
        min(m.id) as id, m.date as date,
        to_char(m.date, 'YYYY') as year,
        to_char(m.date, 'MM') as month,
        m.partner_id as partner_id, m.location_id as location_id,
        m.product_id as product_id, pt.categ_id as product_categ_id,
        l.usage as location_type, l.scrap_location as scrap_location,
        m.company_id,
        m.state as state, m.prodlot_id as prodlot_id,
        -- *** BEGIN of changes ***
        coalesce(sum(-pp.cost_price * m.product_qty * pu.factor / pu2.factor)::decimal, 0.0) as value,
        -- *** END OF CHANGES ***
        coalesce(sum(-m.product_qty * pu.factor / pu2.factor)::decimal, 0.0) as product_qty
    FROM
        stock_move m
            LEFT JOIN stock_picking p ON (m.picking_id=p.id)
            LEFT JOIN product_product pp ON (m.product_id=pp.id)
                LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
                LEFT JOIN product_uom pu2 ON (m.product_uom=pu2.id)
            LEFT JOIN product_uom u ON (m.product_uom=u.id)
            LEFT JOIN stock_location l ON (m.location_id=l.id)
            WHERE m.state != 'cancel'
    GROUP BY
        m.id, m.product_id, m.product_uom, pt.categ_id, m.partner_id,
        m.location_id,  m.location_dest_id, m.prodlot_id, m.date, m.state,
        l.usage, l.scrap_location, m.company_id, pt.uom_id,
        to_char(m.date, 'YYYY'), to_char(m.date, 'MM')
) UNION ALL (
    SELECT
        -m.id as id, m.date as date,
        to_char(m.date, 'YYYY') as year,
        to_char(m.date, 'MM') as month,
        m.partner_id as partner_id, m.location_dest_id as location_id,
        m.product_id as product_id, pt.categ_id as product_categ_id, l.usage as location_type, l.scrap_location as scrap_location,
        m.company_id,
        m.state as state, m.prodlot_id as prodlot_id,
        -- *** BEGIN of changes ***
        coalesce(sum(pp.cost_price * m.product_qty * pu.factor / pu2.factor)::decimal, 0.0) as value,
        -- *** END OF CHANGES ***
        coalesce(sum(m.product_qty * pu.factor / pu2.factor)::decimal, 0.0) as product_qty
    FROM
        stock_move m
            LEFT JOIN stock_picking p ON (m.picking_id=p.id)
            LEFT JOIN product_product pp ON (m.product_id=pp.id)
                LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
                LEFT JOIN product_uom pu2 ON (m.product_uom=pu2.id)
            LEFT JOIN product_uom u ON (m.product_uom=u.id)
            LEFT JOIN stock_location l ON (m.location_dest_id=l.id)
            WHERE m.state != 'cancel'
    GROUP BY
        m.id, m.product_id, m.product_uom, pt.categ_id, m.partner_id,
        m.location_id, m.location_dest_id, m.prodlot_id, m.date, m.state,
        l.usage, l.scrap_location, m.company_id, pt.uom_id,
        to_char(m.date, 'YYYY'), to_char(m.date, 'MM')
    )
);
        """)
