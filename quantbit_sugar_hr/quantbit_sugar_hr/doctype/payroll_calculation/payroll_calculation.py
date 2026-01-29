# Copyright (c) 2026, Quantbit Technologies and contributors
# For license information, please see license.txt

from datetime import datetime
import frappe
from frappe.model.document import Document
from frappe.utils import rounded

class PayrollCalculation(Document):
	
	@frappe.whitelist()
	def get_on_season_dates(self):
		if not self.season_for_payroll:
			frappe.throw("Please select Season For Payroll first")
		if not self.from_date or not self.to_date:
			frappe.throw("Please select From Date and To Date")
		season = frappe.get_doc("Season For Payroll", self.season_for_payroll)
		from_date = frappe.utils.getdate(self.from_date)
		to_date = frappe.utils.getdate(self.to_date)
		self.set("payroll_dates", [])
		season_row = None
		for row in season.season_for_payroll_details:
			season_start = frappe.utils.getdate(row.season_start_date)
			season_end = frappe.utils.getdate(row.season_end_date)
			if not (to_date < season_start or from_date > season_end):
				season_row = row
				break
		if not season_row:
			row = self.append("payroll_dates", {})
			row.from_date = from_date
			row.to_date = to_date
			row.month = from_date.strftime("%B")
			row.year = from_date.year
			row.on_season = 0
			return
		season_start = frappe.utils.getdate(season_row.season_start_date)
		season_end = frappe.utils.getdate(season_row.season_end_date)
		if from_date < season_start:
			row = self.append("payroll_dates", {})
			row.from_date = from_date
			row.to_date = frappe.utils.add_days(season_start, -1)
			row.month = from_date.strftime("%B")
			row.year = from_date.year
			row.on_season = 0
		on_start = max(from_date, season_start)
		on_end = min(to_date, season_end)
		if on_start <= on_end:
			row = self.append("payroll_dates", {})
			row.from_date = on_start
			row.to_date = on_end
			row.month = on_start.strftime("%B")
			row.year = on_start.year
			row.on_season = 1
		if to_date > season_end:
			row = self.append("payroll_dates", {})
			off_start = frappe.utils.add_days(season_end, 1)
			row.from_date = off_start
			row.to_date = to_date
			row.month = off_start.strftime("%B")
			row.year = off_start.year
			row.on_season = 0
