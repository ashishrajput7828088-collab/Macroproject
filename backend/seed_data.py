"""Seed the Arogya Gwalior SQLite database with directory and demo records."""
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash
from database import get_db, init_tables

REAL_HOSPITALS = [
    {
        "id": 1,
        "name": "Jaya Arogya Hospital (JAH Group) & GRMC",
        "type": "Government",
        "category": "Apex Super Speciality & Trauma Center",
        "address": "Medical College Campus, Kampoo Road, Lashkar, Gwalior, MP 474001",
        "locality": "Lashkar / Kampoo",
        "phone": "+91 751 2403200",
        "emergency_phone": "+91 751 2403222",
        "ambulance_phone": "108",
        "email": "dean.grmc@mp.gov.in",
        "website": "http://grmcgwalior.org",
        "lat": 26.1985,
        "lng": 78.1634,
        "emergency_24x7": 1,
        "trauma_center": 1,
        "rating": 4.6,
        "reviews_count": 1840,
        "opd_timings": "Mon - Sat: 08:30 AM - 01:30 PM (Emergency 24x7)",
        "consultation_fee": 20,
        "description": "Apex government tertiary hospital & referral centre in Gwalior-Chambal division. Houses 1,150 beds, Level-1 Trauma Centre, Cath Lab, Burn Unit, and Central Blood Bank.",
        "services": [
            "Level-1 Trauma Care", "Interventional Cardiology", "Neurology & Neurosurgery",
            "Orthopedic Surgery", "Nephrology & Dialysis Unit", "General & Laparoscopic Surgery",
            "Central Blood Bank 24x7", "CT & MRI Diagnostics", "Burn Intensive Care", "Ambulance"
        ],
        "beds": {"general": [850, 590], "icu": [80, 54], "emergency": [60, 41], "oxygen": [220, 155], "ventilator": [40, 28]}
    },
    {
        "id": 2,
        "name": "BIMR Hospitals (Birla Institute of Medical Research)",
        "type": "Trust",
        "category": "Multi Super Speciality Hospital",
        "address": "Surya Mandir Road, Residency Area, Morar, Gwalior, MP 474005",
        "locality": "Morar Cantt",
        "phone": "+91 751 2405600",
        "emergency_phone": "+91 751 2405605",
        "ambulance_phone": "+91 751 2405601",
        "email": "info@bimrhospital.com",
        "website": "https://www.bimrhospital.com",
        "lat": 26.2312,
        "lng": 78.2215,
        "emergency_24x7": 1,
        "trauma_center": 1,
        "rating": 4.8,
        "reviews_count": 1420,
        "opd_timings": "Mon - Sat: 09:00 AM - 08:00 PM (Casualty 24x7)",
        "consultation_fee": 600,
        "description": "Prestigious 350-bed multi-super-speciality hospital founded by the Birla Group. NABH accredited with state-of-the-art Cath Lab, Robotic Joint Replacement, and Critical Care Unit.",
        "services": [
            "24x7 Cardiac Emergency", "Joint Replacement & Arthroscopy", "Neurosurgery & Spine",
            "Medical & Surgical Oncology", "Advanced Gastroenterology", "Intensive Critical Care",
            "Dialysis Unit", "Blood Component Separation", "Pharmacy 24x7", "Cardiac Mobile ICU"
        ],
        "beds": {"general": [280, 190], "icu": [50, 36], "emergency": [25, 14], "oxygen": [110, 75], "ventilator": [25, 17]}
    },
    {
        "id": 3,
        "name": "Cancer Hospital & Research Institute (CHRI)",
        "type": "Trust",
        "category": "Regional Cancer Centre (Apex Oncology)",
        "address": "Mandre Ki Mata Hills, Cancer Hills, Lashkar, Gwalior, MP 474009",
        "locality": "Cancer Hills",
        "phone": "+91 751 2415124",
        "emergency_phone": "+91 751 2415125",
        "ambulance_phone": "+91 751 2415120",
        "email": "contact@cancerhospitalgwalior.org",
        "website": "http://cancerhospitalgwalior.org",
        "lat": 26.1912,
        "lng": 78.1568,
        "emergency_24x7": 1,
        "trauma_center": 0,
        "rating": 4.7,
        "reviews_count": 980,
        "opd_timings": "Mon - Sat: 09:00 AM - 05:00 PM",
        "consultation_fee": 500,
        "description": "Recognized Regional Cancer Centre of Central India. Features Linear Accelerators, HDR Brachytherapy, Surgical Oncology, Bone Marrow Transplant, and Palliative Medicine.",
        "services": [
            "Radiation Oncology (LINAC)", "Surgical Oncology", "Medical Chemotherapy Daycare",
            "Nuclear Medicine & PET-CT", "Onco-Pathology & Genomics", "Palliative Care", "Ambulance"
        ],
        "beds": {"general": [220, 155], "icu": [28, 18], "emergency": [18, 8], "oxygen": [70, 45], "ventilator": [15, 8]}
    },
    {
        "id": 4,
        "name": "Apollo Clinic & Diagnostic Centre Gwalior",
        "type": "Private",
        "category": "Apollo Network Multi-Speciality",
        "address": "Opp. High Court Road, City Centre, Gwalior, MP 474011",
        "locality": "City Centre",
        "phone": "+91 751 4001222",
        "emergency_phone": "1860 500 1066",
        "ambulance_phone": "1066",
        "email": "gwalior@apolloclinic.com",
        "website": "https://www.apolloclinic.com",
        "lat": 26.2198,
        "lng": 78.2045,
        "emergency_24x7": 1,
        "trauma_center": 0,
        "rating": 4.8,
        "reviews_count": 1150,
        "opd_timings": "Mon - Sun: 08:00 AM - 09:00 PM",
        "consultation_fee": 700,
        "description": "Apollo Hospitals network flagship centre in Gwalior providing super-specialist consultations, preventive health checks, 24x7 Apollo Pharmacy, and advanced MRI/CT diagnostics.",
        "services": [
            "Cardiology Consultations", "Orthopedic OPD", "Pediatrics & Neonatology",
            "Gynecology & Women Health", "Apollo 24x7 Pharmacy", "Advanced MRI & Ultrasound",
            "Home Sample Collection", "Preventive Health Checkups"
        ],
        "beds": {"general": [45, 24], "icu": [12, 6], "emergency": [10, 4], "oxygen": [25, 12], "ventilator": [6, 2]}
    },
    {
        "id": 5,
        "name": "Civil Hospital Morar (District Hospital Gwalior)",
        "type": "Government",
        "category": "District Government Hospital",
        "address": "Main Hospital Road, Morar Cantt, Gwalior, MP 474006",
        "locality": "Morar Cantt",
        "phone": "+91 751 2368212",
        "emergency_phone": "108",
        "ambulance_phone": "108",
        "email": "civilhospital.morar@mp.gov.in",
        "website": "",
        "lat": 26.2268,
        "lng": 78.2295,
        "emergency_24x7": 1,
        "trauma_center": 1,
        "rating": 4.3,
        "reviews_count": 780,
        "opd_timings": "Mon - Sat: 08:30 AM - 02:00 PM (Emergency 24x7)",
        "consultation_fee": 10,
        "description": "Major public hospital serving eastern Gwalior and Chambal. Provides free emergency care, round-the-clock maternity services, free generic drug dispensary, and blood storage.",
        "services": [
            "24x7 Emergency Casualty", "General Medicine", "Maternity & Obstetric Ward",
            "Pediatric Care", "Free Drug Dispensary", "Pathology Lab", "Ambulance 108"
        ],
        "beds": {"general": [240, 165], "icu": [20, 11], "emergency": [25, 15], "oxygen": [80, 50], "ventilator": [10, 4]}
    },
    {
        "id": 6,
        "name": "Kamla Raja Hospital (KRH / JAH Campus)",
        "type": "Government",
        "category": "Mother & Child Super Speciality",
        "address": "Medical College Campus, Kampoo, Gwalior, MP 474001",
        "locality": "Lashkar / Kampoo",
        "phone": "+91 751 2403300",
        "emergency_phone": "+91 751 2403322",
        "ambulance_phone": "102",
        "email": "krh.gwalior@mp.gov.in",
        "website": "http://grmcgwalior.org/krh",
        "lat": 26.1965,
        "lng": 78.1618,
        "emergency_24x7": 1,
        "trauma_center": 0,
        "rating": 4.5,
        "reviews_count": 1020,
        "opd_timings": "Mon - Sat: 08:30 AM - 02:00 PM (Emergency 24x7)",
        "consultation_fee": 20,
        "description": "Leading government maternity and pediatric hospital of Central India. Features 450 beds, Level-III NICU, PICU, high-risk pregnancy delivery units, and 24x7 emergency labor room.",
        "services": [
            "Obstetrics & High-Risk Pregnancy", "Level-III Neonatal ICU (NICU)", "Pediatric Intensive Care (PICU)",
            "Painless Delivery Units", "Infertility Clinic", "24x7 Emergency Obstetric Care", "Janani Express 102"
        ],
        "beds": {"general": [420, 305], "icu": [45, 30], "emergency": [35, 22], "oxygen": [130, 88], "ventilator": [20, 13]}
    },
    {
        "id": 7,
        "name": "Kalyan Memorial Hospital & Research Centre",
        "type": "Private",
        "category": "Super Speciality Hospital",
        "address": "University Road, Near Thatipur, City Centre, Gwalior, MP 474011",
        "locality": "City Centre / Thatipur",
        "phone": "+91 751 2232001",
        "emergency_phone": "+91 94251 10002",
        "ambulance_phone": "+91 94251 10002",
        "email": "kalyanhospital@gmail.com",
        "website": "https://kalyanmemorialhospital.com",
        "lat": 26.2115,
        "lng": 78.2098,
        "emergency_24x7": 1,
        "trauma_center": 1,
        "rating": 4.7,
        "reviews_count": 890,
        "opd_timings": "Mon - Sat: 09:30 AM - 08:30 PM",
        "consultation_fee": 500,
        "description": "Multi-speciality hospital known for advanced cardiac care, renal dialysis unit, joint replacement, critical care, and trauma management.",
        "services": [
            "Cardiology & Echo", "Nephrology & Dialysis", "Orthopedic Trauma",
            "General & Laparoscopic Surgery", "ICU & CCU", "24x7 Ambulance", "Pharmacy"
        ],
        "beds": {"general": [110, 68], "icu": [22, 13], "emergency": [15, 7], "oxygen": [45, 28], "ventilator": [12, 6]}
    },
    {
        "id": 8,
        "name": "Global Speciality Hospital",
        "type": "Private",
        "category": "NABH Accredited Multi Speciality",
        "address": "New Govindpuri, Sachin Tendulkar Marg, City Centre, Gwalior, MP 474011",
        "locality": "City Centre",
        "phone": "+91 751 4099900",
        "emergency_phone": "+91 94253 08800",
        "ambulance_phone": "+91 94253 08800",
        "email": "contact@globalspecialityhospital.com",
        "website": "http://globalspecialityhospital.com",
        "lat": 26.2162,
        "lng": 78.2014,
        "emergency_24x7": 1,
        "trauma_center": 1,
        "rating": 4.6,
        "reviews_count": 680,
        "opd_timings": "Mon - Sat: 10:00 AM - 08:00 PM",
        "consultation_fee": 550,
        "description": "Centrally located multi-speciality hospital housing advanced Gastroenterology, Endoscopy, Pulmonology, Orthopedic Joint Replacement, and Critical Care.",
        "services": [
            "Gastroenterology & Endoscopy", "Pulmonology & Bronchoscopy", "Orthopedics & Spine",
            "Critical Care (ICU)", "24x7 Emergency Response", "Pharmacy", "Ambulance"
        ],
        "beds": {"general": [95, 58], "icu": [18, 10], "emergency": [12, 5], "oxygen": [38, 22], "ventilator": [8, 3]}
    },
    {
        "id": 9,
        "name": "Sheetla Sahay Super Speciality Hospital",
        "type": "Trust",
        "category": "Super Speciality & Polytrauma",
        "address": "Cancer Hills Campus, Lashkar, Gwalior, MP 474009",
        "locality": "Cancer Hills",
        "phone": "+91 751 2415120",
        "emergency_phone": "+91 751 2415121",
        "ambulance_phone": "+91 751 2415120",
        "email": "sheetlasahayhospital@gmail.com",
        "website": "",
        "lat": 26.1925,
        "lng": 78.1585,
        "emergency_24x7": 1,
        "trauma_center": 1,
        "rating": 4.7,
        "reviews_count": 540,
        "opd_timings": "Mon - Sat: 09:30 AM - 06:30 PM",
        "consultation_fee": 600,
        "description": "High-tech super speciality hospital with a modern flat-panel Cath Lab, Neurosurgery OT, 24x7 Polytrauma response unit, and advanced Nephrology wing.",
        "services": [
            "Interventional Cath Lab", "Neuro & Spine Surgery", "Nephrology & Hemodialysis",
            "Polytrauma & Critical Care", "24x7 Emergency", "Ambulance", "Blood Bank"
        ],
        "beds": {"general": [130, 82], "icu": [26, 16], "emergency": [16, 8], "oxygen": [50, 30], "ventilator": [12, 6]}
    },
    {
        "id": 10,
        "name": "Bansal Eye Hospital & Laser Surgery Centre",
        "type": "Specialty",
        "category": "Super Speciality Eye Care",
        "address": "Madhav Rao Scindia Marg, City Centre, Gwalior, MP 474002",
        "locality": "City Centre",
        "phone": "+91 751 2445500",
        "emergency_phone": "+91 98262 12345",
        "ambulance_phone": "+91 98262 12345",
        "email": "bansaleye@gmail.com",
        "website": "http://bansaleyehospital.com",
        "lat": 26.2135,
        "lng": 78.1965,
        "emergency_24x7": 0,
        "trauma_center": 0,
        "rating": 4.9,
        "reviews_count": 1380,
        "opd_timings": "Mon - Sat: 09:30 AM - 07:30 PM",
        "consultation_fee": 500,
        "description": "Premier eye care hospital in Central India. Equipped with Contoura Vision Lasik, stitchless Micro-Phaco cataract surgery, Vitreoretinal surgery, and Glaucoma clinics.",
        "services": [
            "Contoura Vision Lasik", "Micro-Phaco Cataract Surgery", "Vitreoretina & Lasers",
            "Cornea & Refractive Surgery", "Pediatric Ophthalmology", "Glaucoma Clinic", "Optical Studio"
        ],
        "beds": {"general": [35, 18], "icu": [4, 1], "emergency": [5, 2], "oxygen": [12, 4], "ventilator": [2, 0]}
    },
    {
        "id": 11,
        "name": "Nidaan Heart & Maternity Hospital",
        "type": "Private",
        "category": "Cardiac & Maternity Speciality",
        "address": "Near Phoolbagh Chowk, Lashkar, Gwalior, MP 474002",
        "locality": "Phoolbagh / Lashkar",
        "phone": "+91 751 2341100",
        "emergency_phone": "+91 98270 54321",
        "ambulance_phone": "+91 98270 54321",
        "email": "nidaan.gwalior@gmail.com",
        "website": "",
        "lat": 26.2088,
        "lng": 78.1745,
        "emergency_24x7": 1,
        "trauma_center": 0,
        "rating": 4.5,
        "reviews_count": 480,
        "opd_timings": "Mon - Sat: 10:00 AM - 08:00 PM",
        "consultation_fee": 500,
        "description": "Specialized non-invasive cardiology and obstetric hospital equipped with 2D Echo, TMT, Holter monitoring, painless labor suites, and neonatal intensive nursery.",
        "services": [
            "Cardiology Consultations", "2D Echo & Stress TMT", "Painless Normal Delivery",
            "Cesarean & High-Risk Pregnancy", "ICU & CCU", "24x7 Pharmacy", "Ambulance"
        ],
        "beds": {"general": [55, 32], "icu": [12, 6], "emergency": [8, 3], "oxygen": [22, 12], "ventilator": [4, 2]}
    },
    {
        "id": 12,
        "name": "Hazira Civil Hospital",
        "type": "Government",
        "category": "Community Civil Hospital",
        "address": "Hazira Chowk, Tansen Road, Gwalior, MP 474003",
        "locality": "Hazira",
        "phone": "+91 751 2480112",
        "emergency_phone": "108",
        "ambulance_phone": "108",
        "email": "hazira.hospital@mp.gov.in",
        "website": "",
        "lat": 26.2285,
        "lng": 78.1788,
        "emergency_24x7": 1,
        "trauma_center": 0,
        "rating": 4.2,
        "reviews_count": 410,
        "opd_timings": "Mon - Sat: 08:30 AM - 02:00 PM (Emergency 24x7)",
        "consultation_fee": 10,
        "description": "Government community civil hospital providing 24x7 primary emergency, maternal & infant care, immunisation, and free medicine distribution for northern Gwalior.",
        "services": [
            "24x7 Emergency Casualty", "General Medicine", "Maternity Ward",
            "Child Immunisation", "Free Pharmacy", "Ambulance 108"
        ],
        "beds": {"general": [90, 55], "icu": [10, 4], "emergency": [15, 7], "oxygen": [30, 16], "ventilator": [4, 1]}
    },
    {
        "id": 13,
        "name": "Sahara Hospital & Trauma Centre",
        "type": "Private",
        "category": "Multi Speciality & Trauma",
        "address": "Near Railway Station Platform 4 side, Lashkar Road, Gwalior, MP 474002",
        "locality": "Railway Station Area",
        "phone": "+91 751 2420088",
        "emergency_phone": "+91 98260 77123",
        "ambulance_phone": "+91 98260 77123",
        "email": "saharahospitalgwl@gmail.com",
        "website": "",
        "lat": 26.2178,
        "lng": 78.1882,
        "emergency_24x7": 1,
        "trauma_center": 1,
        "rating": 4.6,
        "reviews_count": 590,
        "opd_timings": "Mon - Sat: 09:00 AM - 08:00 PM",
        "consultation_fee": 450,
        "description": "Strategic multi-speciality centre specialising in high-speed road accident polytrauma, fracture fixations, general surgery, and emergency critical care.",
        "services": [
            "Polytrauma & Emergency OT", "Orthopedic Joint Fixation", "Urology & Kidney Stones",
            "General Laparoscopy", "ICU", "Ambulance", "Pharmacy 24x7"
        ],
        "beds": {"general": [80, 48], "icu": [15, 8], "emergency": [12, 5], "oxygen": [32, 18], "ventilator": [6, 2]}
    },
    {
        "id": 14,
        "name": "Vatsalya Hospital & Maternity Home",
        "type": "Private",
        "category": "Infertility & Mother-Child Speciality",
        "address": "Patel Nagar, Near City Centre, Gwalior, MP 474011",
        "locality": "City Centre",
        "phone": "+91 751 2235544",
        "emergency_phone": "+91 94251 17890",
        "ambulance_phone": "+91 94251 17890",
        "email": "vatsalyahospital@gmail.com",
        "website": "",
        "lat": 26.2142,
        "lng": 78.2065,
        "emergency_24x7": 1,
        "trauma_center": 0,
        "rating": 4.8,
        "reviews_count": 760,
        "opd_timings": "Mon - Sat: 10:00 AM - 07:30 PM",
        "consultation_fee": 500,
        "description": "Founded by senior gynecologist Dr. Rashmi Gupta. Specialises in advanced infertility management, test tube baby (IVF), high-risk pregnancies, and neonatal intensive care (NICU).",
        "services": [
            "Infertility & IVF Centre", "High-Risk Pregnancy", "Normal & Cesarean Delivery",
            "NICU Level-II", "Pediatrics", "24x7 Emergency Labor", "Pharmacy"
        ],
        "beds": {"general": [50, 28], "icu": [10, 5], "emergency": [8, 3], "oxygen": [20, 11], "ventilator": [4, 1]}
    },
    {
        "id": 15,
        "name": "Maxcare Multispeciality Hospital",
        "type": "Private",
        "category": "Multi Speciality Hospital",
        "address": "New Collectorate Road, City Centre, Gwalior, MP 474011",
        "locality": "City Centre",
        "phone": "+91 751 4018888",
        "emergency_phone": "+91 94257 23456",
        "ambulance_phone": "+91 94257 23456",
        "email": "maxcaregwalior@gmail.com",
        "website": "",
        "lat": 26.2225,
        "lng": 78.2120,
        "emergency_24x7": 1,
        "trauma_center": 0,
        "rating": 4.6,
        "reviews_count": 510,
        "opd_timings": "Mon - Sat: 09:30 AM - 08:00 PM",
        "consultation_fee": 500,
        "description": "Modern facility offering advanced internal medicine, diabetology, pulmonology, critical care, dermatology, and diagnostic pathology.",
        "services": [
            "Internal Medicine & Diabetes", "Pulmonology & Asthma Care", "Critical Care ICU",
            "Dermatology & Hair Clinic", "24x7 Emergency", "Ambulance", "Pharmacy"
        ],
        "beds": {"general": [75, 42], "icu": [14, 7], "emergency": [10, 4], "oxygen": [28, 14], "ventilator": [6, 2]}
    },
    {
        "id": 16,
        "name": "Janak Hospital & Laparoscopy Centre",
        "type": "Private",
        "category": "Surgical Speciality Hospital",
        "address": "Morar Road, Near Thatipur, Gwalior, MP 474005",
        "locality": "Thatipur",
        "phone": "+91 751 2345099",
        "emergency_phone": "+91 98262 55443",
        "ambulance_phone": "+91 98262 55443",
        "email": "janakhospital@gmail.com",
        "website": "",
        "lat": 26.2210,
        "lng": 78.2170,
        "emergency_24x7": 1,
        "trauma_center": 0,
        "rating": 4.5,
        "reviews_count": 420,
        "opd_timings": "Mon - Sat: 10:00 AM - 07:00 PM",
        "consultation_fee": 450,
        "description": "Dedicated surgical centre offering advanced laparoscopic gallbladder, hernia, appendix, and endoscopic urology procedures with fast post-operative recovery.",
        "services": [
            "Laparoscopic General Surgery", "Endourology & Kidney Stones", "Trauma & Fracture Fixation",
            "ICU Support", "24x7 Emergency", "Pharmacy"
        ],
        "beds": {"general": [40, 22], "icu": [8, 4], "emergency": [6, 2], "oxygen": [15, 7], "ventilator": [3, 1]}
    }
,
{
        "id": 17,
        "name": "Gwalior Mansik Arogyashala (Mental Health & Neuroscience Institute)",
        "type": "Government",
        "category": "Apex Psychiatric & Neuroscience Hospital",
        "address": "Jail Road, Near Central Jail, Gwalior, MP 474003",
        "locality": "Hazira / Jail Road",
        "phone": "+91 751 2481014",
        "emergency_phone": "+91 751 2481015",
        "ambulance_phone": "108",
        "email": "director.gma@mp.gov.in",
        "website": "http://gwaliormentalhospital.org",
        "lat": 26.2230,
        "lng": 78.1880,
        "emergency_24x7": 1,
        "trauma_center": 0,
        "rating": 4.5,
        "reviews_count": 520,
        "opd_timings": "Mon - Sat: 09:00 AM - 02:00 PM (Emergency 24x7)",
        "consultation_fee": 20,
        "description": "Historic government apex institute established in 1935 for psychiatric care, behavioral sciences, de-addiction therapy, and clinical neuro-psychology in Madhya Pradesh.",
        "services": [
            "Psychiatry & De-Addiction", "Clinical Psychology", "Neuro-Psychiatry",
            "Emergency 24x7 Crisis Cell", "Rehabilitation & Counseling", "Electroencephalogram (EEG)",
            "Pharmacy & Social Work"
        ],
        "beds": {"general": [180, 110], "icu": [10, 6], "emergency": [12, 7], "oxygen": [35, 20], "ventilator": [2, 1]}
    },
    {
        "id": 18,
        "name": "Scindia Devraj Hospital & Research Centre",
        "type": "Private",
        "category": "Multi-Speciality Centre",
        "address": "Jayendraganj Main Market, Lashkar, Gwalior, MP 474009",
        "locality": "Lashkar / Jayendraganj",
        "phone": "+91 751 2423300",
        "emergency_phone": "+91 751 2423301",
        "ambulance_phone": "+91 751 2423300",
        "email": "info@scindiadevrajhospital.com",
        "website": "",
        "lat": 26.2052,
        "lng": 78.1685,
        "emergency_24x7": 1,
        "trauma_center": 0,
        "rating": 4.6,
        "reviews_count": 340,
        "opd_timings": "Mon - Sat: 09:00 AM - 08:00 PM",
        "consultation_fee": 500,
        "description": "Established multi-speciality medical centre in the heart of Lashkar providing comprehensive surgical, medical, and diagnostics care.",
        "services": [
            "General Surgery", "Urology & Nephrology", "Obstetrics & Gynecology",
            "Internal Medicine", "Pediatrics", "24x7 Pharmacy", "Digital X-Ray"
        ],
        "beds": {"general": [35, 20], "icu": [6, 4], "emergency": [5, 3], "oxygen": [15, 9], "ventilator": [2, 1]}
    },
    {
        "id": 19,
        "name": "K.D. Super Speciality Hospital",
        "type": "Private",
        "category": "Super Speciality & Kidney Care",
        "address": "Near Tansen Tomb Road, Hazira, Gwalior, MP 474003",
        "locality": "Hazira / Tansen Road",
        "phone": "+91 751 2482255",
        "emergency_phone": "+91 751 2482256",
        "ambulance_phone": "+91 751 2482255",
        "email": "kd.hospitalgwl@gmail.com",
        "website": "",
        "lat": 26.2312,
        "lng": 78.1755,
        "emergency_24x7": 1,
        "trauma_center": 1,
        "rating": 4.7,
        "reviews_count": 410,
        "opd_timings": "Mon - Sun: 24 Hours Open",
        "consultation_fee": 500,
        "description": "Advanced multi-specialty healthcare centre near Hazira with modern dialysis units, intensive care facilities, and robotic trauma surgery.",
        "services": [
            "Dialysis Unit 24x7", "Nephrology & Urology", "Critical Care & ICU",
            "Joint Replacement", "Gastroenterology", "24x7 Emergency Trauma"
        ],
        "beds": {"general": [45, 28], "icu": [12, 8], "emergency": [8, 5], "oxygen": [25, 16], "ventilator": [4, 2]}
    },
    {
        "id": 20,
        "name": "Navjeevan Multispeciality Hospital",
        "type": "Private",
        "category": "Multispeciality Hospital",
        "address": "Airport Road, Near Gole Ka Mandir, Gwalior, MP 474005",
        "locality": "Gole Ka Mandir / Airport Road",
        "phone": "+91 751 2490011",
        "emergency_phone": "+91 751 2490012",
        "ambulance_phone": "+91 751 2490011",
        "email": "care@navjeevangwalior.org",
        "website": "",
        "lat": 26.2425,
        "lng": 78.2120,
        "emergency_24x7": 1,
        "trauma_center": 0,
        "rating": 4.5,
        "reviews_count": 285,
        "opd_timings": "Mon - Sat: 09:00 AM - 08:30 PM",
        "consultation_fee": 450,
        "description": "Trusted community multi-speciality hospital catering to Gole Ka Mandir, Maharajpura, and Airport Road catchment.",
        "services": [
            "General Medicine", "Pediatrics & Child Care", "Orthopedic Surgery",
            "Pathology & Ultrasound", "24x7 Casualty", "Day Care Surgeries"
        ],
        "beds": {"general": [38, 22], "icu": [8, 5], "emergency": [6, 4], "oxygen": [20, 13], "ventilator": [2, 1]}
    },
    {
        "id": 21,
        "name": "Chirayu Children Hospital & Neonatal ICU (NICU)",
        "type": "Specialty",
        "category": "Pediatric & Neonatal Super Speciality",
        "address": "Patel Nagar, Near City Centre Bus Stop, Gwalior, MP 474011",
        "locality": "City Centre / Patel Nagar",
        "phone": "+91 751 2234000",
        "emergency_phone": "+91 751 2234001",
        "ambulance_phone": "+91 751 2234000",
        "email": "chirayukids.gwl@gmail.com",
        "website": "",
        "lat": 26.2140,
        "lng": 78.1990,
        "emergency_24x7": 1,
        "trauma_center": 0,
        "rating": 4.8,
        "reviews_count": 620,
        "opd_timings": "Mon - Sat: 09:30 AM - 07:30 PM (Emergency 24x7)",
        "consultation_fee": 500,
        "description": "Premier pediatric hospital in Gwalior equipped with Level-3 Neonatal Intensive Care (NICU), Pediatric Intensive Care (PICU), and advanced infant warmers.",
        "services": [
            "Level-3 NICU (Neonatal ICU)", "Pediatric Intensive Care (PICU)", "Pediatric Surgery",
            "Neonatal Ventilation", "Growth & Vaccination Clinic", "Emergency Pediatric Triage"
        ],
        "beds": {"general": [25, 14], "icu": [14, 9], "emergency": [6, 3], "oxygen": [20, 12], "ventilator": [6, 4]}
    },
    {
        "id": 22,
        "name": "Shri Ram Hospital & Laparoscopy Centre",
        "type": "Private",
        "category": "Minimally Invasive Surgery & Laparoscopy",
        "address": "Kampoo Main Road, Near Madhav Dispensary, Lashkar, Gwalior, MP 474001",
        "locality": "Lashkar / Kampoo",
        "phone": "+91 751 2419080",
        "emergency_phone": "+91 751 2419081",
        "ambulance_phone": "+91 751 2419080",
        "email": "info@shriramhospitalgwl.com",
        "website": "",
        "lat": 26.1950,
        "lng": 78.1580,
        "emergency_24x7": 1,
        "trauma_center": 0,
        "rating": 4.6,
        "reviews_count": 310,
        "opd_timings": "Mon - Sat: 10:00 AM - 07:00 PM",
        "consultation_fee": 500,
        "description": "Renowned centre for minimally invasive laparoscopic, gallbladder, hernia, and gynecological surgical interventions in Gwalior.",
        "services": [
            "Advanced Laparoscopic Surgery", "Gastrointestinal Surgery", "Hernia & Gallbladder Centre",
            "Gynecological Endoscopy", "Intensive Care Unit (ICU)", "24x7 Emergency OT"
        ],
        "beds": {"general": [42, 26], "icu": [8, 5], "emergency": [6, 3], "oxygen": [18, 11], "ventilator": [3, 1]}
    }
]

REAL_DOCTORS = [
    {
        "id": 101,
        "name": "Dr. Ajay Gupta",
        "qualification": "MBBS, MD (Medicine), DM (Cardiology - Gold Medalist)",
        "specialty": "Cardiologist (Heart Specialist)",
        "category": "cardiology",
        "experience_years": 22,
        "hospital_id": 2,
        "hospital_name": "BIMR Hospitals (Birla Heart Centre)",
        "clinic_address": "Surya Mandir Road, Morar & City Centre OPD, Gwalior",
        "phone": "+91 94251 12340",
        "email": "dr.ajaygupta.cardio@gmail.com",
        "opd_timings": "Mon - Sat: 11:00 AM - 03:00 PM & 06:00 PM - 08:30 PM",
        "days_available": "Mon - Sat",
        "fee": 600,
        "rating": 4.9,
        "reviews_count": 430,
        "badge": "Top Cardiologist",
        "avatar": "👨‍⚕️",
        "about": "Senior Interventional Cardiologist with over 15,000+ angiographies and angioplasties performed. Specialized in coronary stenting, pacemakers, heart failure, and hypertension."
    },
    {
        "id": 102,
        "name": "Dr. Rashmi Gupta",
        "qualification": "MBBS, MS (Obstetrics & Gynecology), F.MAS",
        "specialty": "Gynecologist & Infertility Specialist",
        "category": "gynecology",
        "experience_years": 19,
        "hospital_id": 14,
        "hospital_name": "Vatsalya Hospital & Maternity Home",
        "clinic_address": "Patel Nagar, Near City Centre, Gwalior",
        "phone": "+91 94251 17890",
        "email": "dr.rashmigupta.obgyn@gmail.com",
        "opd_timings": "Mon - Sat: 10:00 AM - 02:00 PM & 05:30 PM - 08:00 PM",
        "days_available": "Mon - Sat",
        "fee": 500,
        "rating": 4.9,
        "reviews_count": 490,
        "badge": "Senior Gynecologist",
        "avatar": "👩‍⚕️",
        "about": "Renowned for painless normal deliveries, high-risk pregnancy management, IVF infertility treatments, PCOS, and minimally invasive laparoscopic hysterectomy."
    },
    {
        "id": 103,
        "name": "Dr. Sanjay Dhir",
        "qualification": "MBBS, MS (Surgery), MCh (Neurosurgery - AIIMS New Delhi)",
        "specialty": "Neurosurgeon (Brain & Spine Surgeon)",
        "category": "neurology",
        "experience_years": 21,
        "hospital_id": 1,
        "hospital_name": "JAH Super Speciality / Sheetla Sahay Hospital",
        "clinic_address": "Kampoo Road, Lashkar & Cancer Hills, Gwalior",
        "phone": "+91 751 2403200",
        "email": "dr.sanjaydhir.neuro@gmail.com",
        "opd_timings": "Mon - Fri: 10:00 AM - 02:00 PM",
        "days_available": "Mon - Fri",
        "fee": 700,
        "rating": 4.8,
        "reviews_count": 340,
        "badge": "AIIMS Alumnus",
        "avatar": "👨‍⚕️",
        "about": "Expert in micro-neurosurgery, brain tumor resections, endoscopic slip disc surgeries, spinal fusion, cervical spondylosis, and traumatic head injury rehabilitation."
    },
    {
        "id": 104,
        "name": "Dr. Manish Bansal",
        "qualification": "MBBS, MS (Ophthalmology), Fellowship Sankara Nethralaya",
        "specialty": "Ophthalmologist (Chief Eye Surgeon)",
        "category": "ophthalmology",
        "experience_years": 19,
        "hospital_id": 10,
        "hospital_name": "Bansal Eye Hospital & Laser Surgery Centre",
        "clinic_address": "Madhav Rao Scindia Marg, City Centre, Gwalior",
        "phone": "+91 98262 12345",
        "email": "drmanishbansal@bansaleye.com",
        "opd_timings": "Mon - Sat: 10:00 AM - 01:30 PM & 05:00 PM - 07:30 PM",
        "days_available": "Mon - Sat",
        "fee": 500,
        "rating": 4.9,
        "reviews_count": 580,
        "badge": "Premier Eye Surgeon",
        "avatar": "👨‍⚕️",
        "about": "Pioneer in stitchless Micro-Phaco cataract surgery and Contoura Vision Lasik in Gwalior. Expert in diabetic vitreo-retinal laser treatments and corneal disorders."
    },
    {
        "id": 105,
        "name": "Dr. Neeraj Sharma",
        "qualification": "MBBS, MS (Orthopedics), Joint Replacement Fellow (Germany)",
        "specialty": "Orthopedic & Robotic Joint Surgeon",
        "category": "orthopedics",
        "experience_years": 18,
        "hospital_id": 2,
        "hospital_name": "BIMR Hospitals / Sahara Hospital",
        "clinic_address": "Surya Mandir Road, Morar, Gwalior",
        "phone": "+91 98260 77123",
        "email": "drneerajsharma.ortho@gmail.com",
        "opd_timings": "Mon - Sat: 11:30 AM - 04:00 PM & 06:30 PM - 08:30 PM",
        "days_available": "Mon - Sat",
        "fee": 600,
        "rating": 4.8,
        "reviews_count": 410,
        "badge": "Joint Replacement Expert",
        "avatar": "👨‍⚕️",
        "about": "Specialist in robotic total knee and hip replacements, arthroscopic ACL/PCL ligament reconstruction, complex multi-fragment bone fractures, and arthritis therapy."
    },
    {
        "id": 106,
        "name": "Dr. Archana Shrivastava",
        "qualification": "MBBS, MD (Pediatrics), FIAP",
        "specialty": "Pediatrician & Child Health Specialist",
        "category": "pediatrics",
        "experience_years": 16,
        "hospital_id": 6,
        "hospital_name": "Kamla Raja Hospital (KRH) & Child Care Clinic",
        "clinic_address": "Medical College Road, Kampoo, Lashkar, Gwalior",
        "phone": "+91 751 2403300",
        "email": "drarchana.pediatrics@gmail.com",
        "opd_timings": "Mon - Sat: 09:30 AM - 01:30 PM & 05:00 PM - 07:30 PM",
        "days_available": "Mon - Sat",
        "fee": 500,
        "rating": 4.9,
        "reviews_count": 470,
        "badge": "Child Health Specialist",
        "avatar": "👩‍⚕️",
        "about": "Specialized in newborn intensive care (NICU), pediatric asthma, childhood infections (dengue, typhoid), child growth monitoring, and painless immunisation."
    },
    {
        "id": 107,
        "name": "Dr. Rahul Agarwal",
        "qualification": "MBBS, MD (General Medicine), FICP",
        "specialty": "General Physician & Diabetologist",
        "category": "general",
        "experience_years": 18,
        "hospital_id": 4,
        "hospital_name": "Apollo Clinic & Diagnostic Centre",
        "clinic_address": "Opp. High Court, City Centre, Gwalior",
        "phone": "+91 751 4001222",
        "email": "dr.rahulagarwal@apolloclinic.com",
        "opd_timings": "Mon - Sun: 09:00 AM - 01:00 PM & 05:00 PM - 08:30 PM",
        "days_available": "Mon - Sun",
        "fee": 500,
        "rating": 4.8,
        "reviews_count": 520,
        "badge": "Apollo Consultant",
        "avatar": "👨‍⚕️",
        "about": "Experienced family physician diagnosing acute seasonal fevers (Dengue, Malaria, Typhoid), Diabetes Mellitus, hypertension, thyroid conditions, and geriatric health."
    },
    {
        "id": 108,
        "name": "Dr. Vivek Verma",
        "qualification": "MBBS, MS (Surgery), MCh (Surgical Oncology - Tata Memorial)",
        "specialty": "Oncologist (Cancer Surgeon)",
        "category": "oncology",
        "experience_years": 17,
        "hospital_id": 3,
        "hospital_name": "Cancer Hospital & Research Institute (CHRI)",
        "clinic_address": "Cancer Hills, Mandre Ki Mata, Lashkar, Gwalior",
        "phone": "+91 751 2415124",
        "email": "dr.vivekverma.onco@gmail.com",
        "opd_timings": "Mon - Sat: 10:00 AM - 03:00 PM",
        "days_available": "Mon - Sat",
        "fee": 800,
        "rating": 4.9,
        "reviews_count": 310,
        "badge": "Senior Cancer Surgeon",
        "avatar": "👨‍⚕️",
        "about": "Extensive experience in head & neck cancers, breast conservation surgery, gastrointestinal cancer resections, and comprehensive multidisciplinary oncology."
    },
    {
        "id": 109,
        "name": "Dr. Rajesh Saxena",
        "qualification": "MBBS, MD (Medicine), DM (Gastroenterology - SGPGI)",
        "specialty": "Gastroenterologist & Hepatologist",
        "category": "gastro",
        "experience_years": 16,
        "hospital_id": 8,
        "hospital_name": "Global Speciality Hospital",
        "clinic_address": "Sachin Tendulkar Marg, City Centre, Gwalior",
        "phone": "+91 751 4099900",
        "email": "drrajeshsaxena.gastro@gmail.com",
        "opd_timings": "Mon - Sat: 11:00 AM - 03:00 PM & 06:00 PM - 08:00 PM",
        "days_available": "Mon - Sat",
        "fee": 700,
        "rating": 4.7,
        "reviews_count": 290,
        "badge": "Gastro Specialist",
        "avatar": "👨‍⚕️",
        "about": "Specialist in therapeutic endoscopy, colonoscopy, ERCP, fatty liver, jaundice, hepatitis, chronic pancreatitis, and inflammatory bowel disease."
    },
    {
        "id": 110,
        "name": "Dr. Priya Tomar",
        "qualification": "MBBS, MD (Dermatology, Venereology & Leprosy)",
        "specialty": "Dermatologist & Cosmetologist (Skin & Hair)",
        "category": "dermatology",
        "experience_years": 13,
        "hospital_id": 15,
        "hospital_name": "Maxcare Hospital & Skin Laser Clinic",
        "clinic_address": "New Collectorate Road, City Centre, Gwalior",
        "phone": "+91 94257 23456",
        "email": "drpriyatomar.skin@gmail.com",
        "opd_timings": "Mon - Sat: 10:30 AM - 02:30 PM & 05:30 PM - 08:00 PM",
        "days_available": "Mon - Sat",
        "fee": 500,
        "rating": 4.8,
        "reviews_count": 390,
        "badge": "Skin & Laser Expert",
        "avatar": "👩‍⚕️",
        "about": "Certified cosmetologist treating severe acne, eczema, psoriasis, hair fall with PRP therapy, fungal allergies, laser pigmentation removal, and chemical peels."
    },
    {
        "id": 111,
        "name": "Dr. Alok Purohit",
        "qualification": "MBBS, MD (Pulmonary Medicine - Chest & TB)",
        "specialty": "Pulmonologist (Chest & Lungs Specialist)",
        "category": "pulmonology",
        "experience_years": 15,
        "hospital_id": 1,
        "hospital_name": "JAH Super Speciality / City Centre Chest Clinic",
        "clinic_address": "City Centre & Kampoo, Gwalior",
        "phone": "+91 751 2403201",
        "email": "dralokpurohit.chest@gmail.com",
        "opd_timings": "Mon - Sat: 10:00 AM - 02:00 PM & 06:00 PM - 08:00 PM",
        "days_available": "Mon - Sat",
        "fee": 600,
        "rating": 4.8,
        "reviews_count": 310,
        "badge": "Chest & Asthma Expert",
        "avatar": "👨‍⚕️",
        "about": "Specialist in Bronchial Asthma, COPD, Chronic Bronchitis, Post-Covid lung fibrosis, Sleep Apnea, diagnostic bronchoscopy, and respiratory allergies."
    },
    {
        "id": 112,
        "name": "Dr. Sunita Mishra",
        "qualification": "MBBS, MS (ENT / Otorhinolaryngology)",
        "specialty": "ENT & Head-Neck Surgeon",
        "category": "ent",
        "experience_years": 14,
        "hospital_id": 5,
        "hospital_name": "Civil Hospital Morar / Apollo Clinic",
        "clinic_address": "Morar Cantt & High Court Road, Gwalior",
        "phone": "+91 751 2368212",
        "email": "drsunitamishra.ent@gmail.com",
        "opd_timings": "Mon - Sat: 09:30 AM - 01:30 PM & 05:00 PM - 07:30 PM",
        "days_available": "Mon - Sat",
        "fee": 450,
        "rating": 4.7,
        "reviews_count": 340,
        "badge": "ENT Specialist",
        "avatar": "👩‍⚕️",
        "about": "Treats chronic ear discharge, tympanoplasty, endoscopic sinus surgery (FESS), nasal polyps, tonsillitis, vertigo, and vocal cord disorders."
    }
,
{
        "id": 113,
        "name": "Dr. Pradeep Kashyap",
        "qualification": "MBBS, MS (Gen Surgery), MCh (Urology)",
        "specialty": "Urologist & Kidney Transplant Surgeon",
        "category": "general",
        "experience_years": 16,
        "hospital_id": 19,
        "hospital_name": "K.D. Super Speciality Hospital / Scindia Devraj Hospital",
        "clinic_address": "Hazira Road & Jayendraganj, Lashkar, Gwalior",
        "phone": "+91 94251 22880",
        "email": "dr.pkashyap@gmail.com",
        "opd_timings": "Mon - Sat: 11:00 AM - 02:00 PM, 05:30 PM - 08:00 PM",
        "days_available": "Mon - Sat",
        "fee": 700,
        "rating": 4.9,
        "reviews_count": 210,
        "badge": "Chief Urologist",
        "about": "Expert in laser kidney stone removal (RIRS/PCNL), prostate surgery (TURP), and advanced laparoscopic reconstructive urology.",
        "avatar": "👨‍⚕️"
    },
    {
        "id": 114,
        "name": "Dr. Meenakshi Bansal",
        "qualification": "MBBS, MS (Ophthalmology), Fellow (LVPEI)",
        "specialty": "Pediatric Ophthalmologist & Squint Surgeon",
        "category": "ophthalmology",
        "experience_years": 12,
        "hospital_id": 10,
        "hospital_name": "Bansal Eye Hospital & Laser Surgery Centre",
        "clinic_address": "Madhav Rao Scindia Marg, City Centre, Gwalior",
        "phone": "+91 751 2445500",
        "email": "dr.meenakshi.eye@gmail.com",
        "opd_timings": "Mon - Sat: 10:30 AM - 03:00 PM",
        "days_available": "Mon - Sat",
        "fee": 500,
        "rating": 4.9,
        "reviews_count": 185,
        "badge": "Squint & Pediatric Eye Specialist",
        "about": "Specializes in children eye disorders, amblyopia (lazy eye), squint correction surgery, and pediatric cataract management.",
        "avatar": "👩‍⚕️"
    },
    {
        "id": 115,
        "name": "Dr. Ashish Chauhan",
        "qualification": "MBBS, MD (Anesthesia), FNB (Critical Care Medicine)",
        "specialty": "Chief of Critical Care & Emergency Medicine",
        "category": "general",
        "experience_years": 14,
        "hospital_id": 1,
        "hospital_name": "JAH Level-1 Trauma Centre & BIMR Hospitals",
        "clinic_address": "Medical College Campus, Kampoo, Gwalior",
        "phone": "+91 751 2403222",
        "email": "dr.ashish.icu@gmail.com",
        "opd_timings": "Mon - Sat: 09:00 AM - 01:00 PM (Emergency On-Call 24x7)",
        "days_available": "Mon - Sat",
        "fee": 600,
        "rating": 4.8,
        "reviews_count": 160,
        "badge": "Critical Care Specialist",
        "about": "Head of resuscitation and intensive care, managing complex polytrauma, septic shock, ECMO, and mechanical ventilation.",
        "avatar": "👨‍⚕️"
    },
    {
        "id": 116,
        "name": "Dr. Ritu Saxena",
        "qualification": "BDS, MDS (Oral & Maxillofacial Surgery)",
        "specialty": "Maxillofacial Surgeon & Dental Implantologist",
        "category": "general",
        "experience_years": 11,
        "hospital_id": 4,
        "hospital_name": "Apollo Clinic & Maxcare Dental Centre",
        "clinic_address": "High Court Road, City Centre, Gwalior",
        "phone": "+91 751 4001222",
        "email": "dr.ritusaxena.oral@gmail.com",
        "opd_timings": "Mon - Sat: 10:00 AM - 02:00 PM, 05:00 PM - 08:30 PM",
        "days_available": "Mon - Sat",
        "fee": 400,
        "rating": 4.8,
        "reviews_count": 175,
        "badge": "Dental & Facial Surgeon",
        "about": "Expert in facial bone fractures, dental implants, wisdom tooth impactions, TMJ disorders, and cosmetic smile designs.",
        "avatar": "👩‍⚕️"
    },
    {
        "id": 117,
        "name": "Dr. S. K. Pathak",
        "qualification": "MBBS, MD (Psychiatry), DPM",
        "specialty": "Senior Psychiatrist & Neuro-Behavioral Specialist",
        "category": "neurology",
        "experience_years": 22,
        "hospital_id": 17,
        "hospital_name": "Gwalior Mansik Arogyashala & Mind Clinic",
        "clinic_address": "Jail Road & Phoolbagh, Gwalior",
        "phone": "+91 751 2481014",
        "email": "dr.skpathak.psych@gmail.com",
        "opd_timings": "Mon - Sat: 09:30 AM - 01:30 PM, 05:00 PM - 07:30 PM",
        "days_available": "Mon - Sat",
        "fee": 500,
        "rating": 4.9,
        "reviews_count": 310,
        "badge": "Senior Neuro-Psychiatrist",
        "about": "Decades of experience in depression, clinical anxiety, OCD, sleep disorders, addiction therapy, and adolescent mental health.",
        "avatar": "👨‍⚕️"
    },
    {
        "id": 118,
        "name": "Dr. Deepak Agrawal",
        "qualification": "MBBS, MS (Orthopedics), Fellowship in Arthroscopy (Germany)",
        "specialty": "Arthroscopy, Sports Injury & Knee Surgeon",
        "category": "orthopedics",
        "experience_years": 15,
        "hospital_id": 7,
        "hospital_name": "Kalyan Memorial Hospital & BIMR Hospitals",
        "clinic_address": "University Road, Near Thatipur, Gwalior",
        "phone": "+91 751 2232001",
        "email": "dr.deepak.ortho@gmail.com",
        "opd_timings": "Mon - Sat: 11:30 AM - 03:30 PM, 06:00 PM - 08:30 PM",
        "days_available": "Mon - Sat",
        "fee": 600,
        "rating": 4.9,
        "reviews_count": 240,
        "badge": "Sports Injury & Knee Specialist",
        "about": "Pioneer in keyhole arthroscopic ACL/PCL ligament reconstruction, meniscus repair, and minimally invasive joint restoration.",
        "avatar": "👨‍⚕️"
    }
]

REAL_BLOOD_BANKS = [
    {
        "name": "JAH Central Blood Bank & Component Separation Unit",
        "hospital_id": 1,
        "address": "GRMC Campus, Kampoo Road, Lashkar, Gwalior",
        "contact_person": "Dr. R. K. Jain (Chief Medical Officer)",
        "phone": "+91 751 2403233",
        "emergency_24x7": 1,
        "lat": 26.1985,
        "lng": 78.1634,
        "inventory": {"A+": 42, "A-": 12, "B+": 65, "B-": 15, "O+": 58, "O-": 18, "AB+": 25, "AB-": 8}
    },
    {
        "name": "Indian Red Cross Society Blood Bank Gwalior",
        "hospital_id": None,
        "address": "Near Phoolbagh Ground, Lashkar, Gwalior, MP 474002",
        "contact_person": "Secretary, Red Cross Gwalior",
        "phone": "+91 751 2422002",
        "emergency_24x7": 1,
        "lat": 26.2095,
        "lng": 78.1752,
        "inventory": {"A+": 28, "A-": 8, "B+": 45, "B-": 10, "O+": 38, "O-": 14, "AB+": 18, "AB-": 5}
    },
    {
        "name": "BIMR Hospital Blood Bank",
        "hospital_id": 2,
        "address": "Surya Mandir Road, Residency Area, Morar, Gwalior",
        "contact_person": "Blood Transfusion In-Charge",
        "phone": "+91 751 2405615",
        "emergency_24x7": 1,
        "lat": 26.2312,
        "lng": 78.2215,
        "inventory": {"A+": 24, "A-": 6, "B+": 35, "B-": 8, "O+": 30, "O-": 9, "AB+": 14, "AB-": 4}
    },
    {
        "name": "Civil Hospital Morar Blood Storage Centre",
        "hospital_id": 5,
        "address": "Hospital Road, Morar Cantt, Gwalior",
        "contact_person": "Duty Transfusion Officer",
        "phone": "+91 751 2368212",
        "emergency_24x7": 1,
        "lat": 26.2268,
        "lng": 78.2295,
        "inventory": {"A+": 16, "A-": 4, "B+": 22, "B-": 5, "O+": 20, "O-": 6, "AB+": 8, "AB-": 2}
    },
    {
        "name": "Cancer Hospital (CHRI) Blood Bank",
        "hospital_id": 3,
        "address": "Mandre Ki Mata Hills, Cancer Hills, Gwalior",
        "contact_person": "Transfusion Medicine Head",
        "phone": "+91 751 2415124",
        "emergency_24x7": 1,
        "lat": 26.1912,
        "lng": 78.1568,
        "inventory": {"A+": 18, "A-": 5, "B+": 26, "B-": 6, "O+": 24, "O-": 7, "AB+": 11, "AB-": 3}
    }
,
{
        "name": "Rotary Club Gwalior Blood Bank & Apheresis Centre",
        "hospital_id": 18,
        "address": "Jayendraganj Main Road, Near SBI Zonal Office, Lashkar, Gwalior",
        "contact_person": "Blood Transfusion Officer",
        "phone": "+91 751 2321155",
        "emergency_24x7": 1,
        "lat": 26.2045,
        "lng": 78.1678,
        "inventory": {"A+": 18, "A-": 6, "B+": 25, "B-": 8, "O+": 30, "O-": 7, "AB+": 14, "AB-": 4}
    },
    {
        "name": "Kamla Raja Maternity Hospital (KRH) Blood Storage Centre",
        "hospital_id": 6,
        "address": "KRH Medical College Campus, Kampoo Road, Gwalior",
        "contact_person": "Duty Medical Officer (Blood Bank)",
        "phone": "+91 751 2403322",
        "emergency_24x7": 1,
        "lat": 26.1978,
        "lng": 78.1622,
        "inventory": {"A+": 22, "A-": 8, "B+": 28, "B-": 9, "O+": 35, "O-": 10, "AB+": 16, "AB-": 5}
    }
]

REAL_AMBULANCES = [
    {
        "service_name": "108 National Emergency Ambulance (Gwalior Central Control)",
        "vehicle_type": "ALS (Advanced Life Support)",
        "operator_type": "Government",
        "phone": "108",
        "base_location": "JAH Campus & District Dispatch Centres",
        "lat": 26.1985,
        "lng": 78.1634,
        "available": 1,
        "features": "Defibrillator, Transport Ventilator, Multipara Monitor, Suction Machine, Oxygen Cylinders"
    },
    {
        "service_name": "102 Janani Express Ambulance (Maternity & Infant)",
        "vehicle_type": "BLS (Basic Life Support)",
        "operator_type": "Government",
        "phone": "102",
        "base_location": "Kamla Raja Hospital (KRH), Kampoo",
        "lat": 26.1965,
        "lng": 78.1618,
        "available": 1,
        "features": "Neonatal Warmers, Oxygen Delivery, Emergency Obstetric Delivery Kit"
    },
    {
        "service_name": "BIMR Cardiac Mobile Intensive Care Unit",
        "vehicle_type": "Mobile ICU (Cardiac Super Speciality)",
        "operator_type": "Hospital",
        "phone": "+91 751 2405601",
        "base_location": "BIMR Hospitals, Morar, Gwalior",
        "lat": 26.2312,
        "lng": 78.2215,
        "available": 1,
        "features": "Invasive Blood Pressure Monitoring, Syringe Pumps, Advanced Pacemaker, CPR Auto-Pulse"
    },
    {
        "service_name": "JAH Level-1 Trauma Emergency Ambulance",
        "vehicle_type": "ALS (Advanced Life Support)",
        "operator_type": "Government",
        "phone": "+91 751 2403222",
        "base_location": "Trauma Centre, JAH Kampoo",
        "lat": 26.1985,
        "lng": 78.1634,
        "available": 1,
        "features": "Spine Board, Cervical Collars, Ventilator, Resuscitation Bag, Suction Apparatus"
    },
    {
        "service_name": "Indian Red Cross Emergency Ambulance Service",
        "vehicle_type": "Patient Transport & BLS",
        "operator_type": "Trust",
        "phone": "+91 751 2422002",
        "base_location": "Phoolbagh, Lashkar, Gwalior",
        "lat": 26.2095,
        "lng": 78.1752,
        "available": 1,
        "features": "Oxygen Support, Stretcher, First-Aid Kit, Vital Signs Monitor"
    },
    {
        "service_name": "City Centre 24x7 Private ICU Ambulance Network",
        "vehicle_type": "ALS (Advanced Life Support)",
        "operator_type": "Private",
        "phone": "+91 94251 10002",
        "base_location": "University Road, City Centre, Gwalior",
        "lat": 26.2115,
        "lng": 78.2098,
        "available": 1,
        "features": "Cardiac Defibrillator, Ventilator, Medical Oxygen, On-board Paramedic Team"
    }
,
{
        "service_name": "Gwalior Air Ambulance & Critical Airlift Response",
        "vehicle_type": "Air Ambulance (Aero-Medical Airlift)",
        "operator_type": "Private",
        "phone": "+91 98260 11211",
        "base_location": "Airport Road, Maharajpura Airbase Hub, Gwalior",
        "lat": 26.2700,
        "lng": 78.2250,
        "available": 1,
        "features": "Aviation Ventilator, Transport Incubator, Multipara Cardiac Monitor, Emergency Flight Doctor"
    },
    {
        "service_name": "Trauma Rapid First-Responder Bike Ambulance Unit",
        "vehicle_type": "First Responder Medical Bike",
        "operator_type": "Government",
        "phone": "108",
        "base_location": "Phoolbagh Chowk, Lashkar Hub, Gwalior",
        "lat": 26.2088,
        "lng": 78.1745,
        "available": 1,
        "features": "Automated External Defibrillator (AED), Portable Oxygen Kit, Emergency Trauma Dressing, Paramedic Kit"
    }
]

def seed_database():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = OFF")
    cur.execute("DROP TABLE IF EXISTS services")
    cur.execute("DROP TABLE IF EXISTS beds")
    cur.execute("DROP TABLE IF EXISTS hospitals")
    cur.execute("DROP TABLE IF EXISTS doctors")
    cur.execute("DROP TABLE IF EXISTS blood_banks")
    cur.execute("DROP TABLE IF EXISTS blood_inventory")
    cur.execute("DROP TABLE IF EXISTS ambulances")
    conn.commit()
    conn.close()

    init_tables()
    conn = get_db()
    cur = conn.cursor()
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    # 1. Insert Hospitals
    for h in REAL_HOSPITALS:
        cur.execute("""
            INSERT INTO hospitals (
                id, name, type, category, address, locality, phone, emergency_phone,
                ambulance_phone, email, website, lat, lng, emergency_24x7, trauma_center,
                rating, reviews_count, opd_timings, consultation_fee, description,
                verified, active, source, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 1, 'real', ?)
        """, (
            h["id"], h["name"], h["type"], h["category"], h["address"], h["locality"],
            h["phone"], h["emergency_phone"], h.get("ambulance_phone", "108"),
            h.get("email", ""), h.get("website", ""), h["lat"], h["lng"],
            h["emergency_24x7"], h.get("trauma_center", 0), h["rating"],
            h["reviews_count"], h["opd_timings"], h["consultation_fee"],
            h["description"], now
        ))

        for s in h.get("services", []):
            cur.execute("INSERT INTO services (hospital_id, service) VALUES (?, ?)", (h["id"], s))

        for b_type, (tot, occ) in h.get("beds", {}).items():
            cur.execute("INSERT INTO beds (hospital_id, bed_type, total, occupied) VALUES (?, ?, ?, ?)",
                        (h["id"], b_type, tot, occ))

    # 2. Insert Doctors
    for d in REAL_DOCTORS:
        cur.execute("""
            INSERT INTO doctors (
                id, name, qualification, specialty, category, experience_years,
                hospital_id, hospital_name, clinic_address, phone, email,
                opd_timings, days_available, fee, rating, reviews_count, badge, about, avatar
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            d["id"], d["name"], d["qualification"], d["specialty"], d["category"],
            d["experience_years"], d["hospital_id"], d["hospital_name"], d["clinic_address"],
            d["phone"], d.get("email", ""), d["opd_timings"], d.get("days_available", "Mon - Sat"),
            d["fee"], d["rating"], d["reviews_count"], d["badge"], d["about"], d["avatar"]
        ))

    # 3. Insert Blood Banks & Inventory
    for bb in REAL_BLOOD_BANKS:
        cur.execute("""
            INSERT INTO blood_banks (
                name, hospital_id, address, contact_person, phone, emergency_24x7, lat, lng, verified
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            bb["name"], bb["hospital_id"], bb["address"], bb["contact_person"],
            bb["phone"], bb["emergency_24x7"], bb["lat"], bb["lng"]
        ))
        bb_id = cur.lastrowid

        for b_group, units in bb["inventory"].items():
            cur.execute("""
                INSERT INTO blood_inventory (blood_bank_id, blood_group, units_available, last_updated)
                VALUES (?, ?, ?, ?)
            """, (bb_id, b_group, units, now))

    # 4. Insert Ambulances
    for amb in REAL_AMBULANCES:
        cur.execute("""
            INSERT INTO ambulances (
                service_name, vehicle_type, operator_type, phone, base_location, lat, lng, available, features
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            amb["service_name"], amb["vehicle_type"], amb["operator_type"], amb["phone"],
            amb["base_location"], amb["lat"], amb["lng"], amb["available"], amb["features"]
        ))

    # 5. Insert Default Demo User & Admin
    cur.execute("CREATE TABLE IF NOT EXISTS admins (username TEXT PRIMARY KEY, password_hash TEXT NOT NULL)")
    cur.execute("INSERT OR REPLACE INTO admins VALUES ('admin', ?)", (generate_password_hash("admin123"),))

    cur.execute("""
        INSERT OR IGNORE INTO users (name, phone, email, password_hash, created_at)
        VALUES ('Rahul Sharma', '9826012345', 'rahul@example.com', ?, ?)
    """, (generate_password_hash("password123"), now))

    conn.commit()
    conn.close()
    print("Database successfully seeded with authentic Gwalior medical infrastructure!")

if __name__ == "__main__":
    seed_database()
