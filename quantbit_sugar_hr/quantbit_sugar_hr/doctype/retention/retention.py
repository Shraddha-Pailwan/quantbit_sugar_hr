# Copyright (c) 2025, Quantbit Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import timedelta, datetime

class Retention(Document):
	
	@frappe.whitelist()
	def check_dates(self):
		if(self.to_date and self.from_date):
			if(self.to_date < self.from_date):
				frappe.throw("From date can not greater than To date (सुरुवातीची तारीख शेवटच्या तारखेपेक्षा मोठी असू शकत नाही)")
		self.calculate_total_days()

	def on_submit(self):
		start_date = datetime.strptime(str(self.from_date), "%Y-%m-%d")  
		end_date = datetime.strptime(str(self.to_date), "%Y-%m-%d")   
		while start_date <= end_date:
			att_date = start_date.date()
			existing_att = frappe.get_value("Attendance", {
				"employee": self.employee,
				"attendance_date": att_date},
				"status"
			)
			if existing_att:
				if existing_att == "Absent":
					frappe.db.set_value("Attendance", {"employee": self.employee,"attendance_date": att_date, "status":"Absent"}, {
						"status": "Present"})
				else:
					frappe.throw(f"Attendance for Employee {self.employee} is already marked for date {att_date} ")
			else:
				attendance_doc = {
					"doctype": "Attendance",
					"employee": self.employee,
					"status": "Present",
					"attendance_date": att_date,
					"company": self.company,
					"docstatus": 1  
				}
				frappe.get_doc(attendance_doc).insert(ignore_permissions=True)
			start_date += timedelta(days=1)

	@frappe.whitelist()
	def calculate_total_days(self):
		if self.from_date and self.to_date:
			from_date = datetime.strptime(str(self.from_date), "%Y-%m-%d").date()
			to_date = datetime.strptime(str(self.to_date), "%Y-%m-%d").date()
			self.total_days = ((to_date - from_date).days)+1
   
	def on_cancel(self):
		if(self.to_date):
			data = frappe.db.sql("""
								select name from `tabAttendance` where employee = %(empid)s
									and attendance_date between %(from_date)s and %(to_date)s and docstatus=1
								""",{
								'empid': self.employee,'from_date': self.from_date,'to_date': self.to_date
							},  as_dict=1)	
			if data:
				for row in data:
					frappe.db.set_value('Attendance',row.name ,'docstatus',2)
					frappe.delete_doc('Attendance',row.name)


	


