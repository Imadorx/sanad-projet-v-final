# Debug: test creating prescription with pharmacy_id directly via Odoo
from datetime import date

# Check which patients doctor ahmed has care relationship with
doctor = env['sanad.doctor'].search([('user_id.login', '=', 'ahmed.benali@test.sanad')], limit=1)
print(f"Doctor: id={doctor.id} name={doctor.name}")

# Find care relationships
care_rels = env['sanad.patient.doctor.rel'].search([('doctor_id', '=', doctor.id)])
for rel in care_rels:
    print(f"  Care rel: patient={rel.patient_id.name} ({rel.patient_id.id})")

# Find pharmacy SANAD
pharm = env['sanad.pharmacy.org'].search([('name', '=', 'Pharmacie SANAD')], limit=1)
print(f"Pharmacy SANAD: id={pharm.id} users={pharm.user_ids.mapped('login')}")

# Try to create a prescription
Patient = env['sanad.patient'].search([('user_id.login', '=', 'omar.tazi@test.sanad')], limit=1)
print(f"Target patient: id={Patient.id} name={Patient.name}")

try:
    rx = env['sanad.prescription'].create({
        'patient_id': Patient.id,
        'pharmacy_id': pharm.id,
        'medication': 'Ibuprofen',
        'dosage': '200mg',
        'frequency': '3x daily',
        'duration': '5 days',
        'instructions': 'Take with food',
    })
    env.cr.commit()
    print(f"SUCCESS: Prescription id={rx.id} medication={rx.medication} pharmacy={rx.pharmacy_id.name}")
except Exception as e:
    env.cr.rollback()
    print(f"ERROR: {e}")
