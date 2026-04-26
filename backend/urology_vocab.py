UROLOGY_VOCAB = {
    # Hematuria
    "blood in urine": "hematuria, gross hematuria, microscopic hematuria",
    "pink urine": "hematuria, microscopic hematuria, pigmenturia",
    "red urine": "hematuria, gross hematuria, nephrolithiasis, urothelial carcinoma",
    "blood clots in pee": "gross hematuria with clot, bladder neck obstruction",

    # LUTS / BPH
    "trouble peeing": "dysuria, hesitancy, bladder outlet obstruction, BPH",
    "weak stream": "decreased force of stream, BPH, urethral stricture",
    "frequent urination": "urinary frequency, polyuria, overactive bladder, OAB",
    "getting up at night": "nocturia, BPH, polyuria, overactive bladder",
    "dribbling": "post-void dribbling, terminal dribbling, overflow incontinence",
    "hesitancy": "urinary hesitancy, obstructive uropathy, BPH",
    "feeling not empty": "incomplete emptying, post-void residual, PVR, urinary retention",
    "sudden urge": "urinary urgency, detrusor overactivity, overactive bladder",

    # Stones
    "kidney stone": "nephrolithiasis, renal calculus, urolithiasis",
    "stone pain": "renal colic, ureteral colic, flank pain",
    "flank pain": "costovertebral angle tenderness, CVA tenderness, hydronephrosis, nephrolithiasis",
    "back pain with nausea": "renal colic, nephrolithiasis, obstructive uropathy",

    # UTI / Infection
    "burning when peeing": "dysuria, urethritis, cystitis, urinary tract infection, UTI",
    "bladder infection": "cystitis, lower urinary tract infection",
    "cloudy urine": "pyuria, bacteriuria, UTI",
    "smelly urine": "malodorous urine, bacteriuria, UTI",
    "kidney infection": "pyelonephritis, upper urinary tract infection",

    # Incontinence
    "leaking urine": "urinary incontinence, enuresis",
    "leaking when i cough": "stress urinary incontinence, SUI, intrinsic sphincter deficiency",
    "can't make it to the bathroom": "urge urinary incontinence, UUI, detrusor instability",
    "bed wetting": "nocturnal enuresis",
    "fallen bladder": "cystocele, pelvic organ prolapse",

    # Sexual Health / ED / Prostate
    "no erection": "erectile dysfunction, ED, impotence",
    "trouble getting hard": "erectile dysfunction, organic ED, psychogenic ED",
    "performance issues": "erectile dysfunction, premature ejaculation",
    "curved penis": "Peyronie's disease, penile curvature",
    "high psa": "elevated prostate-specific antigen, prostate cancer screening",
    "enlarged prostate": "benign prostatic hyperplasia, BPH, prostatomegaly",

    # Testicular / Scrotal
    "testicle pain": "orchialgia, testicular torsion, epididymitis",
    "lump in testicle": "testicular mass, spermatocele, hydrocele, testicular cancer",
    "scrotal swelling": "hydrocele, varicocele, scrotal edema",
    "pain in groin": "inguinal pain, epididymitis, inguinal hernia",

    # Post-Procedural
    "after vasectomy": "post-vasectomy follow-up, post-vasectomy pain syndrome",
    "after cystoscopy": "post-procedural dysuria, hematuria following instrumentation",
    "blood after procedure": "post-operative hematuria",
}


def expand_query(query: str) -> str:
    """Append urology clinical synonyms to a lay query before embedding.

    Matches lay phrases case-insensitively. Original query is preserved;
    expansions are appended in parentheses to maximize semantic overlap
    with clinical guideline content.
    """
    query_lower = query.lower()
    expansions = []
    for lay_term, clinical_terms in UROLOGY_VOCAB.items():
        if lay_term in query_lower:
            expansions.append(clinical_terms)
    if expansions:
        return f"{query} ({', '.join(expansions)})"
    return query


# TODO: extend with SNOMED CT urology subset / AUA terminology.
# Vocab layer is intentionally swappable — replace this dict to retarget
# the system at cardiology, orthopedics, or any other specialty.
