from datetime import datetime
from typing import List, Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import (
    Mapped,
    declarative_base,
    mapped_column,
    relationship,
    synonym,
)
from sqlalchemy.sql.sqltypes import Boolean, BigInteger

Base = declarative_base()


class UKRRPatient(Base):
    __tablename__ = "PATIENTS"

    HOSP_CENTRE: Mapped[str] = mapped_column(String)
    hosp_centre: Mapped[str] = synonym("HOSP_CENTRE")

    RR_NO: Mapped[int] = mapped_column(Integer, primary_key=True)
    rr_no: Mapped[int] = synonym("RR_NO")

    SURNAME: Mapped[str] = mapped_column(String)
    surname: Mapped[str] = synonym("SURNAME")

    FORENAME: Mapped[str] = mapped_column(String)
    forename: Mapped[str] = synonym("FORENAME")

    SEX: Mapped[str] = mapped_column(String(1))
    sex: Mapped[str] = synonym("SEX")

    NHS_NO: Mapped[int] = mapped_column("NEW_NHS_NO", Integer)
    nhs_no: Mapped[int] = synonym("NHS_NO")

    CHI_NO: Mapped[int] = mapped_column(Integer)
    chi_no: Mapped[int] = synonym("CHI_NO")

    HSC_NO: Mapped[int] = mapped_column(Integer)
    hsc_no: Mapped[int] = synonym("HSC_NO")

    UKTSSA_NO: Mapped[int] = mapped_column(Integer)
    uk_tssa_no: Mapped[int] = synonym("UKTSSA_NO")

    DATE_BIRTH: Mapped[str] = mapped_column(Date)
    date_birth: Mapped[str] = synonym("DATE_BIRTH")

    DATE_DEATH: Mapped[str] = mapped_column(Date)
    date_death: Mapped[str] = synonym("DATE_DEATH")

    ETHNICITY: Mapped[str] = mapped_column("ETHGR_CODE", String)
    ethnicity: Mapped[str] = synonym("ETHNICITY")

    BLOOD_GROUP: Mapped[str] = mapped_column(String)
    blood_group: Mapped[str] = synonym("BLOOD_GROUP")

    BLOOD_RHESUS: Mapped[str] = mapped_column("BLOOD_GROUP_RHESUS", String)
    blood_rhesus: Mapped[str] = synonym("BLOOD_RHESUS")

    COD_READ: Mapped[str] = mapped_column(String)
    cod_read: Mapped[str] = synonym("COD_READ")

    COD_EDTA1: Mapped[str] = mapped_column(String)
    cod_edta1: Mapped[str] = synonym("COD_EDTA1")

    COD_EDTA2: Mapped[str] = mapped_column(String)
    cod_edta2: Mapped[str] = synonym("COD_EDTA2")

    COD_TEXT: Mapped[str] = mapped_column(String)
    cod_text: Mapped[str] = synonym("COD_TEXT")

    DATE_REGISTERED: Mapped[str] = mapped_column(Date)
    date_registered: Mapped[str] = synonym("DATE_REGISTERED")

    FIRST_SEEN_DATE: Mapped[str] = mapped_column(Date)
    first_seen_date: Mapped[str] = synonym("FIRST_SEEN_DATE")

    OPT_OUT_FLAG: Mapped[str] = mapped_column(String)
    opt_out_flag: Mapped[str] = synonym("OPT_OUT_FLAG")

    PATIENT_DEMOGRAPHICS: Mapped[List["Patient_Demographics"]] = relationship(
        back_populates="UKRR_PATIENT"
    )
    patient_demographics: Mapped[List["Patient_Demographics"]] = synonym(
        "PATIENT_DEMOGRAPHICS"
    )


class Patient_Demographics(Base):
    __tablename__ = "PATIENT_DEMOG"

    RR_NO: Mapped[int] = mapped_column(
        Integer, ForeignKey("PATIENTS.RR_NO"), primary_key=True
    )
    rr_no: Mapped[int] = synonym("RR_NO")

    HOSP_CENTRE: Mapped[str] = mapped_column(String, primary_key=True)
    hosp_centre: Mapped[str] = synonym("HOSP_CENTRE")

    SURNAME: Mapped[str] = mapped_column(String)
    surname: Mapped[str] = synonym("SURNAME")

    FORENAME: Mapped[str] = mapped_column(String)
    forename: Mapped[str] = synonym("FORENAME")

    BIRTH_NAME: Mapped[str] = mapped_column(String)
    birth_name: Mapped[str] = synonym("BIRTH_NAME")

    ALIAS_NAME: Mapped[str] = mapped_column(String)
    alias_name: Mapped[str] = synonym("ALIAS_NAME")

    DATE_BIRTH: Mapped[str] = mapped_column(Date)
    date_birth: Mapped[str] = synonym("DATE_BIRTH")

    DATE_DEATH: Mapped[str] = mapped_column(Date)
    date_death: Mapped[str] = synonym("DATE_DEATH")

    NHS_NO: Mapped[int] = mapped_column("NEW_NHS_NO", Integer)
    nhs_no: Mapped[int] = synonym("NHS_NO")

    CHI_NO: Mapped[int] = mapped_column(Integer)
    chi_no: Mapped[int] = synonym("CHI_NO")

    HSC_NO: Mapped[int] = mapped_column(Integer)
    hsc_no: Mapped[int] = synonym("HSC_NO")

    UKTSSA_NO: Mapped[int] = mapped_column(Integer)
    uk_tssa_no: Mapped[int] = synonym("UKTSSA_NO")

    LOCAL_HOSP_NO: Mapped[str] = mapped_column(String)
    local_hosp_no: Mapped[str] = synonym("LOCAL_HOSP_NO")

    FIRST_SEEN_DATE: Mapped[str] = mapped_column(Date)
    first_seen_date: Mapped[str] = synonym("FIRST_SEEN_DATE")

    UKRR_PATIENT: Mapped["UKRRPatient"] = relationship(
        back_populates="PATIENT_DEMOGRAPHICS"
    )
    ukrr_patient: Mapped["UKRRPatient"] = synonym("UKRR_PATIENT")


class RSA_Extraction_Items(Base):
    __tablename__ = "RSA_EXTRACTION_ITEMS"

    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    id: Mapped[int] = synonym("ID")

    ITEM_GROUP: Mapped[str] = mapped_column(String(50))
    item_group: Mapped[str] = synonym("ITEM_GROUP")

    BLOCK_PREFIX: Mapped[str] = mapped_column(String(10))
    block_prefix: Mapped[str] = synonym("BLOCK_PREFIX")

    VALUE_ITEM: Mapped[str] = mapped_column(String(10))
    value_item: Mapped[str] = synonym("VALUE_ITEM")

    DATE_ITEM: Mapped[str] = mapped_column(String(10))
    date_item: Mapped[str] = synonym("DATE_ITEM")

    PREPOST: Mapped[str] = mapped_column(String(10))
    prepost: Mapped[str] = synonym("PREPOST")

    DESCRIPTION: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = synonym("DESCRIPTION")


class UKRR_Deleted_Patient(Base):
    __tablename__ = "DELETED_PATIENTS"

    RR_NO: Mapped[int] = mapped_column(Integer, primary_key=True)
    rr_no: Mapped[int] = synonym("RR_NO")

    SURNAME: Mapped[str] = mapped_column(String)
    surname: Mapped[str] = synonym("SURNAME")

    FORENAME: Mapped[str] = mapped_column(String)
    forename: Mapped[str] = synonym("FORENAME")

    SEX: Mapped[str] = mapped_column(String)
    sex: Mapped[str] = synonym("SEX")

    NHS_NO: Mapped[int] = mapped_column("NEW_NHS_NO", Integer)
    nhs_no: Mapped[int] = synonym("NHS_NO")

    CHI_NO: Mapped[int] = mapped_column(Integer)
    chi_no: Mapped[int] = synonym("CHI_NO")

    HSC_NO: Mapped[int] = mapped_column(Integer)
    hsc_no: Mapped[int] = synonym("HSC_NO")

    UKTSSA_NO: Mapped[int] = mapped_column(Integer)
    uk_tssa_no: Mapped[int] = synonym("UKTSSA_NO")

    LOCAL_HOSP_NO: Mapped[str] = mapped_column(String)
    local_hosp_no: Mapped[str] = synonym("LOCAL_HOSP_NO")

    DATE_BIRTH: Mapped[str] = mapped_column(Date)
    date_birth: Mapped[str] = synonym("DATE_BIRTH")

    DATE_DEATH: Mapped[str] = mapped_column(Date)
    date_death: Mapped[str] = synonym("DATE_DEATH")


class QuarterlyTreatment(Base):
    __tablename__ = "QUARTERLY_TREATMENT"

    RR_NO: Mapped[int] = mapped_column(Integer, primary_key=True)
    rr_no: Mapped[int] = synonym("RR_NO")

    DATE_START: Mapped[str] = mapped_column(DateTime, primary_key=True)
    date_start: Mapped[str] = synonym("DATE_START")

    TREATMENT_MODALITY: Mapped[str] = mapped_column(String, primary_key=True)
    treatment_modality: Mapped[str] = synonym("TREATMENT_MODALITY")

    TREATMENT_CENTRE: Mapped[str] = mapped_column(String, primary_key=True)
    treatment_centre: Mapped[str] = synonym("TREATMENT_CENTRE")

    HOSP_CENTRE: Mapped[str] = mapped_column(String, primary_key=True)
    hosp_centre: Mapped[str] = synonym("HOSP_CENTRE")

    DATE_END: Mapped[str] = mapped_column(DateTime)
    date_end: Mapped[str] = synonym("DATE_END")

    ADD_HAEMO_ON_PD: Mapped[str] = mapped_column(String)
    add_haemo_on_pd: Mapped[str] = synonym("ADD_HAEMO_ON_PD")

    CREATININE: Mapped[float] = mapped_column(Numeric(38, 4))
    creatinine: Mapped[float] = synonym("CREATININE")

    UREA: Mapped[float] = mapped_column(Numeric(38, 4))
    urea: Mapped[float] = synonym("UREA")

    HAEMOGLOBIN: Mapped[float] = mapped_column(Numeric(38, 4))
    haemoglobin: Mapped[float] = synonym("HAEMOGLOBIN")

    FERRETIN: Mapped[float] = mapped_column(Numeric(38, 4))
    ferretin: Mapped[float] = synonym("FERRETIN")

    ALBUMIN: Mapped[float] = mapped_column(Numeric(38, 4))
    albumin: Mapped[float] = synonym("ALBUMIN")

    ALUMINIUM: Mapped[float] = mapped_column(Numeric(38, 4))
    aluminium: Mapped[float] = synonym("ALUMINIUM")

    HBA1C: Mapped[float] = mapped_column(Numeric(38, 4))
    hba1c: Mapped[float] = synonym("HBA1C")

    CHOLESTEROL: Mapped[float] = mapped_column(Numeric(38, 4))
    cholesterol: Mapped[float] = synonym("CHOLESTEROL")

    IPTH: Mapped[float] = mapped_column(Numeric(38, 4))
    ipth: Mapped[float] = synonym("IPTH")

    CALCIUM_UNCORR: Mapped[float] = mapped_column(Numeric(38, 4))
    calcium_uncorr: Mapped[float] = synonym("CALCIUM_UNCORR")

    CALCIUM_CORR: Mapped[float] = mapped_column(Numeric(38, 4))
    calcium_corr: Mapped[float] = synonym("CALCIUM_CORR")

    PHOSPHATE: Mapped[float] = mapped_column(Numeric(38, 4))
    phosphate: Mapped[float] = synonym("PHOSPHATE")

    BICARBONATE: Mapped[float] = mapped_column(Numeric(38, 4))
    bicarbonate: Mapped[float] = synonym("BICARBONATE")

    SYSTOLIC_BP: Mapped[float] = mapped_column(Numeric(20, 0))
    systolic_bp: Mapped[float] = synonym("SYSTOLIC_BP")

    DIASTOLIC_BP: Mapped[float] = mapped_column(Numeric(20, 0))
    diastolic_bp: Mapped[float] = synonym("DIASTOLIC_BP")

    WEIGHT: Mapped[float] = mapped_column(Numeric(38, 4))
    weight: Mapped[float] = synonym("WEIGHT")

    UREA_REDUCTION_RATIO: Mapped[float] = mapped_column(Numeric(38, 4))
    urea_reduction_ratio: Mapped[float] = synonym("UREA_REDUCTION_RATIO")

    EPO_USE: Mapped[str] = mapped_column(String)
    epo_use: Mapped[str] = synonym("EPO_USE")

    HD_SUPERVISON: Mapped[str] = mapped_column(String)
    hd_supervison: Mapped[str] = synonym("HD_SUPERVISON")

    DIALYSER_USED: Mapped[str] = mapped_column(String)
    dialyser_used: Mapped[str] = synonym("DIALYSER_USED")

    FLOW_RATE: Mapped[float] = mapped_column(Numeric(20, 0))
    flow_rate: Mapped[float] = synonym("FLOW_RATE")

    DIAL_REUSE: Mapped[str] = mapped_column(String)
    dial_reuse: Mapped[str] = synonym("DIAL_REUSE")

    TIMES_PER_WEEK: Mapped[float] = mapped_column(Numeric(20, 0))
    times_per_week: Mapped[float] = synonym("TIMES_PER_WEEK")

    DIAL_TIME: Mapped[float] = mapped_column(Numeric(38, 4))
    dial_time: Mapped[float] = synonym("DIAL_TIME")

    BICARB_DIAL: Mapped[str] = mapped_column(String)
    bicarb_dial: Mapped[str] = synonym("BICARB_DIAL")

    WEEKLY_FLUID_VOL: Mapped[float] = mapped_column(Numeric(38, 4))
    weekly_fluid_vol: Mapped[float] = synonym("WEEKLY_FLUID_VOL")

    BAG_SIZE: Mapped[float] = mapped_column(Numeric(38, 4))
    bag_size: Mapped[float] = synonym("BAG_SIZE")

    CENTRE_PRI: Mapped[str] = mapped_column(String)
    centre_pri: Mapped[str] = synonym("CENTRE_PRI")

    POST_SYSTOLIC_BP: Mapped[float] = mapped_column(Numeric(20, 0))
    post_systolic_bp: Mapped[float] = synonym("POST_SYSTOLIC_BP")

    POST_DIASTOLIC_BP: Mapped[float] = mapped_column(Numeric(20, 0))
    post_diastolic_bp: Mapped[float] = synonym("POST_DIASTOLIC_BP")

    SODIUM: Mapped[float] = mapped_column(Numeric(38, 4))
    sodium: Mapped[float] = synonym("SODIUM")

    PD_DIALYSATE_KTV: Mapped[float] = mapped_column(Numeric(38, 4))
    pd_dialysate_ktv: Mapped[float] = synonym("PD_DIALYSATE_KTV")

    PD_URINE_KTV: Mapped[float] = mapped_column(Numeric(38, 4))
    pd_urine_ktv: Mapped[float] = synonym("PD_URINE_KTV")

    PD_NPCR: Mapped[float] = mapped_column(Numeric(38, 4))
    pd_npcr: Mapped[float] = synonym("PD_NPCR")

    CRP: Mapped[float] = mapped_column(Numeric(38, 4))
    crp: Mapped[float] = synonym("CRP")

    LDL_CHOLESTEROL: Mapped[float] = mapped_column(Numeric(38, 4))
    ldl_cholesterol: Mapped[float] = synonym("LDL_CHOLESTEROL")

    HDL_CHOLESTEROL: Mapped[float] = mapped_column(Numeric(38, 4))
    hdl_cholesterol: Mapped[float] = synonym("HDL_CHOLESTEROL")

    TRIGLYCERIDES: Mapped[float] = mapped_column(Numeric(38, 4))
    triglycerides: Mapped[float] = synonym("TRIGLYCERIDES")

    WAITING_LIST_STATUS: Mapped[str] = mapped_column(String)
    waiting_list_status: Mapped[str] = synonym("WAITING_LIST_STATUS")

    CREATININE_FIRST_MONTH: Mapped[float] = mapped_column(Numeric(38, 4))
    creatinine_first_month: Mapped[float] = synonym("CREATININE_FIRST_MONTH")

    CREATININE_SECOND_MONTH: Mapped[float] = mapped_column(Numeric(38, 4))
    creatinine_second_month: Mapped[float] = synonym("CREATININE_SECOND_MONTH")

    PERCENT_HYPOCHROMIC: Mapped[float] = mapped_column(Numeric(38, 4))
    percent_hypochromic: Mapped[float] = synonym("PERCENT_HYPOCHROMIC")

    MCH: Mapped[float] = mapped_column(Numeric(38, 4))
    mch: Mapped[float] = synonym("MCH")

    B12: Mapped[float] = mapped_column(Numeric(38, 4))
    b12: Mapped[float] = synonym("B12")

    RED_CELL_FOLATE: Mapped[float] = mapped_column(Numeric(38, 4))
    red_cell_folate: Mapped[float] = synonym("RED_CELL_FOLATE")

    TRANSFERRIN_SATURATION: Mapped[float] = mapped_column(Numeric(38, 4))
    transferrin_saturation: Mapped[float] = synonym("TRANSFERRIN_SATURATION")

    SERUM_POTASSIUM: Mapped[float] = mapped_column(Numeric(38, 4))
    serum_potassium: Mapped[float] = synonym("SERUM_POTASSIUM")

    PROTEIN_CREATININE_RATIO: Mapped[float] = mapped_column(Numeric(38, 4))
    protein_creatinine_ratio: Mapped[float] = synonym("PROTEIN_CREATININE_RATIO")

    ALBUMIN_CREATININE_RATIO: Mapped[float] = mapped_column(Numeric(38, 4))
    albumin_creatinine_ratio: Mapped[float] = synonym("ALBUMIN_CREATININE_RATIO")

    SERUM_CELL_FOLATE: Mapped[float] = mapped_column(Numeric(38, 4))
    serum_cell_folate: Mapped[float] = synonym("SERUM_CELL_FOLATE")

    ACE_INHIBITOR: Mapped[str] = mapped_column(String)
    ace_inhibitor: Mapped[str] = synonym("ACE_INHIBITOR")

    RENAGEL: Mapped[str] = mapped_column(String)
    renagel: Mapped[str] = synonym("RENAGEL")

    LANTHANUM: Mapped[str] = mapped_column(String)
    lanthanum: Mapped[str] = synonym("LANTHANUM")

    CINACALCET: Mapped[str] = mapped_column(String)
    cinacalcet: Mapped[str] = synonym("CINACALCET")

    CALCIUM_BASED_BINDER: Mapped[str] = mapped_column(String)
    calcium_based_binder: Mapped[str] = synonym("CALCIUM_BASED_BINDER")

    ALUCAPS: Mapped[str] = mapped_column(String)
    alucaps: Mapped[str] = synonym("ALUCAPS")

    SERUM_URATE: Mapped[float] = mapped_column(Numeric(38, 4))
    serum_urate: Mapped[float] = synonym("SERUM_URATE")

    STATIN_DRUG_USE: Mapped[str] = mapped_column(String)
    statin_drug_use: Mapped[str] = synonym("STATIN_DRUG_USE")

    HBA1C_MMOL: Mapped[float] = mapped_column(Numeric(3, 0))
    hba1c_mmol: Mapped[float] = synonym("HBA1C_MMOL")

    ALKALINE_PHOSPHATASE: Mapped[float] = mapped_column(Numeric(38, 4))
    alkaline_phosphatase: Mapped[float] = synonym("ALKALINE_PHOSPHATASE")


class ModalityCodes(Base):
    __tablename__ = "MODALITY_CODES"
    REGISTRY_CODE: Mapped[str] = mapped_column(String, primary_key=True)
    REGISTRY_CODE_TYPE: Mapped[str] = mapped_column(String)
    ACUTE: Mapped[bool] = mapped_column(Boolean)
    TRANSFER_IN: Mapped[bool] = mapped_column(Boolean)
    CKD_: Mapped[bool] = mapped_column("CKD", Boolean)
    CONS: Mapped[bool] = mapped_column(Boolean)
    RRT: Mapped[bool] = mapped_column(Boolean)
    END_OF_CARE: Mapped[bool] = mapped_column(Boolean)
    IS_IMPRECISE: Mapped[bool] = mapped_column(Boolean)
    REGISTRY_CODE_DESC: Mapped[Optional[str]] = mapped_column(String)
    EQUIV_MODALITY: Mapped[Optional[str]] = mapped_column(String)
    NHSBT_TRANSPLANT_TYPE: Mapped[Optional[str]] = mapped_column(String)
    TRANSFER_OUT: Mapped[Optional[bool]] = mapped_column(Boolean)


class RRNoLoad(Base):
    __tablename__ = "RR_NOLOAD"
    SITE: Mapped[str] = mapped_column(String, primary_key=True)
    QUARTER: Mapped[int] = mapped_column(Integer, primary_key=True)
    LOCAL_HOSP_NO: Mapped[str] = mapped_column(String, primary_key=True)
    SURNAME: Mapped[Optional[str]] = mapped_column(String)
    FORENAME: Mapped[Optional[str]] = mapped_column(String)
    DATE_BIRTH: Mapped[Optional[datetime]] = mapped_column(DateTime)
    NEW_NHS_NO: Mapped[Optional[int]] = mapped_column(BigInteger)
    CODED_REASON: Mapped[Optional[str]] = mapped_column(String)
    REASON_FREETEXT: Mapped[Optional[str]] = mapped_column(String)
    EXTRA_COMMENT: Mapped[Optional[str]] = mapped_column(String)
    INITIALS: Mapped[Optional[str]] = mapped_column(String)
    RR_NO: Mapped[Optional[int]] = mapped_column(BigInteger)
    OTHER_SITE_CODE: Mapped[Optional[str]] = mapped_column(String)
