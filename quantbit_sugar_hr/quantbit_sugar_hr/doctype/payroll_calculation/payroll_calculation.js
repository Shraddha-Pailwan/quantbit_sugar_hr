// Copyright (c) 2025, Quantbit Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Payroll Calculation", {
	from_date(frm) {
		if (frm.doc.from_date) {
			let d = new Date(frm.doc.from_date);
			let year = d.getFullYear();
			let month = d.getMonth();
			let last_day = new Date(year, month + 1, 0);
			frm.set_value(
				"to_date",
				frappe.datetime.obj_to_str(last_day)
			);
		}
		if (frm.doc.from_date && frm.doc.season_for_payroll) {

			frm.call({
				doc: frm.doc,
				method: "get_on_season_dates",
				callback() {
					frm.refresh_field("payroll_dates");
				}
			});
		}
	},
	season_for_payroll(frm) {
		if (frm.doc.from_date && frm.doc.to_date) {
			frm.call({
				doc: frm.doc,
				method: "get_on_season_dates",
				callback() {
					frm.refresh_field("payroll_dates");
				}
			});
		}
	}
});
