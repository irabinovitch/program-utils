#!/usr/bin/env python3
import random
import requests
from html.parser import HTMLParser
import xmltodict

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def process_day(day):
    url = 'https://www.socallinuxexpo.org/scale/21x/sign.xml?cache=' + str(random.choice(range(0,100)))
    schedule = requests.get(url).content

    talks_for_day = []

    doc = xmltodict.parse(schedule)
    for talk in doc['nodes']['node']:
        talk_day = strip_tags(talk['Day'])
        if talk['Topic'] != "BoFs" and talk_day == day:
            if talk['Speakers'] != "None" and talk['Speakers'] is not None:
                speakers = talk['Speakers']
            else:
                speakers = " "
            
            # Extract room, start time, and end time from the talk
            room = strip_tags(talk['Room'])
            start_time = strip_tags(talk['Time']).split('to')[0].strip().split(':')
            end_time = strip_tags(talk['Time']).split('to')[1].strip().split(':')

            talks_for_day.append({
                "Title": talk['Title'],
                "Speakers": speakers,
                "Room": room,
                "StartHour": start_time[0],
                "StartMinute": start_time[1],
                "EndHour": end_time[0],
                "EndMinute": end_time[1],
                "Topic": talk['Topic']
            })

    return talks_for_day


def generate_svg(talks, rooms):

    track_colors = {
        "Sponsored": "#fc8b1c",
        "Career Day": "#8a8c82",
        "Cloud Native": "#6b79b4",
        "Data on Kubernetes": "#ffffff",
        "DevOpsDay LA": "#8881cb",
        "Developer": "#5795ab",
        "Embedded": "#85768a",
        "FOSS @ HOME": "#8ada20",
        "General": "#b17c84",
        "Kernel & Low Level Systems": "#AD9134",
        "Keynote": "#8cadcb",
        "Kubernetes Community Day": "#6caf4d",
        "MySQL": "#4aa784",
        "Next Generation": "#66aebc",
        "NixCon": "#a7e5b4",
        "Observability": "#f7511d",
        "Open Government": "#6493b9",
        "Open Source AI and Applied Science": "#ba9f78",
        "PostgreSQL": "#f1cc0c",
        "Reproducible and Immutable Software": "#955e77",
        "Security": "#cd5465",
        "Systems & Infrastructure": "#4b5d6b",
        "Ubucon": "#774022",
        "UpSCALE": "#956140",
        "Workshops": "#3a3a3a"
    }
    track_colors.setdefault("#FFFFFF")

    cell_width = 84
    cell_height_per_15min = 18  # 18px per 15 mins
    start_of_day = 540  # 0 is 9am, 18 is 9:15am, 36 is 9:30am, etc.
    padding = 1
    rect_padding = 4  # Padding for the inner rect from left, top, and right

    last_talk_end_time = max(int(talk.get("EndHour", 0)) * 60 + int(talk.get("EndMinute", 0)) for talk in talks)
    total_height = ((last_talk_end_time - start_of_day) / 15) * cell_height_per_15min

    # Calculate the total width based on the number of rooms
    width = (len(rooms) + 1) * (cell_width + padding)
    if width > 714:
        width = width + 84 + len(rooms)
    svg_content = f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{width}" height="{total_height}">\n'

    current_time = start_of_day

    for room_index, room_name in enumerate(rooms):
        room_talks = [talk for talk in talks if talk["Room"] == room_name]
        x_coord = (room_index * (cell_width + padding)) + padding

        for index, talk in enumerate(room_talks):
            start_minutes = int(talk.get("StartHour", 0)) * 60 + int(talk.get("StartMinute", 0)) - start_of_day
            end_minutes = int(talk.get("EndHour", 0)) * 60 + int(talk.get("EndMinute", 0)) - start_of_day
            talk_duration = end_minutes - start_minutes

            y_coord = (start_minutes / 15) * cell_height_per_15min
            box_height = (talk_duration / 15) * cell_height_per_15min
            try:
                talk_color = track_colors[talk['Topic']]
            except:
                print("ERROR: ", talk['Title'], "is missing track information. Defaulting to white for track color.")
                talk_color=("#FFFFFF")
                

            # Outer <g> for the entire cell
            svg_content += f'<g id="g{index + 1}" transform="translate({x_coord}, {y_coord})">\n'

            # Outer <rect> for the color
            svg_content += f'<rect rx="1.27" x="0" y="0" width="{cell_width}" height="{box_height}" fill="{talk_color}" stroke="none" />\n'

            # Inner <rect> for the border
            svg_content += f'<rect rx="1.27" x="{rect_padding}" y="{rect_padding}" width="{cell_width - 2}" height="{box_height - 2}" fill="none" stroke="transparent" />\n'

            # Inner <g> with <flowRoot> for text
            svg_content += f'<g id="g1">'
            svg_content += f'<flowRoot  style="font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;font-size:8px;line-height:1.1;font-family:\'Ubuntu Condensed\';-inkscape-font-specification:\'Ubuntu Condensed,\';font-variant-ligatures:normal;font-variant-caps:normal;font-variant-numeric:normal;font-feature-settings:normal;text-align:center;letter-spacing:0px;word-spacing:0px;writing-mode:lr-tb;text-anchor:middle;fill:#000000;fill-opacity:1;stroke:none">'
            svg_content += f'<flowRegion><rect x="0" y="{rect_padding}" width="{cell_width}" height="{box_height}" /></flowRegion>'
            svg_content += f'<flowPara  style="font-style:normal;font-variant:normal;font-weight:500;font-stretch:condensed;font-size:8px;font-family:\'Fira Sans Condensed\';-inkscape-font-specification:\'Fira Sans Condensed,  Medium Condensed\'" font-size="10" text-anchor="middle">{strip_tags(talk.get("Speakers", ""))}</flowPara>'

            svg_content += f'<flowPara font-size="10" text-anchor="middle">{strip_tags(talk.get("Title", "").replace("&", "&amp;"))}</flowPara>'
            svg_content += f'</flowRoot>'
            svg_content += f'</g>'

            svg_content += f'</g>\n'

            current_time += talk_duration

    svg_content += '</svg>'
    svg_content = svg_content.replace("&", "&amp;")

    with open("program.svg", "w") as svg_file:
        svg_file.write(svg_content)

    return svg_content

def main():
    day = input("Enter the day (e.g., Thursday, Friday, Saturday, Sunday): ")
    talks = process_day(day)

    # Get unique room names and sort alphabetically
    rooms = sorted(list(set([talk["Room"] for talk in talks])))

    # Let's generate SVG for one room (you can choose the room)
    room_to_generate = input(f"Enter the room to generate SVG (choose from {', '.join(rooms)}): ")
    
    # Filter talks for the selected room
    if room_to_generate != "all":
        selected_room_talks = [talk for talk in talks if talk["Room"] == room_to_generate]
        rooms = [room_to_generate]
        generate_svg(selected_room_talks, rooms)
    else:
        selected_room_talks = talks
        generate_svg(talks, rooms)

    # Debug printing
    print("Talks for the day:")
    for talk in selected_room_talks:
        print(f"Title: {talk['Title']}, Speakers: {talk['Speakers']}, Room: {talk['Room']}, "
              f"Start: {talk['StartHour']}:{talk['StartMinute']}, End: {talk['EndHour']}:{talk['EndMinute']}")    

if __name__ == "__main__":
    main()
