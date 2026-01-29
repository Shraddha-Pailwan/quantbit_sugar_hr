// Copyright (c) 2026, Quantbit Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Petrol Rate', {
    date: function(frm) {
        if (frm.doc.date) {
            let dateObj = new Date(frm.doc.date);
            let monthName = dateObj.toLocaleString('default', { month: 'long' });
            let year = dateObj.getFullYear();
            frm.set_value('month', monthName);
            frm.set_value('year', year);
        }
    }
});
