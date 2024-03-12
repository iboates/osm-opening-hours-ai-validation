import requests
import json


def _chatgpt_request(chatgpt_client, system_message, content):
    chat_completion = chatgpt_client.chat.completions.create(
        messages=[{"role": "system", "content":system_message},
                  {"role": "user", "content": content}],
        model="gpt-3.5-turbo"
    )
    return chat_completion.choices[0].message.content


def get_address_from_coords(latitude, longitude):
    # Nominatim API endpoint
    nominatim_endpoint = "https://nominatim.openstreetmap.org/reverse"

    # Parameters for the request
    params = {
        "format": "json",
        "lat": latitude,
        "lon": longitude,
        "zoom": 18,  # Adjust the zoom level as needed
    }

    # Making the request
    response = requests.get(nominatim_endpoint, params=params)

    # Checking if the request was successful
    if response.status_code == 200:
        data = response.json()
        return data

    return None


def parse_opening_hours_string(chatgpt_client, opening_hours_string):
    chatgpt_response = _chatgpt_request(chatgpt_client=chatgpt_client,
                                        system_message=open("data/system_message_with_wiki_DEBUG.txt").read(),
                                        content=opening_hours_string)

    try:
        parsed_opening_hours = json.loads(chatgpt_response)
        # opening_hours_gdf = gpd.GeoDataFrame(parsed_opening_hours, geometry="geom", crs=4326)
        # opening_hours_gdf.to_postgis("opening_hours", engine, if_exists="append")
    except:
        print(f"failed to parse JSON with request `{opening_hours_string}`")
        parsed_opening_hours = None

    return parsed_opening_hours


def look_up_opening_hours_by_address(chatgpt_client, content):
    chat_completion = chatgpt_client.chat.completions.create(
        messages=[{"role": "system", "content": open("src/system_messages/00_look_for_opening_hours_on_unknown_website_with_address.txt").read()},
                  {"role": "user", "content": content}],
        model="gpt-4"
    )
    try:
        opening_hours = json.loads(chat_completion.choices[0].message.content)
    except:
        opening_hours = None

    return opening_hours


def look_for_opening_hours_string_on_website(chatgpt_client, content):
    chat_completion = chatgpt_client.chat.completions.create(
        messages=[{"role": "system",
                   "content": open("src/system_messages/00_look_for_opening_hours_on_unknown_website_with_address.txt").read()},
                  {"role": "user", "content": content}],
        model="gpt-4-turbo-preview"
    )
    return chat_completion.choices[0].message.content