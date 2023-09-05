def calculate_free_items(order):
    print(f"order {order}")
    line_items = order.line_items.all()
    print(f"line_items {line_items}")
    promotion = order.promotion
    print(f"promotion {promotion}")
    required_quantity = promotion.required_quantity
    free_items_quantity = promotion.free_items_quantity

    free_items_dict = {}
    quantity_for_get_free = 0
    quantity_sum = 0

    # get dict free item and quantity 
    for line_item in line_items:
        quantity_sum += line_item.quantity
        if line_item.quantity >= required_quantity:
            eligible_quantity_multiplier = line_item.quantity // required_quantity
            free_item_quantity = eligible_quantity_multiplier * free_items_quantity

            free_items_dict[line_item.id] = free_item_quantity
            quantity_for_get_free += eligible_quantity_multiplier * required_quantity
    # get remaining quanity
    remaining_quantity = quantity_sum - quantity_for_get_free

    # add free item and quantity  from  remaining quantity
    if remaining_quantity >= required_quantity:
        free_in_remaining_quantity = remaining_quantity // required_quantity * free_items_quantity
        cheapest_item = min(line_items, key=lambda line_item: line_item.price)
        cheapest_price = 0

        # get cheapest item
        for line_item in line_items:
            if line_item.price < cheapest_price:
                cheapest_price = line_item.price
                cheapest_item = line_item

        if cheapest_item.id in free_items_dict:
            free_items_dict[cheapest_item.id] += free_in_remaining_quantity
        else:
            free_items_dict[cheapest_item.id] = free_in_remaining_quantity

    return free_items_dict


# def reverse_calculate_free_items(order, free_items_dict):
#     """
#     Calculate the original quantity of line items before adding free items
#     """
#     original_quantity_dict = {}
#     for line_item_id, free_item_quantity in free_items_dict.items():
#         line_item = order.line_items.get(id=line_item_id)
#         original_quantity = line_item.quantity - free_item_quantity
#         original_quantity_dict[line_item_id] = original_quantity

#     return original_quantity_dict
