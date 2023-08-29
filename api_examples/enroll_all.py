# import requests


# username = 'test2'
# password = 'test123456'

# baseurl = 'http://127.0.0.1:8000/api/'
# # r = requests.get(baseurl)
# # courses = r.json()

# r = requests.get(f'{baseurl}courses/')
# courses = r.json()

# available_courses = ','.join([course['title'] for course in courses])
# print("---------------------------------------有效课程-------------------------------------------")
# print(available_courses)

# for course in courses:
#     course_id = course['id']
#     course_title = course['title']
#     r = requests.post(f'{baseurl}courses/{course_id}/enroll/', auth=(username, password))
#     if r.status_code == 200:
#         print(f'{username} 注册 {course_title} 课程成功')
import channels.layers
from asgiref.sync import async_to_sync

channel_layer = channels.layers.get_channel_layer()
async_to_sync(channel_layer.send)('test_channels', {'message': 'hello'})
async_to_sync(channel_layer.receive)('test_channels')
