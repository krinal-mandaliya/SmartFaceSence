from django.db.models.functions import TruncDate, TruncMonth, TruncYear
from django.db.models import Count
from datetime import datetime
import uuid
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import *
import cv2
import os
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse
from django.conf import settings
import face_recognition as fr
from .models import *
import logging

# Create your views here.
def homepage(request):
    return render(request, "home.html")

def signup(request):
    if request.method == 'POST':
        form = Signup_form(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email_admin']
            
            if User.objects.filter(email=email).exists():
                form.add_error('email_admin', 'This email address is already in use.')
            else:
                # Hash the password before saving it
                password = form.cleaned_data['password']
                hashed_password = make_password(password)
                form.cleaned_data['password'] = hashed_password

                form.save()
                return redirect('login') 
    else:
        form = Signup_form()
    return render(request, 'signup.html', {'form': form})

def login(request):
    if request.method == 'POST':
        email = request.POST.get('loginemail', '')
        password = request.POST.get('loginpassword', '').strip()

        try:
            user = Signup.objects.get(email_admin=email)
            if password == user.password:
                # Authentication successful
                context = {
                    'name_head': user.name_head,
                    'name_office': user.name_office,
                }

                # Save the context in the session
                request.session['user_context'] = context

                return render(request, 'index.html', context)
            else:
                messages.error(request, 'Incorrect password. Please try again.')

        except Signup.DoesNotExist:
            messages.error(request, 'Email not found. Please try again.')

    return render(request, 'login.html') 

def index(request, name=None):
    user_context = request.session.get('user_context', {})

    return render(request, "index.html", user_context)

def upload_img(request):
    if request.method == 'POST':
        form = Upload_imgForm(request.POST, request.FILES)
        if form.is_valid():
            image = request.FILES['image']
            uploaded_image = fr.load_image_file(image)

            # Perform face encodings for the image
            face_encodings = fr.face_encodings(uploaded_image)

            if len(face_encodings) > 0:
                # Take the first encoding from the list
                uploaded_encoding = face_encodings[0]
                instance = form.save(commit=False)
                instance.face_encoding = uploaded_encoding  # Save the face encoding to the model
                instance.save()
                return redirect('upload')  # Corrected redirect statement
            else:
                messages.error(request, "No faces detected in the uploaded image. Please try again.")
                return redirect('index')
    else:
        form = Upload_imgForm()
    return redirect('index')

def upload(request):
    if request.method == 'POST':
        return redirect('upload')

    last_uploaded_image_table1 = Image.objects.last()
    matching_people, matching_visitors = compare1(request)

    # Calculate age for each matching person or visitor
    for matching_person in matching_people:
        dob = matching_person.dob if hasattr(matching_person, 'dob') else None
        if dob:
            age = calculate_age(dob)
            matching_person.age = age

    context = {
        'last_image': last_uploaded_image_table1,
        'matching_people': matching_people,
        'matching_visitors': matching_visitors,
    }

    return render(request, 'output2.html', context)

def compare1(request):
    last_uploaded_image_table = Image.objects.last()

    if not last_uploaded_image_table:
        messages.error(request, "No uploaded image found.")
        return [], []

    image_path = last_uploaded_image_table.image.path
    face_image = fr.load_image_file(image_path)
    uploaded_encoding = fr.face_encodings(face_image)

    if not uploaded_encoding:
        messages.error(request, "No face found in the uploaded image.")
        return [], []

    uploaded_encoding = uploaded_encoding[0]

    person_table = Person.objects.all()
    visitor_table = Visitor.objects.all()
    matching_people = []

    for person_obj in person_table:
        face_image_path = person_obj.face_image.path
        face_image = fr.load_image_file(face_image_path)
        face_encoding = fr.face_encodings(face_image)

        if face_encoding:
            result = fr.compare_faces([uploaded_encoding], face_encoding[0])

            if True in result:
                matching_people.append(person_obj)

    matching_visitors = []

    for visitor_obj in visitor_table:
        visitor_image_path = visitor_obj.visitor_image.path
        visitor_image = fr.load_image_file(visitor_image_path)
        visitor_encoding = fr.face_encodings(visitor_image)

        if visitor_encoding:
            result = fr.compare_faces([uploaded_encoding], visitor_encoding[0])

            if True in result:
                matching_visitors.append(visitor_obj)

    if not matching_people and not matching_visitors:
        messages.error(request, "Face not matched. Details not found.")

    return matching_people, matching_visitors

def calculate_age(dob):
    today = datetime.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age

def scan(request):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)  # Use camera index 0 (default camera)

    while True:
        ret, frame = cap.read()

        # Convert the frame to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the grayscale frame
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))

        # If faces are detected, save the first detected face as an image
        if len(faces) > 0:
            (x, y, w, h) = faces[0]  # Get the coordinates of the first detected face

            # Crop the detected face region
            face_roi = frame[y:y + h, x:x + w]

            # Generate a unique image name based on the current timestamp
            image_name = f'detected_face_{timezone.now().strftime("%Y%m%d%H%M%S")}.jpg'

            # Save the detected face as an image
            image_path = os.path.join(settings.MEDIA_ROOT, 'captured_faces', image_name)
            cv2.imwrite(image_path, face_roi)

            # Save the image to the database
            captured_image = Image.objects.create(scan_image=image_path)
            captured_image.save()

            cap.release()
            cv2.destroyAllWindows()

            # Redirect to the 'output' view after capturing and saving the image
            return redirect('output')

    # If no face is detected, release resources and show an appropriate message
    cap.release()
    cv2.destroyAllWindows()

    return HttpResponse("No face detected.")

def output(request):
    if request.method == 'POST':
        return redirect('output')

    last_uploaded_image_table = Image.objects.last()

    matching_people = compare(request, model=Person, image_field='face_image')
    matching_visitors = compare(request, model=Visitor, image_field='visitor_image')

    # Calculate age for each matching person
    for person_obj in matching_people:
        dob = person_obj.dob  # Date of Birth from the database

        if dob:
            # Calculate age based on Date of Birth
            age = calculate_age(dob)
            person_obj.age = age  # Add the age to the person_obj object

    context = {
        'last_image': last_uploaded_image_table,
        'matching_people': matching_people,
        'matching_visitors': matching_visitors,
    }

    return render(request, 'output.html', context)

def compare(request, model, image_field):
    last_uploaded_image_table = Image.objects.last()

    if not last_uploaded_image_table:
        messages.error(request, "No uploaded image found.")
        return []

    try:
        uploaded_image_path = last_uploaded_image_table.scan_image.path
        uploaded_image = fr.load_image_file(uploaded_image_path)
        uploaded_encoding = fr.face_encodings(uploaded_image)

        if not uploaded_encoding:
            messages.error(request, "No face found in the uploaded image.")
            return []

        uploaded_encoding = uploaded_encoding[0]

        objects = model.objects.all()
        matching_objects = []

        for obj in objects:
            try:
                obj_image_path = getattr(obj, image_field).path
                obj_image = fr.load_image_file(obj_image_path)
                face_encoding = fr.face_encodings(obj_image)

                if face_encoding:
                    result = fr.compare_faces([uploaded_encoding], face_encoding[0])

                    if True in result:
                        matching_objects.append(obj)

            except AttributeError:
                pass  # Handle the case where 'image_field' is not a field in the model

        if not matching_objects:
            messages.error(request, f"Face not matched for {model.__name__}. Details not found.")

        return matching_objects

    except AttributeError:
        messages.error(request, f"Image field 'scan_image' not found in the Image model.")
        return []

def admin1(request):
    data = Image.objects.all()  
    return render(request, 'admin.html', {'data': data})

def person(request):
    if request.method == 'POST':
        form = Person_imgForm(request.POST, request.FILES)
        if form.is_valid():
            # Check if the person with the same details already exists
            person_name = form.cleaned_data['person_name']
            dob = form.cleaned_data['dob']
            doj = form.cleaned_data['doj']

            if Person.objects.filter(person_name=person_name, dob=dob, doj=doj).exists():
                form.add_error(person_name, 'Details for this person already exist.')
            else:
                form.save()
                messages.success("Your details saved successfully")
                # return redirect('admin1')  
    else:
        form = Person_imgForm()

    return render(request, 'person.html', {'form': form})

def flat(request):
    if request.method == 'POST':
        form = FlatForm(request.POST)
        if form.is_valid():
            # Check if the flat is already allotted
            block_no = form.cleaned_data['block_no']
            flat_no = form.cleaned_data['flat_no']
            if Flat.objects.filter(block_no=block_no, flat_no=flat_no, status='allotted').exists():
                form.add_error(None, 'This flat is already allotted to someone.')
            else:
                # Save the form if the flat is not allotted
                form.save()
                messages.success(request,"Yout data saved successfully")

    else:
        form = FlatForm()

    return render(request, 'flat.html', {'form': form})


def visitor(request):
    if request.method == 'POST':
        form = VisitorForm(request.POST, request.FILES)
        if form.is_valid():
            # Check if the visitor's details already exist
            visitor_name = form.cleaned_data['visitor_name']
            mobile_no = form.cleaned_data['mobile_no']
            
            existing_visitors = Visitor.objects.filter(
                visitor_name=visitor_name,
                mobile_no=mobile_no
            )

            if existing_visitors.exists():
                messages.error(request, 'Visitor details already exist.')
            else:
                form.save()
                messages.success(request, 'Visitor details saved successfully.')

            return redirect('visitor')  # Assuming the URL pattern name is 'visitor'
        else:
            messages.error(request, 'Form is not valid. Please check your inputs.')
    else:
        form = VisitorForm()
    return render(request, 'visitor.html', {'form': form})

def search_images(request):
    if request.method == "POST":
        search_date = request.POST.get("search_date")
        search_choice = request.POST.get("search_choice")

        try:
            # Adjust the strptime format for dd-mm-yyyy
            search_date = datetime.strptime(search_date, "%d-%m-%Y").date()
        except ValueError:
            # Handle invalid date format here
            # You can return an error message or perform other actions as needed
            return HttpResponse("Invalid date format. Please use dd-mm-yyyy format.")

        if search_choice == "date":
            images = Image.objects.filter(timestamp__date=search_date)
        elif search_choice == "month":
            # Use TruncMonth after extracting only the date part
            images = Image.objects.annotate(month=TruncMonth('timestamp__date')).filter(month__month=search_date.month)
        elif search_choice == "year":
            # Use TruncYear after extracting only the date part
            images = Image.objects.annotate(year=TruncYear('timestamp__date')).filter(year__year=search_date.year)
    else:
        images = Image.objects.all()

    return render(request, "admin.html", {"data": images})

logger = logging.getLogger(__name__)

@login_required(login_url='/login/')

def send_forget_password_mail(request, token=None):
    try:
        if request.method == 'POST':
            return HttpResponse("Invalid method. This view only accepts POST requests.")

        email_admin = request.POST.get('email_admin')

        user_obj = Signup.objects.filter(email_admin__iexact=email_admin).first()

        if not user_obj:
            messages.error(request, 'No user found with this email ID.')
            return redirect('/ForgetPassword/')

        token = str(uuid.uuid4())

        profile_obj, created = Profile.objects.get_or_create(signup=user_obj)
        profile_obj.forget_password_token = token
        profile_obj.save()

        subject = 'Your forget password link'
        message = f'Hello, click on the link to reset your password http://127.0.0.1:8000/change_password/{token}/'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email_admin]
        send_mail(subject, message, email_from, recipient_list)

        messages.success(request, f'An email is sent to {email_admin}. Please check your Gmail')
        return True

    except Exception as e:
        logger.error(f"Error in send_forget_password_mail view: {e}")
        messages.error(request, 'Failed to send the forget password email.')
        return False
    
def ForgetPassword(request):
    try:
        if request.method == 'POST':
            email_admin = request.POST.get('email_admin')

            user_obj = Signup.objects.filter(email_admin__iexact=email_admin).first()

            if not user_obj:
                messages.error(request, 'No user found with this email ID.')
                return redirect('/ForgetPassword/')

            token = str(uuid.uuid4())

            profile_obj, created = Profile.objects.get_or_create(signup=user_obj)
            profile_obj.forget_password_token = token
            profile_obj.save()

            if send_forget_password_mail(request, token):  # Pass the request object
                messages.success(request, 'An email is sent. Please check your Gmail')
            else:
                messages.error(request, 'Failed to send the forget password email.')

            return redirect('/ForgetPassword/')

    except Exception as e:
        logger.error(f"Error in forget_password view: {e}")

    return render(request, 'ForgetPassword.html')

def ChangePassword(request, token):
    context = {}
    try:
        profile_obj = Profile.objects.filter(forget_password_token=token).first()

        if profile_obj:
            context = {'user_id': profile_obj.signup.id, 'token': token}

            if request.method == 'POST':
                new_password = request.POST.get('new_password')
                confirm_password = request.POST.get('reconfirm_password')
                user_id = request.POST.get('user_id')

                if not user_id:
                    messages.error(request, 'No user id found.')
                    return redirect(f'/ChangePassword/{token}/')

                if new_password != confirm_password:
                    messages.error(request, 'Passwords do not match.')
                    return redirect(f'/ChangePassword/{token}/')

                user_obj = Signup.objects.get(id=user_id)
                # Hash the password before saving
                user_obj.password = make_password(new_password)
                user_obj.save()
                messages.success(request, 'Password changed successfully. Please login.')
                return redirect('login')

    except Exception as e:
        logger.error(f"Error in change_password view: {e}")

    return render(request, 'ChangePassword.html', context)

def editProfile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'editProfile.html', {'form': form})