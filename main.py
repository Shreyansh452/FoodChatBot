from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import db_helper
import generic_helper

app = FastAPI()

# Store in-progress orders per session
inprogress_orders = {}

@app.get("/")
def health_check():
    return {"status": "FastAPI is running"}

# ✅ Save to DB helper
def save_to_db(order: dict):
    next_order_id = db_helper.get_next_order_id()

    for food_item, quantity in order.items():
        result = db_helper.insert_order_item(food_item, quantity, next_order_id)
        if result == -1:
            return -1
    db_helper.insert_order_tracking(next_order_id, "in progress")
    return next_order_id

# ✅ Complete the order
def complete_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        fulfillment_text = "I'm having trouble finding your order. Can you please place it again?"
    else:
        order = inprogress_orders[session_id]
        order_id = save_to_db(order)

        if order_id == -1:
            fulfillment_text = (
                "Sorry, we couldn't place your order due to a backend error. "
                "Please try placing a new order."
            )
        else:
            order_total = db_helper.get_total_order_price(order_id)
            fulfillment_text = (
                f"Awesome! Your order has been placed. "
                f"Order ID: #{order_id}. Total amount is ₹{order_total}. "
                f"Please pay at the time of delivery."
            )
            del inprogress_orders[session_id]  # Clear session

    return JSONResponse(content={"fulfillmentText": fulfillment_text})

# ✅ Track order
def track_order(parameters: dict):
    order_id = int(parameters.get("order_id", 0))

    if not order_id:
        return JSONResponse(content={"fulfillmentText": "Missing order ID."})

    order_status = db_helper.get_order_status(order_id)

    if order_status:
        fulfillment_text = f"Order ID #{order_id} is currently: {order_status}."
    else:
        fulfillment_text = f"No order found with ID #{order_id}."

    return JSONResponse(content={"fulfillmentText": fulfillment_text})

# ✅ Add to order
def add_to_order(parameters: dict, session_id: str):
    food_items = parameters.get("food-item", [])
    quantities = parameters.get("number", [])

    if len(food_items) != len(quantities):
        fulfillment_text = "Sorry, I didn't understand. Please specify food items and quantities clearly."
    else:
        new_food_dict = dict(zip(food_items, quantities))
        if session_id in inprogress_orders:
            inprogress_orders[session_id].update(new_food_dict)
        else:
            inprogress_orders[session_id] = new_food_dict

        order_str = generic_helper.get_str_from_food_dict(inprogress_orders[session_id])
        fulfillment_text = f"So far you have: {order_str}. Do you need anything else?"

    return JSONResponse(content={"fulfillmentText": fulfillment_text})

# ✅ Remove from order
def remove_from_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        return JSONResponse(content={
            "fulfillmentText": "I'm having trouble finding your order. Can you place a new one?"
        })

    current_order = inprogress_orders[session_id]
    food_items = parameters.get("food-item", [])

    removed_items = []
    no_such_items = []

    for item in food_items:
        if item in current_order:
            del current_order[item]
            removed_items.append(item)
        else:
            no_such_items.append(item)

    fulfillment_text = ""

    if removed_items:
        fulfillment_text += f"Removed {', '.join(removed_items)} from your order. "

    if no_such_items:
        fulfillment_text += f"These items were not in your order: {', '.join(no_such_items)}. "

    if not current_order:
        fulfillment_text += "Your order is now empty."
    else:
        order_str = generic_helper.get_str_from_food_dict(current_order)
        fulfillment_text += f"Here's what's left: {order_str}"

    return JSONResponse(content={"fulfillmentText": fulfillment_text})


# ✅ Main Dialogflow webhook handler
@app.post("/")
async def handle_request(request: Request):
    try:
        payload = await request.json()
        print("Payload received:", payload)

        intent = payload.get('queryResult', {}).get('intent', {}).get('displayName')
        parameters = payload.get('queryResult', {}).get('parameters', {})
        output_contexts = payload.get('queryResult', {}).get('outputContexts', [])

        session_id = generic_helper.extract_session_id(output_contexts[0]["name"])

        intent_handler_dict = {
            'order.add - context: ongoing-order': add_to_order,
            'order.remove - context: ongoing-order': remove_from_order,
            'order.complete - context: ongoing-order': complete_order,
            'track.order - context: ongoing-tracking': track_order
        }

        intents_with_session = [
            'order.add - context: ongoing-order',
            'order.remove - context: ongoing-order',
            'order.complete - context: ongoing-order'
        ]

        if intent in intents_with_session:
            return intent_handler_dict[intent](parameters, session_id)
        else:
            return intent_handler_dict[intent](parameters)

    except Exception as e:
        print("🔥 Exception:", repr(e))
        return JSONResponse(
            content={"fulfillmentText": "Internal server error. Please try again later."},
            status_code=500
        )
