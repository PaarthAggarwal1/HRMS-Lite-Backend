from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import pymongo
import json
from bson import ObjectId


MongoClient = pymongo.MongoClient("mongodb+srv://hrms:hrms123@cluster0.jw8obie.mongodb.net/")

db = MongoClient["HRMS"]
Employees = db["Employees"]
Attendance = db["Attendance"]

@csrf_exempt
def employees_view(request):

    # ================= GET =================
    if request.method == "GET":
        emp_id = request.GET.get("id")

        if emp_id:
            employee = Employees.find_one({"_id": ObjectId(emp_id)})
            if not employee:
                return JsonResponse({"error": "Employee not found"}, status=404)

            employee["id"] = str(employee["_id"])
            del employee["_id"]
            return JsonResponse(employee)

        employees = list(Employees.find())
        for emp in employees:
            emp["id"] = str(emp["_id"])
            del emp["_id"]

        return JsonResponse(employees, safe=False)

    # ================= POST =================
    if request.method == "POST":
        body = json.loads(request.body)

        new_employee = {
            "fullName": body.get("fullName"),
            "email": body.get("email"),
            "department": body.get("department"),
            "role": body.get("role"),
        }

        result = Employees.insert_one(new_employee)

        return JsonResponse({
            "message": "Employee created",
            "id": str(result.inserted_id)
        })

    # ================= PUT =================
    if request.method == "PUT":
        body = json.loads(request.body)
        emp_id = body.get("id")

        if not emp_id:
            return JsonResponse({"error": "Employee ID required"}, status=400)

        update_data = {
            "fullName": body.get("fullName"),
            "email": body.get("email"),
            "department": body.get("department"),
            "role": body.get("role"),
        }

        update_data = {k: v for k, v in update_data.items() if v is not None}

        result = Employees.update_one(
            {"_id": ObjectId(emp_id)},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            return JsonResponse({"error": "Employee not found"}, status=404)

        return JsonResponse({"message": "Employee updated"})

    # ================= DELETE =================
    if request.method == "DELETE":
        body = json.loads(request.body)
        emp_id = body.get("id")

        if not emp_id:
            return JsonResponse({"error": "Employee ID required"}, status=400)

        # Delete the employee
        Employees.delete_one({"_id": ObjectId(emp_id)})
        
        # Delete all attendance records for this employee
        Attendance.delete_many({"employeeId": ObjectId(emp_id)})

        return JsonResponse({"message": "Employee and related attendance records deleted"})

    return JsonResponse({"error": "Invalid method"}, status=405)


@csrf_exempt
def attendance_view(request):

    # ================= GET =================
    if request.method == "GET":
        try:
            date = request.GET.get('date')
            if not date:
                return JsonResponse({"error": "Date parameter required"}, status=400)
            
            attendance_records = list(Attendance.find({"date": date}))
            
            # Convert ObjectId to string for JSON serialization
            for record in attendance_records:
                record['_id'] = str(record['_id'])
                record['employeeId'] = str(record['employeeId'])
            
            return JsonResponse(attendance_records, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    # ================= POST =================
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            employee_id = data.get('employeeId')
            date = data.get('date')
            status = data.get('status')
            
            if not employee_id or not date or not status:
                return JsonResponse({"error": "Missing required fields"}, status=400)
            
            # Update or insert attendance record
            result = Attendance.update_one(
                {"employeeId": ObjectId(employee_id), "date": date},
                {"$set": {"status": status, "date": date, "employeeId": ObjectId(employee_id)}},
                upsert=True
            )
            
            return JsonResponse({"message": "Attendance marked successfully"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    # ================= PUT =================
    if request.method == "PUT":
        try:
            data = json.loads(request.body)
            record_id = data.get('id')
            status = data.get('status')
            
            result = Attendance.update_one(
                {"_id": ObjectId(record_id)},
                {"$set": {"status": status}}
            )
            
            return JsonResponse({"message": "Attendance updated"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    # ================= DELETE =================
    if request.method == "DELETE":
        try:
            data = json.loads(request.body)
            record_id = data.get('id')
            
            Attendance.delete_one({"_id": ObjectId(record_id)})
            
            return JsonResponse({"message": "Attendance deleted"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid method"}, status=405)