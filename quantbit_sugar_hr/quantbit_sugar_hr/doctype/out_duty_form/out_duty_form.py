import frappe
from frappe.model.document import Document
from datetime import timedelta, datetime

class OutDutyForm(Document):
	@frappe.whitelist()
	def check_dates(self):
		if(self.to_date and self.from_date):
			if(self.to_date < self.from_date):
				frappe.throw("From Date can not greater than To Date (सुरुवातीची तारीख शेवटच्या तारखेपेक्षा मोठी असू शकत नाही)")
		self.calculate_total_days()
  
	@frappe.whitelist()
	def calculate_total_days(self):
		if self.from_date and self.to_date:
			from_date = datetime.strptime(str(self.from_date), "%Y-%m-%d").date()
			to_date = datetime.strptime(str(self.to_date), "%Y-%m-%d").date()
			self.total_days = ((to_date - from_date).days)+1
	
	def on_submit(self):    
		start_date = datetime.strptime(str(self.from_date), "%Y-%m-%d")
		end_date = datetime.strptime(str(self.to_date), "%Y-%m-%d")
		while start_date <= end_date:
			exist_doc = frappe.get_value(
				"Attendance",
				{
					"attendance_date": start_date.date(),
					"employee": self.labour_id
				},
				"name"
			)
			if exist_doc:

				frappe.db.set_value(
					"Attendance",
					exist_doc,
					{
						"status": self.status,  
						"half_day_status": self.status if self.status == "Half Day" else ""
					}
				)
			else:
				doc = frappe.new_doc("Attendance")
				doc.employee = self.labour_id
				doc.attendance_date = start_date.date()
				doc.company = self.company
				doc.docstatus = 1
				doc.status = "Present" if self.status != "Half Day" else "Half Day"
				doc.half_day_status = self.status if self.status == "Half Day" else ""
				doc.leave_type = "Casual Leave" if self.status == "Half Day" else ""
				doc.insert(ignore_permissions=True)
			start_date += timedelta(days=1)
