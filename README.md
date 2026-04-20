# 🍔 FoodChatBot

A FastAPI-based food ordering chatbot backend that integrates with Dialogflow to process natural language food orders.

---

## 🎯 Project Purpose

This chatbot enables users to:

- 🛒 Place orders (add items to cart)
- ✏️ Modify orders (remove or update items)
- ✅ Complete orders (finalize and store in database)
- 📦 Track order status

---

## 🏗️ Architecture Overview

### 1. FastAPI Web Server
- Handles HTTP requests from Dialogflow webhook
- Processes user intents in real time
- Exposes REST API endpoints

---

### 2. Session Management

```python
# Stores active orders per user session
inprogress_orders = {
    "session_id_1": {"burger": 2, "pizza": 1},
    "session_id_2": {"pasta": 1}
}

# Clone repository
git clone https://github.com/your-username/FoodChatBot.git

# Navigate to project
cd FoodChatBot

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload
