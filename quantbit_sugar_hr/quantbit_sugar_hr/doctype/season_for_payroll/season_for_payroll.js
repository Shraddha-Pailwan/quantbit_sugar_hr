// Copyright (c) 2025, Quantbit Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

function getMonthDates(input_date) {

  const selected_date = new Date(input_date);
  const year = selected_date.getFullYear();
  const month_name = selected_date.toLocaleString('default', { month: 'long' });

  return {
    year: year,
    month: month_name
  };
}

frappe.ui.form.on("Season For Payroll", {
  refresh(frm) {

  },
  season_start_date(frm, cdt, cdn) {
    frm.call({
      doc: frm.doc,
      method: "add_dates"
    })
  },
  season_end_date(frm, cdt, cdn) {
    frm.call({
      doc: frm.doc,
      method: "add_dates"
    })
  },
});


