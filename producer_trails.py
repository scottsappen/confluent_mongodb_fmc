import sys
import json
import random
from datetime import datetime
from confluent_kafka import Producer
from faker import Faker
import re
from openai import OpenAI
from dotenv import load_dotenv
import os
import configparser

# Load the .env file from the current directory
load_dotenv()

# Access variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")
OPENAI_ENCODING_FORMAT = os.getenv("OPENAI_ENCODING_FORMAT")
CC_TOPIC_NAME = os.getenv("CC_TOPIC_NAME")

genres = ["Enduro", "Downhill", "Single Track", "Road", "Uphill", "Cross Country", "Jumps", "Bike Park"]
difficulties = ["Green Circle (Beginner)", "Blue Square (Intermediate)", "Black Diamond (Expert)", "Double Black Diamond (Expert)", "Orange Oval (Freeride)", "Pro Line (Pro)"]
description_phrases = [
    "Winding forest paths enveloped by towering ancient trees",
    "Breathtaking mountain views from the highest peak",
    "Challenging uphill climbs testing endurance and strength",
    "Serene riverside trails with calming water sounds",
    "Rocky terrains that demand focus and skill",
    "Lush greenery flourishing after a spring rain",
    "Wildlife encounters with deer at dawn",
    "Natural springs offering refreshing breaks",
    "Spectacular sunrise spots for early risers",
    "Peaceful sunset rides under a vibrant sky",
    "Thrilling descents on steep, winding paths",
    "Muddy trails that test your balance and agility",
    "Medium sized jump trail that contains intermediate jumps",
    "Whistler-size jump trail with huge jumps for experts",
    "Hidden waterfalls providing a serene escape",
    "Birdwatching havens alive with chirping melodies",
    "Flower-covered meadows dazzling under the sun",
    "Ancient tree groves standing as nature's sentinels",
    "Crystal-clear lakes reflecting the surrounding beauty",
    "Vibrant autumn leaves painting the trails",
    "Snow-capped peaks offering a chilly adventure",
    "Desert landscapes with unique flora and fauna",
    "Technical single tracks that challenge every rider",
    "Majestic canyons carved by rivers and time",
    "Quiet woodland paths away from the hustle",
    "Open fields where the sky meets the earth",
    "Steep rock gardens requiring precision and control",
    "Fast-flowing creeks crossed by rustic wooden bridges",
    "High-altitude rides where the air is thin",
    "Dense forests with trails like a maze",
    "Wide valleys offering panoramic views",
    "Rugged coastlines with trails next to the sea",
    "Glistening morning dew on wildflowers beside the trail",
    "Adrenaline-fueled moments flying over daring jumps",
    "Twists and turns on muddy bends, splashing with each pedal",
    "Echoes of rushing waterfalls blending with the sounds of nature",
    "Majestic eagles soaring above, guardians of the mountain",
    "Sudden clearings that reveal breathtaking valley views",
    "Ancient ruins hidden among the foliage, whispering old tales",
    "Muddy patches where the earth clings, adding to the challenge",
    "Small jumps that surprise and delight along the forest path",
    "The scent of pine and earth mingling in the fresh air",
    "Mud-splattered smiles after conquering slippery slopes",
    "Galloping wildlife that briefly accompany the ride",
    "Misty mornings that cloak the trails in mystery",
    "Rustic cabins spotted in the distance, hinting at past adventures",
    "Thrilling jumps off natural ramps, landing on soft earth",
    "Sun-dappled trails through the canopy, playing light and shadow",
    "Muddy ruts that test tires and spirit alike",
    "The satisfying crunch of leaves under tire on autumn rides",
    "Gnarly roots that weave a complex dance floor for bikes",
    "Panoramic cliffside views that reward the arduous climb",
    "Jumping over streams that cross the path, uniting land and water",
    "Muddy splashes that leave a mark of adventure on the bike",
    "The serene silence of snow-covered trails in winter",
    "Exhilarating descents that make the heart race",
    "Navigating through foggy landscapes, emerging into clarity",
    "The camaraderie of riding with friends through uncharted paths",
    "Mud-caked tires after a day of exploration",
    "Daring jumps over gaps, feeling weightless in the air",
    "Golden hour rides that end with stunning sunsets",
    "Riding under a canopy of stars on clear night trails",
    "The challenge of steep, muddy inclines that demand determination",
    "Encounters with streams that cool the air and the spirit",
    "Spectacular views of distant storms, safe from the path",
    "The joy of finding unexpected wild berries along the route",
    "Riding through meadows filled with the sound of buzzing life",
    "The feeling of being completely immersed in nature's beauty",
    "Historic trails that hold the stories of those who rode before",
    "The thrill of jumps that end in soft, forgiving landings",
    "Navigating night rides with only the light from your bike",
    "Creek crossings where water and wheel meet",
    "The peaceful solitude of early morning rides",
    "Signs of changing seasons along the trail, from green to gold",
    "Unexpected wildlife sightings that take your breath away",
    "Mastering muddy switchbacks with skill and grace",
    "The exhilaration of reaching the top after a grueling climb",
    "Riding through the aftermath of a storm, discovering a transformed world",
    "The unity of rider and bike as they move as one",
    "Finding moments of zen in the rhythm of pedaling",
    "Challenging jumps that weave through the forest's natural architecture",
    "Muddy adventures that leave you eager for the next ride"
]
# North Carolina specific locations
nclocations = [
    "Asheville", "Brevard", "Hendersonville", "Zirconia",
    "Beech Mountain", "Wilson Creek", "Charlotte", "Bent Creek Experimental Forest",
    "Raleigh", "Boone", "DuPont State Recreational Forest", "Pisgah National Forest"
]

state_map = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
    "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri",
    "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
    "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
    "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming"
}

def create_fake_trail():
    faker = Faker()
    # Decide whether to force state to be North Carolina with a 25% chance
    if random.choices([True, False], weights=(25, 75), k=1)[0]:
        state = "North Carolina"
        city = random.choice(nclocations)
    else:
        fake_address = faker.address()
        match = re.search(r'(?P<city>.+?), (?P<state>\w+)\s+\d{5}', fake_address)
        if match:
            city = match.group('city')
            state = match.group('state')
            state = state_map.get(state.upper(), "North Carolina")
        else:
            state = "North Carolina"
            city = random.choice(nclocations)
    name = faker.word().capitalize() + (' ' + faker. word().capitalize() if random.choice([True, False]) else '')
    genre = random.sample(genres, random.randint(1, len(genres)))
    difficulty = random.choice(difficulties)
    location = f"{city}, {state}"
    description = random.choice(description_phrases) + ' of ' + difficulty + ' difficulty located near ' + location
    description_embedding = None
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.embeddings.create(
            model=OPENAI_MODEL,
            input=[f"text:{description}"],
            encoding_format=OPENAI_ENCODING_FORMAT
        )
        # Extract the embeddings correctly
        description_embedding = response.data[0].embedding
    except Exception as e:
        print(f"Error retrieving embeddings: {e}")

    return {
        "name": name,
        "genres": genre,
        "location": location,
        "difficulty": difficulty,
        "description": description,
        "description_embedding": description_embedding
    }
   
def produce(number_of_trails, producer_config):
    # creates a new producer instance
    producer = Producer(producer_config)

    messages = []
    for i in range(1, number_of_trails + 1):
        message = create_fake_trail()
        messages.append(message)

    for message in messages:
        value = json.dumps(message)
        producer.produce(CC_TOPIC_NAME, key=None, value=value, callback=acked)
        producer.poll(0)  # Adjust poll interval as needed
    producer.flush()

def acked(err, msg):
    """Delivery report handler called on successful or failed delivery of message."""
    if err is not None:
        print("Failed to deliver message: %s: %s" % (str(msg), str(err)))
    else:
        a = 'a'
        #print("Message produced: %s" % (str(msg)))

def load_config(file_path):
    config = configparser.ConfigParser()
    with open(file_path) as f:
        # ConfigParser requires section headers, so we fake one
        config.read_string("[default]\n" + f.read())
    return dict(config["default"])

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 producer_trails.py <number_of_trails>")
        sys.exit(1)

    number_of_trails = int(sys.argv[1])

    # Load the config file from the same directory as the script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "client.properties")
    producer_config = load_config(config_path)

    produce(number_of_trails, producer_config)

    print("Program finished, go check your topic!")

main()
