from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router, Form

from company.models import Employee, Department
from company.schemas import EmployeeIn, DepartmentIn, EmployeeOut

router = Router()


@router.post('/employees')
def create_employee(request, payload: EmployeeIn = Form(...)):
    employee = Employee.objects.create(**payload.dict())
    return {'id': employee.id}


@router.get('/employees/{int:employee_id}', response=EmployeeOut)
def get_employee(request, employee_id: int):
    employee = get_object_or_404(Employee, id=employee_id)
    return employee


@router.get('/employees', response=List[EmployeeOut])
def list_employees(request):
    qs = Employee.objects.all()
    return qs


@router.put('/employees/{int:employee_id}')
def update_employee(request, employee_id: int, payload: EmployeeIn):
    employee = get_object_or_404(Employee, id=employee_id)
    for attr, value in payload.dict().items():
        setattr(employee, attr, value)
    employee.save()
    return {'success': True}


@router.delete('/employees/{int:employee_id}')
def delete_employee(request, employee_id: int):
    employee = get_object_or_404(Employee, id=employee_id)
    employee.delete()
    return {'success': True}


@router.post('/department')
def create_department(request, payload: DepartmentIn = Form(...)):
    department = Department.objects.create(**payload.dict())
    return {'id': department.id}