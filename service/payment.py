from order.models import LineItem


def calculate_free_items(order, items_dict={}):
    line_items = order.line_items.all()
    promotion = order.promotion
    required_quantity = promotion.required_quantity
    free_items_quantity = promotion.free_items_quantity
    line_items = order.line_items.all()
    line_items_dict = {}

    for line_item in order.line_items.all():
        line_items_dict[line_item.id] = line_item.quantity

    # Substract the quantities from items_dict and line_items_dict
    if items_dict:
        for line_item_id, quantity_to_subtract in items_dict.items():
            if line_item_id in line_items_dict:
                line_items_dict[line_item_id] -= quantity_to_subtract

    # Calculate the free items
    quantity_for_get_free = 0
    quantity_sum = 0
    free_items_dict = {}

    for line_item_id, quantity in line_items_dict.items():
        quantity_sum += quantity
        if quantity >= required_quantity:

            eligible_quantity_multiplier = quantity // required_quantity
            free_item_quantity = eligible_quantity_multiplier * free_items_quantity

            free_items_dict[line_item_id] = free_item_quantity
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



def check_refund_condition(order):
    """
    This function checks if an order is eligible for a refund.
    """
    payments = order.payments.all()
    for payment in payments :

        if payment.status == "paid" and order.status == "failed":
            return True

        # the order is canceled before it is shipped
        elif  payment.status == "paid" and order.status == "cancelled" and payment.method == "vnpay":
                return True
    return False


def calculate_total_refund_amount(items_dict):
    """
    This function cal total  refund amount .
    """
    total_quantity_amount = 0
    original_free_quantity = {}
    for line_item_id, quantity in items_dict.items():
        # Calculate the total refund amount for each line item
        item = LineItem.objects.get(pk=line_item_id)
        order = item.order
        original_free_quantity[item.pk] = item.free_quantity
        total_quantity_amount += item.price * item.quantity
    print(f"original_free_quantity : {original_free_quantity}")

    if item.free_quantity != 0:
        # dict current_free_quantity
        current_free_quantity = calculate_free_items(order, items_dict)
        print(f"current_free_quantity : {current_free_quantity}")

        for line_item_id, quantity in current_free_quantity.items():

            if line_item_id in original_free_quantity:

                # if current quantity < original quantity => total_quantity_amount - (changed_quantity * item.price)
                if quantity < original_free_quantity[line_item_id]:
                    print("has change")
                    changed_quantity = original_free_quantity[line_item_id] - quantity
                    item = LineItem.objects.get(pk=line_item_id)
                    total_quantity_amount -= changed_quantity * item.price

    return total_quantity_amount
