#. Place a new *Sale Order* and add a line with an stockable product. Set a
   quantity higher than one.
#. Confirm the *Sale Order* and deliver just a partial amount of product in the
   picking.
#. Go to *Sales > Reporting > Sales* and unfold the *Order Reference* dimension
   and the *Margin* and *Margin Delivered* to compare them.

For example:

In an order line with a product at a cost of 10 and a sell price of 25 we
deliver 2 of 3 units. Then, the reported margins would be:

`margin`: 45 (3 * 15)
`margin_delivered`: 30 (2 * 15)

Additionaly, you can check the margin and the margin percent in the sale order
line.
