from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


# Create your views here.
@login_required
def course_chat_room(request, course_id):
    try:
        course = request.user.courses_joined.get(id=course_id)
    except Exception:
        return HttpResponseForbidden()
    html = 'chat/room.html'
    data = {'course': course}
    return render(request, html, data)
