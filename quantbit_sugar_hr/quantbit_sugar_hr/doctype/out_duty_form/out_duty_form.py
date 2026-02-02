import frappe
from frappe.model.document import Document
from datetime import timedelta, datetime

class OutDutyForm(Document):
	@frappe.whitelist()
	def check_dates(self):
		if self.to_date and self.from_date:
			if self.to_date < self.from_date:
				frappe.throw(
					"From Date can not greater than To Date (सुरुवातीची तारीख शेवटच्या तारखेपेक्षा मोठी असू शकत नाही)"
				)
		self.calculate_total_days()

	@frappe.whitelist()
	def calculate_total_days(self):
		if self.from_date and self.to_date:
			from_date = datetime.strptime(str(self.from_date), "%Y-%m-%d").date()
			to_date = datetime.strptime(str(self.to_date), "%Y-%m-%d").date()
			self.total_days = ((to_date - from_date).days) + 1
	def on_submit(self):
		start_date = datetime.strptime(self.from_date, "%Y-%m-%d")
		end_date = datetime.strptime(self.to_date, "%Y-%m-%d")
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
						"leave_type": "Casual Leave" if self.status == "Half Day" else "",
						"half_day_status": self.status_for_other_half if self.status == "Half Day" else "",
						"custom_is_out_duty_half_day": 1 if self.status == "Half Day" else 0
					}
				)
				frappe.db.commit()
			else:
				doc = frappe.new_doc("Attendance")
				doc.employee = self.labour_id
				doc.status = self.status
				doc.attendance_date = start_date.date()
				doc.company = self.company
				doc.docstatus = 1
				doc.leave_type = "Casual Leave" if self.status == "Half Day" else ""
				doc.custom_is_out_duty_half_day = 1 if self.status == "Half Day" else 0
				doc.insert(ignore_permissions=True)
				if self.status == "Half Day":
					att_name = frappe.db.get_value(
						"Attendance",
						{
							"attendance_date": start_date.date(),
							"employee": self.labour_id
						},
						"name"
					)
					frappe.db.set_value(
						"Attendance",
						att_name,
						"half_day_status",
						self.status_for_other_half
					)
			start_date += timedelta(days=1)

	def on_cancel(self):
		if self.to_date:
			data = frappe.db.sql(
				"""
				SELECT name
				FROM `tabAttendance`
				WHERE employee = %(empid)s
				AND attendance_date BETWEEN %(from_date)s AND %(to_date)s
				AND docstatus = 1
				""",
				{
					"empid": self.labour_id,
					"from_date": self.from_date,
					"to_date": self.to_date
				},
				as_dict=1
			)
			if data:
				for row in data:
					frappe.db.set_value(
						"Attendance",
						row.name,
						"docstatus",
						2
					)
					frappe.delete_doc("Attendance", row.name)
