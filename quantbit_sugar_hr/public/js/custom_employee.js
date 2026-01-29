frappe.ui.form.on("Employee Payroll Details", {
    basic: calculate_total,
    hra: calculate_total,
    lta: calculate_total,
    ca: calculate_total,
    medical_allowance: calculate_total,
    fda: calculate_total,
    da: calculate_total,
    leave_encashment: calculate_total,
    washing_allowance: calculate_total,
    night_shift_allowance: calculate_total,
    weight_allowance: calculate_total,
    cashier_allowance: calculate_total,
    gun_allowance: calculate_total
});
function calculate_total(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    let total =
        flt(row.basic) +
        flt(row.hra) +
        flt(row.medical_allowance) +
        flt(row.lta) +
        flt(row.ca) +
        flt(row.fda) +
        flt(row.da) +  
        flt(row.leave_encashment) +
        flt(row.washing_allowance) +
        flt(row.night_shift_allowance) +
        flt(row.weight_allowance) +
        flt(row.cashier_allowance) +
        flt(row.gun_allowance);
    frappe.model.set_value(cdt, cdn, "total_amount", total);
}
