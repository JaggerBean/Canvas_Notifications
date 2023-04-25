import requests
import datetime
import telegram
import asyncio
import time
from datetime import datetime, timedelta


bot = telegram.Bot(token='6298584965:AAEb5m8KVUiM-VlG2BVpAZdhgxxrj5RIjdA')
async def send_msg(text):
    await bot.send_message(chat_id='6236203521', text=text)


current_semester = "Sp23"
# Set up the API endpoint and personal access token
base_url = "https://utexas.instructure.com/api/v1"
token = "1017~mkR7MteCD0YkTLbUBfcYEHh9TtO1HjJjrqZcnVRm2DmZHjRkQhtUjHeObZxTO98f"

# Set up the headers to include the access token
headers = {
    "Authorization": f"Bearer {token}"
}

# Set up the parameters to include only the relevant classes

# Make the API request to retrieve the upcoming classes
course_schedule = requests.get(f"{base_url}/courses?per_page=250", headers=headers)
# print(response)
# Parse the JSON response to extract the class_ information
classes = course_schedule.json()
# print(classes)
# for class_ in classes:
#     try:
#         print(f"{class_['name']} ")
#     except:
#         if ({class_['access_restricted_by_date']}):
#             continue


current_classes = []
current_ids = []
for class_ in classes:
    try:
        # Check if the course name contains the current semester
        if current_semester in class_['name']:
            print(f"{class_['name']} ")
            current_classes.append({'name': class_['name']})
            current_ids.append({'id': class_['id']})

    except:
        if ({class_['access_restricted_by_date']}):
            continue



print(current_classes)
print(current_ids)

assignments = []
for i, id in enumerate(current_ids):
    # Get assignments for the current class ID
    assignments_temp = requests.get(f"{base_url}/courses/{id['id']}/assignments?per_page=1000", headers=headers)
    assignments_json = assignments_temp.json()

    # Get the class name for the current class ID
    class_name = current_classes[i]['name']

    # Add the class name to each assignment dictionary and append it to the assignments list
    for assignment in assignments_json:
        assignment['class_name'] = class_name
        assignments.append(assignment)


future_assignments = []
for i, assignment in enumerate(assignments):
        try:
            due_date = assignment['due_at']
            if due_date != None:
                due_date_formatted = datetime.strptime(due_date, '%Y-%m-%dT%H:%M:%SZ')
                # print(due_date_formatted)
                if due_date_formatted > datetime.now():
                    future_assignments.append((assignment))
        except ValueError as e:
            print(f'Error: {e}')

# Calculate datetime for 8 days from now
now = datetime.utcnow()
due_cutoff = now + timedelta(days=8)

new_assignments = []
for assignment in future_assignments:
    due_date_str = assignment['due_at']
    if due_date_str is not None:
        due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M:%SZ')
        if due_date < due_cutoff:
            new_assignments.append({
                'class': assignment['class_name'],
                'title': assignment['name'],
                'href': assignment['html_url'],
                'due_at': assignment['due_at'],
                'points_possible': assignment['points_possible']
            })

message = ''
for assignment in new_assignments:
    due_date = datetime.strptime(assignment['due_at'], '%Y-%m-%dT%H:%M:%SZ')
    due_date -= timedelta(hours=5)  # subtract 5 hours
    due_date_str = due_date.strftime('%m/%d/%Y %I:%M %p')
    message += f"{assignment['class']} - {assignment['title']} - Due at: {due_date_str} - Points: {assignment['points_possible']}\n\n"

asyncio.run(send_msg(message))