"""Regulatory templates for Medizintechnik projects."""

MDR_TEMPLATES = [
    {
        "framework": "EU-MDR 2017/745",
        "clause": "Annex I, Chapter I",
        "title": "General Safety and Performance Requirements (GSPR)",
        "description": "Devices shall achieve the performance intended by their manufacturer and shall be designed and manufactured in such a way that, during normal conditions of use, they are suitable for their intended purpose.",
        "applies_to": "All Levels",
    },
    {
        "framework": "EU-MDR 2017/745",
        "clause": "Annex II",
        "title": "Technical Documentation",
        "description": "Device description, specification, reference to previous/similar generations, design and manufacturing information, general safety and performance requirements.",
        "applies_to": "All Levels",
    },
    {
        "framework": "EU-MDR 2017/745",
        "clause": "Annex III",
        "title": "Post-Market Surveillance",
        "description": "The post-market surveillance system shall be proportionate to the risk class and appropriate for the type of device.",
        "applies_to": "All Levels",
    },
    {
        "framework": "EU-MDR 2017/745",
        "clause": "Annex XIV",
        "title": "Clinical Evaluation",
        "description": "Clinical evaluation shall follow a defined and methodologically sound procedure based on a critical evaluation of relevant scientific literature, clinical investigation results, and post-market clinical follow-up.",
        "applies_to": "Level C-E",
    },
    {
        "framework": "EU-MDR 2017/745",
        "clause": "Article 10",
        "title": "General Obligations of Manufacturers",
        "description": "Manufacturers shall ensure that their devices are designed and manufactured in accordance with the requirements of this Regulation and establish, document, implement and maintain a quality management system.",
        "applies_to": "All Levels",
    },
    {
        "framework": "EU-MDR 2017/745",
        "clause": "Annex IX",
        "title": "Conformity Assessment Based on QMS and Technical Documentation",
        "description": "Assessment of quality management system covering design and development, production processes, and post-market activities.",
        "applies_to": "Level B-E",
    },
]

ISO_13485_TEMPLATES = [
    {
        "framework": "ISO 13485:2016",
        "clause": "4.1",
        "title": "Quality Management System — General Requirements",
        "description": "Organizations must document a quality management system and maintain its effectiveness in accordance with the requirements of this International Standard.",
        "applies_to": "All Levels",
    },
    {
        "framework": "ISO 13485:2016",
        "clause": "7.3",
        "title": "Design and Development",
        "description": "Planning, inputs, outputs, review, verification, validation, and transfer of design.",
        "applies_to": "All Levels",
    },
    {
        "framework": "ISO 13485:2016",
        "clause": "7.5",
        "title": "Production and Service Provision",
        "description": "Control of production and service provision including validation of processes, identification and traceability, and preservation of product.",
        "applies_to": "Level B-E",
    },
    {
        "framework": "ISO 13485:2016",
        "clause": "8.2",
        "title": "Monitoring and Measurement — Feedback and Complaints",
        "description": "Gather and monitor information about conformity of product, including customer feedback and complaint handling procedures.",
        "applies_to": "All Levels",
    },
]

ISO_14971_TEMPLATES = [
    {
        "framework": "ISO 14971:2019",
        "clause": "4.2",
        "title": "Risk Management Plan",
        "description": "A risk management plan shall be established for each medical device.",
        "applies_to": "All Levels",
    },
    {
        "framework": "ISO 14971:2019",
        "clause": "5.4",
        "title": "Risk Estimation",
        "description": "For each identified hazardous situation, the associated risk(s) shall be estimated using available information or data.",
        "applies_to": "All Levels",
    },
    {
        "framework": "ISO 14971:2019",
        "clause": "6",
        "title": "Risk Evaluation and Control",
        "description": "Each identified risk shall be evaluated. Risk control measures shall be implemented and verified for effectiveness.",
        "applies_to": "All Levels",
    },
    {
        "framework": "ISO 14971:2019",
        "clause": "9",
        "title": "Post-Production Information",
        "description": "A system for production and post-production information shall be established to gather and review information about the device during its lifecycle.",
        "applies_to": "Level B-E",
    },
]

IEC_62304_TEMPLATES = [
    {
        "framework": "IEC 62304:2006+A1:2015",
        "clause": "5.1",
        "title": "Software Development Planning",
        "description": "Establish a software development plan tailored to the software safety class (A, B, or C). Plan shall cover: development life cycle model, tools, standards, and activities.",
        "applies_to": "Level C-E",
    },
    {
        "framework": "IEC 62304:2006+A1:2015",
        "clause": "5.2",
        "title": "Software Requirements Analysis",
        "description": "Define and document software requirements derived from system requirements including functional, performance, interface, and safety requirements.",
        "applies_to": "Level C-E",
    },
    {
        "framework": "IEC 62304:2006+A1:2015",
        "clause": "5.3",
        "title": "Software Architectural Design",
        "description": "Develop and document the software architecture identifying software items and their interfaces. Verify architecture against requirements.",
        "applies_to": "Level C-E",
    },
    {
        "framework": "IEC 62304:2006+A1:2015",
        "clause": "5.5",
        "title": "Software Unit Implementation and Verification",
        "description": "Implement each software unit and verify that it meets its requirements. Document unit testing procedures and results.",
        "applies_to": "Level C-E",
    },
    {
        "framework": "IEC 62304:2006+A1:2015",
        "clause": "5.7",
        "title": "Software Integration and Integration Testing",
        "description": "Integrate the software items and test the integrated software against the software architectural design.",
        "applies_to": "Level C-E",
    },
    {
        "framework": "IEC 62304:2006+A1:2015",
        "clause": "7.1",
        "title": "Software Maintenance Plan",
        "description": "Establish a software maintenance plan including procedures for feedback and problem resolution throughout the software lifecycle.",
        "applies_to": "Level C-E",
    },
]

IEC_62366_TEMPLATES = [
    {
        "framework": "IEC 62366-1:2015+A1:2020",
        "clause": "5.1",
        "title": "Usability Engineering Process",
        "description": "Establish, document, and maintain a usability engineering process. Specify intended users, uses, and use environments for the device.",
        "applies_to": "Level B-E",
    },
    {
        "framework": "IEC 62366-1:2015+A1:2020",
        "clause": "5.4",
        "title": "Formative and Summative Evaluation",
        "description": "Conduct formative evaluations during development and a summative evaluation to confirm the user interface meets usability requirements and does not cause unacceptable risks.",
        "applies_to": "Level B-E",
    },
    {
        "framework": "IEC 62366-1:2015+A1:2020",
        "clause": "5.6",
        "title": "Usability Validation Testing",
        "description": "Validate the usability of the device with representative users under simulated or actual use conditions.",
        "applies_to": "Level C-E",
    },
]

ISO_10993_TEMPLATES = [
    {
        "framework": "ISO 10993-1:2018",
        "clause": "Part 1",
        "title": "Biocompatibility Evaluation — Framework",
        "description": "Evaluate and manage the biological risk of medical devices based on their nature and extent of body contact. Categorize by contact type (surface, externally communicating, implant) and duration.",
        "applies_to": "Level D-E",
    },
    {
        "framework": "ISO 10993-5:2009",
        "clause": "Part 5",
        "title": "Cytotoxicity Testing",
        "description": "Test for the potential of medical device materials to cause cytotoxic effects in vitro using cell culture methods.",
        "applies_to": "Level D-E",
    },
    {
        "framework": "ISO 10993-10:2021",
        "clause": "Part 10",
        "title": "Irritation and Skin Sensitization",
        "description": "Evaluate the potential of device materials to cause irritation or skin sensitization through appropriate in vitro and/or in vivo tests.",
        "applies_to": "Level D-E",
    },
]

GDPR_TEMPLATES = [
    {
        "framework": "DSGVO / GDPR",
        "clause": "Art. 5",
        "title": "Grundsätze der Datenverarbeitung / Principles of Processing",
        "description": "Personenbezogene Daten müssen auf rechtmäßige, faire und transparente Weise verarbeitet werden (Rechtmäßigkeit, Zweckbindung, Datenminimierung, Richtigkeit, Speicherbegrenzung, Integrität).",
        "applies_to": "All Levels",
    },
    {
        "framework": "DSGVO / GDPR",
        "clause": "Art. 25",
        "title": "Datenschutz durch Technikgestaltung / Privacy by Design",
        "description": "Der Verantwortliche trifft geeignete technische und organisatorische Maßnahmen, um Datenschutzgrundsätze wirksam umzusetzen (Privacy by Default und Privacy by Design).",
        "applies_to": "All Levels",
    },
    {
        "framework": "DSGVO / GDPR",
        "clause": "Art. 35",
        "title": "Datenschutz-Folgenabschätzung / Data Protection Impact Assessment",
        "description": "Bei Verarbeitungsvorgängen mit voraussichtlich hohem Risiko muss der Verantwortliche vorab eine Datenschutz-Folgenabschätzung durchführen.",
        "applies_to": "Level C-E",
    },
]

ALL_TEMPLATES = (
    MDR_TEMPLATES
    + ISO_13485_TEMPLATES
    + ISO_14971_TEMPLATES
    + IEC_62304_TEMPLATES
    + IEC_62366_TEMPLATES
    + ISO_10993_TEMPLATES
    + GDPR_TEMPLATES
)
