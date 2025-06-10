from flask import Flask, request, jsonify, render_template
from datetime import datetime, timedelta

app = Flask(__name__)

# In-memory storage for user busy slots
# Format: {user_id: [["HH:MM", "HH:MM"], ...]}
user_busy_slots = {}
booked_slots = {} # {user_id: [["HH:MM", "HH:MM"], ...]} - Optional bonus

WORKDAY_START = datetime.strptime("09:00", "%H:%M").time()
WORKDAY_END = datetime.strptime("18:00", "%H:%M").time()

def time_to_minutes(time_obj):
    """Converts a datetime.time object to minutes from midnight."""
    return time_obj.hour * 60 + time_obj.minute

def minutes_to_time(minutes):
    """Converts minutes from midnight to a HH:MM string."""
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"

def parse_time_range(time_str):
    """Parses HH:MM string to datetime.time object."""
    return datetime.strptime(time_str, "%H:%M").time()

def is_overlapping(slot1_start_minutes, slot1_end_minutes, slot2_start_minutes, slot2_end_minutes):
    """Checks if two time slots overlap."""
    return not (slot1_end_minutes <= slot2_start_minutes or slot2_end_minutes <= slot1_start_minutes)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/slots', methods=['POST'])
def add_slots():
    data = request.get_json()
    if not data or 'users' not in data:
        return jsonify({"error": "Invalid input format. Expected JSON with 'users' key."}), 400

    for user_data in data['users']:
        user_id = str(user_data.get('id'))
        busy_intervals = user_data.get('busy', [])

        processed_intervals = []
        for start_str, end_str in busy_intervals:
            try:
                start_time = parse_time_range(start_str)
                end_time = parse_time_range(end_str)
                processed_intervals.append([start_time, end_time])
            except ValueError:
                return jsonify({"error": f"Invalid time format for user {user_id}: {start_str}-{end_str}. Use HH:MM."}), 400
        user_busy_slots[user_id] = processed_intervals
    return jsonify({"message": "Busy slots updated successfully."}), 200

@app.route('/suggest', methods=['GET'])
def suggest_slots():
    duration_str = request.args.get('duration')
    if not duration_str:
        return jsonify({"error": "Missing 'duration' parameter."}), 400
    try:
        duration_minutes = int(duration_str)
        if duration_minutes <= 0:
            return jsonify({"error": "Duration must be a positive integer."}), 400
    except ValueError:
        return jsonify({"error": "Invalid 'duration' format. Must be an integer."}), 400

    if not user_busy_slots:
        return jsonify({"message": "No users or busy slots defined yet. Add users via /slots first."}), 200

    # Convert workday start/end to minutes
    workday_start_minutes = time_to_minutes(WORKDAY_START)
    workday_end_minutes = time_to_minutes(WORKDAY_END)

    # Generate all possible meeting start times within the workday at 1-minute intervals
    possible_start_minutes = []
    for m in range(workday_start_minutes, workday_end_minutes - duration_minutes + 1):
        possible_start_minutes.append(m)

    free_slots = []

    for start_minutes in possible_start_minutes:
        end_minutes = start_minutes + duration_minutes
        is_free_for_all = True
        for user_id, busy_intervals in user_busy_slots.items():
            # Include booked slots for the user
            all_user_intervals = busy_intervals + booked_slots.get(user_id, [])

            for busy_start_time, busy_end_time in all_user_intervals:
                busy_start_minutes = time_to_minutes(busy_start_time)
                busy_end_minutes = time_to_minutes(busy_end_time)

                if is_overlapping(start_minutes, end_minutes, busy_start_minutes, busy_end_minutes):
                    is_free_for_all = False
                    break
            if not is_free_for_all:
                break
        
        if is_free_for_all:
            free_slots.append([minutes_to_time(start_minutes), minutes_to_time(end_minutes)])
            if len(free_slots) >= 3: # We only need the first three
                break
    
    return jsonify(free_slots), 200

@app.route('/calendar/<userId>', methods=['GET'])
def get_user_calendar(userId):
    user_id = str(userId)
    if user_id not in user_busy_slots:
        return jsonify({"error": f"User with ID {user_id} not found."}), 404
    
    busy = [[s.strftime("%H:%M"), e.strftime("%H:%M")] for s, e in user_busy_slots.get(user_id, [])]
    booked = [[s.strftime("%H:%M"), e.strftime("%H:%M")] for s, e in booked_slots.get(user_id, [])]

    return jsonify({
        "user_id": user_id,
        "busy_slots": busy,
        "booked_slots": booked
    }), 200

@app.route('/book', methods=['POST'])
def book_slot():
    data = request.get_json()
    user_id = str(data.get('user_id'))
    start_time_str = data.get('start_time')
    end_time_str = data.get('end_time')

    if not all([user_id, start_time_str, end_time_str]):
        return jsonify({"error": "Missing user_id, start_time, or end_time."}), 400

    try:
        start_time = parse_time_range(start_time_str)
        end_time = parse_time_range(end_time_str)
    except ValueError:
        return jsonify({"error": "Invalid time format. Use HH:MM."}), 400

    # Simple booking: just add to booked_slots. No conflict checking for this bonus.
    if user_id not in booked_slots:
        booked_slots[user_id] = []
    
    booked_slots[user_id].append([start_time, end_time])
    return jsonify({"message": f"Slot {start_time_str}-{end_time_str} booked for user {user_id}."}), 200


if __name__ == '__main__':
    app.run(debug=True)