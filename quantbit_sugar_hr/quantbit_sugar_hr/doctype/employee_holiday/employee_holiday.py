import frappe
from frappe.model.document import Document
from frappe.utils import getdate, add_days, date_diff, formatdate
from datetime import datetime

class EmployeeHoliday(Document):
	def before_submit(self):
		self.mark_attendance()

	@frappe.whitelist()
	def add_dates(self):
		self.set("holiday_date_details", [])
		if self.season_type == "On Season":
			from_date = getdate(self.from_date)
			to_date = getdate(self.to_date)
			if from_date > to_date:
				frappe.throw("From Date cannot be after To Date")
			total_days = date_diff(to_date, from_date) + 1
			for i in range(total_days):
				current_date = add_days(from_date, i)
				day_name = current_date.strftime("%A")
				self.append("holiday_date_details", {
					"date": current_date,
					"day": day_name
				})

	@frappe.whitelist()
	def add_staff(self):
		self.set("employee_holiday_details", [])
		if self.company and self.branch:
			employees = frappe.get_all(
				"Employee",
				filters={
					"company": self.company,
					"branch": self.branch,
					"status": "Active"
				},
				fields=["name", "employee_name", "date_of_joining"]
			)
			for employee in employees:
				self.append("employee_holiday_details", {
					"employee_id": employee.name,
					"employee_name": employee.employee_name,
					"joining_date": employee.date_of_joining
				})

	def mark_attendance(self):
		holiday_list = []
		from_date = getdate(self.from_date)
		to_date = getdate(self.to_date)
		settings = frappe.get_single("HR and Payroll Settings")
		public_holiday = settings.public_holiday_list
		off_days = settings.off_season_holiday_day
		if public_holiday:
			public_holidays = frappe.get_doc("Holiday List", public_holiday)
			for holiday in public_holidays.holidays:
				if holiday.holiday_date <= to_date and holiday.holiday_date >= from_date:
					holiday_list.append(
						formatdate(holiday.holiday_date, "yyyy-MM-dd")
					)
		if self.season_type == "On Season":
			for holiday_date in self.holiday_date_details:
				if holiday_date.check and holiday_date.date not in holiday_list:
					holiday_list.append(
						formatdate(holiday_date.date, "yyyy-MM-dd")
					)
		if self.season_type == "Off Season":
			total_days = date_diff(to_date, from_date) + 1
			for i in range(total_days):
				current_date = add_days(from_date, i)
				day_name = current_date.strftime("%A")
				if day_name == off_days:
					holiday_list.append(
						formatdate(current_date, "yyyy-MM-dd")
					)
		holiday_list = sorted(list(set(holiday_list)))
		for employee in self.employee_holiday_details:
			for holiday_date in holiday_list:
				if not holiday_date or not employee.joining_date:
					continue
				holiday_date = getdate(holiday_date)
				joining_date = getdate(employee.joining_date)
				if holiday_date < joining_date:
					continue
				attendance = frappe.db.exists(
					"Attendance",
					{
						"employee": employee.employee_id,
						"attendance_date": holiday_date,
						"docstatus": 1
					}
				)
				if not attendance:
					attendance_doc = frappe.new_doc("Attendance")
					attendance_doc.employee = employee.employee_id
					attendance_doc.employee_name = employee.employee_name
					attendance_doc.attendance_date = holiday_date
					attendance_doc.company = self.company
					attendance_doc.custom_holiday = 1
					attendance_doc.status = "Present"
					attendance_doc.insert(ignore_permissions=True)
					attendance_doc.submit()
