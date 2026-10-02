"""
views.py — HTTP request handlers for AttendanceChimp.

Each view corresponds to one URL endpoint.  Views receive an HTTP request,
interact with the database via models.py, and return an HTTP response.
"""

from django.shortcuts import render, redirect
from django.http import (HttpResponse, HttpResponseForbidden,
                         HttpResponseBadRequest, JsonResponse)
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from datetime import datetime
import zoneinfo
import json
import io

from .models import (InstructorProfile, StudentProfile, Course, Enrollment,
                     Lecture, QRCodeUpload, is_instructor, is_student)

CDT = zoneinfo.ZoneInfo("America/Chicago")


# ---------------------------------------------------------------------------
# HW2 — time, sum 
# ---------------------------------------------------------------------------

@csrf_exempt
def time_view(request):
    """Return the current Chicago time as HH:MM."""
    if request.method != "GET":
        return HttpResponse("Error: only GET is allowed", status=405)
    now = datetime.now().astimezone(CDT)
    return HttpResponse(now.strftime("%H:%M"))


@csrf_exempt
def sum_view(request):
    """Return the sum of query parameters n1 and n2."""
    if request.method != "GET":
        return HttpResponse("Error: only GET is allowed", status=405)
    try:
        n1 = float(request.GET['n1'])
        n2 = float(request.GET['n2'])
    except (KeyError, ValueError):
        return HttpResponse("Error: provide numeric n1 and n2", status=400)
    result = n1 + n2
    if result == int(result):
        return HttpResponse(str(int(result)))
    return HttpResponse(str(result))


# ---------------------------------------------------------------------------
# HW4  — index, user creation
# ---------------------------------------------------------------------------

def new(request):
    """Render the sign-up form (GET only)."""
    if request.method != "GET":
        return HttpResponse("Error: only GET is allowed", status=405)
    return render(request, 'app/new.html')

def index(request):
    """Render the home page (index.html)."""
    now = datetime.now().astimezone(CDT)
    context = {
        'current_time': now.strftime("%H:%M"),
        'user': request.user,
    }
    return render(request, 'app/index.html', context)

@csrf_exempt
def createUser(request):
    """Create a new student or instructor user (POST only)."""
    if request.method != "POST":
        return HttpResponse("Error: only POST is allowed", status=405)
    try:
        user_name = request.POST['user_name']
        password = request.POST['password']
        email = request.POST['email']
        is_student_flag = request.POST.get('is_student', '1')
    except KeyError:
        return HttpResponse("Error: missing required fields", status=400)

    if User.objects.filter(email=email).exists():
        return HttpResponse("Error: email already in use", status=400)
    if User.objects.filter(username=user_name).exists():
        return HttpResponse("Error: user name already in use", status=400)

    user = User.objects.create_user(username=user_name, password=password,
                                    email=email)
    if str(is_student_flag) in ('1', 'true', 'True', 'on'):
        StudentProfile.objects.create(user=user)
    else:
        InstructorProfile.objects.create(user=user)

    user = authenticate(username=user_name, password=password)
    if user is not None:
        login(request, user)
    return HttpResponse("User created successfully", status=200)

# ---------------------------------------------------------------------------
# HW5  — courses, lectures, QR uploads, dump
# ---------------------------------------------------------------------------

@csrf_exempt
def new_course(request):
    """Render the new-course form."""
    return render(request, 'app/new_course.html')


@csrf_exempt
def new_lecture(request):
    """Render the new-lecture form."""
    courses = Course.objects.all()
    return render(request, 'app/new_lecture.html', {'courses': courses})


@csrf_exempt
def new_qr_upload(request):
    """Render the QR upload form."""
    return render(request, 'app/new_qr_upload.html')


@csrf_exempt
def createCourse(request):
    """Create a new course (POST, instructor only)."""
    if request.method != "POST":
        return HttpResponse("Error: only POST is allowed", status=405)
    if not request.user.is_authenticated or not is_instructor(request.user):
        return HttpResponse("Unauthorized", status=401)
    try:
        name = request.POST['course-name']
        start_time = request.POST.get('start-time', '')
        end_time = request.POST.get('end-time', '')
    except KeyError:
        return HttpResponse("Error: missing course-name", status=400)

    from datetime import time as dt_time
    st = et = None
    try:
        if start_time:
            parts = start_time.split(':')
            st = dt_time(int(parts[0]), int(parts[1]))
        if end_time:
            parts = end_time.split(':')
            et = dt_time(int(parts[0]), int(parts[1]))
    except (ValueError, IndexError):
        pass

    course = Course.objects.create(
        name=name,
        instructor=request.user,
        start_time=st,
        end_time=et,
        day_mon=bool(request.POST.get('day-mon', '')),
        day_tue=bool(request.POST.get('day-tue', '')),
        day_wed=bool(request.POST.get('day-wed', '')),
        day_thu=bool(request.POST.get('day-thu', '')),
        day_fri=bool(request.POST.get('day-fri', '')),
    )
    return HttpResponse(f"Course {course.name} created", status=200)


@csrf_exempt
def createLecture(request):
    """Create a new lecture for a course (POST, instructor only)."""
    if request.method != "POST":
        return HttpResponse("Error: only POST is allowed", status=405)
    if not request.user.is_authenticated or not is_instructor(request.user):
        return HttpResponse("Unauthorized", status=401)

    course_name = request.POST.get('choice', '')
    qrdata = request.POST.get('qrdata', '')

    try:
        course = Course.objects.get(name=course_name)
    except Course.DoesNotExist:
        return HttpResponse("Error: course not found", status=400)

    kwargs = {'course': course}
    if qrdata:
        kwargs['qr_code_data'] = qrdata

    lecture = Lecture.objects.create(**kwargs)
    return HttpResponse(f"Lecture created for {course.name}", status=200)


@csrf_exempt
def createQRCodeUpload(request):
    """Upload a QR code image (POST, student only). """
    
    if request.method != "POST":
        return HttpResponse("Error: only POST is allowed", status=405)
    if not request.user.is_authenticated or not is_student(request.user):
        return HttpResponse("Unauthorized", status=401)

    image_file = request.FILES.get('imageUpload')
    if not image_file:
        return HttpResponse("Error: no image uploaded", status=400)

    decoded_data = ''
    
    #######
    # Here we will eventually decode the QR code, compare to 
    # the lecture code, and reject if they don't match. 
    #######
    
    QRCodeUpload.objects.create(
        student=request.user,
        decoded_data=decoded_data,
        is_valid=True,
        # lecture=matched_lecture, # In HW7 we will have a value for this. 
                                                    # In the mean time it will be NULL by default. 
  )
    return HttpResponse("Upload successful", status=200)

@csrf_exempt
def dumpUploads(request):
    """Return JSON list of all uploads (GET, instructor only)."""
    if not request.user.is_authenticated or not is_instructor(request.user):
        return HttpResponse("Unauthorized", status=401)
    uploads = QRCodeUpload.objects.all()
    data = [{'username': u.student.username,
             'upload_time': str(u.uploaded_at)} for u in uploads]
    return JsonResponse(data, safe=False)


