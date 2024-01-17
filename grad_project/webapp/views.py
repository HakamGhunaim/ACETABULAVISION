from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.urls import reverse
from datetime import datetime
from ultralytics import YOLO
import math
import cv2
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .db.Database import register_user_in_db

def home_screen(request):
    return render(request,'newHomeScreen.html')

@csrf_exempt
def process_form(request):
    if request.method == 'POST':
        doctor_id = request.POST.get('drid')
        patient_id = request.POST.get('id')
        gender = request.POST.get('gender')
        right_m = request.POST.get('rindex')
        left_m = request.POST.get('lindex')
        date_of_birth = request.POST.get('date')
        # x_ray_image = request.FILES.get('image')
        x_ray_image = request.FILES['image']
        age = calculate_age(date_of_birth)


        # Perform validation
        if not all([patient_id, gender, date_of_birth, x_ray_image]):
            return JsonResponse({'error': 'All fields are required.'}, status=400)

        print(f"Patient ID: {patient_id}")
        print(f"Gender: {gender}")
        print(f"Date of Birth: {date_of_birth}")
        print(f"X-ray Image: {x_ray_image.name}")

        # Save X_ray_image into images directory
        # upload_folder = 'C:\\Users\\User\\Desktop\\hakam\\grad_project\\webapp\\images\\x_ray_image.jpeg'
        upload_folder = 'C:\\Users\\LENOVO\\Desktop\\hakam-main\\grad_project\\grad_project\\webapp\\images\\x_ray_image.jpeg'
        content = x_ray_image.read()
        content_file = ContentFile(content)
        saved_path = default_storage.save(upload_folder, content_file)
        angle_r,angle_l, ddh = predict(saved_path)
        os.remove(saved_path)


        left = angle_l
        right = angle_r
        ddh_res = ddh
        return redirect(reverse('result') + f'?drid={doctor_id}&id={patient_id}&gender={gender}&date={date_of_birth}&age={age}&leftm={left_m}&rightm={right_m}&&left={left}&right={right}&result={ddh_res}')
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@csrf_exempt
def result(request):
    doctor_id = request.GET.get('drid')
    patient_id = request.GET.get('id')
    gender = request.GET.get('gender')
    ddh_result = request.GET.get('result')
    date_of_birth = request.GET.get('date')
    age = request.GET.get('age')
    right_m = request.GET.get('rightm')
    left_m = request.GET.get('leftm')
    left =  request.GET.get('left')
    right = request.GET.get('right')

    doc={
        "doctor_id":doctor_id,
        "patient_id":patient_id,
        "Gender":gender,
        "Dob": date_of_birth,
        "age": age,
        "leftm": left_m,
        "left": left,
        "rightm": right_m,
        "right": right,
        "result":ddh_result
    }

    register_user_in_db("C:\\Users\\LENOVO\\Desktop\\hakam-main\\grad_project\\webapp\\db\\Results.sqlite3","Results", params=doc)

    return render(request, 'result.html', {'doctor_id': doctor_id,'patient_id': patient_id, 'gender': gender, 'date_of_birth': date_of_birth, 'age':age, 'rightm': right_m, 'leftm': left_m,'left':left, 'right':right, 'result':ddh_result })

def calculate_age(date_of_birth):
    dob = datetime.strptime(date_of_birth, '%Y-%m-%d')
    today = datetime.now()

    years = today.year - dob.year
    months = today.month - dob.month
    days = today.day - dob.day

    if days < 0:
        # Adjust months and days if the birth date is later in the month than today's date
        months -= 1
        days += 30  # Assuming a month is 30 days

    age_str = ""

    if years > 0:
        age_str += f"{years} {'year' if years == 1 else 'years'}"

    if months > 0:
        if age_str:
            age_str += ", "
        age_str += f"{months} {'month' if months == 1 else 'months'}"

    if days > 0:
        if age_str:
            age_str += ", "
        age_str += f"{days} {'day' if days == 1 else 'days'}"

    return age_str if age_str else "0 days"


def predict(img):

    model=YOLO("C:\\Users\\LENOVO\\Desktop\\hakam-main\\grad_project\\webapp\\best.pt")
    
    results = model(img)
    img = cv2.imread(img)
    if results and len(results[0].boxes) > 1:
            boxes = results[0].boxes.xyxy.cpu().numpy()  # Extract bounding boxes in xyxy format

            # Initialize variables to store left and right bounding boxes
            left_bbox = None
            right_bbox = None

            # Iterate through bounding boxes
            for i in range(2):  # Assuming there are exactly 2 bounding boxes
                bbox = list(map(int, boxes[i]))  # Convert map object to list

                # Your logic to distinguish between left and right bounding boxes
                if i == 0 or i == 1:
                    if right_bbox is None:
                        right_bbox = bbox
                    else:
                        left_bbox = bbox

            if right_bbox is None or left_bbox is None:
                print(f"No predictions for either left or right angle in X-Ray image")
                return 0

            # Your additional logic to determine left and right based on coordinates
            if right_bbox[2] > left_bbox[0]:
                right_bbox, left_bbox = left_bbox, right_bbox

            # Draw bounding boxes and lines
            x_min, y_min, x_max, y_max = right_bbox
            cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (255, 0, 0), 2)  # Blue color for right bbox
            cv2.line(img, (x_max, y_min), (x_min, y_max), (173, 216, 230), 2)  # Lighter blue diagonal line
            cv2.line(img, (x_min, y_max), (x_max, y_max), (173, 216, 230), 2)  # Lighter blue bottom line

            # Calculate and print the angle for the right bbox
            angle_right = calculate_angle_between_lines((x_max, y_min), (x_min, y_max),
                                                         (x_min, y_max), (x_max, y_max))
            print(f"Angle for right bbox in img: {angle_right} degrees")

            x_min, y_min, x_max, y_max = left_bbox
            cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (0, 0, 255), 2)  # Red color for left bbox
            cv2.line(img, (x_max, y_min), (x_min, y_max), (255, 192, 203), 2)  # Lighter red diagonal line
            cv2.line(img, (x_min, y_max), (x_max, y_max), (255, 192, 203), 2)  # Lighter red bottom line

            # Calculate and print the angle for the left bbox
            angle_left = calculate_angle_between_lines((x_max, y_min), (x_min, y_max),
                                                        (x_min, y_max), (x_max, y_max))
            print(f"Angle for left bbox in image: {angle_left} degrees")

            if angle_left > 30 and angle_right > 30: 
                ddh = "Bilateral DDH"
            elif angle_left > 30:
                ddh = "Left DDH"
            elif angle_right > 30:
                ddh = "Right DDH"
            else:
                ddh= "No DHH"
            

            
            return angle_right,angle_left,ddh
    else:
        print(f"Less than 2 detections in image")
        return 0



def calculate_angle_between_lines(line1_start, line1_end, line2_start, line2_end):
    m1 = (line1_end[1] - line1_start[1]) / (line1_end[0] - line1_start[0])
    m2 = (line2_end[1] - line2_start[1]) / (line2_end[0] - line2_start[0])
    angleR = math.atan(abs((m2 - m1) / (1 + m2 * m1)))
    angleD = int(round(math.degrees(angleR)))
    return angleD

