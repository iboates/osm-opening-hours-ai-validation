import json
import warnings
import os

import geopandas as gpd
import sqlalchemy as sa
from tqdm import tqdm
import requests
from dotenv import load_dotenv

from openai import OpenAI

from src import *


def _noop():
    pass


def validate_opening_hours_with_chatgpt(limit):

    chatgpt_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), )

    engine = sa.create_engine("postgresql+psycopg2://o2p:o2p@127.0.0.1:5432/o2p")

    with open("data/fix_opening_hours_table.sql") as f:
        with engine.connect() as c:
            c.execute(sa.text(f.read()))
            c.commit()

    gdf = gpd.read_postgis(open("data/select_points_with_opening_hours.sql").read(), engine)

    i = 0
    for _, row in tqdm(gdf.iterrows(), total=len(gdf)):
    #for _, row in gdf.iterrows():

        # First check if we already have this one in the table, and if so, skip it
        with open("data/node_id_exists_in_fix_opening_hours_table.sql") as f:
            with engine.connect() as c:
                cursor = c.execute(sa.text(f.read()), parameters={"node_id": row["node_id"]})
        results = cursor.fetchone()
        if results is not None:
            continue

        #nominatum_response = get_address_from_coords(row["geom"].y, row["geom"].x)

        nominatim_object = {
            "lat": row["geom"].y,
            "lon": row["geom"].x,
            "address": {
                "country_code": "de",
                "state": "Baden-Württemberg"
            }
        }
        post_data = {
            "strings": [row["opening_hours"]],
            "nominatim_object": nominatim_object,
            "verbose": True
        }

        r = requests.post("http://localhost:8080/validate", json=post_data)
        validator_response = r.json()[0]
        if not validator_response["success"]:

            system_message = open("data/system_message_opening_hours_validate_and_propose_if_wrong.txt").read()
            content = json.dumps({
                      "opening_hours": row["opening_hours"],
                      "error": validator_response["error"],
                      "country_code": row["country_code"],
                      "state": row["state"]
                    })

            chat_completion = chatgpt_client.chat.completions.create(
                messages=[{"role": "system", "content": system_message},
                          {"role": "user", "content": content}],
                model="gpt-4-turbo-preview"
            )
            chatgpt_response = chat_completion.choices[0].message.content

            try:
                chatgpt_response = json.loads(chatgpt_response)
            except json.JSONDecodeError:
                # sometimes it returns it surrounded by 3 backticks like markdown
                try:
                    chatgpt_response = json.loads(chatgpt_response[3:-3])
                except:
                    print(f"\tfailed to parse ChatGPT response for node_id={row['node_id']}")
                    continue

            chatgpt_proposal_data = {
                "strings": [chatgpt_response["proposal"]],
                "nominatim_object": nominatim_object,
                "verbose": True
            }
            r = requests.post("http://localhost:8080/validate", json=chatgpt_proposal_data)
            validator_response_for_chatgpt_proposal = r.json()[0]

            postgis_ready_result = {
                "node_id": row["node_id"],
                "name": row["name"],
                "opening_hours": row["opening_hours"],
                "chatgpt_analysis": chatgpt_response["analysis"],
                "chatgpt_proposal": chatgpt_response["proposal"],
                "chatgpt_extra": chatgpt_response["extra"],
                "chatgpt_proposal_is_valid": validator_response_for_chatgpt_proposal["success"],
                "geom": row["geom"]
            }
            load_gdf = gpd.GeoDataFrame([postgis_ready_result], geometry="geom", crs=4326)
            load_gdf.to_postgis("fix_opening_hours", engine, if_exists="append")

            i += 1
            #print(i)
            _noop()



def search_internet_for_opening_hours(region, limit):

    SHOULD_DO = {
        "PARSE_STRING": False,
        "SEARCH_WEBSITE": False,
        "FIND_AND_SEARCH_WEBSITE_WITH_KNOWN_ADDRESS": False,
        "FIND_AND_SEARCH_WEBSITE_WITH_UNKNOWN_ADDRESS": True,
    }

    chatgpt_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), )

    engine = sa.create_engine("postgresql+psycopg2://o2p:o2p@127.0.0.1:5432/o2p")
    with open("data/opening_hours_table.sql") as f:
        with engine.connect() as c:
            c.execute(sa.text(f.read()))
            c.commit()
    with open("data/chatgpt_results_table.sql") as f:
        with engine.connect() as c:
            c.execute(sa.text(f.read()))
            c.commit()
    gdf = gpd.read_postgis(open("data/select_points.sql").read(), engine, params={"limit": LIMIT, "region": REGION})

    postgis_ready_results = []
    for _, row in tqdm(gdf.iterrows(), total=len(gdf)):


        # First check if we already have this one in the table, and if so, skip it
        with open("data/node_id_exists_in_chatgpt_outputs_table.sql") as f:
            with engine.connect() as c:
                cursor = c.execute(sa.text(f.read()), parameters={"node_id": row["node_id"]})
        results = cursor.fetchone()
        if results is not None:
            continue
        # if row["opening_hours"] is not None and SHOULD_DO["PARSE_STRING"]:
        #     response = parse_opening_hours_string(chatgpt_client, row["opening_hours"])
        # elif row["website"] is not None and SHOULD_DO["SEARCH_WEBSITE"]:
        #     response = look_for_opening_hours_string_on_website(chatgpt_client, row["website"])
        # elif row["street"] is not None and SHOULD_DO["FIND_AND_SEARCH_WEBSITE_WITH_KNOWN_ADDRESS"]:
        #     content = f"Name: {row['name']}\n Address: {row['street']} {row['number']}"
        #     response = look_up_opening_hours_by_address(chatgpt_client, content)
        # elif SHOULD_DO["FIND_AND_SEARCH_WEBSITE_WITH_UNKNOWN_ADDRESS"]:
        address = get_address_from_coords(row.geom.y, row.geom.x)
        content = f"Name: {row['name']}\n Address: {address}"
        response = look_for_opening_hours_string_on_website(chatgpt_client, content)

        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            # sometimes chatgpt returns the response as a markdown-formatted codeblock even when ordered not to
            if response.startswith("```") and response.endswith("```"):
                try:
                    response = json.loads(response[3:-3])
                except json.JSONDecodeError:
                    result = {"response": response}

        # Prep results for loading into PostGIS
        try:
            postgis_ready_result = {**row}
            if len(result.keys()) == 1 and "response" in result:
                # ChatGPT screwed up
                postgis_ready_result["chatgpt_response"] = result["response"]
            else:
                for k1 in result:
                    if k1 != "response":
                        for k2 in result[k1]:
                            if k1 == "website" and k2 == "url" and result[k1][k2] is not None:
                                # handle cases when more than one website is returned
                                postgis_ready_result[f"chatgpt_{k1}_{k2}"] = ";".join(result.get("website", {}).get("url", []))
                            else:
                                postgis_ready_result[f"chatgpt_{k1}_{k2}"] = result[k1][k2]
            postgis_ready_results.append(postgis_ready_result)

            # Test if the URL works
            if "chatgpt_website_url" in postgis_ready_result and postgis_ready_result["chatgpt_website_url"] is not None:
                for url in postgis_ready_result["chatgpt_website_url"].split(";"):
                    try:
                        requests.get(url)
                        postgis_ready_result["chatgpt_at_least_one_url_works"] = True
                    except requests.exceptions.ConnectionError:
                        postgis_ready_result["chatgpt_at_least_one_url_works"] = False
                    except requests.exceptions.MissingSchema:
                        postgis_ready_result["chatgpt_at_least_one_url_works"] = False

            if "chatgpt_response" not in postgis_ready_result:
                postgis_ready_result["chatgpt_response"] = None
            load_gdf = gpd.GeoDataFrame([postgis_ready_result], geometry="geom", crs=4326)
            load_gdf.to_postgis("chatgpt_results", engine, if_exists="append")

        except Exception as e:
            warning_msg = f"An exception occurred while processing {row['node_id']} (Name: `{row['name']}`): {type(e).__name__}: {e}"
            warnings.warn(warning_msg)


        _noop()  # breakpoint inside loop
    _noop()  # breakpoint after loop


if __name__ == "__main__":

    load_dotenv()

    # REGION = "new_york"
    # LIMIT = 1000
    # search_internet_for_opening_hours(REGION, LIMIT)

    LIMIT = 10
    validate_opening_hours_with_chatgpt(LIMIT)
