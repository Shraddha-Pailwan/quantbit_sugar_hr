# # Copyright (c) 2026, Quantbit Technologies and contributors
# # For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate
from frappe import _
from collections import defaultdict

class OvertimeCalculation(Document):
    @frappe.whitelist()
    def get_overtime(self):
        self.set("overtime_details", [])
        self.set("overtime_hours_calculation", [])
        if not self.from_date or not self.to_date:
            frappe.throw(_("Please select From Date and To Date"))
        try:
            from_date = getdate(self.from_date)
            to_date = getdate(self.to_date)
            num_days = (to_date - from_date).days + 1
        except Exception as e:
            frappe.throw(_("Invalid Date: {0}").format(e))
        overtime_ids = [
            d.overtime_id for d in self.supevisor_details if d.check
        ]
        if not overtime_ids:
            frappe.throw(_("Please select at least one Overtime Entry"))
        data = frappe.db.sql("""
        SELECT
            oe.name AS overtime_id,
            oe.date,
            oe.supervisor,
            oe.supervisor_name,
            oed.employee_id,
            oed.employee_name,
            oed.overtime_hrs,
            emp.custom_overtime_percentage,
            epd.basic,
            epd.hra,
            epd.lta,
            epd.ca,
            epd.medical_allowance,
            epd.fda,
            epd.bonus,
            epd.da,
            epd.overtime_ot,
            epd.leave_encashment,
            epd.washing_allowance
        FROM `tabOvertime Entry` oe
        INNER JOIN `tabOvertime Entry Details` oed
            ON oe.name = oed.parent
        LEFT JOIN `tabEmployee` emp
            ON emp.name = oed.employee_id
        LEFT JOIN `tabEmployee Payroll Details` epd
            ON epd.parent = oed.employee_id
            AND epd.from_date = (
                SELECT from_date FROM `tabEmployee Payroll Details`
                WHERE parent = oed.employee_id
                ORDER BY
                    CASE
                        WHEN from_date <= %(from_date)s THEN 0
                        ELSE 1
                    END,
                    from_date DESC
                LIMIT 1
            )
        WHERE oe.name IN %(overtime_ids)s
    """, {
        "overtime_ids": tuple(overtime_ids),
        "from_date": from_date
    }, as_dict=True)
        if not data:
            frappe.msgprint(_("No overtime data found"))
            return
        for row in data:
            total_salary = self.get_total_salary(row)
            hourly_rate = (
                (total_salary / num_days) / 8
                if num_days > 0 else 0
            )
            final_rate = hourly_rate
            if row.custom_overtime_based_on == "Percentage Wise":
                percentage = row.custom_overtime_percentage or 0
                if percentage <= 0:
                    frappe.throw(
                        _("Overtime Percentage not set for Employee {0}")
                        .format(row.employee_name)
                    )
                final_rate = hourly_rate * (percentage / 100)
            elif row.custom_overtime_based_on == "Salary Rate Wise":
                final_rate = hourly_rate
            self.append("overtime_details", {
                "overtime_id": row.overtime_id,
                "supervisor_name": row.supervisor_name,
                "supervisor_id": row.supervisor,
                "employee_name": row.employee_name,
                "employee_id": row.employee_id,
                "date": row.date,
                "overtime_hrs": row.overtime_hrs,
                "overtime_rate": final_rate,
                "total_amount": final_rate * row.overtime_hrs
            })
        self.get_employee_sum()
    def get_total_salary(self, row):
        salary_fields = [
            "basic", "hra", "lta", "ca",
            "medical_allowance", "fda",
            "bonus", "da", "overtime_ot",
            "leave_encashment", "washing_allowance"
        ]
        return sum((row.get(f) or 0) for f in salary_fields)
    def get_employee_sum(self):
        summary = defaultdict(lambda: {
            "employee_name": "",
            "employee_id": "",
            "overtime_rate": 0,
            "overtime_hrs": 0,
            "total_amount": 0
        })
        for row in self.overtime_details:
            emp = summary[row.employee_id]
            emp["employee_name"] = row.employee_name
            emp["employee_id"] = row.employee_id
            emp["overtime_rate"] = row.overtime_rate
            emp["overtime_hrs"] += row.overtime_hrs
            emp["total_amount"] += row.total_amount
        for emp in summary.values():
            self.append("overtime_hours_calculation", {
                "employee_name": emp["employee_name"],
                "employee_id": emp["employee_id"],
                "overtime_rate": emp["overtime_rate"],
                "overtime_hrs": emp["overtime_hrs"],
                "total_overtime_amount": emp["total_amount"],
                "start_date": self.from_date,
                "end_date": self.to_date
            })
