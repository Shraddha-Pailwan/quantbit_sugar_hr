import frappe
from erpnext.controllers.status_updater import validate_status
from hrms.hr.utils import validate_active_employee
import hrms.hr.doctype.attendance.attendance as attendance

def custom_validate(doc,method=None):
    validate_status(doc.status, [
        "Present",
        "Absent",
        "On Leave",
        "Half Day",
        "Work From Home",
        "On Out Duty",
        "On Retention"
    ])

    validate_active_employee(doc.employee)
    doc.validate_attendance_date()
    doc.validate_duplicate_record()
    doc.validate_overlapping_shift_attendance()
    doc.validate_employee_status()
    doc.check_leave_record()
attendance.Attendance.validate = custom_validate

@frappe.whitelist()
def create_employee(docname,date_of_joining):
    if frappe.db.exists("Employee", docname):
        frappe.throw(f"Employee with name {docname} already exists.({docname} नावाचा कर्मचारी आधीच अस्तित्वात आहे.)")
        
    supplier = frappe.get_doc("Supplier", docname)
    employee = frappe.new_doc("Employee")
    employee.name = docname
    employee.employee = docname
    employee.first_name = supplier.custom_first_name
    employee.middle_name = supplier.custom_middle_name
    employee.last_name = supplier.custom_last_name
    employee.gender = supplier.custom_gender
    employee.date_of_birth = supplier.custom_date_of_birth
    employee.date_of_joining = date_of_joining
    employee.custom_aadhar_card_number = supplier.custom_aadhaar_number
    employee.insert(ignore_permissions=True)
    frappe.db.set_value("Employee",employee.name,{
        "employee":docname,
        "name":docname
    })
    frappe.msgprint(msg=f"Employee Created Successfully: <a href='/app/employee/{docname}' target='_blank'>{docname}</a>",
        title="Success",
        indicator="green"
        )
