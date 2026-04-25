import requests
from datetime import datetime, timezone

# -----------------------------
# FLOOD AGENT CONFIGURATION
# -----------------------------

GAGES = [
    {
        "name": "Example USGS Gage",
        "site": "08158000",
        "action_stage_ft": 20.0,
        "flood_stage_ft": 24.0,
        "related_infrastructure": [
            "Low-water crossings",
            "Nearby roads",
            "Public access areas"
        ]
    }
]

NWS_STATE = "TX"

HEADERS = {
    "User-Agent": "flood-agent-learning-project"
}


# -----------------------------
# DATA PULLS
# -----------------------------

def get_gage_height(site):
    url = (
        "https://waterservices.usgs.gov/nwis/iv/"
        f"?format=json&sites={site}&parameterCd=00065"
    )

    response = requests.get(url, timeout=20)
    response.raise_for_status()
    data = response.json()

    value = data["value"]["timeSeries"][0]["values"][0]["value"][0]["value"]
    time = data["value"]["timeSeries"][0]["values"][0]["value"][0]["dateTime"]

    return float(value), time


def get_nws_flood_alerts(state):
    url = f"https://api.weather.gov/alerts/active?area={state}"

    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    data = response.json()

    flood_alerts = []

    for alert in data.get("features", []):
        event = alert["properties"].get("event", "")
        headline = alert["properties"].get("headline", "")

        if "Flood" in event or "Flood" in headline:
            flood_alerts.append(headline or event)

    return flood_alerts


# -----------------------------
# ANALYSIS
# -----------------------------

def classify_status(height, action_stage, flood_stage):
    if height >= flood_stage:
        return "RED — flood stage exceeded"
    elif height >= action_stage:
        return "YELLOW — action stage exceeded"
    else:
        return "GREEN — below action stage"


def build_update(gage_results, alerts):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    highest_status = "GREEN"

    for gage in gage_results:
        if gage["status"].startswith("RED"):
            highest_status = "RED"
            break
        elif gage["status"].startswith("YELLOW"):
            highest_status = "YELLOW"

    lines = []

    lines.append("FLOOD FIGHT LEADERSHIP UPDATE")
    lines.append(f"Generated: {now}")
    lines.append("")

    lines.append("BLUF:")
    if highest_status == "RED":
        lines.append("One or more monitored gages are at or above flood stage. Leadership attention is required.")
    elif highest_status == "YELLOW":
        lines.append("One or more monitored gages are above action stage. Conditions warrant increased monitoring.")
    else:
        lines.append("Monitored gages are currently below action stage. Continue routine monitoring.")
    lines.append("")

    lines.append("CURRENT CONDITIONS:")
    for gage in gage_results:
        lines.append(
            f"- {gage['name']}: {gage['height']} ft as of {gage['time']} "
            f"({gage['status']})"
        )
    lines.append("")

    lines.append("NWS FLOOD ALERTS:")
    if alerts:
        for alert in alerts[:5]:
            lines.append(f"- {alert}")
    else:
        lines.append("- No active NWS flood alerts found for configured area.")
    lines.append("")

    lines.append("IMPACTS / AT-RISK INFRASTRUCTURE:")
    for gage in gage_results:
        lines.append(f"- {gage['name']}:")
        for item in gage["related_infrastructure"]:
            lines.append(f"  - {item}")
    lines.append("")

    lines.append("DECISIONS NEEDED:")
    if highest_status == "RED":
        lines.append("- Determine whether to activate enhanced flood fight coordination.")
        lines.append("- Confirm reporting rhythm and leadership notification requirements.")
        lines.append("- Validate field resource posture and potential public safety impacts.")
    elif highest_status == "YELLOW":
        lines.append("- Decide whether to increase monitoring frequency.")
        lines.append("- Confirm readiness of response personnel and reporting channels.")
    else:
        lines.append("- No immediate leadership decision required.")
    lines.append("")

    lines.append("NEXT UPDATE:")
    lines.append("- Recommend next update in 6 hours or earlier if conditions change.")
    lines.append("")

    lines.append("DATA SOURCES:")
    lines.append("- USGS Water Services instantaneous values")
    lines.append("- National Weather Service active alerts")
    lines.append("")

    return "\n".join(lines)


# -----------------------------
# MAIN EXECUTION
# -----------------------------

def main():
    print("Flood agent starting...")

    gage_results = []

    for gage in GAGES:
        height, time = get_gage_height(gage["site"])

        status = classify_status(
            height,
            gage["action_stage_ft"],
            gage["flood_stage_ft"]
        )

        gage_results.append({
            "name": gage["name"],
            "height": height,
            "time": time,
            "status": status,
            "related_infrastructure": gage["related_infrastructure"]
        })

    alerts = get_nws_flood_alerts(NWS_STATE)

    update = build_update(gage_results, alerts)

    print("")
    print(update)
    print("")
    print("Flood agent complete.")


if __name__ == "__main__":
    main()
