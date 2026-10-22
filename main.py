import time
from agents import (
    flowchart_agent,
    trip_plan_agent,
    budget_agent
)


# ============================================================
# USER INPUT
# ============================================================

print("=" * 50)
print("✈️ MULTI-AGENT TRIP PLANNER")
print("=" * 50)

destination = input("\nEnter destination: ")
start_location = input("Enter starting location: ")
transport = input("Enter transport type: ")
start_time = input("Enter trip start time: ")
end_time = input("Enter trip end time: ")

days = int(input("Enter number of days: "))
people = int(input("Enter number of people: "))
budget = float(input("Enter budget per person: ₹"))


# ============================================================
# AGENT 1 - FLOW
# ============================================================

print("\n" + "=" * 50)
print("🗺️ TRIP FLOW")
print("=" * 50)

flowchart = f"""
Start
↓
Travel from {start_location} to {destination}
↓
Sightseeing and activities
↓
Return journey
↓
End
"""

print(flowchart)


# ============================================================
# AGENT 2 - TRIP PLAN
# ============================================================

print("\n" + "=" * 50)
print("🗓️ TRIP PLAN")
print("=" * 50)

trip_plan = trip_plan_agent(
    destination,
    start_location,
    transport,
    start_time,
    end_time,
    days,
    people,
    flowchart
)

print(trip_plan)


# ============================================================
# AGENT 3 - BUDGET
# ============================================================

print("\n" + "=" * 50)
print("💰 BUDGET")
print("=" * 50)

budget_result = budget_agent(
    destination,
    start_location,
    transport,
    start_time,
    end_time,
    days,
    people,
    budget,
    trip_plan
)

print(budget_result)


# ============================================================
# END
# ============================================================

print("\n" + "=" * 50)
print("✈️ HAVE A GREAT TRIP!")
print("=" * 50)

