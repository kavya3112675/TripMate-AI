
import os
import json
import re
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from datetime import time

load_dotenv()

st.set_page_config(
    page_title="TripMate AI",
    page_icon="✈️",
    layout="wide"
)

st.title("✈️ TripMate AI")
st.write("Your smart AI-powered trip planner")
st.divider()

with st.form("trip_form"):
    col1, col2 = st.columns(2)

    with col1:
        start = st.text_input("Starting Location", "Erode")
        destination = st.text_input("Destination", "Ooty")
        days = st.number_input("Number of Days", 1, 15, 2)
        people = st.number_input("Number of Members", 1, 100, 4)

    with col2:
        budget = st.number_input(
            "Budget Per Person (₹)",
            min_value=100,
            value=3000,
            step=500
        )
        transport = st.selectbox(
            "Transport",
            ["Bus", "Train", "Car", "Bike", "Flight"]
        )
        start_time = st.time_input(
            "Trip Start Time", time(6, 0)
        )
        end_time = st.time_input(
            "Trip End Time", time(20, 0)
        )

    submitted = st.form_submit_button(
        "✨ Generate My Trip Plan",
        use_container_width=True
    )

if submitted:
    if not start.strip() or not destination.strip():
        st.error("Enter both starting location and destination.")

    elif start.strip().lower() == destination.strip().lower():
        st.error("Starting location and destination must differ.")

    elif start_time == end_time:
        st.error("Choose different start and end times.")

    elif not os.getenv("GROQ_API_KEY"):
        st.error("GEMINI_API_KEY missing. Check your .env file.")

    else:
        try:
            client = OpenAI(
                api_key=os.getenv("GROQ_API_KEY"),
                base_url="https://api.groq.com/openai/v1",
                timeout=45.0,
                max_retries=0
            )

            model = os.getenv("GROQ_MODEL")

            prompt = f"""
You are TripMate AI, a practical trip planning assistant.

Create a concise trip plan using these details:
Starting location: {start}
Destination: {destination}
Days: {days}
Members: {people}
Budget per person: INR {budget}
Transport: {transport}
Start time: {start_time}
End time: {end_time}

Return ONLY valid JSON in this structure:
{{
  "itinerary": [
    {{
      "day": "Day 1",
      "morning": "activity and approximate time",
      "afternoon": "activity and approximate time",
      "evening": "activity and approximate time"
    }}
  ],
  "costs": {{
    "transport": 0,
    "hotel": 0,
    "food": 0,
    "activities": 0,
    "other": 0
  }},
  "alternative_plan": "Affordable alternative itinerary",
  "alternative_cost_per_person": 0,
  "notes": "Important assumptions and price limitations"
}}

Rules:
- Create exactly {days} itinerary days.
- Use realistic, well-known places at the destination.
- Keep activities practical and timings approximate.
- Consider the starting location, transport and group size.
- Costs must be estimated INR PER PERSON for the entire trip.
- Include transport, accommodation, food, activities and other expenses.
- Do not invent verified live prices or claim live availability.
- If the given budget seems insufficient, suggest a cheaper plan.
- If it seems sufficient, alternative_plan can be empty.
- alternative_cost_per_person must be a realistic estimate.
- Keep the answer short. JSON only.
"""

            with st.spinner(
                "🤖 AI is creating your itinerary and budget..."
            ):
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=1800
                )

            raw = response.choices[0].message.content or ""
            match = re.search(r"\{.*\}", raw, re.DOTALL)

            if not match:
                raise ValueError("AI did not return valid JSON.")

            data = json.loads(match.group())

            costs = data["costs"]
            categories = [
                "transport", "hotel", "food",
                "activities", "other"
            ]

            total = sum(float(costs[k]) for k in categories)
            per_person_budget = float(budget)
            difference = total - per_person_budget

            st.success("Your trip plan is ready!")

            a, b, c = st.columns(3)
            a.metric("Members", int(people))
            b.metric("Days", int(days))
            c.metric("Estimated Cost / Person", f"₹{total:,.0f}")

            st.header("📅 Day-wise Itinerary")

            for day in data["itinerary"]:
                with st.expander(day["day"], expanded=True):
                    st.write("🌅 Morning:", day["morning"])
                    st.write("☀️ Afternoon:", day["afternoon"])
                    st.write("🌙 Evening:", day["evening"])

            st.header("💰 Budget Breakdown")

            for key in categories:
                st.write(
                    f"**{key.title()}:** ₹{float(costs[key]):,.0f}"
                )

            st.write(f"**Your budget:** ₹{per_person_budget:,.0f} per person")

            if difference <= 0:
                st.success(
                    f"BUDGET MATCH — estimated remaining "
                    f"₹{abs(difference):,.0f} per person."
                )
            else:
                st.warning(
                    f"BUDGET NOT MATCH — estimated extra "
                    f"₹{difference:,.0f} per person."
                )

                st.subheader("💡 Affordable Alternative")
                st.write(
                    data.get("alternative_plan")
                    or "Try cheaper transport, accommodation "
                       "and free attractions."
                )

                alt_cost = data.get("alternative_cost_per_person")
                if alt_cost is not None:
                    alt_cost = float(alt_cost)
                    st.write(
                        f"Alternative estimated cost: ₹{alt_cost:,.0f} "
                        "per person"
                    )

                    if alt_cost <= per_person_budget:
                        st.success("Alternative estimate fits your budget.")
                    else:
                        st.info(
                            "Even the alternative estimate exceeds "
                            "your budget. Consider increasing your budget."
                        )

            st.info(
                "These are AI-generated estimates, not verified live prices. "
                "Confirm fares, hotel rates, entry fees and opening hours "
                "before travelling. Budget match is based on the returned "
                "cost estimates."
            )

            st.caption("AI notes: " + str(data.get("notes", "")))

        except json.JSONDecodeError:
            st.error("AI response format was invalid. Please try again.")

        except Exception as e:
            message = str(e)

            if "503" in message or "UNAVAILABLE" in message:
                st.error(
                    "Gemini is busy right now. Please try again shortly."
                )
            elif "404" in message or "NOT_FOUND" in message:
                st.error(
                    "Model unavailable. Check GEMINI_MODEL in your .env file."
                )
            elif "401" in message or "403" in message:
                st.error(
                    "API authentication failed. Check your API key."
                )
            else:
                st.error("Unable to create the trip plan.")
                st.caption(message)
