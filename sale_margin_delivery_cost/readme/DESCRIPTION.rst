Track expected shipping costs, allowing more accurate margin calculations.

Costs could include packaging, documentation or customs expenses.
These may be consumables or services, not directly included in sales order lines
nor accounted with the invoice.
But we may still ant the Sales Order margin to consider these costs,
especially if business margins are tight.

Also allows for carrier shipping costs to be estimated separately,
instead of being automatically added as a sales order line, to charge the customer.

This is useful in the case the customer is charge with a shipping fee
that can be very different from the actual shipping cost,
or when no shipping fee is charged at all.

In this case the expected shipping costs, computed by the UPDATE SHIPPING COSTS
button, can be stored as Other Costs and considered for the sales order margin,
instead being added as a sales order line and charged to the customer.
