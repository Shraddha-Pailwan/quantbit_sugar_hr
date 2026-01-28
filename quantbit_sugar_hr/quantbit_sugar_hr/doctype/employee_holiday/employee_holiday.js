// Copyright (c) 2025, Quantbit Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

function getDayNameFromDate(input_date) {
    const days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    const d = new Date(input_date);
    const dayName = days[d.getDay()];
    return dayName;
}
frappe.ui.form.on("Employee Holiday", {
    from_date: function (frm) {
        if (frm.doc.from_date && frm.doc.to_date) {
            frm.call({
                doc: frm.doc,
                method: "add_dates",
                callback: function (r) {
                    frm.refresh_field("holiday_date_details")
                }
            })
        }
    },
    to_date: function (frm) {
        if (frm.doc.from_date && frm.doc.to_date) {
            frm.call({
                doc: frm.doc,
                method: "add_dates",
                callback: function (r) {
                    frm.refresh_field("holiday_date_details")
                }
            })
        }
    },
    season_type: function (frm) {
        if (frm.doc.from_date && frm.doc.to_date) {
            frm.call({
                doc: frm.doc,
                method: "add_dates",
                callback: function (r) {
                    frm.refresh_field("holiday_date_details")
                }
            })
        }
    },
    branch: function (frm) {
        frm.call({
            method: "add_staff",
            doc: frm.doc,
            callback: function (r) {
                frm.refresh_field("employee_holiday_details")
            }
        })
    },
    company: function (frm) {
        frm.call({
            method: "add_staff",
            doc: frm.doc,
            callback: function (r) {
                frm.refresh_field("employee_holiday_details")
            }
        })
    },
    select_all: function (frm) {
        frm.dirty()
        let child_table_field_name = "holiday_date_details";
        if (frm.doc[child_table_field_name] && frm.doc[child_table_field_name].length > 0) {
            let any_unchecked = frm.doc[child_table_field_name].some(row => !row.check);
            let new_check_state = any_unchecked ? 1 : 0;

            frm.doc[child_table_field_name].forEach(function (row) {
                row.check = new_check_state;
            });
            frm.refresh_field(child_table_field_name);
        }
    },
});
