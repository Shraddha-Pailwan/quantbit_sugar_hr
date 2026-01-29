import frappe
from frappe.model.document import Document
from datetime import datetime
import calendar

class SeasonForPayroll(Document):
    @frappe.whitelist()
    def add_dates(self):
        if self.season_start_date and self.season_end_date:
            # convert strings to date objects
            start_date = datetime.strptime(self.season_start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(self.season_end_date, "%Y-%m-%d").date()

            if end_date < start_date:
                frappe.throw("End Date cannot be before Start Date")

            # clear old child rows
            self.set("season_for_payroll_details", [])

            current = start_date

            while current <= end_date:
                year = current.year
                month = current.month

                # get last day of this month
                last_day = calendar.monthrange(year, month)[1]
                month_end = datetime(year, month, last_day).date()

                # restrict within overall end_date
                if month_end > end_date:
                    month_end = end_date

                # calculate total days
                total_season_days = (month_end - current).days + 1

                # add child row
                child = self.append("season_for_payroll_details", {})
                child.season_start_date = current
                child.season_end_date = month_end
                child.month = current.strftime("%B")
                child.total_season_days = total_season_days
                child.year = year
                # move to first day of next month
                next_month = month + 1
                next_year = year
                if next_month == 13:
                    next_month = 1
                    next_year += 1
                current = datetime(next_year, next_month, 1).date()
