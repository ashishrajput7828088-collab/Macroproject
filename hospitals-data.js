/**
 * Hospital & Doctor Directory for Gwalior, Madhya Pradesh
 * Authoritative medical infrastructure dataset synced with Arogya Gwalior SQLite database.
 * Total: 22 Hospitals, 18 Specialist Doctors, 7 Blood Banks, 8 24x7 Ambulances.
 */

const HOSPITAL_DATABASE = [
  {
    "id": 10,
    "name": "Bansal Eye Hospital & Laser Surgery Centre",
    "type": "Specialty",
    "lat": 26.2135,
    "lng": 78.1965,
    "address": "Madhav Rao Scindia Marg, City Centre, Gwalior, MP 474002",
    "phone": "+91 751 2445500",
    "emergencyPhone": "+91 751 2445500",
    "emergency24x7": true,
    "rating": 4.9,
    "reviewsCount": 150,
    "verified": true,
    "opdTimings": "09:00 AM - 05:00 PM",
    "consultationFee": 500,
    "description": "Premier eye care hospital in Central India. Equipped with Contoura Vision Lasik, stitchless Micro-Phaco cataract surgery, Vitreoretinal surgery, and Glaucoma clinics.",
    "services": [
      "Contoura Vision Lasik",
      "Micro-Phaco Cataract Surgery",
      "Vitreoretina & Lasers",
      "Cornea & Refractive Surgery",
      "Pediatric Ophthalmology",
      "Glaucoma Clinic",
      "Optical Studio"
    ],
    "beds": {
      "general": [
        35,
        18
      ],
      "icu": [
        4,
        1
      ],
      "emergency": [
        5,
        2
      ],
      "oxygen": [
        12,
        4
      ],
      "ventilator": [
        2,
        0
      ]
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
    "emergencyPhone": "+91 751 2405600",
    "emergency24x7": true,
    "rating": 4.8,
    "reviewsCount": 150,
    "verified": true,
    "opdTimings": "09:00 AM - 05:00 PM",
    "consultationFee": 500,
    "description": "Prestigious 350-bed multi-super-speciality hospital founded by the Birla Group. NABH accredited with state-of-the-art Cath Lab, Robotic Joint Replacement, and Critical Care Unit.",
    "services": [
      "24x7 Cardiac Emergency",
      "Joint Replacement & Arthroscopy",
      "Neurosurgery & Spine",
      "Medical & Surgical Oncology",
      "Advanced Gastroenterology",
      "Intensive Critical Care",
      "Dialysis Unit",
      "Blood Component Separation",
      "Pharmacy 24x7",
      "Cardiac Mobile ICU"
    ],
    "beds": {
      "general": [
        280,
        190
      ],
      "icu": [
        50,
        36
      ],
      "emergency": [
        25,
        14
      ],
      "oxygen": [
        110,
        75
      ],
      "ventilator": [
        25,
        17
      ]
    }
  },
  {
    "id": 4,
    "name": "Apollo Clinic & Diagnostic Centre Gwalior",
    "type": "Private",
    "lat": 26.2198,
    "lng": 78.2045,
    "address": "Opp. High Court Road, City Centre, Gwalior, MP 474011",
    "phone": "+91 751 4001222",
    "emergencyPhone": "+91 751 4001222",
    "emergency24x7": true,
    "rating": 4.8,
    "reviewsCount": 150,
    "verified": true,
    "opdTimings": "09:00 AM - 05:00 PM",
    "consultationFee": 500,
    "description": "Apollo Hospitals network flagship centre in Gwalior providing super-specialist consultations, preventive health checks, 24x7 Apollo Pharmacy, and advanced MRI/CT diagnostics.",
    "services": [
      "Cardiology Consultations",
      "Orthopedic OPD",
      "Pediatrics & Neonatology",
      "Gynecology & Women Health",
      "Apollo 24x7 Pharmacy",
      "Advanced MRI & Ultrasound",
      "Home Sample Collection",
      "Preventive Health Checkups"
    ],
    "beds": {
      "general": [
        45,
        24
      ],
      "icu": [
        12,
        6
      ],
      "emergency": [
        10,
        4
      ],
      "oxygen": [
        25,
        12
      ],
      "ventilator": [
        6,
        2
      ]
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
    "emergencyPhone": "+91 751 2235544",
    "emergency24x7": true,
    "rating": 4.8,
    "reviewsCount": 150,
    "verified": true,
    "opdTimings": "09:00 AM - 05:00 PM",
    "consultationFee": 500,
    "description": "Founded by senior gynecologist Dr. Rashmi Gupta. Specialises in advanced infertility management, test tube baby (IVF), high-risk pregnancies, and neonatal intensive care (NICU).",
    "services": [
      "Infertility & IVF Centre",
      "High-Risk Pregnancy",
      "Normal & Cesarean Delivery",
      "NICU Level-II",
      "Pediatrics",
      "24x7 Emergency Labor",
      "Pharmacy"
    ],
    "beds": {
      "general": [
        50,
        28
      ],
      "icu": [
        10,
        5
      ],
      "emergency": [
        8,
        3
      ],
      "oxygen": [
        20,
        11
      ],
      "ventilator": [
        4,
        1
      ]
    }
  },
  {
    "id": 21,
    "name": "Chirayu Children Hospital & Neonatal ICU (NICU)",
    "type": "Specialty",
    "lat": 26.214,
    "lng": 78.199,
    "address": "Patel Nagar, Near City Centre Bus Stop, Gwalior, MP 474011",
    "phone": "+91 751 2234000",
    "emergencyPhone": "+91 751 2234000",
    "emergency24x7": true,
    "rating": 4.8,
    "reviewsCount": 150,
    "verified": true,
    "opdTimings": "09:00 AM - 05:00 PM",
    "consultationFee": 500,
    "description": "Premier pediatric hospital in Gwalior equipped with Level-3 Neonatal Intensive Care (NICU), Pediatric Intensive Care (PICU), and advanced infant warmers.",
    "services": [
      "Level-3 NICU (Neonatal ICU)",
      "Pediatric Intensive Care (PICU)",
      "Pediatric Surgery",
      "Neonatal Ventilation",
      "Growth & Vaccination Clinic",
      "Emergency Pediatric Triage"
    ],
    "beds": {
      "general": [
        25,
        14
      ],
      "icu": [
        14,
        9
      ],
      "emergency": [
        6,
        3
      ],
      "oxygen": [
        20,
        12
      ],
      "ventilator": [
        6,
        4
      ]
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
    "emergencyPhone": "+91 751 2415124",
    "emergency24x7": true,
    "rating": 4.7,
    "reviewsCount": 150,
    "verified": true,
    "opdTimings": "09:00 AM - 05:00 PM",
    "consultationFee": 500,
    "description": "Recognized Regional Cancer Centre of Central India. Features Linear Accelerators, HDR Brachytherapy, Surgical Oncology, Bone Marrow Transplant, and Palliative Medicine.",
    "services": [
      "Radiation Oncology (LINAC)",
      "Surgical Oncology",
      "Medical Chemotherapy Daycare",
      "Nuclear Medicine & PET-CT",
      "Onco-Pathology & Genomics",
      "Palliative Care",
      "Ambulance"
    ],
    "beds": {
      "general": [
        220,
        155
      ],
      "icu": [
        28,
        18
      ],
      "emergency": [
        18,
        8
      ],
      "oxygen": [
        70,
        45
      ],
      "ventilator": [
        15,
        8
      ]
    }
  },
  {
    "id": 7,
    "name": "Kalyan Memorial Hospital & Research Centre",
    "type": "Private",
    "lat": 26.2115,
    "lng": 78.2098,
    "address": "University Road, Near Thatipur, City Centre, Gwalior, MP 474011",
    "phone": "+91 751 2232001",
    "emergencyPhone": "+91 751 2232001",
    "emergency24x7": true,
    "rating": 4.7,
    "reviewsCount": 150,
    "verified": true,
    "opdTimings": "09:00 AM - 05:00 PM",
    "consultationFee": 500,
    "description": "Multi-speciality hospital known for advanced cardiac care, renal dialysis unit, joint replacement, critical care, and trauma management.",
    "services": [
      "Cardiology & Echo",
      "Nephrology & Dialysis",
      "Orthopedic Trauma",
      "General & Laparoscopic Surgery",
      "ICU & CCU",
      "24x7 Ambulance",
      "Pharmacy"
    ],
    "beds": {
      "general": [
        110,
        68
      ],
      "icu": [
        22,
        13
      ],
      "emergency": [
        15,
        7
      ],
      "oxygen": [
        45,
        28
      ],
      "ventilator": [
        12,
        6
      ]
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
    "emergencyPhone": "+91 751 2415120",
    "emergency24x7": true,
    "rating": 4.7,
    "reviewsCount": 150,
    "verified": true,
    "opdTimings": "09:00 AM - 05:00 PM",
    "consultationFee": 500,
    "description": "High-tech super speciality hospital with a modern flat-panel Cath Lab, Neurosurgery OT, 24x7 Polytrauma response unit, and advanced Nephrology wing.",
    "services": [
      "Interventional Cath Lab",
      "Neuro & Spine Surgery",
      "Nephrology & Hemodialysis",
      "Polytrauma & Critical Care",
      "24x7 Emergency",
      "Ambulance",
      "Blood Bank"
    ],
    "beds": {
      "general": [
        130,
        82
      ],
      "icu": [
        26,
        16
      ],
      "emergency": [
        16,
        8
      ],
      "oxygen": [
        50,
        30
      ],
      "ventilator": [
        12,
        6
      ]
    }
  },
  {
    "id": 19,
    "name": "K.D. Super Speciality Hospital",
    "type": "Private",
    "lat": 26.2312,
    "lng": 78.1755,
    "address": "Near Tansen Tomb Road, Hazira, Gwalior, MP 474003",
    "phone": "+91 751 2482255",
    "emergencyPhone": "+91 751 2482255",
    "emergency24x7": true,
    "rating": 4.7,
    "reviewsCount": 150,
    "verified": true,
    "opdTimings": "09:00 AM - 05:00 PM",
    "consultationFee": 500,
    "description": "Advanced multi-specialty healthcare centre near Hazira with modern dialysis units, intensive care facilities, and robotic trauma surgery.",
    "services": [
      "Dialysis Unit 24x7",
      "Nephrology & Urology",
      "Critical Care & ICU",
      "Joint Replacement",
      "Gastroenterology",
      "24x7 Emergency Trauma"
    ],
    "beds": {
      "general": [
        45,
        28
      ],
      "icu": [
        12,
        8
      ],
      "emergency": [
        8,
        5
      ],
      "oxygen": [
        25,
        16
      ],
      "ventilator": [
        4,
        2
      ]
    }
  },
  {
    "id": 1,
    "name": "Jaya Arogya Hospital (JAH Group) & GRMC",
    "type": "Government",
    "lat": 26.1985,
    "lng": 78.1634,
    "address": "Medical College Campus, Kampoo Road, Lashkar, Gwalior, MP 474001",
    "phone": "+91 751 2403200",
    "emergencyPhone": "+91 751 2403200",
    "emergency24x7": true,
    "rating": 4.6,
    "reviewsCount": 150,
    "verified": true,
    "opdTimings": "09:00 AM - 05:00 PM",
    "consultationFee": 500,
    "description": "Apex government tertiary hospital & referral centre in Gwalior-Chambal division. Houses 1,150 beds, Level-1 Trauma Centre, Cath Lab, Burn Unit, and Central Blood Bank.",
    "services": [
      "Level-1 Trauma Care",
      "Interventional Cardiology",
      "Neurology & Neurosurgery",
      "Orthopedic Surgery",
      "Nephrology & Dialysis Unit",
      "General & Laparoscopic Surgery",
      "Central Blood Bank 24x7",
      "CT & MRI Diagnostics",
      "Burn Intensive Care",
      "Ambulance"
    ],
    "beds": {
      "general": [
        850,
        590
      ],
      "icu": [
        80,
        54
      ],
      "emergency": [
        60,
        41
      ],
      "oxygen": [
        220,
        155
      ],
      "ventilator": [
        40,
        28
      ]
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
    "emergencyPhone": "+91 751 4099900",
    "emergency24x7": true,
    "rating": 4.6,
    "reviewsCount": 150,
    "verified": true,
    "opdTimings": "09:00 AM - 05:00 PM",
    "consultationFee": 500,
    "description": "Centrally located multi-speciality hospital housing advanced Gastroenterology, Endoscopy, Pulmonology, Orthopedic Joint Replacement, and Critical Care.",
    "services": [
      "Gastroenterology & Endoscopy",
      "Pulmonology & Bronchoscopy",
      "Orthopedics & Spine",
      "Critical Care (ICU)",
      "24x7 Emergency Response",
      "Pharmacy",
      "Ambulance"
    ],
    "beds": {
      "general": [
        95,
        58
      ],
      "icu": [
        18,
        10
      ],
      "emergency": [
        12,
        5
      ],
      "oxygen": [
        38,
        22
      ],
      "ventilator": [
        8,
        3
      ]
    }
  },
  {
    "id": 13,
    "name": "Sahara Hospital & Trauma Centre",
    "type": "Private",
    "lat": 26.2178,
    "lng": 78.1882,
    "address": "Near Railway Station Platform 4 side, Lashkar Road, Gwalior, MP 474002",
    "phone": "+91 751 2420088",
    "emergencyPhone": "+91 751 2420088",
    "emergency24x7": true,
    "rating": 4.6,
    "reviewsCount": 150,
    "verified": true,
    "opdTimings": "09:00 AM - 05:00 PM",
    "consultationFee": 500,
    "description": "Strategic multi-speciality centre specialising in high-speed road accident polytrauma, fracture fixations, general surgery, and emergency critical care.",
    "services": [
      "Polytrauma & Emergency OT",
      "Orthopedic Joint Fixation",
      "Urology & Kidney Stones",
      "General Laparoscopy",
      "ICU",
      "Ambulance",
      "Pharmacy 24x7"
    ],
    "beds": {
      "general": [
        80,
        48
      ],
      "icu": [
        15,
        8
      ],
      "emergency": [
        12,
        5
      ],
      "oxygen": [
        32,
        18
      ],
      "ventilator": [
        6,
        2
      ]
    }
  },
  {
    "id": 15,
    "name": "Maxcare Multispeciality Hospital",
    "type": "Private",
    "lat": 26.2225,
    "lng": 78.212,
    "address": "New Collectorate Road, City Centre, Gwalior, MP 474011",
    "phone": "+91 751 4018888",
    "emergencyPhone": "+91 751 4018888",
    "emergency24x7": true,
    "rating": 4.6,
    "reviewsCount": 150,
    "verified": true,
    "opdTimings": "09:00 AM - 05:00 PM",
    "consultationFee": 500,
    "description": "Modern facility offering advanced internal medicine, diabetology, pulmonology, critical care, dermatology, and diagnostic pathology.",
    "services": [
      "Internal Medicine & Diabetes",
      "Pulmonology & Asthma Care",
      "Critical Care ICU",
      "Dermatology & Hair Clinic",
      "24x7 Emergency",
      "Ambulance",
      "Pharmacy"
    ],
    "beds": {
      "general": [
        75,
        42
      ],
      "icu": [
        14,
        7
      ],
      "emergency": [
        10,
        4
      ],
      "oxygen": [
        28,
        14
      ],
      "ventilator": [
        6,
        2
      ]
    }
  },
  {
    "id": 18,
    "name": "Scindia Devraj Hospital & Research Centre",
    "type": "Private",
    "lat": 26.2052,
    "lng": 78.1685,
    "address": "Jayendraganj Main Market, Lashkar, Gwalior, MP 474009",
    "phone": "+91 751 2423300",
    "emergencyPhone": "+91 751 2423300",
    "emergency24x7": true,
    "rating": 4.6,
    "reviewsCount": 150,
    "verified": true,
    "opdTimings": "09:00 AM - 05:00 PM",
    "consultationFee": 500,
    "description": "Established multi-speciality medical centre in the heart of Lashkar providing comprehensive surgical, medical, and diagnostics care.",
    "services": [
      "General Surgery",
      "Urology & Nephrology",
      "Obstetrics & Gynecology",
      "Internal Medicine",
      "Pediatrics",
      "24x7 Pharmacy",
      "Digital X-Ray"
    ],
    "beds": {
      "general": [
        35,
        20
      ],
      "icu": [
        6,
        4
      ],
      "emergency": [
        5,
        3
      ],
      "oxygen": [
        15,
        9
      ],
      "ventilator": [
        2,
        1
      ]
    }
  },
  {
    "id": 22,
    "name": "Shri Ram Hospital & Laparoscopy Centre",
    "type": "Private",
    "lat": 26.195,
    "lng": 78.158,
    "address": "Kampoo Main Road, Near Madhav Dispensary, Lashkar, Gwalior, MP 474001",
    "phone": "+91 751 2419080",
    "emergencyPhone": "+91 751 2419080",
    "emergency24x7": true,
    "rating": 4.6,
    "reviewsCount": 150,
    "verified": true,
    "opdTimings": "09:00 AM - 05:00 PM",
    "consultationFee": 500,
    "description": "Renowned centre for minimally invasive laparoscopic, gallbladder, hernia, and gynecological surgical interventions in Gwalior.",
    "services": [
      "Advanced Laparoscopic Surgery",
      "Gastrointestinal Surgery",
      "Hernia & Gallbladder Centre",
      "Gynecological Endoscopy",
      "Intensive Care Unit (ICU)",
      "24x7 Emergency OT"
    ],
    "beds": {
      "general": [
        42,
        26
      ],
      "icu": [
        8,
        5
      ],
      "emergency": [
        6,
        3
      ],
      "oxygen": [
        18,
        11
      ],
      "ventilator": [
        3,
        1
      ]
    }
  },
  {
    "id": 6,
    "name": "Kamla Raja Hospital (KRH / JAH Campus)",
    "type": "Government",
    "lat": 26.1965,
    "lng": 78.1618,
    "address": "Medical College Campus, Kampoo, Gwalior, MP 474001",
    "phone": "+91 751 2403300",
    "emergencyPhone": "+91 751 2403300",
    "emergency24x7": true,
    "rating": 4.5,
    "reviewsCount": 150,
    "verified": true,
    "opdTimings": "09:00 AM - 05:00 PM",
    "consultationFee": 500,
    "description": "Leading government maternity and pediatric hospital of Central India. Features 450 beds, Level-III NICU, PICU, high-risk pregnancy delivery units, and 24x7 emergency labor room.",
    "services": [
      "Obstetrics & High-Risk Pregnancy",
      "Level-III Neonatal ICU (NICU)",
      "Pediatric Intensive Care (PICU)",
      "Painless Delivery Units",
      "Infertility Clinic",
      "24x7 Emergency Obstetric Care",
      "Janani Express 102"
    ],
    "beds": {
      "general": [
        420,
        305
      ],
      "icu": [
        45,
        30
      ],
      "emergency": [
        35,
        22
      ],
      "oxygen": [
        130,
        88
      ],
      "ventilator": [
        20,
        13
      ]
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
    "emergencyPhone": "+91 751 2341100",
    "emergency24x7": true,
    "rating": 4.5,
    "reviewsCount": 150,
    "verified": true,
    "opdTimings": "09:00 AM - 05:00 PM",
    "consultationFee": 500,
    "description": "Specialized non-invasive cardiology and obstetric hospital equipped with 2D Echo, TMT, Holter monitoring, painless labor suites, and neonatal intensive nursery.",
    "services": [
      "Cardiology Consultations",
      "2D Echo & Stress TMT",
      "Painless Normal Delivery",
      "Cesarean & High-Risk Pregnancy",
      "ICU & CCU",
      "24x7 Pharmacy",
      "Ambulance"
    ],
    "beds": {
      "general": [
        55,
        32
      ],
      "icu": [
        12,
        6
      ],
      "emergency": [
        8,
        3
      ],
      "oxygen": [
        22,
        12
      ],
      "ventilator": [
        4,
        2
      ]
    }
  },
  {
    "id": 16,
    "name": "Janak Hospital & Laparoscopy Centre",
    "type": "Private",
    "lat": 26.221,
    "lng": 78.217,
    "address": "Morar Road, Near Thatipur, Gwalior, MP 474005",
    "phone": "+91 751 2345099",
    "emergencyPhone": "+91 751 2345099",
    "emergency24x7": true,
    "rating": 4.5,
    "reviewsCount": 150,
    "verified": true,
    "opdTimings": "09:00 AM - 05:00 PM",
    "consultationFee": 500,
    "description": "Dedicated surgical centre offering advanced laparoscopic gallbladder, hernia, appendix, and endoscopic urology procedures with fast post-operative recovery.",
    "services": [
      "Laparoscopic General Surgery",
      "Endourology & Kidney Stones",
      "Trauma & Fracture Fixation",
      "ICU Support",
      "24x7 Emergency",
      "Pharmacy"
    ],
    "beds": {
      "general": [
        40,
        22
      ],
      "icu": [
        8,
        4
      ],
      "emergency": [
        6,
        2
      ],
      "oxygen": [
        15,
        7
      ],
      "ventilator": [
        3,
        1
      ]
    }
  },
  {
    "id": 17,
    "name": "Gwalior Mansik Arogyashala (Mental Health & Neuroscience Institute)",
    "type": "Government",
    "lat": 26.223,
    "lng": 78.188,
    "address": "Jail Road, Near Central Jail, Gwalior, MP 474003",
    "phone": "+91 751 2481014",
    "emergencyPhone": "+91 751 2481014",
    "emergency24x7": true,
    "rating": 4.5,
    "reviewsCount": 150,
    "verified": true,
    "opdTimings": "09:00 AM - 05:00 PM",
    "consultationFee": 500,
    "description": "Historic government apex institute established in 1935 for psychiatric care, behavioral sciences, de-addiction therapy, and clinical neuro-psychology in Madhya Pradesh.",
    "services": [
      "Psychiatry & De-Addiction",
      "Clinical Psychology",
      "Neuro-Psychiatry",
      "Emergency 24x7 Crisis Cell",
      "Rehabilitation & Counseling",
      "Electroencephalogram (EEG)",
      "Pharmacy & Social Work"
    ],
    "beds": {
      "general": [
        180,
        110
      ],
      "icu": [
        10,
        6
      ],
      "emergency": [
        12,
        7
      ],
      "oxygen": [
        35,
        20
      ],
      "ventilator": [
        2,
        1
      ]
    }
  },
  {
    "id": 20,
    "name": "Navjeevan Multispeciality Hospital",
    "type": "Private",
    "lat": 26.2425,
    "lng": 78.212,
    "address": "Airport Road, Near Gole Ka Mandir, Gwalior, MP 474005",
    "phone": "+91 751 2490011",
    "emergencyPhone": "+91 751 2490011",
    "emergency24x7": true,
    "rating": 4.5,
    "reviewsCount": 150,
    "verified": true,
    "opdTimings": "09:00 AM - 05:00 PM",
    "consultationFee": 500,
    "description": "Trusted community multi-speciality hospital catering to Gole Ka Mandir, Maharajpura, and Airport Road catchment.",
    "services": [
      "General Medicine",
      "Pediatrics & Child Care",
      "Orthopedic Surgery",
      "Pathology & Ultrasound",
      "24x7 Casualty",
      "Day Care Surgeries"
    ],
    "beds": {
      "general": [
        38,
        22
      ],
      "icu": [
        8,
        5
      ],
      "emergency": [
        6,
        4
      ],
      "oxygen": [
        20,
        13
      ],
      "ventilator": [
        2,
        1
      ]
    }
  },
  {
    "id": 5,
    "name": "Civil Hospital Morar (District Hospital Gwalior)",
    "type": "Government",
    "lat": 26.2268,
    "lng": 78.2295,
    "address": "Main Hospital Road, Morar Cantt, Gwalior, MP 474006",
    "phone": "+91 751 2368212",
    "emergencyPhone": "+91 751 2368212",
    "emergency24x7": true,
    "rating": 4.3,
    "reviewsCount": 150,
    "verified": true,
    "opdTimings": "09:00 AM - 05:00 PM",
    "consultationFee": 500,
    "description": "Major public hospital serving eastern Gwalior and Chambal. Provides free emergency care, round-the-clock maternity services, free generic drug dispensary, and blood storage.",
    "services": [
      "24x7 Emergency Casualty",
      "General Medicine",
      "Maternity & Obstetric Ward",
      "Pediatric Care",
      "Free Drug Dispensary",
      "Pathology Lab",
      "Ambulance 108"
    ],
    "beds": {
      "general": [
        240,
        165
      ],
      "icu": [
        20,
        11
      ],
      "emergency": [
        25,
        15
      ],
      "oxygen": [
        80,
        50
      ],
      "ventilator": [
        10,
        4
      ]
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
    "emergencyPhone": "+91 751 2480112",
    "emergency24x7": true,
    "rating": 4.2,
    "reviewsCount": 150,
    "verified": true,
    "opdTimings": "09:00 AM - 05:00 PM",
    "consultationFee": 500,
    "description": "Government community civil hospital providing 24x7 primary emergency, maternal & infant care, immunisation, and free medicine distribution for northern Gwalior.",
    "services": [
      "24x7 Emergency Casualty",
      "General Medicine",
      "Maternity Ward",
      "Child Immunisation",
      "Free Pharmacy",
      "Ambulance 108"
    ],
    "beds": {
      "general": [
        90,
        55
      ],
      "icu": [
        10,
        4
      ],
      "emergency": [
        15,
        7
      ],
      "oxygen": [
        30,
        16
      ],
      "ventilator": [
        4,
        1
      ]
    }
  }
];

const DOCTORS_DATABASE = [
  {
    "id": 101,
    "name": "Dr. Ajay Gupta",
    "qualification": "MBBS, MD (Medicine), DM (Cardiology - Gold Medalist)",
    "specialty": "Cardiologist (Heart Specialist)",
    "category": "cardiology",
    "experience": "22+ years",
    "experience_years": 22,
    "hospitalId": 2,
    "hospital_id": 2,
    "hospitalName": "BIMR Hospitals (Birla Heart Centre)",
    "hospital_name": "BIMR Hospitals (Birla Heart Centre)",
    "clinicAddress": "Surya Mandir Road, Morar & City Centre OPD, Gwalior",
    "phone": "+91 94251 12340",
    "email": "dr.ajaygupta.cardio@gmail.com",
    "opdTimings": "Mon - Sat: 11:00 AM - 03:00 PM & 06:00 PM - 08:30 PM",
    "daysAvailable": "Mon - Sat",
    "fee": 600,
    "rating": 4.9,
    "reviewsCount": 430,
    "badge": "Top Cardiologist",
    "about": "Senior Interventional Cardiologist with over 15,000+ angiographies and angioplasties performed. Specialized in coronary stenting, pacemakers, heart failure, and hypertension.",
    "avatar": "👨‍⚕️",
    "verified": true
  },
  {
    "id": 102,
    "name": "Dr. Rashmi Gupta",
    "qualification": "MBBS, MS (Obstetrics & Gynecology), F.MAS",
    "specialty": "Gynecologist & Infertility Specialist",
    "category": "gynecology",
    "experience": "19+ years",
    "experience_years": 19,
    "hospitalId": 14,
    "hospital_id": 14,
    "hospitalName": "Vatsalya Hospital & Maternity Home",
    "hospital_name": "Vatsalya Hospital & Maternity Home",
    "clinicAddress": "Patel Nagar, Near City Centre, Gwalior",
    "phone": "+91 94251 17890",
    "email": "dr.rashmigupta.obgyn@gmail.com",
    "opdTimings": "Mon - Sat: 10:00 AM - 02:00 PM & 05:30 PM - 08:00 PM",
    "daysAvailable": "Mon - Sat",
    "fee": 500,
    "rating": 4.9,
    "reviewsCount": 490,
    "badge": "Senior Gynecologist",
    "about": "Renowned for painless normal deliveries, high-risk pregnancy management, IVF infertility treatments, PCOS, and minimally invasive laparoscopic hysterectomy.",
    "avatar": "👩‍⚕️",
    "verified": true
  },
  {
    "id": 103,
    "name": "Dr. Sanjay Dhir",
    "qualification": "MBBS, MS (Surgery), MCh (Neurosurgery - AIIMS New Delhi)",
    "specialty": "Neurosurgeon (Brain & Spine Surgeon)",
    "category": "neurology",
    "experience": "21+ years",
    "experience_years": 21,
    "hospitalId": 1,
    "hospital_id": 1,
    "hospitalName": "JAH Super Speciality / Sheetla Sahay Hospital",
    "hospital_name": "JAH Super Speciality / Sheetla Sahay Hospital",
    "clinicAddress": "Kampoo Road, Lashkar & Cancer Hills, Gwalior",
    "phone": "+91 751 2403200",
    "email": "dr.sanjaydhir.neuro@gmail.com",
    "opdTimings": "Mon - Fri: 10:00 AM - 02:00 PM",
    "daysAvailable": "Mon - Fri",
    "fee": 700,
    "rating": 4.8,
    "reviewsCount": 340,
    "badge": "AIIMS Alumnus",
    "about": "Expert in micro-neurosurgery, brain tumor resections, endoscopic slip disc surgeries, spinal fusion, cervical spondylosis, and traumatic head injury rehabilitation.",
    "avatar": "👨‍⚕️",
    "verified": true
  },
  {
    "id": 104,
    "name": "Dr. Manish Bansal",
    "qualification": "MBBS, MS (Ophthalmology), Fellowship Sankara Nethralaya",
    "specialty": "Ophthalmologist (Chief Eye Surgeon)",
    "category": "ophthalmology",
    "experience": "19+ years",
    "experience_years": 19,
    "hospitalId": 10,
    "hospital_id": 10,
    "hospitalName": "Bansal Eye Hospital & Laser Surgery Centre",
    "hospital_name": "Bansal Eye Hospital & Laser Surgery Centre",
    "clinicAddress": "Madhav Rao Scindia Marg, City Centre, Gwalior",
    "phone": "+91 98262 12345",
    "email": "drmanishbansal@bansaleye.com",
    "opdTimings": "Mon - Sat: 10:00 AM - 01:30 PM & 05:00 PM - 07:30 PM",
    "daysAvailable": "Mon - Sat",
    "fee": 500,
    "rating": 4.9,
    "reviewsCount": 580,
    "badge": "Premier Eye Surgeon",
    "about": "Pioneer in stitchless Micro-Phaco cataract surgery and Contoura Vision Lasik in Gwalior. Expert in diabetic vitreo-retinal laser treatments and corneal disorders.",
    "avatar": "👨‍⚕️",
    "verified": true
  },
  {
    "id": 105,
    "name": "Dr. Neeraj Sharma",
    "qualification": "MBBS, MS (Orthopedics), Joint Replacement Fellow (Germany)",
    "specialty": "Orthopedic & Robotic Joint Surgeon",
    "category": "orthopedics",
    "experience": "18+ years",
    "experience_years": 18,
    "hospitalId": 2,
    "hospital_id": 2,
    "hospitalName": "BIMR Hospitals / Sahara Hospital",
    "hospital_name": "BIMR Hospitals / Sahara Hospital",
    "clinicAddress": "Surya Mandir Road, Morar, Gwalior",
    "phone": "+91 98260 77123",
    "email": "drneerajsharma.ortho@gmail.com",
    "opdTimings": "Mon - Sat: 11:30 AM - 04:00 PM & 06:30 PM - 08:30 PM",
    "daysAvailable": "Mon - Sat",
    "fee": 600,
    "rating": 4.8,
    "reviewsCount": 410,
    "badge": "Joint Replacement Expert",
    "about": "Specialist in robotic total knee and hip replacements, arthroscopic ACL/PCL ligament reconstruction, complex multi-fragment bone fractures, and arthritis therapy.",
    "avatar": "👨‍⚕️",
    "verified": true
  },
  {
    "id": 106,
    "name": "Dr. Archana Shrivastava",
    "qualification": "MBBS, MD (Pediatrics), FIAP",
    "specialty": "Pediatrician & Child Health Specialist",
    "category": "pediatrics",
    "experience": "16+ years",
    "experience_years": 16,
    "hospitalId": 6,
    "hospital_id": 6,
    "hospitalName": "Kamla Raja Hospital (KRH) & Child Care Clinic",
    "hospital_name": "Kamla Raja Hospital (KRH) & Child Care Clinic",
    "clinicAddress": "Medical College Road, Kampoo, Lashkar, Gwalior",
    "phone": "+91 751 2403300",
    "email": "drarchana.pediatrics@gmail.com",
    "opdTimings": "Mon - Sat: 09:30 AM - 01:30 PM & 05:00 PM - 07:30 PM",
    "daysAvailable": "Mon - Sat",
    "fee": 500,
    "rating": 4.9,
    "reviewsCount": 470,
    "badge": "Child Health Specialist",
    "about": "Specialized in newborn intensive care (NICU), pediatric asthma, childhood infections (dengue, typhoid), child growth monitoring, and painless immunisation.",
    "avatar": "👩‍⚕️",
    "verified": true
  },
  {
    "id": 107,
    "name": "Dr. Rahul Agarwal",
    "qualification": "MBBS, MD (General Medicine), FICP",
    "specialty": "General Physician & Diabetologist",
    "category": "general",
    "experience": "18+ years",
    "experience_years": 18,
    "hospitalId": 4,
    "hospital_id": 4,
    "hospitalName": "Apollo Clinic & Diagnostic Centre",
    "hospital_name": "Apollo Clinic & Diagnostic Centre",
    "clinicAddress": "Opp. High Court, City Centre, Gwalior",
    "phone": "+91 751 4001222",
    "email": "dr.rahulagarwal@apolloclinic.com",
    "opdTimings": "Mon - Sun: 09:00 AM - 01:00 PM & 05:00 PM - 08:30 PM",
    "daysAvailable": "Mon - Sun",
    "fee": 500,
    "rating": 4.8,
    "reviewsCount": 520,
    "badge": "Apollo Consultant",
    "about": "Experienced family physician diagnosing acute seasonal fevers (Dengue, Malaria, Typhoid), Diabetes Mellitus, hypertension, thyroid conditions, and geriatric health.",
    "avatar": "👨‍⚕️",
    "verified": true
  },
  {
    "id": 108,
    "name": "Dr. Vivek Verma",
    "qualification": "MBBS, MS (Surgery), MCh (Surgical Oncology - Tata Memorial)",
    "specialty": "Oncologist (Cancer Surgeon)",
    "category": "oncology",
    "experience": "17+ years",
    "experience_years": 17,
    "hospitalId": 3,
    "hospital_id": 3,
    "hospitalName": "Cancer Hospital & Research Institute (CHRI)",
    "hospital_name": "Cancer Hospital & Research Institute (CHRI)",
    "clinicAddress": "Cancer Hills, Mandre Ki Mata, Lashkar, Gwalior",
    "phone": "+91 751 2415124",
    "email": "dr.vivekverma.onco@gmail.com",
    "opdTimings": "Mon - Sat: 10:00 AM - 03:00 PM",
    "daysAvailable": "Mon - Sat",
    "fee": 800,
    "rating": 4.9,
    "reviewsCount": 310,
    "badge": "Senior Cancer Surgeon",
    "about": "Extensive experience in head & neck cancers, breast conservation surgery, gastrointestinal cancer resections, and comprehensive multidisciplinary oncology.",
    "avatar": "👨‍⚕️",
    "verified": true
  },
  {
    "id": 109,
    "name": "Dr. Rajesh Saxena",
    "qualification": "MBBS, MD (Medicine), DM (Gastroenterology - SGPGI)",
    "specialty": "Gastroenterologist & Hepatologist",
    "category": "gastro",
    "experience": "16+ years",
    "experience_years": 16,
    "hospitalId": 8,
    "hospital_id": 8,
    "hospitalName": "Global Speciality Hospital",
    "hospital_name": "Global Speciality Hospital",
    "clinicAddress": "Sachin Tendulkar Marg, City Centre, Gwalior",
    "phone": "+91 751 4099900",
    "email": "drrajeshsaxena.gastro@gmail.com",
    "opdTimings": "Mon - Sat: 11:00 AM - 03:00 PM & 06:00 PM - 08:00 PM",
    "daysAvailable": "Mon - Sat",
    "fee": 700,
    "rating": 4.7,
    "reviewsCount": 290,
    "badge": "Gastro Specialist",
    "about": "Specialist in therapeutic endoscopy, colonoscopy, ERCP, fatty liver, jaundice, hepatitis, chronic pancreatitis, and inflammatory bowel disease.",
    "avatar": "👨‍⚕️",
    "verified": true
  },
  {
    "id": 110,
    "name": "Dr. Priya Tomar",
    "qualification": "MBBS, MD (Dermatology, Venereology & Leprosy)",
    "specialty": "Dermatologist & Cosmetologist (Skin & Hair)",
    "category": "dermatology",
    "experience": "13+ years",
    "experience_years": 13,
    "hospitalId": 15,
    "hospital_id": 15,
    "hospitalName": "Maxcare Hospital & Skin Laser Clinic",
    "hospital_name": "Maxcare Hospital & Skin Laser Clinic",
    "clinicAddress": "New Collectorate Road, City Centre, Gwalior",
    "phone": "+91 94257 23456",
    "email": "drpriyatomar.skin@gmail.com",
    "opdTimings": "Mon - Sat: 10:30 AM - 02:30 PM & 05:30 PM - 08:00 PM",
    "daysAvailable": "Mon - Sat",
    "fee": 500,
    "rating": 4.8,
    "reviewsCount": 390,
    "badge": "Skin & Laser Expert",
    "about": "Certified cosmetologist treating severe acne, eczema, psoriasis, hair fall with PRP therapy, fungal allergies, laser pigmentation removal, and chemical peels.",
    "avatar": "👩‍⚕️",
    "verified": true
  },
  {
    "id": 111,
    "name": "Dr. Alok Purohit",
    "qualification": "MBBS, MD (Pulmonary Medicine - Chest & TB)",
    "specialty": "Pulmonologist (Chest & Lungs Specialist)",
    "category": "pulmonology",
    "experience": "15+ years",
    "experience_years": 15,
    "hospitalId": 1,
    "hospital_id": 1,
    "hospitalName": "JAH Super Speciality / City Centre Chest Clinic",
    "hospital_name": "JAH Super Speciality / City Centre Chest Clinic",
    "clinicAddress": "City Centre & Kampoo, Gwalior",
    "phone": "+91 751 2403201",
    "email": "dralokpurohit.chest@gmail.com",
    "opdTimings": "Mon - Sat: 10:00 AM - 02:00 PM & 06:00 PM - 08:00 PM",
    "daysAvailable": "Mon - Sat",
    "fee": 600,
    "rating": 4.8,
    "reviewsCount": 310,
    "badge": "Chest & Asthma Expert",
    "about": "Specialist in Bronchial Asthma, COPD, Chronic Bronchitis, Post-Covid lung fibrosis, Sleep Apnea, diagnostic bronchoscopy, and respiratory allergies.",
    "avatar": "👨‍⚕️",
    "verified": true
  },
  {
    "id": 112,
    "name": "Dr. Sunita Mishra",
    "qualification": "MBBS, MS (ENT / Otorhinolaryngology)",
    "specialty": "ENT & Head-Neck Surgeon",
    "category": "ent",
    "experience": "14+ years",
    "experience_years": 14,
    "hospitalId": 5,
    "hospital_id": 5,
    "hospitalName": "Civil Hospital Morar / Apollo Clinic",
    "hospital_name": "Civil Hospital Morar / Apollo Clinic",
    "clinicAddress": "Morar Cantt & High Court Road, Gwalior",
    "phone": "+91 751 2368212",
    "email": "drsunitamishra.ent@gmail.com",
    "opdTimings": "Mon - Sat: 09:30 AM - 01:30 PM & 05:00 PM - 07:30 PM",
    "daysAvailable": "Mon - Sat",
    "fee": 450,
    "rating": 4.7,
    "reviewsCount": 340,
    "badge": "ENT Specialist",
    "about": "Treats chronic ear discharge, tympanoplasty, endoscopic sinus surgery (FESS), nasal polyps, tonsillitis, vertigo, and vocal cord disorders.",
    "avatar": "👩‍⚕️",
    "verified": true
  },
  {
    "id": 113,
    "name": "Dr. Pradeep Kashyap",
    "qualification": "MBBS, MS (Gen Surgery), MCh (Urology)",
    "specialty": "Urologist & Kidney Transplant Surgeon",
    "category": "general",
    "experience": "16+ years",
    "experience_years": 16,
    "hospitalId": 19,
    "hospital_id": 19,
    "hospitalName": "K.D. Super Speciality Hospital / Scindia Devraj Hospital",
    "hospital_name": "K.D. Super Speciality Hospital / Scindia Devraj Hospital",
    "clinicAddress": "Hazira Road & Jayendraganj, Lashkar, Gwalior",
    "phone": "+91 94251 22880",
    "email": "dr.pkashyap@gmail.com",
    "opdTimings": "Mon - Sat: 11:00 AM - 02:00 PM, 05:30 PM - 08:00 PM",
    "daysAvailable": "Mon - Sat",
    "fee": 700,
    "rating": 4.9,
    "reviewsCount": 210,
    "badge": "Chief Urologist",
    "about": "Expert in laser kidney stone removal (RIRS/PCNL), prostate surgery (TURP), and advanced laparoscopic reconstructive urology.",
    "avatar": "👨‍⚕️",
    "verified": true
  },
  {
    "id": 114,
    "name": "Dr. Meenakshi Bansal",
    "qualification": "MBBS, MS (Ophthalmology), Fellow (LVPEI)",
    "specialty": "Pediatric Ophthalmologist & Squint Surgeon",
    "category": "ophthalmology",
    "experience": "12+ years",
    "experience_years": 12,
    "hospitalId": 10,
    "hospital_id": 10,
    "hospitalName": "Bansal Eye Hospital & Laser Surgery Centre",
    "hospital_name": "Bansal Eye Hospital & Laser Surgery Centre",
    "clinicAddress": "Madhav Rao Scindia Marg, City Centre, Gwalior",
    "phone": "+91 751 2445500",
    "email": "dr.meenakshi.eye@gmail.com",
    "opdTimings": "Mon - Sat: 10:30 AM - 03:00 PM",
    "daysAvailable": "Mon - Sat",
    "fee": 500,
    "rating": 4.9,
    "reviewsCount": 185,
    "badge": "Squint & Pediatric Eye Specialist",
    "about": "Specializes in children eye disorders, amblyopia (lazy eye), squint correction surgery, and pediatric cataract management.",
    "avatar": "👩‍⚕️",
    "verified": true
  },
  {
    "id": 115,
    "name": "Dr. Ashish Chauhan",
    "qualification": "MBBS, MD (Anesthesia), FNB (Critical Care Medicine)",
    "specialty": "Chief of Critical Care & Emergency Medicine",
    "category": "general",
    "experience": "14+ years",
    "experience_years": 14,
    "hospitalId": 1,
    "hospital_id": 1,
    "hospitalName": "JAH Level-1 Trauma Centre & BIMR Hospitals",
    "hospital_name": "JAH Level-1 Trauma Centre & BIMR Hospitals",
    "clinicAddress": "Medical College Campus, Kampoo, Gwalior",
    "phone": "+91 751 2403222",
    "email": "dr.ashish.icu@gmail.com",
    "opdTimings": "Mon - Sat: 09:00 AM - 01:00 PM (Emergency On-Call 24x7)",
    "daysAvailable": "Mon - Sat",
    "fee": 600,
    "rating": 4.8,
    "reviewsCount": 160,
    "badge": "Critical Care Specialist",
    "about": "Head of resuscitation and intensive care, managing complex polytrauma, septic shock, ECMO, and mechanical ventilation.",
    "avatar": "👨‍⚕️",
    "verified": true
  },
  {
    "id": 116,
    "name": "Dr. Ritu Saxena",
    "qualification": "BDS, MDS (Oral & Maxillofacial Surgery)",
    "specialty": "Maxillofacial Surgeon & Dental Implantologist",
    "category": "general",
    "experience": "11+ years",
    "experience_years": 11,
    "hospitalId": 4,
    "hospital_id": 4,
    "hospitalName": "Apollo Clinic & Maxcare Dental Centre",
    "hospital_name": "Apollo Clinic & Maxcare Dental Centre",
    "clinicAddress": "High Court Road, City Centre, Gwalior",
    "phone": "+91 751 4001222",
    "email": "dr.ritusaxena.oral@gmail.com",
    "opdTimings": "Mon - Sat: 10:00 AM - 02:00 PM, 05:00 PM - 08:30 PM",
    "daysAvailable": "Mon - Sat",
    "fee": 400,
    "rating": 4.8,
    "reviewsCount": 175,
    "badge": "Dental & Facial Surgeon",
    "about": "Expert in facial bone fractures, dental implants, wisdom tooth impactions, TMJ disorders, and cosmetic smile designs.",
    "avatar": "👩‍⚕️",
    "verified": true
  },
  {
    "id": 117,
    "name": "Dr. S. K. Pathak",
    "qualification": "MBBS, MD (Psychiatry), DPM",
    "specialty": "Senior Psychiatrist & Neuro-Behavioral Specialist",
    "category": "neurology",
    "experience": "22+ years",
    "experience_years": 22,
    "hospitalId": 17,
    "hospital_id": 17,
    "hospitalName": "Gwalior Mansik Arogyashala & Mind Clinic",
    "hospital_name": "Gwalior Mansik Arogyashala & Mind Clinic",
    "clinicAddress": "Jail Road & Phoolbagh, Gwalior",
    "phone": "+91 751 2481014",
    "email": "dr.skpathak.psych@gmail.com",
    "opdTimings": "Mon - Sat: 09:30 AM - 01:30 PM, 05:00 PM - 07:30 PM",
    "daysAvailable": "Mon - Sat",
    "fee": 500,
    "rating": 4.9,
    "reviewsCount": 310,
    "badge": "Senior Neuro-Psychiatrist",
    "about": "Decades of experience in depression, clinical anxiety, OCD, sleep disorders, addiction therapy, and adolescent mental health.",
    "avatar": "👨‍⚕️",
    "verified": true
  },
  {
    "id": 118,
    "name": "Dr. Deepak Agrawal",
    "qualification": "MBBS, MS (Orthopedics), Fellowship in Arthroscopy (Germany)",
    "specialty": "Arthroscopy, Sports Injury & Knee Surgeon",
    "category": "orthopedics",
    "experience": "15+ years",
    "experience_years": 15,
    "hospitalId": 7,
    "hospital_id": 7,
    "hospitalName": "Kalyan Memorial Hospital & BIMR Hospitals",
    "hospital_name": "Kalyan Memorial Hospital & BIMR Hospitals",
    "clinicAddress": "University Road, Near Thatipur, Gwalior",
    "phone": "+91 751 2232001",
    "email": "dr.deepak.ortho@gmail.com",
    "opdTimings": "Mon - Sat: 11:30 AM - 03:30 PM, 06:00 PM - 08:30 PM",
    "daysAvailable": "Mon - Sat",
    "fee": 600,
    "rating": 4.9,
    "reviewsCount": 240,
    "badge": "Sports Injury & Knee Specialist",
    "about": "Pioneer in keyhole arthroscopic ACL/PCL ligament reconstruction, meniscus repair, and minimally invasive joint restoration.",
    "avatar": "👨‍⚕️",
    "verified": true
  }
];

const BLOOD_BANKS_DATABASE = [
  {
    "id": 1,
    "name": "JAH Central Blood Bank & Component Separation Unit",
    "hospitalId": 1,
    "hospital_id": 1,
    "address": "GRMC Campus, Kampoo Road, Lashkar, Gwalior",
    "contactPerson": "Dr. R. K. Jain (Chief Medical Officer)",
    "phone": "+91 751 2403233",
    "emergency24x7": true,
    "lat": 26.1985,
    "lng": 78.1634,
    "verified": true,
    "inventory": {
      "A+": 42,
      "A-": 12,
      "AB+": 25,
      "AB-": 8,
      "B+": 65,
      "B-": 15,
      "O+": 58,
      "O-": 18
    }
  },
  {
    "id": 2,
    "name": "Indian Red Cross Society Blood Bank Gwalior",
    "hospitalId": null,
    "hospital_id": null,
    "address": "Near Phoolbagh Ground, Lashkar, Gwalior, MP 474002",
    "contactPerson": "Secretary, Red Cross Gwalior",
    "phone": "+91 751 2422002",
    "emergency24x7": true,
    "lat": 26.2095,
    "lng": 78.1752,
    "verified": true,
    "inventory": {
      "A+": 28,
      "A-": 8,
      "AB+": 18,
      "AB-": 5,
      "B+": 45,
      "B-": 10,
      "O+": 38,
      "O-": 14
    }
  },
  {
    "id": 3,
    "name": "BIMR Hospital Blood Bank",
    "hospitalId": 2,
    "hospital_id": 2,
    "address": "Surya Mandir Road, Residency Area, Morar, Gwalior",
    "contactPerson": "Blood Transfusion In-Charge",
    "phone": "+91 751 2405615",
    "emergency24x7": true,
    "lat": 26.2312,
    "lng": 78.2215,
    "verified": true,
    "inventory": {
      "A+": 24,
      "A-": 6,
      "AB+": 14,
      "AB-": 4,
      "B+": 35,
      "B-": 8,
      "O+": 30,
      "O-": 9
    }
  },
  {
    "id": 4,
    "name": "Civil Hospital Morar Blood Storage Centre",
    "hospitalId": 5,
    "hospital_id": 5,
    "address": "Hospital Road, Morar Cantt, Gwalior",
    "contactPerson": "Duty Transfusion Officer",
    "phone": "+91 751 2368212",
    "emergency24x7": true,
    "lat": 26.2268,
    "lng": 78.2295,
    "verified": true,
    "inventory": {
      "A+": 16,
      "A-": 4,
      "AB+": 8,
      "AB-": 2,
      "B+": 22,
      "B-": 5,
      "O+": 20,
      "O-": 6
    }
  },
  {
    "id": 5,
    "name": "Cancer Hospital (CHRI) Blood Bank",
    "hospitalId": 3,
    "hospital_id": 3,
    "address": "Mandre Ki Mata Hills, Cancer Hills, Gwalior",
    "contactPerson": "Transfusion Medicine Head",
    "phone": "+91 751 2415124",
    "emergency24x7": true,
    "lat": 26.1912,
    "lng": 78.1568,
    "verified": true,
    "inventory": {
      "A+": 18,
      "A-": 5,
      "AB+": 11,
      "AB-": 3,
      "B+": 26,
      "B-": 6,
      "O+": 24,
      "O-": 7
    }
  },
  {
    "id": 6,
    "name": "Rotary Club Gwalior Blood Bank & Apheresis Centre",
    "hospitalId": 18,
    "hospital_id": 18,
    "address": "Jayendraganj Main Road, Near SBI Zonal Office, Lashkar, Gwalior",
    "contactPerson": "Blood Transfusion Officer",
    "phone": "+91 751 2321155",
    "emergency24x7": true,
    "lat": 26.2045,
    "lng": 78.1678,
    "verified": true,
    "inventory": {
      "A+": 18,
      "A-": 6,
      "AB+": 14,
      "AB-": 4,
      "B+": 25,
      "B-": 8,
      "O+": 30,
      "O-": 7
    }
  },
  {
    "id": 7,
    "name": "Kamla Raja Maternity Hospital (KRH) Blood Storage Centre",
    "hospitalId": 6,
    "hospital_id": 6,
    "address": "KRH Medical College Campus, Kampoo Road, Gwalior",
    "contactPerson": "Duty Medical Officer (Blood Bank)",
    "phone": "+91 751 2403322",
    "emergency24x7": true,
    "lat": 26.1978,
    "lng": 78.1622,
    "verified": true,
    "inventory": {
      "A+": 22,
      "A-": 8,
      "AB+": 16,
      "AB-": 5,
      "B+": 28,
      "B-": 9,
      "O+": 35,
      "O-": 10
    }
  }
];

const AMBULANCES_DATABASE = [
  {
    "id": 1,
    "serviceName": "108 National Emergency Ambulance (Gwalior Central Control)",
    "service_name": "108 National Emergency Ambulance (Gwalior Central Control)",
    "vehicleType": "ALS (Advanced Life Support)",
    "vehicle_type": "ALS (Advanced Life Support)",
    "operatorType": "Government",
    "operator_type": "Government",
    "phone": "108",
    "baseLocation": "JAH Campus & District Dispatch Centres",
    "base_location": "JAH Campus & District Dispatch Centres",
    "lat": 26.1985,
    "lng": 78.1634,
    "available": true,
    "features": "Defibrillator, Transport Ventilator, Multipara Monitor, Suction Machine, Oxygen Cylinders"
  },
  {
    "id": 2,
    "serviceName": "102 Janani Express Ambulance (Maternity & Infant)",
    "service_name": "102 Janani Express Ambulance (Maternity & Infant)",
    "vehicleType": "BLS (Basic Life Support)",
    "vehicle_type": "BLS (Basic Life Support)",
    "operatorType": "Government",
    "operator_type": "Government",
    "phone": "102",
    "baseLocation": "Kamla Raja Hospital (KRH), Kampoo",
    "base_location": "Kamla Raja Hospital (KRH), Kampoo",
    "lat": 26.1965,
    "lng": 78.1618,
    "available": true,
    "features": "Neonatal Warmers, Oxygen Delivery, Emergency Obstetric Delivery Kit"
  },
  {
    "id": 3,
    "serviceName": "BIMR Cardiac Mobile Intensive Care Unit",
    "service_name": "BIMR Cardiac Mobile Intensive Care Unit",
    "vehicleType": "Mobile ICU (Cardiac Super Speciality)",
    "vehicle_type": "Mobile ICU (Cardiac Super Speciality)",
    "operatorType": "Hospital",
    "operator_type": "Hospital",
    "phone": "+91 751 2405601",
    "baseLocation": "BIMR Hospitals, Morar, Gwalior",
    "base_location": "BIMR Hospitals, Morar, Gwalior",
    "lat": 26.2312,
    "lng": 78.2215,
    "available": true,
    "features": "Invasive Blood Pressure Monitoring, Syringe Pumps, Advanced Pacemaker, CPR Auto-Pulse"
  },
  {
    "id": 4,
    "serviceName": "JAH Level-1 Trauma Emergency Ambulance",
    "service_name": "JAH Level-1 Trauma Emergency Ambulance",
    "vehicleType": "ALS (Advanced Life Support)",
    "vehicle_type": "ALS (Advanced Life Support)",
    "operatorType": "Government",
    "operator_type": "Government",
    "phone": "+91 751 2403222",
    "baseLocation": "Trauma Centre, JAH Kampoo",
    "base_location": "Trauma Centre, JAH Kampoo",
    "lat": 26.1985,
    "lng": 78.1634,
    "available": true,
    "features": "Spine Board, Cervical Collars, Ventilator, Resuscitation Bag, Suction Apparatus"
  },
  {
    "id": 5,
    "serviceName": "Indian Red Cross Emergency Ambulance Service",
    "service_name": "Indian Red Cross Emergency Ambulance Service",
    "vehicleType": "Patient Transport & BLS",
    "vehicle_type": "Patient Transport & BLS",
    "operatorType": "Trust",
    "operator_type": "Trust",
    "phone": "+91 751 2422002",
    "baseLocation": "Phoolbagh, Lashkar, Gwalior",
    "base_location": "Phoolbagh, Lashkar, Gwalior",
    "lat": 26.2095,
    "lng": 78.1752,
    "available": true,
    "features": "Oxygen Support, Stretcher, First-Aid Kit, Vital Signs Monitor"
  },
  {
    "id": 6,
    "serviceName": "City Centre 24x7 Private ICU Ambulance Network",
    "service_name": "City Centre 24x7 Private ICU Ambulance Network",
    "vehicleType": "ALS (Advanced Life Support)",
    "vehicle_type": "ALS (Advanced Life Support)",
    "operatorType": "Private",
    "operator_type": "Private",
    "phone": "+91 94251 10002",
    "baseLocation": "University Road, City Centre, Gwalior",
    "base_location": "University Road, City Centre, Gwalior",
    "lat": 26.2115,
    "lng": 78.2098,
    "available": true,
    "features": "Cardiac Defibrillator, Ventilator, Medical Oxygen, On-board Paramedic Team"
  },
  {
    "id": 7,
    "serviceName": "Gwalior Air Ambulance & Critical Airlift Response",
    "service_name": "Gwalior Air Ambulance & Critical Airlift Response",
    "vehicleType": "Air Ambulance (Aero-Medical Airlift)",
    "vehicle_type": "Air Ambulance (Aero-Medical Airlift)",
    "operatorType": "Private",
    "operator_type": "Private",
    "phone": "+91 98260 11211",
    "baseLocation": "Airport Road, Maharajpura Airbase Hub, Gwalior",
    "base_location": "Airport Road, Maharajpura Airbase Hub, Gwalior",
    "lat": 26.27,
    "lng": 78.225,
    "available": true,
    "features": "Aviation Ventilator, Transport Incubator, Multipara Cardiac Monitor, Emergency Flight Doctor"
  },
  {
    "id": 8,
    "serviceName": "Trauma Rapid First-Responder Bike Ambulance Unit",
    "service_name": "Trauma Rapid First-Responder Bike Ambulance Unit",
    "vehicleType": "First Responder Medical Bike",
    "vehicle_type": "First Responder Medical Bike",
    "operatorType": "Government",
    "operator_type": "Government",
    "phone": "108",
    "baseLocation": "Phoolbagh Chowk, Lashkar Hub, Gwalior",
    "base_location": "Phoolbagh Chowk, Lashkar Hub, Gwalior",
    "lat": 26.2088,
    "lng": 78.1745,
    "available": true,
    "features": "Automated External Defibrillator (AED), Portable Oxygen Kit, Emergency Trauma Dressing, Paramedic Kit"
  }
];

if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    HOSPITAL_DATABASE,
    DOCTORS_DATABASE,
    BLOOD_BANKS_DATABASE,
    AMBULANCES_DATABASE
  };
}
