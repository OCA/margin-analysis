# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Joel Grand-Guillaume
#    Copyright 2012 Camptocamp SA
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

import tools
from osv import fields,osv

# TODO: use another table name and provide another improved analysis with different 
# graph view on margin
class account_invoice_report(osv.osv):
    _inherit = "account.invoice.report"
    _columns = {
        'subtotal_cost_price_company': fields.float('Total Cost', readonly=True),
        'margin_absolute': fields.float('Real Margin', readonly=True),
        
        # TODO: The conversion is right here, just rename it in the view the field to be consistenet with 
        # product historical margin
        # 'subtotal_company': fields.float('Total Without Tax (company currency)', readonly=True),
    }
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'account_invoice_report')
        cr.execute("""
            create or replace view account_invoice_report as (
                 select min(ail.id) as id,
                    ai.date_invoice as date,
                    to_char(ai.date_invoice, 'YYYY') as year,
                    to_char(ai.date_invoice, 'MM') as month,
                    to_char(ai.date_invoice, 'YYYY-MM-DD') as day,
                    ail.product_id,
                    ai.partner_id as partner_id,
                    ai.payment_term as payment_term,
                    ai.period_id as period_id,
                    (case when u.uom_type not in ('reference') then
                        (select name from product_uom where uom_type='reference' and active and category_id=u.category_id LIMIT 1)
                    else
                        u.name
                    end) as uom_name,
                    ai.currency_id as currency_id,
                    ai.journal_id as journal_id,
                    ai.fiscal_position as fiscal_position,
                    ai.user_id as user_id,
                    ai.company_id as company_id,
                    count(ail.*) as nbr,
                    ai.type as type,
                    ai.state,
                    pt.categ_id,
                    ai.date_due as date_due,
                    ai.address_contact_id as address_contact_id,
                    ai.address_invoice_id as address_invoice_id,
                    ai.account_id as account_id,
                    ail.account_id as account_line_id,
                    ai.partner_bank_id as partner_bank_id,
                    sum(case when ai.type in ('out_refund','in_invoice') then
                         -ail.quantity / u.factor
                        else
                         ail.quantity / u.factor
                        end) as product_qty,

                    sum(case when ai.type in ('out_refund','in_invoice') then
                         -ail.price_subtotal
                        else
                          ail.price_subtotal
                        end) / cr.rate as price_total,
                    
                    -- *** BEGIN CHG ***
                    sum(ail.subtotal_cost_price_company) as subtotal_cost_price_company,
                                            
                    sum(ail.price_subtotal/cr.rate-ail.subtotal_cost_price_company) as margin_absolute,
                    -- *** END CHG *** 
                    
                    (case when ai.type in ('out_refund','in_invoice') then
                      sum(-ail.price_subtotal)
                    else
                      sum(ail.price_subtotal)
                    end) / (CASE WHEN sum(ail.quantity/u.factor) <> 0
                       THEN
                         (case when ai.type in ('out_refund','in_invoice')
                          then sum(-ail.quantity/u.factor)
                          else sum(ail.quantity/u.factor) end)
                       ELSE 1
                       END)
                     / cr.rate as price_average,

                    cr.rate as currency_rate,
                    sum((select extract(epoch from avg(date_trunc('day',aml.date_created)-date_trunc('day',l.create_date)))/(24*60*60)::decimal(16,2)
                        from account_move_line as aml
                        left join account_invoice as a ON (a.move_id=aml.move_id)
                        left join account_invoice_line as l ON (a.id=l.invoice_id)
                        where a.id=ai.id)) as delay_to_pay,
                    sum((select extract(epoch from avg(date_trunc('day',a.date_due)-date_trunc('day',a.date_invoice)))/(24*60*60)::decimal(16,2)
                        from account_move_line as aml
                        left join account_invoice as a ON (a.move_id=aml.move_id)
                        left join account_invoice_line as l ON (a.id=l.invoice_id)
                        where a.id=ai.id)) as due_delay,
                    (case when ai.type in ('out_refund','in_invoice') then
                      -ai.residual
                    else
                      ai.residual
                    end)/ (CASE WHEN
                        (select count(l.id) from account_invoice_line as l
                         left join account_invoice as a ON (a.id=l.invoice_id)
                         where a.id=ai.id) <> 0
                       THEN
                        (select count(l.id) from account_invoice_line as l
                         left join account_invoice as a ON (a.id=l.invoice_id)
                         where a.id=ai.id)
                       ELSE 1
                       END) / cr.rate as residual
                from account_invoice_line as ail
                left join account_invoice as ai ON (ai.id=ail.invoice_id)
                left join product_product pr on (pr.id=ail.product_id)
                left join product_template pt on (pt.id=pr.product_tmpl_id)
                left join product_uom u on (u.id=ail.uos_id),
                res_currency_rate cr
                where cr.id in (select id from res_currency_rate cr2  where (cr2.currency_id = ai.currency_id)
                and ((ai.date_invoice is not null and cr.name <= ai.date_invoice) or (ai.date_invoice is null and cr.name <= NOW())) limit 1)
                group by ail.product_id,
                    ai.date_invoice,
                    ai.id,
                    cr.rate,
                    to_char(ai.date_invoice, 'YYYY'),
                    to_char(ai.date_invoice, 'MM'),
                    to_char(ai.date_invoice, 'YYYY-MM-DD'),
                    ai.partner_id,
                    ai.payment_term,
                    ai.period_id,
                    u.name,
                    ai.currency_id,
                    ai.journal_id,
                    ai.fiscal_position,
                    ai.user_id,
                    ai.company_id,
                    ai.type,
                    ai.state,
                    pt.categ_id,
                    ai.date_due,
                    ai.address_contact_id,
                    ai.address_invoice_id,
                    ai.account_id,
                    ail.account_id,
                    ai.partner_bank_id,
                    ai.residual,
                    ai.amount_total,
                    u.uom_type,
                    u.category_id
            )
        """)

account_invoice_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
