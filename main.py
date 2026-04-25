import requests

print("Flood agent starting...")

# Example USGS gage (you can change this later)
url = "https://waterservices.usgs.gov/nwis/iv/?format=json&sites=08158000&parameterCd=00065"

response = requests.get(url)
data = response.json()

# Pull water level value
value = data["value"]["timeSeries"][0]["values"][0]["value"][0]["value"]

print(f"Current river level: {value}")

print("Flood agent complete.")
