// Copyright (c) 2026, Quantbit Technologies and contributors
// For license information, please see license.txt

function getMonthDates(input_date) {
    const selected_date = new Date(input_date);
    const year = selected_date.getFullYear();
    const month_index = selected_date.getMonth();
    const start_date = new Date(year, month_index, 1);
    const end_date = new Date(year, month_index + 1, 0);
    const month_name = start_date.toLocaleString('default', { month: 'long' });
    return {
        start_date: start_date,
        end_date: end_date,
        year: year,
        month: month_name
    };
}

frappe.ui.form.on("Overtime Calculation", {
    select_all: function(frm) {
        frm.dirty()
        let child_table_field_name = "supevisor_details"; 
        if (frm.doc[child_table_field_name] && frm.doc[child_table_field_name].length > 0) {
            let any_unchecked = frm.doc[child_table_field_name].some(row => !row.check);
            let new_check_state = any_unchecked ? 1 : 0;
            frm.doc[child_table_field_name].forEach(function(row) {
                row.check = new_check_state;
            });            
            frm.refresh_field(child_table_field_name);            
        } 
    },

    from_date: function(frm) {
        if (frm.doc.from_date) {
            let dates = getMonthDates(frm.doc.from_date);
            let start_date_str = frappe.datetime.obj_to_str(dates.start_date);
            if (frm.doc.from_date !== start_date_str) {
                frm.set_value("from_date", start_date_str);
                return; 
            }
            frm.set_value("to_date", frappe.datetime.obj_to_str(dates.end_date));
            frm.set_value("year", dates.year);
            frm.set_value("month", dates.month);
            frm.trigger("get_ot_form");
        } else {
            frm.set_value("to_date", null);
            frm.set_value("year", null);
            frm.set_value("month", null);
            frm.clear_table("supevisor_details");
            frm.refresh_field("supevisor_details");
            frm.clear_table("overtime_hours_calculation");
            frm.refresh_field("overtime_hours_calculation");
            frm.clear_table("overtime_details");
            frm.refresh_field("overtime_details");
        }
    },

    get_ot_form: function(frm) {
        let child_table_name = "supevisor_details";
        let summary_table = "overtime_hours_calculation";
        let details_table = "overtime_details";
        frm.clear_table(child_table_name);
        frm.clear_table(summary_table);
        frm.clear_table(details_table);
        if (!frm.doc.from_date || !frm.doc.to_date) {
            frm.refresh_field(child_table_name); 
            frm.refresh_field(summary_table);
            frm.refresh_field(details_table);
            return;
        }
        let source_doctype = "Overtime Entry";
        let fields_to_fetch = ["name", "date", "supervisor", "supervisor_name"];
        frappe.db.get_list(source_doctype, {
            filters: {
                "date": ["between", [frm.doc.from_date, frm.doc.to_date]]
            },
            fields: fields_to_fetch,
            distinct: true
        }).then(data => {
            if (data && data.length > 0) {
                data.forEach(d => {
                    frm.add_child(child_table_name, {
                        "overtime_id": d.name,
                        "date": d.date,
                        "supervisor_name": d.supervisor_name,
                        "supervisor_id": d.supervisor 
                    });
                });
            } else {
                frappe.msgprint(__("No Overtime Entries found for this period. (या कालावधीसाठी कोणतीही ओव्हरटाईम नोंद आढळली नाही.)"));
            }
            frm.refresh_field(child_table_name);
            frm.refresh_field(summary_table);
            frm.refresh_field(details_table);
        });
    },
    
    get_overtime: function(frm) {
        frm.dirty()
        let summary_table = "overtime_hours_calculation";
        let details_table = "overtime_details";
        frm.clear_table(summary_table);
        frm.clear_table(details_table);
        frappe.msgprint(__("Calculating overtime... This may take a moment. (ओव्हरटाईमची गणना सुरू आहे... कृपया थोडा वेळ थांबा.)"));
        let checked_rows = frm.doc.supevisor_details.filter(row => row.check);
        frm.call({
            method: 'get_overtime',
            doc: frm.doc,
            callback: function(r) {
                if (!r.exc) {
                    frm.refresh_field("overtime_hours_calculation");
                    frm.refresh_field("overtime_details");
                    frappe.msgprint(__("Overtime calculation complete. (ओव्हरटाईमची गणना पूर्ण झाली आहे.)"));
                }
            }
        });
    }
});