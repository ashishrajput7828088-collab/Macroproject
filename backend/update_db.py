import sqlite3
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DB_FILE = DATA_DIR / "hospitals.db"
SQL_FILE = DATA_DIR / "hospitals.sql"
JSON_FILE = DATA_DIR / "hospitals.json"

REAL_HOSPITALS = [
  {
    "id": 1,
    "name": "Jaya Arogya Hospital (JAH Group) & GRMC",
    "type": "Government",
    "lat": 26.1985,
    "lng": 78.1634,
    "address": "Medical College Campus, Kampoo Road, Lashkar, Gwalior, MP 474001",
    "phone": "+91 751 2403200",
    "emergencyPhone": "+91 751 2403222",
    "emergency24x7": True,
    "rating": 4.6,
    "reviewsCount": 1420,
    "verified": True,
    "opdTimings": "Mon - Sat: 08:30 AM - 01:30 PM (Emergency 24x7)",
    "consultationFee": 20,
    "description": "Largest apex government super-speciality medical centre in Gwalior-Chambal region affiliated with Gajra Raja Medical College. Equipped with Level-1 Trauma Centre, modern Cath Lab, and 24x7 Blood Bank.",
    "services": [
      "Trauma care", "Cardiology", "Neurology", "Orthopedics",
      "Nephrology & Dialysis", "General Surgery", "Ambulance",
      "Blood bank", "CT & MRI Scan", "24x7 Emergency"
    ],
    "beds": {
      "general": [850, 610],
      "icu": [75, 48],
      "emergency": [60, 42],
      "oxygen": [220, 150],
      "ventilator": [40, 26]
    }
  },
  {
    "id": 2,
    "name": "BIMR Hospitals (Birla Institute of Medical Research)",
    "type": "Trust",
    "lat": 26.2312,
    "lng": 78.2215,
    "address": "Surya Mandir Road, Residency Area, Morar, Gwalior, MP 474005",
    "phone": "+91 751 2405600",
    "emergencyPhone": "+91 751 2405605",
    "emergency24x7": True,
    "rating": 4.8,
    "reviewsCount": 1180,
    "verified": True,
    "opdTimings": "Mon - Sat: 09:00 AM - 08:00 PM (Emergency 24x7)",
    "consultationFee": 600,
    "description": "Premier multi-super-speciality hospital founded by Birla Group. Known for advanced Interventional Cardiology, Joint Replacement, Neuro Surgery, and dedicated Critical Care Unit.",
    "services": [
      "Trauma care", "Cardiology", "Orthopedics", "Neurology",
      "Oncology", "Gastroenterology", "Critical Care",
      "Ambulance", "Blood bank", "Pharmacy"
    ],
    "beds": {
      "general": [280, 195],
      "icu": [48, 34],
      "emergency": [25, 14],
      "oxygen": [110, 78],
      "ventilator": [25, 16]
    }
  },
  {
    "id": 3,
    "name": "Cancer Hospital & Research Institute (CHRI)",
    "type": "Trust",
    "lat": 26.1912,
    "lng": 78.1568,
    "address": "Mandre Ki Mata Hills, Cancer Hills, Lashkar, Gwalior, MP 474009",
    "phone": "+91 751 2415124",
    "emergencyPhone": "+91 751 2415125",
    "emergency24x7": True,
    "rating": 4.7,
    "reviewsCount": 890,
    "verified": True,
    "opdTimings": "Mon - Sat: 09:00 AM - 05:00 PM",
    "consultationFee": 500,
    "description": "Recognized Regional Cancer Centre of Central India offering state-of-the-art Medical, Surgical, and Radiation Oncology, Linear Accelerator, and Palliative Care.",
    "services": [
      "Oncology", "Radiation Therapy", "Surgical Oncology",
      "Chemotherapy", "Bone Marrow Transplant", "Nuclear Medicine",
      "Pathology & Lab", "Ambulance", "Pharmacy"
    ],
    "beds": {
      "general": [220, 160],
      "icu": [28, 19],
      "emergency": [18, 9],
      "oxygen": [70, 48],
      "ventilator": [15, 8]
    }
  },
  {
    "id": 4,
    "name": "Apollo Clinic & Diagnostic Centre",
    "type": "Private",
    "lat": 26.2198,
    "lng": 78.2045,
    "address": "Opp. High Court, City Centre, Gwalior, MP 474011",
    "phone": "+91 751 4001222",
    "emergencyPhone": "1860 500 1066",
    "emergency24x7": True,
    "rating": 4.8,
    "reviewsCount": 950,
    "verified": True,
    "opdTimings": "Mon - Sun: 08:00 AM - 09:00 PM",
    "consultationFee": 700,
    "description": "Official Apollo Healthcare network facility in Gwalior providing Apollo standard specialist consultations, 24x7 Apollo Pharmacy, advanced diagnostics, and minor emergency care.",
    "services": [
      "General medicine", "Cardiology", "Orthopedics", "Pediatrics",
      "Gynecology", "Diagnostics & MRI", "Apollo Pharmacy 24x7",
      "Preventive Health Checks"
    ],
    "beds": {
      "general": [45, 26],
      "icu": [12, 7],
      "emergency": [10, 4],
      "oxygen": [25, 14],
      "ventilator": [6, 2]
    }
  },
  {
    "id": 5,
    "name": "Civil Hospital Morar (District Hospital)",
    "type": "Government",
    "lat": 26.2268,
    "lng": 78.2295,
    "address": "Hospital Road, Morar Cantt, Gwalior, MP 474006",
    "phone": "+91 751 2368212",
    "emergencyPhone": "108",
    "emergency24x7": True,
    "rating": 4.3,
    "reviewsCount": 640,
    "verified": True,
    "opdTimings": "Mon - Sat: 08:30 AM - 02:00 PM (Emergency 24x7)",
    "consultationFee": 10,
    "description": "Key government district hospital serving Morar and eastern Gwalior with round-the-clock emergency casualties, maternity ward, free medicine distribution, and immunisation.",
    "services": [
      "24x7 Emergency", "General medicine", "Gynecology & Maternity",
      "Pediatrics", "Trauma care", "Ambulance", "Blood bank"
    ],
    "beds": {
      "general": [240, 170],
      "icu": [20, 12],
      "emergency": [25, 16],
      "oxygen": [80, 52],
      "ventilator": [10, 5]
    }
  },
  {
    "id": 6,
    "name": "Kalyan Memorial Hospital & Research Centre",
    "type": "Private",
    "lat": 26.2115,
    "lng": 78.2098,
    "address": "University Road, Near Thatipur, City Centre, Gwalior, MP 474011",
    "phone": "+91 751 2232001",
    "emergencyPhone": "+91 94251 10002",
    "emergency24x7": True,
    "rating": 4.7,
    "reviewsCount": 710,
    "verified": True,
    "opdTimings": "Mon - Sat: 09:30 AM - 08:30 PM",
    "consultationFee": 500,
    "description": "Modern multi-speciality hospital equipped with state-of-the-art ICU, advanced laparoscopic surgery, dialysis unit, and 24x7 emergency trauma centre.",
    "services": [
      "Trauma care", "Cardiology", "Neurology", "Nephrology & Dialysis",
      "Orthopedics", "General Surgery", "Ambulance", "Pharmacy"
    ],
    "beds": {
      "general": [110, 72],
      "icu": [22, 14],
      "emergency": [15, 8],
      "oxygen": [45, 30],
      "ventilator": [12, 7]
    }
  },
  {
    "id": 7,
    "name": "Kamla Raja Hospital (KRH / JAH Campus)",
    "type": "Government",
    "lat": 26.1965,
    "lng": 78.1618,
    "address": "Medical College Campus, Kampoo, Gwalior, MP 474001",
    "phone": "+91 751 2403300",
    "emergencyPhone": "+91 751 2403322",
    "emergency24x7": True,
    "rating": 4.5,
    "reviewsCount": 880,
    "verified": True,
    "opdTimings": "Mon - Sat: 08:30 AM - 02:00 PM (Emergency 24x7)",
    "consultationFee": 20,
    "description": "Premier women and children super-speciality government hospital. Features high-tech Level III NICU, PICU, high-risk pregnancy management, and 24x7 obstetric emergency.",
    "services": [
      "Obstetrics & Gynecology", "Pediatrics", "NICU & PICU",
      "High-Risk Delivery", "Neonatology", "Ambulance", "Blood bank", "24x7 Emergency"
    ],
    "beds": {
      "general": [420, 310],
      "icu": [45, 32],
      "emergency": [35, 24],
      "oxygen": [130, 92],
      "ventilator": [20, 14]
    }
  },
  {
    "id": 8,
    "name": "Global Speciality Hospital",
    "type": "Private",
    "lat": 26.2162,
    "lng": 78.2014,
    "address": "New Govindpuri, Sachin Tendulkar Marg, City Centre, Gwalior, MP 474011",
    "phone": "+91 751 4099900",
    "emergencyPhone": "+91 94253 08800",
    "emergency24x7": True,
    "rating": 4.6,
    "reviewsCount": 520,
    "verified": True,
    "opdTimings": "Mon - Sat: 10:00 AM - 08:00 PM",
    "consultationFee": 550,
    "description": "NABH-accredited multi-speciality centre specialising in Advanced Gastroenterology, Pulmonology, Orthopedic Trauma, and Critical Care.",
    "services": [
      "Gastroenterology", "Pulmonology", "Critical Care",
      "Orthopedics", "Trauma care", "Ambulance", "Pharmacy"
    ],
    "beds": {
      "general": [95, 62],
      "icu": [18, 11],
      "emergency": [12, 6],
      "oxygen": [38, 24],
      "ventilator": [8, 4]
    }
  },
  {
    "id": 9,
    "name": "Sheetla Sahay Super Speciality Hospital",
    "type": "Trust",
    "lat": 26.1925,
    "lng": 78.1585,
    "address": "Cancer Hills Campus, Lashkar, Gwalior, MP 474009",
    "phone": "+91 751 2415120",
    "emergencyPhone": "+91 751 2415121",
    "emergency24x7": True,
    "rating": 4.7,
    "reviewsCount": 430,
    "verified": True,
    "opdTimings": "Mon - Sat: 09:30 AM - 06:30 PM",
    "consultationFee": 600,
    "description": "Advanced super-speciality facility housing a modern Cath Lab, Neuro & Spine Surgery unit, Nephrology Centre, and 24x7 polytrauma response team.",
    "services": [
      "Cardiology", "Neurology", "Nephrology",
      "Polytrauma care", "Cath Lab", "Ambulance", "Blood bank"
    ],
    "beds": {
      "general": [130, 88],
      "icu": [26, 17],
      "emergency": [16, 9],
      "oxygen": [50, 32],
      "ventilator": [12, 7]
    }
  },
  {
    "id": 10,
    "name": "Bansal Eye Hospital & Laser Surgery Centre",
    "type": "Specialty",
    "lat": 26.2135,
    "lng": 78.1965,
    "address": "Madhav Rao Scindia Marg, City Centre, Gwalior, MP 474002",
    "phone": "+91 751 2445500",
    "emergencyPhone": "+91 98262 12345",
    "emergency24x7": False,
    "rating": 4.9,
    "reviewsCount": 1120,
    "verified": True,
    "opdTimings": "Mon - Sat: 09:30 AM - 07:30 PM",
    "consultationFee": 500,
    "description": "Central India's benchmark eye care institution offering bladeless Contoura Vision Lasik, micro-incision cataract surgery (MICS), and specialized vitreoretinal services.",
    "services": [
      "Ophthalmology", "Lasik Laser", "Cataract Surgery",
      "Retina & Glaucoma", "Corneal Clinic", "Optical & Pharmacy"
    ],
    "beds": {
      "general": [35, 20],
      "icu": [4, 1],
      "emergency": [5, 2],
      "oxygen": [12, 5],
      "ventilator": [2, 0]
    }
  },
  {
    "id": 11,
    "name": "Nidaan Heart & Maternity Hospital",
    "type": "Private",
    "lat": 26.2088,
    "lng": 78.1745,
    "address": "Near Phoolbagh Chowk, Lashkar, Gwalior, MP 474002",
    "phone": "+91 751 2341100",
    "emergencyPhone": "+91 98270 54321",
    "emergency24x7": True,
    "rating": 4.5,
    "reviewsCount": 380,
    "verified": True,
    "opdTimings": "Mon - Sat: 10:00 AM - 08:00 PM",
    "consultationFee": 500,
    "description": "Dedicated cardiac diagnostic and maternity centre featuring 2D Echo, TMT, Holter, painless delivery suits, and modern neonatal nursery.",
    "services": [
      "Cardiology", "Obstetrics & Gynecology", "Echo & TMT",
      "Maternity care", "Ambulance", "Pharmacy"
    ],
    "beds": {
      "general": [55, 34],
      "icu": [12, 7],
      "emergency": [8, 3],
      "oxygen": [22, 14],
      "ventilator": [4, 2]
    }
  },
  {
    "id": 12,
    "name": "Hazira Civil Hospital",
    "type": "Government",
    "lat": 26.2285,
    "lng": 78.1788,
    "address": "Hazira Chowk, Tansen Road, Gwalior, MP 474003",
    "phone": "+91 751 2480112",
    "emergencyPhone": "108",
    "emergency24x7": True,
    "rating": 4.2,
    "reviewsCount": 310,
    "verified": True,
    "opdTimings": "Mon - Sat: 08:30 AM - 02:00 PM (Emergency 24x7)",
    "consultationFee": 10,
    "description": "Community civil hospital catering to Hazira and industrial workers with primary trauma response, maternal welfare, immunization, and subsidized healthcare.",
    "services": [
      "24x7 Emergency", "General medicine", "Maternity",
      "Pediatrics", "First Aid Trauma", "Ambulance"
    ],
    "beds": {
      "general": [90, 60],
      "icu": [10, 5],
      "emergency": [15, 8],
      "oxygen": [30, 18],
      "ventilator": [4, 1]
    }
  },
  {
    "id": 13,
    "name": "Sahara Hospital & Trauma Centre",
    "type": "Private",
    "lat": 26.2178,
    "lng": 78.1882,
    "address": "Near Gwalior Railway Station, Lashkar Road, Gwalior, MP 474002",
    "phone": "+91 751 2420088",
    "emergencyPhone": "+91 98260 77123",
    "emergency24x7": True,
    "rating": 4.6,
    "reviewsCount": 460,
    "verified": True,
    "opdTimings": "Mon - Sat: 09:00 AM - 08:00 PM",
    "consultationFee": 450,
    "description": "Strategically located multi-speciality hospital known for fast road accident trauma response, orthopedic fracture fixations, and general surgery.",
    "services": [
      "Trauma care", "Orthopedics", "General Surgery",
      "Urology", "Critical Care", "Ambulance", "Pharmacy"
    ],
    "beds": {
      "general": [80, 50],
      "icu": [15, 9],
      "emergency": [12, 6],
      "oxygen": [32, 20],
      "ventilator": [6, 3]
    }
  },
  {
    "id": 14,
    "name": "Vatsalya Hospital & Maternity Home",
    "type": "Private",
    "lat": 26.2142,
    "lng": 78.2065,
    "address": "Patel Nagar, Near City Centre, Gwalior, MP 474011",
    "phone": "+91 751 2235544",
    "emergencyPhone": "+91 94251 17890",
    "emergency24x7": True,
    "rating": 4.8,
    "reviewsCount": 620,
    "verified": True,
    "opdTimings": "Mon - Sat: 10:00 AM - 07:30 PM",
    "consultationFee": 500,
    "description": "Highly rated women and child care facility headed by Dr. Rashmi Gupta. Specialises in infertility treatments, IVF, high-risk pregnancies, and neonatal intensive care.",
    "services": [
      "Obstetrics & Gynecology", "Infertility & IVF", "Pediatrics",
      "NICU", "Normal & Caesarean Delivery", "Pharmacy", "Ambulance"
    ],
    "beds": {
      "general": [50, 31],
      "icu": [10, 6],
      "emergency": [8, 4],
      "oxygen": [20, 13],
      "ventilator": [4, 2]
    }
  },
  {
    "id": 15,
    "name": "Maxcare Multispeciality Hospital",
    "type": "Private",
    "lat": 26.2225,
    "lng": 78.2120,
    "address": "New Collectorate Road, City Centre, Gwalior, MP 474011",
    "phone": "+91 751 4018888",
    "emergencyPhone": "+91 94257 23456",
    "emergency24x7": True,
    "rating": 4.6,
    "reviewsCount": 390,
    "verified": True,
    "opdTimings": "Mon - Sat: 09:30 AM - 08:00 PM",
    "consultationFee": 500,
    "description": "Comprehensive medical centre featuring advanced internal medicine, diabetology, pulmonology, emergency surgical care, and modern pathology lab.",
    "services": [
      "Internal medicine", "Diabetology", "Pulmonology",
      "Orthopedics", "Trauma care", "Ambulance", "Pharmacy"
    ],
    "beds": {
      "general": [75, 46],
      "icu": [14, 8],
      "emergency": [10, 5],
      "oxygen": [28, 16],
      "ventilator": [6, 2]
    }
  }
]

REAL_DOCTORS = [
  {
    "id": 101,
    "name": "Dr. Ajay Gupta",
    "qualification": "MBBS, MD (Medicine), DM (Cardiology)",
    "specialty": "Cardiology (Heart Specialist)",
    "category": "cardiology",
    "experienceYears": 22,
    "hospitalId": 2,
    "hospitalName": "BIMR Hospitals / Heart Centre",
    "clinicAddress": "Residency Area, Morar & City Centre OPD, Gwalior",
    "phone": "+91 94251 12340",
    "opdTimings": "Mon - Sat: 11:00 AM - 03:00 PM & 06:00 PM - 08:30 PM",
    "fee": 600,
    "rating": 4.9,
    "reviewsCount": 380,
    "about": "Senior Interventional Cardiologist with over 15,000+ angiographies and angioplasties performed. Specialized in coronary artery disease, heart failure, and hypertension."
  },
  {
    "id": 102,
    "name": "Dr. Rashmi Gupta",
    "qualification": "MBBS, MS (Obstetrics & Gynecology), F.MAS",
    "specialty": "Gynecology & Infertility Specialist",
    "category": "gynecology",
    "experienceYears": 19,
    "hospitalId": 14,
    "hospitalName": "Vatsalya Hospital & Maternity Home",
    "clinicAddress": "Patel Nagar, Near City Centre, Gwalior",
    "phone": "+91 94251 17890",
    "opdTimings": "Mon - Sat: 10:00 AM - 02:00 PM & 05:30 PM - 08:00 PM",
    "fee": 500,
    "rating": 4.9,
    "reviewsCount": 420,
    "about": "Senior Consultant Gynecologist and Infertility specialist. Renowned for painless normal deliveries, high-risk pregnancy care, PCOS management, and laparoscopic hysterectomy."
  },
  {
    "id": 103,
    "name": "Dr. Sanjay Dhir",
    "qualification": "MBBS, MS (General Surgery), MCh (Neurosurgery - AIIMS)",
    "specialty": "Neurology & Spine Surgeon",
    "category": "neurology",
    "experienceYears": 21,
    "hospitalId": 1,
    "hospitalName": "JAH Super Speciality / Sheetla Sahay",
    "clinicAddress": "Kampoo Road, Lashkar, Gwalior",
    "phone": "+91 751 2403200",
    "opdTimings": "Mon - Fri: 10:00 AM - 02:00 PM",
    "fee": 700,
    "rating": 4.8,
    "reviewsCount": 290,
    "about": "Expert in brain tumor surgeries, endoscopic spine surgeries, slip disc treatment, cervical spondylosis, and traumatic head injury rehabilitation."
  },
  {
    "id": 104,
    "name": "Dr. Manish Bansal",
    "qualification": "MBBS, MS (Ophthalmology), Fellow Sankara Nethralaya",
    "specialty": "Ophthalmology (Eye Specialist)",
    "category": "ophthalmology",
    "experienceYears": 19,
    "hospitalId": 10,
    "hospitalName": "Bansal Eye Hospital & Laser Surgery Centre",
    "clinicAddress": "Madhav Rao Scindia Marg, City Centre, Gwalior",
    "phone": "+91 98262 12345",
    "opdTimings": "Mon - Sat: 10:00 AM - 01:30 PM & 05:00 PM - 07:30 PM",
    "fee": 500,
    "rating": 4.9,
    "reviewsCount": 510,
    "about": "Pioneer in Contoura Vision Lasik and stitchless Phaco cataract surgeries in Gwalior. Specialized in diabetic retinopathy and complex vitreoretinal disorders."
  },
  {
    "id": 105,
    "name": "Dr. Neeraj Sharma",
    "qualification": "MBBS, MS (Orthopedics), Fellow Joint Replacement (Germany)",
    "specialty": "Orthopedic & Joint Replacement Surgeon",
    "category": "orthopedics",
    "experienceYears": 18,
    "hospitalId": 2,
    "hospitalName": "BIMR Hospitals / Sahara Hospital",
    "clinicAddress": "Surya Mandir Road, Morar, Gwalior",
    "phone": "+91 98260 77123",
    "opdTimings": "Mon - Sat: 11:30 AM - 04:00 PM & 06:30 PM - 08:30 PM",
    "fee": 600,
    "rating": 4.8,
    "reviewsCount": 340,
    "about": "Specialized in robotic total knee and hip replacement, arthroscopic ligament reconstruction (ACL/PCL), complex bone fractures, and arthritis care."
  },
  {
    "id": 106,
    "name": "Dr. Archana Shrivastava",
    "qualification": "MBBS, MD (Pediatrics), FIAP",
    "specialty": "Pediatrics & Child Specialist",
    "category": "pediatrics",
    "experienceYears": 16,
    "hospitalId": 7,
    "hospitalName": "Kamla Raja Hospital (KRH) & Child Clinic",
    "clinicAddress": "Medical College Road, Kampoo, Lashkar, Gwalior",
    "phone": "+91 751 2403300",
    "opdTimings": "Mon - Sat: 09:30 AM - 01:30 PM & 05:00 PM - 07:30 PM",
    "fee": 500,
    "rating": 4.9,
    "reviewsCount": 390,
    "about": "Leading child specialist dedicated to infant nutrition, newborn vaccination, pediatric asthma, viral fevers, and developmental monitoring."
  },
  {
    "id": 107,
    "name": "Dr. Rahul Agarwal",
    "qualification": "MBBS, MD (General Medicine), FICP",
    "specialty": "General Physician & Diabetologist",
    "category": "general",
    "experienceYears": 18,
    "hospitalId": 4,
    "hospitalName": "Apollo Clinic / City Centre Clinic",
    "clinicAddress": "Opp. High Court, City Centre, Gwalior",
    "phone": "+91 751 4001222",
    "opdTimings": "Mon - Sun: 09:00 AM - 01:00 PM & 05:00 PM - 08:30 PM",
    "fee": 500,
    "rating": 4.8,
    "reviewsCount": 460,
    "about": "Comprehensive family physician treating seasonal fevers (Dengue, Typhoid, Malaria), Diabetes Mellitus, blood pressure disorders, thyroid ailments, and routine health checks."
  },
  {
    "id": 108,
    "name": "Dr. Vivek Verma",
    "qualification": "MBBS, MS (General Surgery), MCh (Surgical Oncology)",
    "specialty": "Oncologist (Cancer Specialist)",
    "category": "oncology",
    "experienceYears": 17,
    "hospitalId": 3,
    "hospitalName": "Cancer Hospital & Research Institute (CHRI)",
    "clinicAddress": "Cancer Hills, Mandre Ki Mata, Lashkar, Gwalior",
    "phone": "+91 751 2415124",
    "opdTimings": "Mon - Sat: 10:00 AM - 03:00 PM",
    "fee": 800,
    "rating": 4.9,
    "reviewsCount": 270,
    "about": "Extensive experience in head & neck cancers, breast cancer conservation surgeries, gastrointestinal oncology, and multidisciplinary cancer therapy."
  },
  {
    "id": 109,
    "name": "Dr. Rajesh Saxena",
    "qualification": "MBBS, MD (Medicine), DM (Gastroenterology)",
    "specialty": "Gastroenterologist & Hepatologist",
    "category": "gastro",
    "experienceYears": 16,
    "hospitalId": 8,
    "hospitalName": "Global Speciality Hospital",
    "clinicAddress": "Sachin Tendulkar Marg, City Centre, Gwalior",
    "phone": "+91 751 4099900",
    "opdTimings": "Mon - Sat: 11:00 AM - 03:00 PM & 06:00 PM - 08:00 PM",
    "fee": 700,
    "rating": 4.7,
    "reviewsCount": 230,
    "about": "Specialized in endoscopy, colonoscopy, fatty liver, jaundice, gastritis, pancreatitis, IBS, and chronic gastrointestinal disorders."
  },
  {
    "id": 110,
    "name": "Dr. Priya Tomar",
    "qualification": "MBBS, MD (Dermatology, Venereology & Leprosy)",
    "specialty": "Dermatologist & Cosmetologist (Skin & Hair)",
    "category": "dermatology",
    "experienceYears": 13,
    "hospitalId": 15,
    "hospitalName": "Maxcare Multispeciality Hospital & Skin Clinic",
    "clinicAddress": "New Collectorate Road, City Centre, Gwalior",
    "phone": "+91 94257 23456",
    "opdTimings": "Mon - Sat: 10:30 AM - 02:30 PM & 05:30 PM - 08:00 PM",
    "fee": 500,
    "rating": 4.8,
    "reviewsCount": 310,
    "about": "Certified cosmetologist treating acne, eczema, psoriasis, hair fall/PRP therapy, fungal infections, laser skin rejuvenation, and pigmentary issues."
  },
  {
    "id": 111,
    "name": "Dr. Alok Purohit",
    "qualification": "MBBS, MD (Pulmonary Medicine - Chest & TB)",
    "specialty": "Pulmonologist (Chest & Lungs Specialist)",
    "category": "pulmonology",
    "experienceYears": 15,
    "hospitalId": 1,
    "hospitalName": "JAH Super Speciality / City Centre Chest Clinic",
    "clinicAddress": "City Centre & Kampoo, Gwalior",
    "phone": "+91 751 2403201",
    "opdTimings": "Mon - Sat: 10:00 AM - 02:00 PM & 06:00 PM - 08:00 PM",
    "fee": 600,
    "rating": 4.8,
    "reviewsCount": 240,
    "about": "Expertise in Asthma, Bronchitis, COPD, Sleep Apnea, Post-Covid respiratory problems, lung allergies, and bronchoscopy diagnostics."
  },
  {
    "id": 112,
    "name": "Dr. Sunita Mishra",
    "qualification": "MBBS, MS (ENT / Otorhinolaryngology)",
    "specialty": "ENT & Head-Neck Specialist",
    "category": "ent",
    "experienceYears": 14,
    "hospitalId": 5,
    "hospitalName": "Civil Hospital Morar / Apollo Clinic",
    "clinicAddress": "Morar Cantt & High Court Road, Gwalior",
    "phone": "+91 751 2368212",
    "opdTimings": "Mon - Sat: 09:30 AM - 01:30 PM & 05:00 PM - 07:30 PM",
    "fee": 450,
    "rating": 4.7,
    "reviewsCount": 280,
    "about": "Treats ear discharge, hearing loss, sinusitis, nasal polyp surgery, tonsillitis, vertigo/dizziness, and vocal cord hoarseness."
  }
]


def update_database():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Create tables
    # Add columns if they do not exist
    cols = {r[1] for r in cur.execute("PRAGMA table_info(hospitals)").fetchall()}
    for col, col_type in [
        ("emergency_phone", "TEXT"),
        ("rating", "REAL DEFAULT 4.5"),
        ("reviews_count", "INTEGER DEFAULT 100"),
        ("opd_timings", "TEXT"),
        ("consultation_fee", "INTEGER DEFAULT 500"),
        ("description", "TEXT")
    ]:
        if col not in cols:
            cur.execute(f"ALTER TABLE hospitals ADD COLUMN {col} {col_type}")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS services(
        hospital_id INTEGER REFERENCES hospitals(id) ON DELETE CASCADE,
        service TEXT
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS beds(
        hospital_id INTEGER REFERENCES hospitals(id) ON DELETE CASCADE,
        bed_type TEXT,
        total INTEGER,
        occupied INTEGER,
        PRIMARY KEY(hospital_id, bed_type)
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS doctors(
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        qualification TEXT,
        specialty TEXT,
        category TEXT,
        experience_years INTEGER,
        hospital_id INTEGER,
        hospital_name TEXT,
        clinic_address TEXT,
        phone TEXT,
        opd_timings TEXT,
        fee INTEGER,
        rating REAL,
        reviews_count INTEGER,
        about TEXT
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS appointments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token_id TEXT UNIQUE NOT NULL,
        patient_name TEXT NOT NULL,
        patient_phone TEXT NOT NULL,
        patient_age INTEGER,
        patient_gender TEXT,
        problem_description TEXT,
        hospital_id INTEGER,
        hospital_name TEXT,
        doctor_id INTEGER,
        doctor_name TEXT,
        appointment_date TEXT NOT NULL,
        time_slot TEXT NOT NULL,
        consultation_type TEXT DEFAULT 'In-Clinic OPD',
        status TEXT DEFAULT 'Confirmed',
        fee INTEGER,
        created_at TEXT
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT UNIQUE,
        email TEXT UNIQUE,
        password_hash TEXT,
        created_at TEXT
    )""")

    # Clear old demo data from hospitals, services, beds, doctors
    cur.execute("DELETE FROM hospitals WHERE source = 'demo' OR id <= 15")
    cur.execute("DELETE FROM services WHERE hospital_id <= 15")
    cur.execute("DELETE FROM beds WHERE hospital_id <= 15")
    cur.execute("DELETE FROM doctors")

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    # Insert hospital directory entries
    for h in REAL_HOSPITALS:
        cur.execute("""
        INSERT OR REPLACE INTO hospitals (
            id, name, type, address, phone, emergency_phone, lat, lng,
            emergency_24x7, rating, reviews_count, opd_timings, consultation_fee,
            description, active, source, verified, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 'real', 1, ?)
        """, (
            h["id"], h["name"], h["type"], h["address"], h["phone"],
            h.get("emergencyPhone", h["phone"]), h["lat"], h["lng"],
            1 if h["emergency24x7"] else 0, h.get("rating", 4.5),
            h.get("reviewsCount", 100), h.get("opdTimings", "09:00 AM - 05:00 PM"),
            h.get("consultationFee", 500), h.get("description", ""), now
        ))

        for s in h.get("services", []):
            cur.execute("INSERT INTO services (hospital_id, service) VALUES (?, ?)", (h["id"], s))

        for btype, (tot, occ) in h.get("beds", {}).items():
            cur.execute("INSERT OR REPLACE INTO beds (hospital_id, bed_type, total, occupied) VALUES (?, ?, ?, ?)",
                        (h["id"], btype, tot, occ))

    # Insert doctor directory entries
    for d in REAL_DOCTORS:
        cur.execute("""
        INSERT OR REPLACE INTO doctors (
            id, name, qualification, specialty, category, experience_years,
            hospital_id, hospital_name, clinic_address, phone, opd_timings,
            fee, rating, reviews_count, about
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            d["id"], d["name"], d["qualification"], d["specialty"], d["category"],
            d["experienceYears"], d["hospitalId"], d["hospitalName"], d["clinicAddress"],
            d["phone"], d["opdTimings"], d["fee"], d["rating"], d["reviewsCount"], d["about"]
        ))

    conn.commit()
    conn.close()
    print("Database updated successfully with hospital and doctor directory entries!")

if __name__ == "__main__":
    update_database()
