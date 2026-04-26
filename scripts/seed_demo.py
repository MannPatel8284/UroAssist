import os
import uuid
from fpdf import FPDF
from backend.ingestion import ingest_pdf

def create_clinical_pdf(path: str):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    
    pdf.set_font("Helvetica", style="B", size=16)
    pdf.cell(200, 10, txt="Urology Clinical Guidelines", ln=1, align="C")
    pdf.ln(10)
    
    pdf.set_font("Helvetica", style="B", size=14)
    pdf.cell(200, 10, txt="1. Hematuria Workup", ln=1)
    pdf.set_font("Helvetica", size=12)
    text1 = (
        "Gross hematuria or painless gross hematuria in adults is a red flag and requires "
        "immediate evaluation to rule out malignancy. The standard evaluation includes a "
        "CT urography to assess the upper urinary tract and cystoscopy to assess the bladder "
        "and urethra. Microscopic hematuria also requires workup depending on patient risk factors."
    )
    pdf.multi_cell(0, 10, txt=text1)
    pdf.ln(5)
    
    pdf.set_font("Helvetica", style="B", size=14)
    pdf.cell(200, 10, txt="2. BPH Evaluation", ln=1)
    pdf.set_font("Helvetica", size=12)
    text2 = (
        "Evaluation of Benign Prostatic Hyperplasia (BPH) includes the IPSS scoring questionnaire, "
        "uroflowmetry, and post-void residual (PVR) measurement. First-line medical therapy "
        "includes alpha-blockers (e.g., tamsulosin) and 5-alpha reductase inhibitors (5-ARIs). "
        "Urinary retention is a severe complication of BPH."
    )
    pdf.multi_cell(0, 10, txt=text2)
    pdf.ln(5)
    
    pdf.set_font("Helvetica", style="B", size=14)
    pdf.cell(200, 10, txt="3. Kidney Stone Management", ln=1)
    pdf.set_font("Helvetica", size=12)
    text3 = (
        "Patients presenting with flank pain should be evaluated for nephrolithiasis. "
        "Non-contrast CT KUB is the imaging modality of choice. Management depends on stone size. "
        "Medical Expulsive Therapy (MET) may be used for small stones. Larger stones may "
        "require surgical intervention such as ureteroscopy or ESWL. Fever with flank pain "
        "suggests an infected stone and is a urologic emergency due to sepsis risk."
    )
    pdf.multi_cell(0, 10, txt=text3)
    pdf.ln(5)
    
    pdf.set_font("Helvetica", style="B", size=14)
    pdf.cell(200, 10, txt="4. UTI Workup", ln=1)
    pdf.set_font("Helvetica", size=12)
    text4 = (
        "Urinalysis and urine culture are standard for diagnosing UTI. Distinguish between "
        "complicated and uncomplicated UTIs."
    )
    pdf.multi_cell(0, 10, txt=text4)
    pdf.ln(5)
    
    pdf.set_font("Helvetica", style="B", size=14)
    pdf.cell(200, 10, txt="5. Red Flags", ln=1)
    pdf.set_font("Helvetica", size=12)
    text5 = (
        "Acute testicular pain requires immediate evaluation with scrotal ultrasound to rule out "
        "testicular torsion, a surgical emergency. Urinary retention and fever with flank pain "
        "also require urgent evaluation."
    )
    pdf.multi_cell(0, 10, txt=text5)
    
    pdf.output(path)

def create_coding_pdf(path: str):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    
    pdf.set_font("Helvetica", style="B", size=16)
    pdf.cell(200, 10, txt="Urology Coding Reference", ln=1, align="C")
    pdf.ln(10)
    
    pdf.set_font("Helvetica", style="B", size=14)
    pdf.cell(200, 10, txt="Common CPT Codes", ln=1)
    pdf.set_font("Helvetica", size=12)
    text1 = (
        "52000 - Cystourethroscopy (separate procedure).\n"
        "52204 - Cystourethroscopy, with biopsy(s).\n"
        "52601 - Transurethral resection of prostate (TURP).\n"
        "50590 - Lithotripsy, extracorporeal shock wave.\n"
        "55250 - Vasectomy, unilateral or bilateral.\n"
        "55700 - Biopsy, prostate; needle or punch, single or multiple, any approach.\n"
        "51798 - Measurement of post-voiding residual urine and/or bladder capacity by ultrasound.\n"
        "51741 - Complex uroflowmetry."
    )
    pdf.multi_cell(0, 10, txt=text1)
    pdf.ln(5)
    
    pdf.set_font("Helvetica", style="B", size=14)
    pdf.cell(200, 10, txt="Common ICD-10 Codes", ln=1)
    pdf.set_font("Helvetica", size=12)
    text2 = (
        "N39.0 - Urinary tract infection, site not specified.\n"
        "R31.0 - Gross hematuria.\n"
        "R31.1 - Benign essential microscopic hematuria.\n"
        "R31.2 - Other microscopic hematuria.\n"
        "N20.0 - Calculus of kidney.\n"
        "N40.0 - Benign prostatic hyperplasia without lower urinary tract symptoms.\n"
        "N52.9 - Male erectile dysfunction, unspecified.\n"
        "N81.10 - Cystocele, unspecified.\n"
        "N45.1 - Epididymitis.\n"
        "N45.2 - Orchitis.\n"
        "Z12.5 - Encounter for screening for malignant neoplasm of prostate (PSA screening)."
    )
    pdf.multi_cell(0, 10, txt=text2)
    pdf.ln(5)
    
    pdf.set_font("Helvetica", style="B", size=14)
    pdf.cell(200, 10, txt="Modifiers", ln=1)
    pdf.set_font("Helvetica", size=12)
    text3 = (
        "Modifier 22 - Increased procedural services.\n"
        "Modifier 59 - Distinct procedural service.\n"
        "Modifier 78 - Unplanned return to operating room."
    )
    pdf.multi_cell(0, 10, txt=text3)
    
    pdf.output(path)

def main():
    clinical_dir = "data/clinical"
    coding_dir = "data/coding"
    
    os.makedirs(clinical_dir, exist_ok=True)
    os.makedirs(coding_dir, exist_ok=True)
    
    clinical_pdf_path = os.path.join(clinical_dir, "sample_urology_guideline.pdf")
    coding_pdf_path = os.path.join(coding_dir, "sample_urology_coding.pdf")
    
    if not os.listdir(clinical_dir):
        print(f"Creating {clinical_pdf_path}...")
        create_clinical_pdf(clinical_pdf_path)
    
    if not os.listdir(coding_dir):
        print(f"Creating {coding_pdf_path}...")
        create_coding_pdf(coding_pdf_path)
        
    print("Ingesting clinical PDF...")
    clinical_res = ingest_pdf(clinical_pdf_path, str(uuid.uuid4()), "clinical")
    print(f"Ingested {clinical_res['doc_name']} into {clinical_res['collection']} ({clinical_res['num_chunks']} chunks)")
    
    print("Ingesting coding PDF...")
    coding_res = ingest_pdf(coding_pdf_path, str(uuid.uuid4()), "coding")
    print(f"Ingested {coding_res['doc_name']} into {coding_res['collection']} ({coding_res['num_chunks']} chunks)")
    
    print("Demo data seeded successfully. Ready to demo!")

if __name__ == "__main__":
    main()
