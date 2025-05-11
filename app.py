from flask import Flask, request, jsonify
from ai.qa import MedicalQABot
from ai.symptom_checker import SymptomChecker
from ai.drug_info import DrugInfoLookup
from ai.reminder import ReminderManager
from ai.order import OrderManager
from ai.user import UserManager
import json
import os
import random

app = Flask(__name__)

# Initialize AI modules
qa_bot = MedicalQABot()
symptom_checker = SymptomChecker()
drug_lookup = DrugInfoLookup()
reminder_manager = ReminderManager()
order_manager = OrderManager()
user_manager = UserManager()

# Load sample Q&A data
DATA_PATH = os.path.join('data', 'medquad.json')
if os.path.exists(DATA_PATH):
    with open(DATA_PATH, 'r') as f:
        qa_data = json.load(f)
else:
    qa_data = []

HEALTH_TIPS = [
    "Drink plenty of water every day.",
    "Exercise regularly for at least 30 minutes.",
    "Eat a balanced diet rich in fruits and vegetables.",
    "Get enough sleep every night.",
    "Wash your hands frequently to prevent illness."
]

@app.route('/')
def index():
    return jsonify({"message": "Welcome to AIforHelp Healthcare Assistant API!"})

@app.route('/qa', methods=['POST'])
def medical_qa():
    """Answer a medical question using context from the dataset."""
    data = request.json
    question = data.get('question')
    context = qa_data[0]['context'] if qa_data else "Medical information."
    if question and qa_data:
        answer = qa_bot.answer(question, context)
        return jsonify({'question': question, 'answer': answer, 'context': context})
    return jsonify({'error': 'No question provided or dataset missing.'}), 400

@app.route('/symptom-checker', methods=['POST'])
def check_symptoms():
    """Check symptoms and return possible conditions (stub)."""
    data = request.json
    symptoms = data.get('symptoms', [])
    result = symptom_checker.check(symptoms)
    return jsonify(result)

@app.route('/drug-info', methods=['GET'])
def drug_info():
    """Fetch drug information from OpenFDA."""
    drug_name = request.args.get('name')
    if not drug_name:
        return jsonify({'error': 'No drug name provided.'}), 400
    info = drug_lookup.search(drug_name)
    return jsonify(info)

@app.route('/set-reminder', methods=['POST'])
def set_reminder():
    """Set a medication reminder for a user."""
    data = request.json
    user = data.get('user')
    medicine = data.get('medicine')
    time = data.get('time')
    if not all([user, medicine, time]):
        return jsonify({'error': 'Missing user, medicine, or time.'}), 400
    result = reminder_manager.set_reminder(user, medicine, time)
    return jsonify(result)

@app.route('/get-reminders', methods=['GET'])
def get_reminders():
    """Get all reminders for a user."""
    user = request.args.get('user')
    if not user:
        return jsonify({'error': 'Missing user.'}), 400
    reminders = reminder_manager.get_reminders(user)
    return jsonify({'reminders': reminders})

@app.route('/order-medicine', methods=['POST'])
def order_medicine():
    """Place a new medicine order for a user."""
    data = request.json
    user = data.get('user')
    medicine = data.get('medicine')
    quantity = data.get('quantity')
    if not all([user, medicine, quantity]):
        return jsonify({'error': 'Missing user, medicine, or quantity.'}), 400
    result = order_manager.place_order(user, medicine, quantity)
    return jsonify(result)

@app.route('/get-orders', methods=['GET'])
def get_orders():
    """Get all orders for a user."""
    user = request.args.get('user')
    if not user:
        return jsonify({'error': 'Missing user.'}), 400
    orders = order_manager.get_orders(user)
    return jsonify({'orders': orders})

@app.route('/repeat-order', methods=['POST'])
def repeat_order():
    """Repeat a previous order by order_id."""
    data = request.json
    user = data.get('user')
    order_id = data.get('order_id')
    if not all([user, order_id]):
        return jsonify({'error': 'Missing user or order_id.'}), 400
    result = order_manager.repeat_order(user, order_id)
    return jsonify(result)

@app.route('/user', methods=['POST'])
def create_user():
    """Create a new user profile."""
    data = request.json
    username = data.get('username')
    info = data.get('info', {})
    if not username:
        return jsonify({'error': 'Missing username.'}), 400
    result = user_manager.create_user(username, info)
    return jsonify(result)

@app.route('/user', methods=['GET'])
def get_user():
    """Get a user profile by username."""
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'Missing username.'}), 400
    user = user_manager.get_user(username)
    if user:
        return jsonify({'user': user})
    return jsonify({'error': 'User not found.'}), 404

@app.route('/health-tip', methods=['GET'])
def health_tip():
    """Get a random daily health tip."""
    tip = random.choice(HEALTH_TIPS)
    return jsonify({'health_tip': tip})

if __name__ == '__main__':
    app.run(debug=True) 