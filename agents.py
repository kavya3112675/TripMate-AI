import os
import time
from dotenv import load_dotenv
from openai import OpenAI

# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


# ============================================================
# COMMON FUNCTION
# ============================================================

import time

def call_agent(instruction, task):
    start = time.perf_counter()

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": instruction},
                {"role": "user", "content": task}
            ],
            max_tokens=800
        )

        return response.choices[0].message.content

    finally:
        elapsed = time.perf_counter() - start
        print(f"AI API response time: {elapsed:.2f} seconds")
# ============================================================
# AGENT 1 - TRIP FLOW
# ============================================================

def flowchart_agent(
    destination,
    start_location,
    transport,
    start_time,
    end_time,
    days
):

    task = f"""
Create a simple trip flow.

Starting location: {start_location}
Destination: {destination}
Transport: {transport}
Start time: {start_time}
End time: {end_time}
Number of days: {days}

Give only a simple flow using arrows.

Example:

Start
↓
Travel to destination
↓
Check-in
↓
Sightseeing
↓
Food
↓
Activities
↓
Return journey
↓
End

Do not give explanations.
"""

    return call_agent(
        "You are a simple travel flow agent.",
        task
    )


# ============================================================
# AGENT 2 - SIMPLE TRIP PLAN
# ============================================================

def trip_plan_agent(
    destination,
    start_location,
    transport,
    start_time,
    end_time,
    days,
    people,
    flowchart
):

    task = f"""
Create a SIMPLE day-wise trip plan.

Starting location: {start_location}
Destination: {destination}
Transport: {transport}
Start time: {start_time}
End time: {end_time}
Days: {days}
People: {people}

Trip flow:
{flowchart}

IMPORTANT:

- Keep the output short and neat.
- Use Day 1, Day 2, etc.
- For each day give Morning, Afternoon and Evening.
- Include approximate times.
- Use the given start time and end time.
- Include only important places and activities.
- Do not give detailed explanations.
- Do not repeat the input information.

Use this format:

Day 1
Morning (time) - activity
Afternoon (time) - activity
Evening (time) - activity

Day 2
Morning (time) - activity
Afternoon (time) - activity
Evening (time) - activity

Continue until Day {days}.
"""

    return call_agent(
        "You are a simple and practical trip planning agent.",
        task
    )


# ============================================================
# AGENT 3 - BUDGET
# ============================================================

def budget_agent(
    destination,
    start_location,
    transport,
    start_time,
    end_time,
    days,
    people,
    budget,
    trip_plan
):

    task = f"""
Estimate the trip cost using these details.

Starting location: {start_location}
Destination: {destination}
Transport: {transport}
Days: {days}
People: {people}
Budget per person: Rs.{budget}

Trip plan:
{trip_plan}

Return:
1. Transport cost per person
2. Hotel cost per person
3. Food cost per person
4. Activities cost per person
5. Other expenses per person
6. Total cost per person
7. Budget status
8. Affordable alternative if budget is insufficient

Keep the response concise.
Clearly label estimates. Do not claim prices are verified
unless reliable price data is available.
"""

    return call_agent(
        "You are a simple travel budget agent. Your job is to check the budget and provide an affordable alternative only when necessary.",
        task
    )