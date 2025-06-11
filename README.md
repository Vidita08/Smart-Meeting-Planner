# Smart Meeting Planner

This project implements a tiny service to help plan meetings by suggesting common free time windows for users based on their busy schedules.

## Functional Requirements Implemented

* **POST /slots**: Accepts a JSON list of users with their busy intervals (HH:MM). Stores them in-memory.
* **GET /suggest?duration=30**: Returns the first three time-ranges (HH:MM–HH:MM) where all users are free for the given meeting length. The workday is assumed to be 09:00–18:00 IST.
* **GET /calendar/:userId**: Shows a specific user's busy slots plus anything newly "booked".
* **Optional Bonus: POST /book**: Allows booking a suggested slot for a user.

## Setup and Running

1.  **Clone the repository:**
    ```bash
    git clone [[https://github.com/Vidita08/smart-meeting-planner.git](https://github.com/Vidita08/Smart-Meeting-Planner.git)]
    cd smart-meeting-planner
    ```

2.  **Create virtual environment**
    ```bash
    python -m venv venv
    
3.  **Install Flask:**
    ```bash
    pip install Flask
    ```

4.  **Run the Flask application:**
    ```bash
    python app.py
    ```
    The application will typically run on `http://127.0.0.1:5000/`.

5.  **Open the front-end:**
    Navigate to `http://127.0.0.1:5000/` in your web browser.

## How to Use

1.  **Set Busy Slots:**
    * In the "1. Set Busy Slots" section, paste the example JSON payload (or your own) into the textarea.
    * Click "Update Busy Slots". You should see a success message.

    Example payload:
    ```json
    {
        "users": [
            { "id": 1, "busy": [["09:00","10:30"], ["13:00","14:00"]] },
            { "id": 2, "busy": [["11:00","12:00"], ["15:00","16:00"]] }
        ]
    }
    ```

2.  **Suggest Free Windows:**
    * In the "2. Suggest Free Windows" section, enter the desired meeting `Duration` in minutes (e.g., 30).
    * Click "Suggest Meeting Times". The first three common free windows will be displayed in the table below.

3.  **View User Calendar:**
    * In the "3. View User Calendar" section, enter a `User ID` (e.g., `1` or `2`).
    * Click "Show Calendar". The user's busy and booked slots will be listed.

4.  **Book a Slot (Optional Bonus):**
    * After getting suggestions, click the "Book (User 1)" button next to a suggested slot. This will simulate booking that slot for User 1.
    * You can then check User 1's calendar to see the newly booked slot.

## Reflection Questions

### 1. How exactly did you use AI while building this?

I used AI (specifically, a large language model like ChatGPT) primarily for:

* **Initial boilerplate and structure:** I started by asking for a basic Flask application structure with routes for `/slots` and `/suggest`, including a simple `index.html` template. This saved time setting up the basic framework.
* **Time calculations and manipulation:** I leveraged AI to get suggestions on how to convert HH:MM strings to a comparable format (e.g., minutes from midnight) for easier interval checking and conflict detection. Prompts like "Python function to convert HH:MM string to minutes from midnight" or "How to check if two time ranges overlap in Python" were helpful.
* **Front-end JavaScript for API calls:** I asked for basic JavaScript `fetch` API calls for POST and GET requests to interact with the Flask backend, including handling JSON parsing and displaying results in the HTML.
* **Refinement and debugging:** When I encountered minor errors or wanted to refine a logic (e.g., ensuring correct handling of edge cases for time overlaps or refining the workday boundaries), I would describe the problem to the AI and get suggestions for corrections or alternative approaches.

**Successes:**
* Rapid prototyping and setup.
* Quick generation of utility functions (time conversions, overlap checks).
* Learning about common pitfalls in API interactions and front-end handling of responses.

**Failures/Challenges:**
* Initially, AI might suggest overly complex solutions for time management or overlap detection. I had to guide it towards simpler, more direct approaches suitable for this "tiny service" requirement.
* Sometimes, AI might produce code that's syntactically correct but semantically slightly off (e.g., off-by-one errors in time calculations). Careful review and testing were always necessary.
* The "booking" functionality was a simple add-on. AI might propose more robust booking systems (e.g., with conflict resolution, database integration), which I had to explicitly tell it to simplify for an in-memory bonus feature.

### 2. If given two more days, what would you refactor or add first, and why?

If given two more days, I would prioritize the following:

1.  **Robust Error Handling and Input Validation:**
    * **Why:** Currently, the error handling is basic. For a more production-ready service, comprehensive validation of all incoming data (e.g., ensuring `duration` is a positive integer, busy slots are in correct HH:MM format and `start_time < end_time`, preventing duplicate user IDs in the input) is crucial. This would involve more specific error messages and HTTP status codes. This would make the API more reliable and user-friendly.

2.  **Improved Time Slot Management and Merging for Users:**
    * **Why:** Currently, `user_busy_slots` simply stores the raw intervals. If a user has overlapping busy slots (e.g., `["09:00", "10:00"]` and `["09:30", "10:30"]`), these are treated as separate intervals. For accurate free slot calculation, it's better to **merge** overlapping busy intervals for each user into a consolidated list of non-overlapping busy periods. This would simplify the `suggest_slots` logic and make it more efficient, especially for users with many busy entries. This also ensures that if a user has a booked slot that slightly overlaps with an existing busy slot, the merged time accurately reflects their unavailability.

3.  **Consideration for "Today" and Date Handling:**
    * **Why:** While the current requirement focuses on "today," a real-world meeting planner needs to consider specific dates. I would refactor the time handling to include dates (e.g., using `datetime.datetime` objects instead of just `datetime.time`). This would allow users to specify busy slots for future dates and for the suggestion algorithm to work across multiple days. This is a fundamental step towards making the planner truly useful beyond a single day.

These three areas would significantly improve the robustness, accuracy, and real-world applicability of the service, moving it from a "tiny service" proof-of-concept to a more reliable foundation.
