from typing import List, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Computed,
    DECIMAL,
    Date,
    DateTime,
    Float,
    ForeignKeyConstraint,
    Identity,
    Index,
    Integer,
    LargeBinary,
    NCHAR,
    Numeric,
    PrimaryKeyConstraint,
    SmallInteger,
    String,
    Table,
    Unicode,
    text,
)
from sqlalchemy.dialects.mssql import DATETIME2
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
    relationship,
)
import datetime
import decimal


class Base(MappedAsDataclass, DeclarativeBase):
    pass


t_ACCESS_CLINIC_TIMELINE = Table(
    "ACCESS_CLINIC_TIMELINE",
    Base.metadata,
    Column("RR_NO", BigInteger),
    Column("DATE_FIRST_SEEN", DateTime),
    Column("WAITING_LIST_DATE", DateTime),
    Column("LAB_REFERRAL_DATE", DateTime),
    Column("LAB_APPOINT_DATE", DateTime),
    Column("DATE_REFERRAL_1", DateTime),
    Column("DATE_SCHEDULED_1", DateTime),
    Column("DATE_REFERRAL_2", DateTime),
    Column("DATE_SCHEDULED_2", DateTime),
    Column("CREATININE_REF", Numeric(38, 4)),
    Column("CREAT_DATE_REF", DateTime),
    Column("EGFR_REF", Numeric(38, 0)),
)


t_ADDRESSBASE_POSTCODES = Table(
    "ADDRESSBASE_POSTCODES",
    Base.metadata,
    Column("POSTCODE", String(50, "Latin1_General_CI_AS")),
)


t_ADDRESSBASE_POSTCODE_AREAS = Table(
    "ADDRESSBASE_POSTCODE_AREAS",
    Base.metadata,
    Column("POSTCODE_AREA", String(50, "Latin1_General_CI_AS")),
)


class AKI(Base):
    __tablename__ = "AKI"
    __table_args__ = (
        PrimaryKeyConstraint("RR_NO", "HOSP_CENTRE", "AKI_DATE", name="PK_AKI"),
    )

    RR_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    HOSP_CENTRE: Mapped[str] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS"), primary_key=True
    )
    AKI_DATE: Mapped[datetime.date] = mapped_column(
        Date, primary_key=True, server_default=text("('1/1/1900')")
    )
    FIRST_TREAT_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    FIRST_TREAT_WEIGHT: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    FIRST_TREAT_CREATININE: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    PRIMARY_DISEASE_CODE: Mapped[Optional[str]] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS")
    )
    EDTA_DISEASE_CODE: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    SECONDARY_ESRF_1: Mapped[Optional[str]] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS")
    )
    SECONDARY_ESRF_2: Mapped[Optional[str]] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS")
    )
    SECONDARY_ESRF_3: Mapped[Optional[str]] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS")
    )
    PRIMARY_DISEASE_TEXT: Mapped[Optional[str]] = mapped_column(
        Unicode(70, "Latin1_General_CI_AS")
    )
    ANGINA: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    PREV_MI_LE3M: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    PREV_MI_GT3M: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    PREV_CAGB: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    SMOKER: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    COPD: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    SYMPT_CEREBRO_VASC: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    DIABETES_NON_ESRF: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    MALIGNANCY: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    LIVER_DISEASE: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    CLAUDICATION: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    ISCH_NEUROPATH_ULCERS: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    ANGIOPLASTY_NC: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    PVD_AMPUTATION: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    ANTENATAL_DIAG: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    ANTENATAL_TREAT: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    PRETERM: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    CEREBRAL_PALSY: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    DEVEL_EDUC_HANDICAP: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    CONGEN_HEART_DISEASE: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    OTHER_CONGEN_ABNORM: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    DOWNS_SYNDROME: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    OTHER_CHROMO_ABNORM: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    OTHER_SYNDROME: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    NEURAL_TUBE_DEFECT: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    DATE_CREAT_PRIOR_TO_ESRF: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime
    )
    CREAT_PRIOR_TO_ESRF: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    DATE_HB_PRIOR_TO_ESRF: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    HB_PRIOR_TO_ESRF: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    ACCESS_USED_AT_FIRST_DIALYSIS: Mapped[Optional[str]] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS")
    )
    EPISODE_OF_HEART_FAILURE: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    EDTA_NEW_DISEASE_CODE_CONV: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    EDTA_NEW_DISEASE_CODE: Mapped[Optional[str]] = mapped_column(
        Unicode(20, "Latin1_General_CI_AS")
    )
    CKD5_REACHED_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    SECONDARY_DISEASE_CODE: Mapped[Optional[str]] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS")
    )
    FIRST_REPLACEMENT_MODALITY: Mapped[Optional[str]] = mapped_column(
        Unicode(4, "Latin1_General_CI_AS")
    )
    BMI_AT_START_OF_RRT: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    ACCESS_AT_3_MONTHS: Mapped[Optional[str]] = mapped_column(
        Unicode(5, "Latin1_General_CI_AS")
    )
    FIRST_TREATMENT_CENTRE: Mapped[Optional[str]] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS")
    )
    TRANSPLANT_SUITABILITY: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    CONNECTION_DECISION_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime
    )
    FIRST_HEIGHT: Mapped[Optional[float]] = mapped_column(Float(53))
    ON_RRT: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    REASON_NO_RRT: Mapped[Optional[str]] = mapped_column(
        Unicode(150, "Latin1_General_CI_AS")
    )
    PRESUMED_INHERITENCE: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    GENETIC_DISEASE: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    GENETIC_DISEASE_DETAILS: Mapped[Optional[str]] = mapped_column(
        Unicode(150, "Latin1_General_CI_AS")
    )
    OTHER_CONGENITAL_DETAILS: Mapped[Optional[str]] = mapped_column(
        Unicode(150, "Latin1_General_CI_AS")
    )
    OTHER_ORGAN_TRANSPLANT_1: Mapped[Optional[str]] = mapped_column(
        Unicode(20, "Latin1_General_CI_AS")
    )
    OTHER_ORGAN_TRANSPLANT_2: Mapped[Optional[str]] = mapped_column(
        Unicode(20, "Latin1_General_CI_AS")
    )
    OTHER_ORGAN_TRANSPLANT_3: Mapped[Optional[str]] = mapped_column(
        Unicode(20, "Latin1_General_CI_AS")
    )
    FIRST_MALIGNANCY_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(
        DATETIME2
    )
    OTHER_FAMILY_ERF: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    CKD_EGFR_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    CKD_EGFR: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    CKD_EGFR_CREATININE: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )


class ANNUALCOMORBID(Base):
    __tablename__ = "ANNUAL_COMORBID"
    __table_args__ = (
        PrimaryKeyConstraint("RR_NO", "DATE_CM_DISEASE", name="PK_ANNUAL_COMORBID"),
    )

    RR_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    DATE_CM_DISEASE: Mapped[datetime.datetime] = mapped_column(
        DateTime, primary_key=True
    )
    ANGINA: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    PREV_MI_LE3M: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    PREV_MI_GT3M: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    PREV_CAGB: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    SMOKER: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    COPD: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    SYMPT_CEREBRO_VASC: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    DIABETES_NON_ESRF: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    MALIGNANCY: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    LIVER_DISEASE: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    CLAUDICATION: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    ISCH_NEUROPATH_ULCERS: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    ANGIOPLASTY_NC: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    PVD_AMPUTATION: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    HEART_FAILURE_EPISODE: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    KARNOFSKY_PERFORMANCE_SCALE: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )


t_ATTOM_PATIENTS = Table(
    "ATTOM_PATIENTS",
    Base.metadata,
    Column("PATIENTID", String(50, "Latin1_General_CI_AS")),
    Column("ATTOM_GROUP", String(50, "Latin1_General_CI_AS")),
    Column("COHORT", String(50, "Latin1_General_CI_AS")),
    Column("SURNAME", String(50, "Latin1_General_CI_AS")),
    Column("FORENAME", String(50, "Latin1_General_CI_AS")),
    Column("DOB", String(50, "Latin1_General_CI_AS")),
    Column("SEX", String(50, "Latin1_General_CI_AS")),
    Column("ETH_GRP", String(50, "Latin1_General_CI_AS")),
    Column("HEIGHT", String(50, "Latin1_General_CI_AS")),
    Column("WEIGHT", String(50, "Latin1_General_CI_AS")),
    Column("MAIN_HOS_NO", String(50, "Latin1_General_CI_AS")),
    Column("OTHER_HOS_NO", String(50, "Latin1_General_CI_AS")),
    Column("NHS_NO", BigInteger),
    Column("CHI_NO", BigInteger),
    Column("ADD1", String(50, "Latin1_General_CI_AS")),
    Column("ADD2", String(50, "Latin1_General_CI_AS")),
    Column("ADD3", String(50, "Latin1_General_CI_AS")),
    Column("POSTCODE", String(50, "Latin1_General_CI_AS")),
    Column("DATE_REG", String(50, "Latin1_General_CI_AS")),
    Column("CENTRE", String(50, "Latin1_General_CI_AS")),
    Column("RENAL_UNIT", String(50, "Latin1_General_CI_AS")),
    Column("PREV_ID", String(50, "Latin1_General_CI_AS")),
    Column("NEXT_ID", String(50, "Latin1_General_CI_AS")),
    Column("first_seen_date", String(50, "Latin1_General_CI_AS")),
    Column("recip_id", String(50, "Latin1_General_CI_AS")),
    Column("RR_NO", BigInteger),
    Column("TRACING_RESPONSE", BigInteger),
    Column("TRACING_DATE_DEATH", DateTime),
)


t_AUDIT_ACCESS_CLINIC_TIMELINE = Table(
    "AUDIT_ACCESS_CLINIC_TIMELINE",
    Base.metadata,
    Column("RR_NO", BigInteger),
    Column("DATE_FIRST_SEEN", DateTime),
    Column("WAITING_LIST_DATE", DateTime),
    Column("LAB_REFERRAL_DATE", DateTime),
    Column("LAB_APPOINT_DATE", DateTime),
    Column("DATE_REFERRAL_1", DateTime),
    Column("DATE_SCHEDULED_1", DateTime),
    Column("DATE_REFERRAL_2", DateTime),
    Column("DATE_SCHEDULED_2", DateTime),
    Column("CREATININE_REF", Numeric(38, 4)),
    Column("CREAT_DATE_REF", DateTime),
    Column("EGFR_REF", Numeric(38, 0)),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_ADDRESSBASE_POSTCODES = Table(
    "AUDIT_ADDRESSBASE_POSTCODES",
    Base.metadata,
    Column("POSTCODE", String(50, "Latin1_General_CI_AS")),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_ADDRESSBASE_POSTCODE_AREAS = Table(
    "AUDIT_ADDRESSBASE_POSTCODE_AREAS",
    Base.metadata,
    Column("POSTCODE_AREA", String(50, "Latin1_General_CI_AS")),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_AKI = Table(
    "AUDIT_AKI",
    Base.metadata,
    Column("RR_NO", BigInteger),
    Column("FIRST_TREAT_DATE", DateTime),
    Column("FIRST_TREAT_WEIGHT", Numeric(38, 4)),
    Column("FIRST_TREAT_CREATININE", Numeric(38, 4)),
    Column("PRIMARY_DISEASE_CODE", Unicode(8, "Latin1_General_CI_AS")),
    Column("EDTA_DISEASE_CODE", Numeric(20, 0)),
    Column("SECONDARY_ESRF_1", Unicode(8, "Latin1_General_CI_AS")),
    Column("SECONDARY_ESRF_2", Unicode(8, "Latin1_General_CI_AS")),
    Column("SECONDARY_ESRF_3", Unicode(8, "Latin1_General_CI_AS")),
    Column("PRIMARY_DISEASE_TEXT", Unicode(70, "Latin1_General_CI_AS")),
    Column("ANGINA", Unicode(1, "Latin1_General_CI_AS")),
    Column("PREV_MI_LE3M", Unicode(1, "Latin1_General_CI_AS")),
    Column("PREV_MI_GT3M", Unicode(1, "Latin1_General_CI_AS")),
    Column("PREV_CAGB", Unicode(1, "Latin1_General_CI_AS")),
    Column("SMOKER", Unicode(1, "Latin1_General_CI_AS")),
    Column("COPD", Unicode(1, "Latin1_General_CI_AS")),
    Column("SYMPT_CEREBRO_VASC", Unicode(1, "Latin1_General_CI_AS")),
    Column("DIABETES_NON_ESRF", Unicode(1, "Latin1_General_CI_AS")),
    Column("MALIGNANCY", Unicode(1, "Latin1_General_CI_AS")),
    Column("LIVER_DISEASE", Unicode(1, "Latin1_General_CI_AS")),
    Column("CLAUDICATION", Unicode(1, "Latin1_General_CI_AS")),
    Column("ISCH_NEUROPATH_ULCERS", Unicode(1, "Latin1_General_CI_AS")),
    Column("ANGIOPLASTY_NC", Unicode(1, "Latin1_General_CI_AS")),
    Column("PVD_AMPUTATION", Unicode(1, "Latin1_General_CI_AS")),
    Column("ANTENATAL_DIAG", Unicode(1, "Latin1_General_CI_AS")),
    Column("ANTENATAL_TREAT", Unicode(1, "Latin1_General_CI_AS")),
    Column("PRETERM", Unicode(1, "Latin1_General_CI_AS")),
    Column("CEREBRAL_PALSY", Unicode(1, "Latin1_General_CI_AS")),
    Column("DEVEL_EDUC_HANDICAP", Unicode(1, "Latin1_General_CI_AS")),
    Column("CONGEN_HEART_DISEASE", Unicode(1, "Latin1_General_CI_AS")),
    Column("OTHER_CONGEN_ABNORM", Unicode(1, "Latin1_General_CI_AS")),
    Column("DOWNS_SYNDROME", Unicode(1, "Latin1_General_CI_AS")),
    Column("OTHER_CHROMO_ABNORM", Unicode(1, "Latin1_General_CI_AS")),
    Column("OTHER_SYNDROME", Unicode(1, "Latin1_General_CI_AS")),
    Column("NEURAL_TUBE_DEFECT", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
    Column("DATE_CREAT_PRIOR_TO_ESRF", DateTime),
    Column("CREAT_PRIOR_TO_ESRF", Numeric(38, 4)),
    Column("DATE_HB_PRIOR_TO_ESRF", DateTime),
    Column("HB_PRIOR_TO_ESRF", Numeric(38, 4)),
    Column("ACCESS_USED_AT_FIRST_DIALYSIS", Unicode(10, "Latin1_General_CI_AS")),
    Column("HOSP_CENTRE", Unicode(10, "Latin1_General_CI_AS")),
    Column("EPISODE_OF_HEART_FAILURE", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("EDTA_NEW_DISEASE_CODE", Unicode(20, "Latin1_General_CI_AS")),
    Column("EDTA_NEW_DISEASE_CODE_CONV", Unicode(1, "Latin1_General_CI_AS")),
    Column("CKD5_REACHED_DATE", DateTime),
    Column("SECONDARY_DISEASE_CODE", Unicode(8, "Latin1_General_CI_AS")),
    Column("FIRST_REPLACEMENT_MODALITY", Unicode(4, "Latin1_General_CI_AS")),
    Column("BMI_AT_START_OF_RRT", Numeric(38, 4)),
    Column("ACCESS_AT_3_MONTHS", Unicode(5, "Latin1_General_CI_AS")),
    Column("FIRST_TREATMENT_CENTRE", Unicode(10, "Latin1_General_CI_AS")),
    Column("TRANSPLANT_SUITABILITY", Unicode(1, "Latin1_General_CI_AS")),
    Column("CONNECTION_DECISION_DATE", DateTime),
    Column("FIRST_HEIGHT", Float(53)),
    Column("ON_RRT", Unicode(1, "Latin1_General_CI_AS")),
    Column("REASON_NO_RRT", Unicode(150, "Latin1_General_CI_AS")),
    Column("PRESUMED_INHERITENCE", Unicode(1, "Latin1_General_CI_AS")),
    Column("GENETIC_DISEASE", Unicode(1, "Latin1_General_CI_AS")),
    Column("GENETIC_DISEASE_DETAILS", Unicode(150, "Latin1_General_CI_AS")),
    Column("OTHER_CONGENITAL_DETAILS", Unicode(150, "Latin1_General_CI_AS")),
    Column("OTHER_ORGAN_TRANSPLANT_1", Unicode(20, "Latin1_General_CI_AS")),
    Column("OTHER_ORGAN_TRANSPLANT_2", Unicode(20, "Latin1_General_CI_AS")),
    Column("OTHER_ORGAN_TRANSPLANT_3", Unicode(20, "Latin1_General_CI_AS")),
    Column("FIRST_MALIGNANCY_DATE", DATETIME2),
    Column("OTHER_FAMILY_ERF", Unicode(1, "Latin1_General_CI_AS")),
    Column("CKD_EGFR_DATE", DateTime),
    Column("CKD_EGFR", Numeric(38, 4)),
    Column("CKD_EGFR_CREATININE", Numeric(38, 4)),
    Column("AKI_DATE", Date),
)


t_AUDIT_ANNUAL_COMORBID = Table(
    "AUDIT_ANNUAL_COMORBID",
    Base.metadata,
    Column("RR_NO", BigInteger),
    Column("DATE_CM_DISEASE", DateTime),
    Column("ANGINA", Unicode(1, "Latin1_General_CI_AS")),
    Column("PREV_MI_LE3M", Unicode(1, "Latin1_General_CI_AS")),
    Column("PREV_MI_GT3M", Unicode(1, "Latin1_General_CI_AS")),
    Column("PREV_CAGB", Unicode(1, "Latin1_General_CI_AS")),
    Column("SMOKER", Unicode(1, "Latin1_General_CI_AS")),
    Column("COPD", Unicode(1, "Latin1_General_CI_AS")),
    Column("SYMPT_CEREBRO_VASC", Unicode(1, "Latin1_General_CI_AS")),
    Column("DIABETES_NON_ESRF", Unicode(1, "Latin1_General_CI_AS")),
    Column("MALIGNANCY", Unicode(1, "Latin1_General_CI_AS")),
    Column("LIVER_DISEASE", Unicode(1, "Latin1_General_CI_AS")),
    Column("CLAUDICATION", Unicode(1, "Latin1_General_CI_AS")),
    Column("ISCH_NEUROPATH_ULCERS", Unicode(1, "Latin1_General_CI_AS")),
    Column("ANGIOPLASTY_NC", Unicode(1, "Latin1_General_CI_AS")),
    Column("PVD_AMPUTATION", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
    Column("HEART_FAILURE_EPISODE", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("KARNOFSKY_PERFORMANCE_SCALE", Numeric(38, 4)),
)


t_AUDIT_ATTOM_PATIENTS = Table(
    "AUDIT_ATTOM_PATIENTS",
    Base.metadata,
    Column("PATIENTID", String(50, "Latin1_General_CI_AS")),
    Column("ATTOM_GROUP", String(50, "Latin1_General_CI_AS")),
    Column("COHORT", String(50, "Latin1_General_CI_AS")),
    Column("SURNAME", String(50, "Latin1_General_CI_AS")),
    Column("FORENAME", String(50, "Latin1_General_CI_AS")),
    Column("DOB", String(50, "Latin1_General_CI_AS")),
    Column("SEX", String(50, "Latin1_General_CI_AS")),
    Column("ETH_GRP", String(50, "Latin1_General_CI_AS")),
    Column("HEIGHT", String(50, "Latin1_General_CI_AS")),
    Column("WEIGHT", String(50, "Latin1_General_CI_AS")),
    Column("MAIN_HOS_NO", String(50, "Latin1_General_CI_AS")),
    Column("OTHER_HOS_NO", String(50, "Latin1_General_CI_AS")),
    Column("NHS_NO", BigInteger),
    Column("CHI_NO", BigInteger),
    Column("ADD1", String(50, "Latin1_General_CI_AS")),
    Column("ADD2", String(50, "Latin1_General_CI_AS")),
    Column("ADD3", String(50, "Latin1_General_CI_AS")),
    Column("POSTCODE", String(50, "Latin1_General_CI_AS")),
    Column("DATE_REG", String(50, "Latin1_General_CI_AS")),
    Column("CENTRE", String(50, "Latin1_General_CI_AS")),
    Column("RENAL_UNIT", String(50, "Latin1_General_CI_AS")),
    Column("PREV_ID", String(50, "Latin1_General_CI_AS")),
    Column("NEXT_ID", String(50, "Latin1_General_CI_AS")),
    Column("first_seen_date", String(50, "Latin1_General_CI_AS")),
    Column("recip_id", String(50, "Latin1_General_CI_AS")),
    Column("RR_NO", BigInteger),
    Column("TRACING_RESPONSE", BigInteger),
    Column("TRACING_DATE_DEATH", DateTime),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_CKD = Table(
    "AUDIT_CKD",
    Base.metadata,
    Column("RR_NO", BigInteger),
    Column("FIRST_TREAT_DATE", DateTime),
    Column("FIRST_TREAT_WEIGHT", Numeric(38, 4)),
    Column("FIRST_TREAT_CREATININE", Numeric(38, 4)),
    Column("PRIMARY_DISEASE_CODE", Unicode(8, "Latin1_General_CI_AS")),
    Column("EDTA_DISEASE_CODE", Numeric(20, 0)),
    Column("SECONDARY_ESRF_1", Unicode(8, "Latin1_General_CI_AS")),
    Column("SECONDARY_ESRF_2", Unicode(8, "Latin1_General_CI_AS")),
    Column("SECONDARY_ESRF_3", Unicode(8, "Latin1_General_CI_AS")),
    Column("PRIMARY_DISEASE_TEXT", Unicode(70, "Latin1_General_CI_AS")),
    Column("ANGINA", Unicode(1, "Latin1_General_CI_AS")),
    Column("PREV_MI_LE3M", Unicode(1, "Latin1_General_CI_AS")),
    Column("PREV_MI_GT3M", Unicode(1, "Latin1_General_CI_AS")),
    Column("PREV_CAGB", Unicode(1, "Latin1_General_CI_AS")),
    Column("SMOKER", Unicode(1, "Latin1_General_CI_AS")),
    Column("COPD", Unicode(1, "Latin1_General_CI_AS")),
    Column("SYMPT_CEREBRO_VASC", Unicode(1, "Latin1_General_CI_AS")),
    Column("DIABETES_NON_ESRF", Unicode(1, "Latin1_General_CI_AS")),
    Column("MALIGNANCY", Unicode(1, "Latin1_General_CI_AS")),
    Column("LIVER_DISEASE", Unicode(1, "Latin1_General_CI_AS")),
    Column("CLAUDICATION", Unicode(1, "Latin1_General_CI_AS")),
    Column("ISCH_NEUROPATH_ULCERS", Unicode(1, "Latin1_General_CI_AS")),
    Column("ANGIOPLASTY_NC", Unicode(1, "Latin1_General_CI_AS")),
    Column("PVD_AMPUTATION", Unicode(1, "Latin1_General_CI_AS")),
    Column("ANTENATAL_DIAG", Unicode(1, "Latin1_General_CI_AS")),
    Column("ANTENATAL_TREAT", Unicode(1, "Latin1_General_CI_AS")),
    Column("PRETERM", Unicode(1, "Latin1_General_CI_AS")),
    Column("CEREBRAL_PALSY", Unicode(1, "Latin1_General_CI_AS")),
    Column("DEVEL_EDUC_HANDICAP", Unicode(1, "Latin1_General_CI_AS")),
    Column("CONGEN_HEART_DISEASE", Unicode(1, "Latin1_General_CI_AS")),
    Column("OTHER_CONGEN_ABNORM", Unicode(1, "Latin1_General_CI_AS")),
    Column("DOWNS_SYNDROME", Unicode(1, "Latin1_General_CI_AS")),
    Column("OTHER_CHROMO_ABNORM", Unicode(1, "Latin1_General_CI_AS")),
    Column("OTHER_SYNDROME", Unicode(1, "Latin1_General_CI_AS")),
    Column("NEURAL_TUBE_DEFECT", Unicode(1, "Latin1_General_CI_AS")),
    Column("DATE_CREAT_PRIOR_TO_ESRF", DateTime),
    Column("CREAT_PRIOR_TO_ESRF", Numeric(38, 4)),
    Column("DATE_HB_PRIOR_TO_ESRF", DateTime),
    Column("HB_PRIOR_TO_ESRF", Numeric(38, 4)),
    Column("ACCESS_USED_AT_FIRST_DIALYSIS", Unicode(10, "Latin1_General_CI_AS")),
    Column("HOSP_CENTRE", Unicode(8, "Latin1_General_CI_AS")),
    Column("EPISODE_OF_HEART_FAILURE", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
    Column("EDTA_NEW_DISEASE_CODE", Unicode(20, "Latin1_General_CI_AS")),
    Column("EDTA_NEW_DISEASE_CODE_CONV", Unicode(1, "Latin1_General_CI_AS")),
    Column("CKD5_REACHED_DATE", DateTime),
    Column("SECONDARY_DISEASE_CODE", Unicode(8, "Latin1_General_CI_AS")),
    Column("FIRST_REPLACEMENT_MODALITY", Unicode(4, "Latin1_General_CI_AS")),
    Column("BMI_AT_START_OF_RRT", Numeric(38, 4)),
    Column("ACCESS_AT_3_MONTHS", Unicode(5, "Latin1_General_CI_AS")),
    Column("FIRST_TREATMENT_CENTRE", Unicode(10, "Latin1_General_CI_AS")),
    Column("TRANSPLANT_SUITABILITY", Unicode(1, "Latin1_General_CI_AS")),
    Column("CONNECTION_DECISION_DATE", DateTime),
    Column("FIRST_HEIGHT", Float(53)),
    Column("ON_RRT", Unicode(1, "Latin1_General_CI_AS")),
    Column("REASON_NO_RRT", Unicode(150, "Latin1_General_CI_AS")),
    Column("PRESUMED_INHERITENCE", Integer),
    Column("GENETIC_DISEASE", Integer),
    Column("GENETIC_DISEASE_DETAILS", Unicode(150, "Latin1_General_CI_AS")),
    Column("OTHER_CONGENITAL_DETAILS", Unicode(150, "Latin1_General_CI_AS")),
    Column("OTHER_ORGAN_TRANSPLANT_1", Unicode(20, "Latin1_General_CI_AS")),
    Column("OTHER_ORGAN_TRANSPLANT_2", Unicode(20, "Latin1_General_CI_AS")),
    Column("OTHER_ORGAN_TRANSPLANT_3", Unicode(20, "Latin1_General_CI_AS")),
    Column("FIRST_MALIGNANCY_DATE", DATETIME2),
    Column("OTHER_FAMILY_ERF", Integer),
    Column("CKD_EGFR_DATE", DateTime),
    Column("CKD_EGFR", Numeric(38, 4)),
    Column("CKD_EGFR_CREATININE", Numeric(38, 4)),
)


t_AUDIT_CMV_ANTIBODY = Table(
    "AUDIT_CMV_ANTIBODY",
    Base.metadata,
    Column("RR_NO", BigInteger),
    Column("CMV_ANTIBODY_DATE", DateTime),
    Column("CMV_ANTIBODY_STATUS", Unicode(5, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_CMV_ANTIGENAEMIA = Table(
    "AUDIT_CMV_ANTIGENAEMIA",
    Base.metadata,
    Column("RR_NO", BigInteger, nullable=False),
    Column("CMV_ANTIGENAEMIA_DATE", DateTime, nullable=False),
    Column("CMV_ANTIGENAEMIA", Numeric(5, 0)),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_CMV_PCR = Table(
    "AUDIT_CMV_PCR",
    Base.metadata,
    Column("RR_NO", BigInteger, nullable=False),
    Column("CMV_PCR_DATE", DateTime, nullable=False),
    Column("CMV_PCR", Numeric(5, 0)),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_COMORBIDITY = Table(
    "AUDIT_COMORBIDITY",
    Base.metadata,
    Column("RR_NO", BigInteger),
    Column("HOSP_CENTRE", Unicode(8, "Latin1_General_CI_AS")),
    Column("CABG", String(1, "Latin1_General_CI_AS")),
    Column("HEART_FAILURE", String(1, "Latin1_General_CI_AS")),
    Column("COPD", String(1, "Latin1_General_CI_AS")),
    Column("LIVER_DISEASE", String(1, "Latin1_General_CI_AS")),
    Column("CLAUDICATION", String(1, "Latin1_General_CI_AS")),
    Column("IN_ULCERS", String(1, "Latin1_General_CI_AS")),
    Column("STENT", String(1, "Latin1_General_CI_AS")),
    Column("AMPUTATION_FOR_PVD", String(1, "Latin1_General_CI_AS")),
    Column("DIABETES", Unicode(10, "Latin1_General_CI_AS")),
    Column("DIABETES_DIAGNOSED_DATE", DATETIME2),
    Column("HEART_DISEASE", String(1, "Latin1_General_CI_AS")),
    Column("ST_SEGMENT_ELEVATION_DATE", DATETIME2),
    Column("NON_ST_SEG_ELEVATION_DATE", DATETIME2),
    Column("ANGINA_DIAGNOSED_DATE", DATETIME2),
    Column("CABG_DATE", DATETIME2),
    Column("HEART_FAILURE_DATE", DATETIME2),
    Column("ATRIAL_FIBRILLATION_DATE", DATETIME2),
    Column("MALIGNANCY", String(1, "Latin1_General_CI_AS")),
    Column("MALIGNANCY_SITE", SmallInteger),
    Column("MALIGNANCY_DIAGNOSED_DATE", DATETIME2),
    Column("CEREBROVASCULAR_DISEASE", String(1, "Latin1_General_CI_AS")),
    Column("TIA_DATE", DATETIME2),
    Column("CVE_STROKE_DATE", DATETIME2),
    Column("SMOKING", Unicode(20, "Latin1_General_CI_AS")),
    Column("COPD_DIAGNOSED_DATE", DATETIME2),
    Column("LIVER_DISEASE_DIAGNOSED_DATE", DATETIME2),
    Column("PVD_DIAGNOSED_DATE", DATETIME2),
    Column("CLAUDICATION_DIAGNOSED_DATE", DATETIME2),
    Column("ULCERS_DIAGNOSED_DATE", DATETIME2),
    Column("STENT_DIAGNOSED_DATE", DATETIME2),
    Column("PVD_AMPUTATION_DATE", DATETIME2),
    Column("DEMENTIA_DIAGNOSED_DATE", DATETIME2),
    Column("PVD", String(1, "Latin1_General_CI_AS")),
    Column("DEMENTIA", String(1, "Latin1_General_CI_AS")),
    Column("ATRIAL_FIBRILLATION", String(1, "Latin1_General_CI_AS")),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_CONSTRAINT_TABLE = Table(
    "AUDIT_CONSTRAINT_TABLE",
    Base.metadata,
    Column("FIELD_ID", Unicode(5, "Latin1_General_CI_AS")),
    Column("FIELD_NAME", Unicode(30, "Latin1_General_CI_AS"), nullable=False),
    Column("LOWER_LIMIT", Numeric(38, 4)),
    Column("UPPER_LIMIT", Numeric(38, 4)),
    Column("LOWER_WARN", Numeric(38, 4)),
    Column("UPPER_WARN", Numeric(38, 4)),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_DATA_ITEM_SUBMISSION = Table(
    "AUDIT_DATA_ITEM_SUBMISSION",
    Base.metadata,
    Column("HOSP_CENTRE", Unicode(8, "Latin1_General_CI_AS")),
    Column("QUARTER", BigInteger),
    Column("DATA_ITEM", Unicode(30, "Latin1_General_CI_AS")),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_DIALYSIS_ACCESS_DETAIL = Table(
    "AUDIT_DIALYSIS_ACCESS_DETAIL",
    Base.metadata,
    Column("RR_NO", BigInteger, nullable=False),
    Column("HOSP_CENTRE", String(20, "Latin1_General_CI_AS"), nullable=False),
    Column("ACCESS_DATE", DateTime, nullable=False),
    Column("ACCESS_TYPE", String(3, "Latin1_General_CI_AS"), nullable=False),
    Column("ANATOMICAL_SIDE", String(1, "Latin1_General_CI_AS"), nullable=False),
    Column("VASCULAR_SITE_ACCESS", String(2, "Latin1_General_CI_AS"), nullable=False),
    Column("FIRST_ACCESS_DATE", DateTime),
    Column("ACCESS_FAILURE_DATE", DateTime),
    Column("REMOVAL_DATE", DateTime),
    Column("HD_REMOVAL_REASON", Integer),
    Column("PD_INSERTION_TECHNIQUE", Integer),
    Column("PD_REMOVAL_REASON", Integer),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_DIALYSIS_ACCESS_EVENT = Table(
    "AUDIT_DIALYSIS_ACCESS_EVENT",
    Base.metadata,
    Column("RR_NO", BigInteger, nullable=False),
    Column("ACCESS_DATE", DateTime, nullable=False),
    Column("ACCESS_TYPE", String(5, "Latin1_General_CI_AS"), nullable=False),
    Column("LOCATION", String(5, "Latin1_General_CI_AS"), nullable=False),
    Column("TENCKHOFF_DATE", DateTime),
    Column("COMPLICATION_DATE", DateTime, nullable=False),
    Column("HD_COMPLICATION", Integer, nullable=False),
    Column("PD_COMPLICATION", Integer),
    Column("PERITONITIS_ORGANISM_1", Integer),
    Column("PERITONITIS_ORGANISM_2", Integer),
    Column("PERITONITIS_ORGANISM_3", Integer),
    Column("SWITCH_FROM_PD_REASON", Integer),
    Column("SWITCH_FROM_PD_REASON_2", Integer),
    Column("SWITCH_FROM_PD_REASON_3", Integer),
    Column("HOSP_CENTRE", Unicode(8, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_EPO_DOSAGE = Table(
    "AUDIT_EPO_DOSAGE",
    Base.metadata,
    Column("RR_NO", BigInteger),
    Column("DATE_START", DateTime),
    Column("DATE_END", DateTime),
    Column("UNITS_TRANSFUSED", Numeric(20, 0)),
    Column("PARENTERAL_IRON", Unicode(1, "Latin1_General_CI_AS")),
    Column("EPO_DRUG_NAME", Unicode(8, "Latin1_General_CI_AS")),
    Column("EPO_DOSAGE", Numeric(20, 0)),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("EPO_WEEKLY_DOSAGE", Numeric(38, 4)),
    Column("EPO_ADMIN_ROUTE", Unicode(20, "Latin1_General_CI_AS")),
    Column("EPO_FREQUENCY", Unicode(20, "Latin1_General_CI_AS")),
    Column("HOSP_CENTRE", Unicode(8, "Latin1_General_CI_AS")),
    Column("EPO_WEEKLY_RAW", Numeric(38, 4)),
)


t_AUDIT_ESRF = Table(
    "AUDIT_ESRF",
    Base.metadata,
    Column("RR_NO", BigInteger),
    Column("FIRST_TREAT_DATE", DateTime),
    Column("FIRST_TREAT_WEIGHT", Numeric(38, 4)),
    Column("FIRST_TREAT_CREATININE", Numeric(38, 4)),
    Column("PRIMARY_DISEASE_CODE", Unicode(8, "Latin1_General_CI_AS")),
    Column("EDTA_DISEASE_CODE", Numeric(20, 0)),
    Column("SECONDARY_ESRF_1", Unicode(8, "Latin1_General_CI_AS")),
    Column("SECONDARY_ESRF_2", Unicode(8, "Latin1_General_CI_AS")),
    Column("SECONDARY_ESRF_3", Unicode(8, "Latin1_General_CI_AS")),
    Column("PRIMARY_DISEASE_TEXT", Unicode(70, "Latin1_General_CI_AS")),
    Column("ANGINA", Unicode(1, "Latin1_General_CI_AS")),
    Column("PREV_MI_LE3M", Unicode(1, "Latin1_General_CI_AS")),
    Column("PREV_MI_GT3M", Unicode(1, "Latin1_General_CI_AS")),
    Column("PREV_CAGB", Unicode(1, "Latin1_General_CI_AS")),
    Column("SMOKER", Unicode(1, "Latin1_General_CI_AS")),
    Column("COPD", Unicode(1, "Latin1_General_CI_AS")),
    Column("SYMPT_CEREBRO_VASC", Unicode(1, "Latin1_General_CI_AS")),
    Column("DIABETES_NON_ESRF", Unicode(1, "Latin1_General_CI_AS")),
    Column("MALIGNANCY", Unicode(1, "Latin1_General_CI_AS")),
    Column("LIVER_DISEASE", Unicode(1, "Latin1_General_CI_AS")),
    Column("CLAUDICATION", Unicode(1, "Latin1_General_CI_AS")),
    Column("ISCH_NEUROPATH_ULCERS", Unicode(1, "Latin1_General_CI_AS")),
    Column("ANGIOPLASTY_NC", Unicode(1, "Latin1_General_CI_AS")),
    Column("PVD_AMPUTATION", Unicode(1, "Latin1_General_CI_AS")),
    Column("ANTENATAL_DIAG", Unicode(1, "Latin1_General_CI_AS")),
    Column("ANTENATAL_TREAT", Unicode(1, "Latin1_General_CI_AS")),
    Column("PRETERM", Unicode(1, "Latin1_General_CI_AS")),
    Column("CEREBRAL_PALSY", Unicode(1, "Latin1_General_CI_AS")),
    Column("DEVEL_EDUC_HANDICAP", Unicode(1, "Latin1_General_CI_AS")),
    Column("CONGEN_HEART_DISEASE", Unicode(1, "Latin1_General_CI_AS")),
    Column("OTHER_CONGEN_ABNORM", Unicode(1, "Latin1_General_CI_AS")),
    Column("DOWNS_SYNDROME", Unicode(1, "Latin1_General_CI_AS")),
    Column("OTHER_CHROMO_ABNORM", Unicode(1, "Latin1_General_CI_AS")),
    Column("OTHER_SYNDROME", Unicode(1, "Latin1_General_CI_AS")),
    Column("NEURAL_TUBE_DEFECT", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
    Column("DATE_CREAT_PRIOR_TO_ESRF", DateTime),
    Column("CREAT_PRIOR_TO_ESRF", Numeric(38, 4)),
    Column("DATE_HB_PRIOR_TO_ESRF", DateTime),
    Column("HB_PRIOR_TO_ESRF", Numeric(38, 4)),
    Column("ACCESS_USED_AT_FIRST_DIALYSIS", Unicode(10, "Latin1_General_CI_AS")),
    Column("HOSP_CENTRE", Unicode(10, "Latin1_General_CI_AS")),
    Column("EPISODE_OF_HEART_FAILURE", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("EDTA_NEW_DISEASE_CODE", Unicode(20, "Latin1_General_CI_AS")),
    Column("EDTA_NEW_DISEASE_CODE_CONV", Unicode(1, "Latin1_General_CI_AS")),
    Column("CKD5_REACHED_DATE", DateTime),
    Column("SECONDARY_DISEASE_CODE", Unicode(8, "Latin1_General_CI_AS")),
    Column("FIRST_REPLACEMENT_MODALITY", Unicode(4, "Latin1_General_CI_AS")),
    Column("BMI_AT_START_OF_RRT", Numeric(38, 4)),
    Column("ACCESS_AT_3_MONTHS", Unicode(5, "Latin1_General_CI_AS")),
    Column("FIRST_TREATMENT_CENTRE", Unicode(10, "Latin1_General_CI_AS")),
    Column("TRANSPLANT_SUITABILITY", Unicode(1, "Latin1_General_CI_AS")),
    Column("CONNECTION_DECISION_DATE", DateTime),
    Column("FIRST_HEIGHT", Float(53)),
    Column("ON_RRT", Unicode(1, "Latin1_General_CI_AS")),
    Column("REASON_NO_RRT", Unicode(150, "Latin1_General_CI_AS")),
    Column("PRESUMED_INHERITENCE", Unicode(1, "Latin1_General_CI_AS")),
    Column("GENETIC_DISEASE", Unicode(1, "Latin1_General_CI_AS")),
    Column("GENETIC_DISEASE_DETAILS", Unicode(150, "Latin1_General_CI_AS")),
    Column("OTHER_CONGENITAL_DETAILS", Unicode(150, "Latin1_General_CI_AS")),
    Column("OTHER_ORGAN_TRANSPLANT_1", Unicode(20, "Latin1_General_CI_AS")),
    Column("OTHER_ORGAN_TRANSPLANT_2", Unicode(20, "Latin1_General_CI_AS")),
    Column("OTHER_ORGAN_TRANSPLANT_3", Unicode(20, "Latin1_General_CI_AS")),
    Column("FIRST_MALIGNANCY_DATE", DATETIME2),
    Column("OTHER_FAMILY_ERF", Unicode(1, "Latin1_General_CI_AS")),
    Column("CKD_EGFR_DATE", DateTime),
    Column("CKD_EGFR", Numeric(38, 4)),
    Column("CKD_EGFR_CREATININE", Numeric(38, 4)),
)


t_AUDIT_EXTERNAL_COMM = Table(
    "AUDIT_EXTERNAL_COMM",
    Base.metadata,
    Column("RR_NO", BigInteger),
    Column("UKTSSA_DATA", Unicode(1, "Latin1_General_CI_AS")),
    Column("EDTA_DATA", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_FOLLOW_UP = Table(
    "AUDIT_FOLLOW_UP",
    Base.metadata,
    Column("RR_NO", BigInteger, nullable=False),
    Column("DATE_FILE", DateTime, nullable=False),
    Column("CLINICAL_ASSESS", Unicode(1, "Latin1_General_CI_AS")),
    Column("DATE_LAST_ASSESS", DateTime),
    Column("CREATININE", Numeric(20, 0)),
    Column("DATE_CREATININE", DateTime),
    Column("AZATHIOPRINE_PROPHLAXIS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AZATHIOPRINE_ACUTE_REJECT", Unicode(1, "Latin1_General_CI_AS")),
    Column("CYCLOSPORIN_PROPHLAXIS", Unicode(1, "Latin1_General_CI_AS")),
    Column("CYCLOSPORIN_ACUTE_REJECT", Unicode(1, "Latin1_General_CI_AS")),
    Column("STEROID_PROPHLAXIS", Unicode(1, "Latin1_General_CI_AS")),
    Column("STEROID_ACUTE_REJECT", Unicode(1, "Latin1_General_CI_AS")),
    Column("OKT3_PROPHLAXIS", Unicode(1, "Latin1_General_CI_AS")),
    Column("OKT3_ACUTE_REJECT", Unicode(1, "Latin1_General_CI_AS")),
    Column("ATG_PROPHLAXIS", Unicode(1, "Latin1_General_CI_AS")),
    Column("ATG_ACUTE_REJECT", Unicode(1, "Latin1_General_CI_AS")),
    Column("ALG_PROPHLAXIS", Unicode(1, "Latin1_General_CI_AS")),
    Column("ALG_ACUTE_REJECT", Unicode(1, "Latin1_General_CI_AS")),
    Column("TACROLIMUS_PROPHLAXIS", Unicode(1, "Latin1_General_CI_AS")),
    Column("TACROLIMUS_ACUTE_REJECT", Unicode(1, "Latin1_General_CI_AS")),
    Column("RS61443_PROPHLAXIS", Unicode(1, "Latin1_General_CI_AS")),
    Column("RS61443_ACUTE_REJECT", Unicode(1, "Latin1_General_CI_AS")),
    Column("OTHER_PROPHLAXIS", Unicode(1, "Latin1_General_CI_AS")),
    Column("OTHER_ACUTE_REJECT", Unicode(1, "Latin1_General_CI_AS")),
    Column("DATE_LAST_IMMSUP", DateTime),
    Column("REDIR_ADDRESS_1", Unicode(40, "Latin1_General_CI_AS")),
    Column("REDIR_ADDRESS_2", Unicode(40, "Latin1_General_CI_AS")),
    Column("REDIR_TOWN", Unicode(40, "Latin1_General_CI_AS")),
    Column("REDIR_POST_CODE", Unicode(8, "Latin1_General_CI_AS")),
    Column("ORGAN_TRANSPLANT", Unicode(1, "Latin1_General_CI_AS")),
    Column("TRANSPLANT_DATE", DateTime),
    Column("TRANSPLANT_NO", Numeric(20, 0), nullable=False),
    Column("TRANSPLANT_FAILURE", Unicode(1, "Latin1_General_CI_AS")),
    Column("DATE_FAILURE", DateTime),
    Column("CAUSE_FAILURE", Unicode(8, "Latin1_General_CI_AS")),
    Column("FAILURE_TEXT", Unicode(70, "Latin1_General_CI_AS")),
    Column("DATE_END_DIAL", DateTime),
    Column("DATE_RETURN_DIAL", DateTime),
    Column("DATE_GRAFT_NEPHRECTOMY", DateTime),
    Column("IMM_SUP_SIROLIMUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_GP_ADDRESS = Table(
    "AUDIT_GP_ADDRESS",
    Base.metadata,
    Column("CENTRE_CODE", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_NO", BigInteger),
    Column("DATE_START", DateTime),
    Column("DATE_END", DateTime),
    Column("ADDRESS_1", Unicode(60, "Latin1_General_CI_AS")),
    Column("ADDRESS_2", Unicode(60, "Latin1_General_CI_AS")),
    Column("ADDRESS_3", Unicode(60, "Latin1_General_CI_AS")),
    Column("ADDRESS_4", Unicode(60, "Latin1_General_CI_AS")),
    Column("POST_CODE", Unicode(8, "Latin1_General_CI_AS")),
    Column("CENTRE_PRI", Unicode(1, "Latin1_General_CI_AS")),
    Column("NHS_CODE", Unicode(3, "Latin1_General_CI_AS")),
    Column("NHS_NAME", Unicode(60, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_HAEMODIALYSIS_PRESCRIPTION = Table(
    "AUDIT_HAEMODIALYSIS_PRESCRIPTION",
    Base.metadata,
    Column("RR_NO", BigInteger, nullable=False),
    Column("HOSP_CENTRE", Unicode(8, "Latin1_General_CI_AS"), nullable=False),
    Column("DIALYSIS_PRESC_DATE", DateTime),
    Column("TIMES_PER_WEEK", Integer),
    Column("TIME_DIALYSED", Integer),
    Column("BLOOD_FLOW_RATE", Integer),
    Column("SODIUM_IN_DIALYSATE", Integer),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_HAEMODIALYSIS_SESSION = Table(
    "AUDIT_HAEMODIALYSIS_SESSION",
    Base.metadata,
    Column("RR_NO", BigInteger, nullable=False),
    Column("START_DATE", DateTime),
    Column("END_DATE", DateTime),
    Column("HD_SESSION_DATE", DateTime, nullable=False),
    Column("PRE_HD_WEIGHT", Numeric(38, 4)),
    Column("PRE_HD_SYSTOLIC_BP", Numeric(38, 4)),
    Column("PRE_HD_DIASTOLIC_BP", Numeric(38, 4)),
    Column("POST_HD_WEIGHT", Numeric(38, 4)),
    Column("POST_HD_SYSTOLIC_BP", Numeric(38, 4)),
    Column("POST_HD_DIASTOLIC_BP", Numeric(38, 4)),
    Column("SYMPTOMATIC_HYPOTENSION", Unicode(1, "Latin1_General_CI_AS")),
    Column("VASCULAR_ACCESS", Unicode(3, "Latin1_General_CI_AS")),
    Column("VASCULAR_ACCESS_SITE", Unicode(8, "Latin1_General_CI_AS")),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
    Column("COUNTER", Integer),
    Column("ACCESS_IN_TWO_SITES", NCHAR(1, "Latin1_General_CI_AS")),
    Column("SESSION_TYPE", NCHAR(10, "Latin1_General_CI_AS")),
    Column("SESSION_START_TIME", Unicode(10, "Latin1_General_CI_AS")),
    Column("BLOOD_FLOW_RATE", Integer),
    Column("TIME_DIALYSED", Integer),
    Column("HOSP_CENTRE", Unicode(8, "Latin1_General_CI_AS")),
    Column("NEEDLING_METHOD", String(1, "Latin1_General_CI_AS")),
    Column("DIALYSATE_SODIUM", Integer),
)


t_AUDIT_HBV_ANTIBODY = Table(
    "AUDIT_HBV_ANTIBODY",
    Base.metadata,
    Column("RR_NO", BigInteger),
    Column("HBV_ANTIBODY_DATE", DateTime),
    Column("HBV_ANTIBODY_STATUS", Unicode(5, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_HBV_S_ANTIGEN = Table(
    "AUDIT_HBV_S_ANTIGEN",
    Base.metadata,
    Column("RR_NO", BigInteger),
    Column("HBV_S_ANTIGEN_DATE", DateTime),
    Column("HBV_S_ANTIGEN_STATUS", Unicode(5, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_HCV_ANTIBODY = Table(
    "AUDIT_HCV_ANTIBODY",
    Base.metadata,
    Column("RR_NO", BigInteger),
    Column("HCV_ANTIBODY_DATE", DateTime),
    Column("HCV_ANTIBODY_STATUS", Unicode(5, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_HIV_ANTIGEN = Table(
    "AUDIT_HIV_ANTIGEN",
    Base.metadata,
    Column("RR_NO", BigInteger),
    Column("HIV_ANTIGEN_DATE", DateTime),
    Column("HIV_ANTIGEN", Unicode(5, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_KTV = Table(
    "AUDIT_KTV",
    Base.metadata,
    Column("RR_NO", BigInteger),
    Column("DATE_START", DateTime),
    Column("DATE_END", DateTime),
    Column("PRE_DIAL_UREA", Numeric(20, 0)),
    Column("POST_DIAL_UREA", Numeric(20, 0)),
    Column("PRE_DIAL_WEIGHT", Numeric(20, 0)),
    Column("POST_DIAL_WEIGHT", Numeric(20, 0)),
    Column("BLOOD_FLOW_RATE", Numeric(20, 0)),
    Column("DIAL_FLOW_RATE", Numeric(20, 0)),
    Column("DIAL_MAKE", Unicode(100, "Latin1_General_CI_AS")),
    Column("DIAL_TIME", Numeric(20, 0)),
    Column("RESIDUAL_RENAL_CLEAR", Numeric(20, 0)),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
    Column("PRE_POST_IND_FOR_WT", Unicode(10, "Latin1_General_CI_AS")),
    Column("WEIGHT_FOR_PD_CALC", Numeric(38, 4)),
    Column("DIALYSATE_UREA", Numeric(38, 4)),
    Column("URINE_UREA", Numeric(38, 4)),
    Column("BLOOD_UREA", Numeric(38, 4)),
    Column("DIALYSATE_KTV", Numeric(38, 4)),
    Column("URINE_KTV", Numeric(38, 4)),
    Column("DIALYSATE_EFFLUENT_VOL", Numeric(38, 4)),
    Column("URINE_VOLUME", Numeric(38, 4)),
    Column("COMBINED_KTV", Numeric(38, 4)),
    Column("URINE_IND", Unicode(1, "Latin1_General_CI_AS")),
    Column("NORMALISED_PROTEIN_CATABOLIC", Numeric(38, 4)),
    Column("PROTEIN_LOSS_24_HOUR", Numeric(38, 4)),
    Column("DIALYSATE_CREATININE", Numeric(38, 4)),
    Column("URINE_CREATININE", Numeric(38, 4)),
    Column("SERUM_CREATININE", Numeric(38, 4)),
    Column("WEEKLY_NORMALISED_CREAT", Numeric(38, 4)),
    Column("CREAT_DIALYSATE_PLASMA_RATIO", Numeric(38, 4)),
    Column("DIALYSATE_GLUCOSE", Numeric(38, 4)),
    Column("HOSP_CENTRE", String(20, "Latin1_General_CI_AS")),
)


t_AUDIT_LOCATIONS = Table(
    "AUDIT_LOCATIONS",
    Base.metadata,
    Column("CENTRE_CODE", Unicode(10, "Latin1_General_CI_AS"), nullable=False),
    Column("CENTRE_NAME", Unicode(255, "Latin1_General_CI_AS"), nullable=False),
    Column("COUNTRY_CODE", Unicode(6, "Latin1_General_CI_AS"), nullable=False),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
    Column("REGION_CODE", Unicode(10, "Latin1_General_CI_AS")),
    Column("PAED_UNIT", Integer),
)


t_AUDIT_MEDICATION = Table(
    "AUDIT_MEDICATION",
    Base.metadata,
    Column("RR_NO", BigInteger, nullable=False),
    Column("START_DATE", DateTime),
    Column("END_DATE", DateTime),
    Column("DRUG_NAME", Unicode(100, "Latin1_General_CI_AS")),
    Column("DRUG_BRAND", Unicode(100, "Latin1_General_CI_AS")),
    Column("UNIT", Unicode(10, "Latin1_General_CI_AS")),
    Column("DOSE", Integer),
    Column("ROUTE", Integer),
    Column("FREQUENCY", Unicode(50, "Latin1_General_CI_AS")),
    Column("COMMENTS", Unicode(250, "Latin1_General_CI_AS")),
    Column("HOSP_CENTRE", String(20, "Latin1_General_CI_AS")),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_MODALITY_CODES = Table(
    "AUDIT_MODALITY_CODES",
    Base.metadata,
    Column("REGISTRY_CODE", Unicode(8, "Latin1_General_CI_AS"), nullable=False),
    Column("REGISTRY_CODE_DESC", Unicode(100, "Latin1_General_CI_AS")),
    Column("REGISTRY_CODE_TYPE", Unicode(3, "Latin1_General_CI_AS")),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
    Column("TRANSFER_IN", Boolean),
    Column("ACUTE", Boolean),
    Column("CKD", Boolean),
    Column("CONS", Boolean),
    Column("RRT", Boolean),
    Column("EQUIV_MODALITY", Unicode(8, "Latin1_General_CI_AS")),
    Column("END_OF_CARE", Boolean),
    Column("IS_IMPRECISE", Boolean),
    Column("NHSBT_TRANSPLANT_TYPE", Unicode(4, "Latin1_General_CI_AS")),
    Column("TRANSFER_OUT", Boolean),
)


t_AUDIT_MONTHLY_TREATMENT = Table(
    "AUDIT_MONTHLY_TREATMENT",
    Base.metadata,
    Column("RR_NO", BigInteger, nullable=False),
    Column("START_DATE", DateTime, nullable=False),
    Column("END_DATE", DateTime),
    Column("HOSP_CENTRE", Unicode(8, "Latin1_General_CI_AS"), nullable=False),
    Column("TREATMENT_MODALITY", Unicode(8, "Latin1_General_CI_AS")),
    Column("ADD_HAEMO_ON_PD", Unicode(1, "Latin1_General_CI_AS")),
    Column("TREATMENT_CENTRE", Unicode(8, "Latin1_General_CI_AS"), nullable=False),
    Column("HD_SUPERVISION", Unicode(6, "Latin1_General_CI_AS")),
    Column("CENTRE_PRI", Unicode(1, "Latin1_General_CI_AS")),
    Column("SERUM_CREATININE_DATE", DateTime),
    Column("SERUM_CREATININE", Numeric(38, 4)),
    Column("SERUM_UREA", Numeric(38, 4)),
    Column("SERUM_BICARBONATE_DATE", DateTime),
    Column("SERUM_BICARBONATE", Numeric(38, 4)),
    Column("SERUM_SODIUM_DATE", DateTime),
    Column("SERUM_SODIUM", Numeric(38, 4)),
    Column("SERUM_POTASSIUM_DATE", DateTime),
    Column("SERUM_POTASSIUM", Numeric(38, 4)),
    Column("LAB_CALCULATED_EGFR", Numeric(38, 4)),
    Column("SERUM_URIC_ACID_DATE", DateTime),
    Column("SERUM_URIC_ACID", Numeric(38, 4)),
    Column("SERUM_PHOSPHATE_DATE", DateTime),
    Column("SERUM_PHOSPHATE", Numeric(38, 4)),
    Column("SERUM_CALCIUM", Numeric(38, 4)),
    Column("SERUM_CALCIUM_CORRECTED", Numeric(38, 4)),
    Column("SERUM_ALKA_PHOSPHATASE_DATE", DateTime),
    Column("SERUM_ALKA_PHOSPHATASE", Numeric(38, 4)),
    Column("SERUM_ALBUMIN_DATE", DateTime),
    Column("SERUM_ALBUMIN", Numeric(38, 4)),
    Column("SERUM_IPTH_DATE", DateTime),
    Column("SERUM_IPTH", Numeric(38, 4)),
    Column("UPC_RATIO_DATE", DateTime),
    Column("UPC_RATIO", Numeric(38, 4)),
    Column("UAC_RATIO_DATE", DateTime),
    Column("UAC_RATIO", Numeric(38, 4)),
    Column("SERUM_CHOLESTEROL_DATE", DateTime),
    Column("SERUM_CHOLESTEROL", Numeric(38, 4)),
    Column("SERUM_HDL_CHOLESTEROL", Numeric(38, 4)),
    Column("SERUM_LDL_CHOLESTEROL", Numeric(38, 4)),
    Column("SERUM_TRIGLYCERIDES", Numeric(38, 4)),
    Column("CRP_DATE", DateTime),
    Column("CRP", Numeric(38, 4)),
    Column("HBA1C_DATE", DateTime),
    Column("HBA1C_PERCENT", Numeric(38, 4)),
    Column("HAEMOGLOBIN_DATE", DateTime),
    Column("HAEMOGLOBIN", Numeric(38, 4)),
    Column("MCH", Numeric(38, 4)),
    Column("PLATELETS", Numeric(38, 4)),
    Column("WBC", Numeric(38, 4)),
    Column("SERUM_FERRITIN_DATE", DateTime),
    Column("SERUM_FERRITIN", Numeric(38, 4)),
    Column("TRANSFERRIN_SATURATION_DATE", DateTime),
    Column("TRANSFERRIN_SATURATION", Numeric(38, 4)),
    Column("HYPOCHROMIC_RED_CELLS_DATE", DateTime),
    Column("HYPOCHROMIC_RED_CELLS", Numeric(38, 4)),
    Column("SERUM_B12_DATE", DateTime),
    Column("SERUM_B12", Numeric(38, 4)),
    Column("SERUM_FOLATE_DATE", DateTime),
    Column("SERUM_FOLATE", Numeric(38, 4)),
    Column("RED_CELL_FOLATE_DATE", DateTime),
    Column("RED_CELL_FOLATE", Numeric(38, 4)),
    Column("SERUM_ALUMINIUM_DATE", DateTime),
    Column("SERUM_ALUMINIUM", Numeric(38, 4)),
    Column("WEIGHT_DATE", DateTime),
    Column("WEIGHT", Numeric(38, 4)),
    Column("BP_DATE", DateTime),
    Column("SYSTOLIC_BP", Numeric(38, 4)),
    Column("DIASTOLIC_BP", Numeric(38, 4)),
    Column("POST_BP_DATE", DateTime),
    Column("POST_SYSTOLIC_BP", Numeric(38, 4)),
    Column("POST_DIASTOLIC_BP", Numeric(38, 4)),
    Column("URR_DATE", DateTime),
    Column("URR", Numeric(38, 4)),
    Column("BLOOD_FLOW_RATE", Numeric(38, 4)),
    Column("HD_TIMES_PER_WEEK", Numeric(38, 4)),
    Column("DIALYSIS_TIME", Numeric(38, 4)),
    Column("WEEKLY_FLUID_VOL", Numeric(38, 4)),
    Column("BAG_SIZE", Numeric(38, 4)),
    Column("STATIN_DRUG_USE", Unicode(1, "Latin1_General_CI_AS")),
    Column("ACE_INHIBITOR", Unicode(1, "Latin1_General_CI_AS")),
    Column("ANGIOTENSIN_RECEPTOR_BLOCKER", Unicode(1, "Latin1_General_CI_AS")),
    Column("ORAL_B_BLOCKER", Unicode(1, "Latin1_General_CI_AS")),
    Column("RENAGEL", Unicode(1, "Latin1_General_CI_AS")),
    Column("LANTHANUM", Unicode(1, "Latin1_General_CI_AS")),
    Column("CINACALCET", Unicode(1, "Latin1_General_CI_AS")),
    Column("CALCIUM_BASED_BINDER", Unicode(1, "Latin1_General_CI_AS")),
    Column("ALUCAPS", Unicode(1, "Latin1_General_CI_AS")),
    Column("HBA1C_VALUE", Numeric(38, 4)),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
    Column("SHARED_CARE", SmallInteger),
    Column("SERUM_UREA_DATE", DateTime),
    Column("LAB_CALCULATED_EGFR_DATE", DateTime),
    Column("SERUM_CALCIUM_DATE", DateTime),
    Column("SERUM_CALCIUM_CORRECTED_DATE", DateTime),
    Column("IPTH_ASSAY_METHOD", Unicode(30, "Latin1_General_CI_AS")),
    Column("SERUM_HDL_DATE", DateTime),
    Column("SERUM_LDL_DATE", DateTime),
    Column("SERUM_TRIGLYCERIDES_DATE", DateTime),
    Column("MCH_DATE", DateTime),
    Column("PLATELETS_DATE", DateTime),
    Column("WBC_DATE", DateTime),
    Column("HAEMOGLOBIN_GL", Numeric(38, 4)),
    Column("TACROLIMUS_LEVEL", Numeric(38, 4)),
    Column("TACROLIMUS_LEVEL_DATE", DateTime),
    Column("SIROLIMUS_LEVEL", Numeric(38, 4)),
    Column("SIROLIMUS_LEVEL_DATE", DateTime),
    Column("CICLOSPORIN_LEVEL", Numeric(38, 4)),
    Column("CICLOSPORIN_LEVEL_DATE", DateTime),
    Column("MYCOPHENOLATE_LEVEL", Numeric(38, 4)),
    Column("MYCOPHENOLATE_LEVEL_DATE", DateTime),
    Column("HEIGHT", Numeric(38, 4)),
    Column("HEIGHT_DATE", DateTime),
    Column("LAST_APPT_ATTENDED_DATE", DateTime),
    Column("ACCESS_USED", Unicode(10, "Latin1_General_CI_AS")),
    Column("KTV", Numeric(38, 4)),
    Column("KTV_DATE", DateTime),
    Column("HBV_ANTIBODY", Unicode(10, "Latin1_General_CI_AS")),
    Column("HBV_ANTIBODY_DATE", DateTime),
    Column("HBV_ANTIGEN", Unicode(10, "Latin1_General_CI_AS")),
    Column("HBV_ANTIGEN_DATE", DateTime),
    Column("HCV_ANTIBODY", Unicode(10, "Latin1_General_CI_AS")),
    Column("HCV_ANTIBODY_DATE", DateTime),
    Column("CMV_ANTIBODY", Unicode(10, "Latin1_General_CI_AS")),
    Column("CMV_ANTIBODY_DATE", DateTime),
    Column("CMV_PCR_DATE", DateTime),
    Column("CMV_PCR", Numeric(38, 4)),
    Column("HIV_TEST_DATE", DateTime),
    Column("HIV_ANTIGEN", Unicode(10, "Latin1_General_CI_AS")),
    Column("EBV_STATUS", Unicode(10, "Latin1_General_CI_AS")),
    Column("EBV_PCR_COUNT", Numeric(38, 4)),
    Column("EBV_TEST_DATE", DateTime),
    Column("URINE_DATE", DateTime),
    Column("URINE_VOL", Numeric(38, 4)),
    Column("URINARY_CREATININE", Numeric(38, 4)),
    Column("SELF_CARE", String(1, "Latin1_General_CI_AS")),
    Column("TRANSPLANTED_KIDNEY_DRAINAGE", Integer),
    Column("NON_RENAL_GRAFT_1", Unicode(20, "Latin1_General_CI_AS")),
    Column("NON_RENAL_GRAFT_2", Unicode(20, "Latin1_General_CI_AS")),
    Column("NON_RENAL_GRAFT_3", Unicode(20, "Latin1_General_CI_AS")),
    Column("DIAGNOSED_PTLD", String(1, "Latin1_General_CI_AS")),
    Column("MENTAL_DISABILITY", Integer),
    Column("PHYSICAL_DISABILITY", Integer),
    Column("VISUAL_DISABILITY", Integer),
    Column("AUDITORY_DISABILITY", Integer),
    Column("PTH_ULN", DECIMAL(18, 0)),
    Column("PTH_ULN_RATIO", DECIMAL(18, 0)),
    Column("ALT", Integer),
    Column("ANC", DECIMAL(18, 0)),
    Column("ALC", DECIMAL(18, 0)),
    Column("VARICELLA", String(3, "Latin1_General_CI_AS")),
    Column("VARICELLA_TEST_DATE", DateTime),
    Column("MYOPATHY", String(1, "Latin1_General_CI_AS")),
    Column("ANTHROPATHY", String(1, "Latin1_General_CI_AS")),
    Column("CENTRAL_NERVOUS_COM", Unicode(150, "Latin1_General_CI_AS")),
    Column("RESPIRATORY_COM", Unicode(150, "Latin1_General_CI_AS")),
    Column("CARDIOVASCULAR_COM", Unicode(150, "Latin1_General_CI_AS")),
    Column("GASTRO_INTESTINAL_COM", Unicode(150, "Latin1_General_CI_AS")),
    Column("HEPATIC_COM", Unicode(150, "Latin1_General_CI_AS")),
    Column("GENITO_URINARY_COM", Unicode(150, "Latin1_General_CI_AS")),
    Column("ENDOCRINE_COM", Unicode(150, "Latin1_General_CI_AS")),
    Column("SOCIAL_PSYCHIATRIC_COM", Unicode(150, "Latin1_General_CI_AS")),
    Column("PUBERTY_DATE", DateTime),
    Column("DATE_UNIT_CALC_EGFR", DateTime),
    Column("EGFR_CALC_BY_UNIT", Numeric(38, 4)),
)


t_AUDIT_NHS_TRACING_MISMATCHES = Table(
    "AUDIT_NHS_TRACING_MISMATCHES",
    Base.metadata,
    Column("RR_NO", BigInteger),
    Column("NHS_NO", BigInteger),
    Column("NOTES", Unicode(collation="Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_PATIENTS = Table(
    "AUDIT_PATIENTS",
    Base.metadata,
    Column("RR_NO", BigInteger),
    Column("SURNAME", Unicode(50, "Latin1_General_CI_AS"), nullable=False),
    Column("FORENAME", Unicode(50, "Latin1_General_CI_AS")),
    Column("DATE_BIRTH", DateTime),
    Column("LOCAL_HOSP_NO", Unicode(15, "Latin1_General_CI_AS")),
    Column("DATE_REGISTERED", DateTime),
    Column("SEX", Unicode(1, "Latin1_General_CI_AS")),
    Column("HOSP_CENTRE", Unicode(8, "Latin1_General_CI_AS")),
    Column("MIN_DATA_IND", Unicode(2, "Latin1_General_CI_AS")),
    Column("ESRF_IND", Unicode(1, "Latin1_General_CI_AS")),
    Column("PAEDIATRIC_IND", Unicode(1, "Latin1_General_CI_AS")),
    Column("UKTSSA_NO", BigInteger),
    Column("CHI_NO", BigInteger),
    Column("SUPER_CHI_NO", Unicode(15, "Latin1_General_CI_AS")),
    Column("NEW_NHS_NO", BigInteger),
    Column("OLD_NHS_NO", Unicode(15, "Latin1_General_CI_AS")),
    Column("MRC_NO", Unicode(10, "Latin1_General_CI_AS")),
    Column("SCOT_REG_NO", Unicode(10, "Latin1_General_CI_AS")),
    Column("MARITAL_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("ETHGR_CODE", Unicode(8, "Latin1_General_CI_AS")),
    Column("ADULT_HEIGHT", Numeric(38, 4)),
    Column("FIRST_SEEN_HEIGHT", Numeric(38, 4)),
    Column("FIRST_SEEN_WEIGHT", Numeric(38, 4)),
    Column("FIRST_SEEN_DATE", DateTime),
    Column("FIRST_SEEN_CREATININE", Numeric(38, 4)),
    Column("DATE_DEATH", DateTime),
    Column("COD_READ", Unicode(8, "Latin1_General_CI_AS")),
    Column("COD_EDTA1", Numeric(20, 0)),
    Column("COD_EDTA2", Numeric(20, 0)),
    Column("COD_TEXT", Unicode(70, "Latin1_General_CI_AS")),
    Column("TRANSFER_IND", Unicode(1, "Latin1_General_CI_AS")),
    Column("TRANSFER_DATE", DateTime),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
    Column("BLOOD_GROUP", Unicode(2, "Latin1_General_CI_AS")),
    Column("BLOOD_GROUP_RHESUS", Unicode(3, "Latin1_General_CI_AS")),
    Column("SURNAME_SOUNDEX", Unicode(4, "Latin1_General_CI_AS")),
    Column("CENTRE_PRI", Unicode(1, "Latin1_General_CI_AS")),
    Column("GP_POSTCODE", Unicode(8, "Latin1_General_CI_AS")),
    Column("OPT_OUT_FLAG", Unicode(1, "Latin1_General_CI_AS")),
    Column("YEAR_OF_BIRTH", Numeric(20, 0)),
    Column("DESCRIPTION", Unicode(30, "Latin1_General_CI_AS")),
    Column("UNIQUE_IDENTIFIER", Unicode(20, "Latin1_General_CI_AS")),
    Column("TRACING_DATE_DEATH", DateTime),
    Column("TRACING_DATE_BIRTH", DateTime),
    Column("DOMINANT_ARM", Unicode(10, "Latin1_General_CI_AS")),
    Column("REFERRAL_CODE", Unicode(20, "Latin1_General_CI_AS")),
    Column("REFERRAL_DATE", DateTime),
    Column("REFERRING_GP_CODE", Unicode(20, "Latin1_General_CI_AS")),
    Column("TRACING_NHS_NO", BigInteger),
    Column("DATE_CKD5_START", DateTime),
    Column("CKD5_START", Numeric(38, 4)),
    Column("DATE_CKD5_GE_90", DateTime),
    Column("CKD5_GE_90", Numeric(38, 4)),
    Column("UKT_UKTSSA_NO", BigInteger),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("DATE_STAT", DateTime),
    Column("TRACING_RESPONSE", Unicode(2, "Latin1_General_CI_AS")),
    Column("BAPN_NO", Unicode(20, "Latin1_General_CI_AS")),
    Column("DATE_LAST_TRACED", DateTime),
    Column("SOUNDEX_FORENAME", String(5, "Latin1_General_CI_AS")),
    Column("BIRTH_NAME", Unicode(50, "Latin1_General_CI_AS")),
    Column("ALIAS_NAME", Unicode(50, "Latin1_General_CI_AS")),
    Column("HSC_NO", BigInteger),
    Column("GP_CODE", Unicode(10, "Latin1_General_CI_AS")),
    Column("RPV_FLAG", Unicode(1, "Latin1_General_CI_AS")),
    Column("REFERRING_GP_PRACTICE_CODE", Unicode(10, "Latin1_General_CI_AS")),
    Column("SOUNDEX_SURNAME", String(5, "Latin1_General_CI_AS")),
    Column("RR_DATE_FIRST_CKD4", DateTime),
    Column("RR_DATE_FIRST_CKD5", DateTime),
    Column("RR_DATE_FIRST_AKI", DateTime),
    Column("RR_DATE_FIRST_ESRF", DateTime),
    Column("RR_DATE_FIRST_CONS", DateTime),
    Column("RR_DATE_FIRST_CKD1", DateTime),
    Column("RR_DATE_FIRST_CKD2", DateTime),
    Column("RR_DATE_FIRST_CKD3", DateTime),
    Column("RR_DATE_FIRST_PAED", DateTime),
)


t_AUDIT_PATIENT_DEMOG = Table(
    "AUDIT_PATIENT_DEMOG",
    Base.metadata,
    Column("RR_NO", BigInteger),
    Column("HOSP_CENTRE", Unicode(8, "Latin1_General_CI_AS")),
    Column("LOCAL_HOSP_NO", Unicode(15, "Latin1_General_CI_AS")),
    Column("SURNAME", Unicode(50, "Latin1_General_CI_AS")),
    Column("FORENAME", Unicode(50, "Latin1_General_CI_AS")),
    Column("DATE_BIRTH", DateTime),
    Column("DATE_DEATH", DateTime),
    Column("NEW_NHS_NO", BigInteger),
    Column("CHI_NO", BigInteger),
    Column("FIRST_SEEN_DATE", DateTime),
    Column("ETHGR_CODE", Unicode(8, "Latin1_General_CI_AS")),
    Column("UKTSSA_NO", BigInteger),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
    Column("BIRTH_NAME", Unicode(50, "Latin1_General_CI_AS")),
    Column("ALIAS_NAME", Unicode(50, "Latin1_General_CI_AS")),
    Column("HSC_NO", BigInteger),
)


t_AUDIT_PATIENT_NOTES = Table(
    "AUDIT_PATIENT_NOTES",
    Base.metadata,
    Column("RR_NO", BigInteger, nullable=False),
    Column("NOTES", Unicode(4000, "Latin1_General_CI_AS")),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_PATIENT_XREF = Table(
    "AUDIT_PATIENT_XREF",
    Base.metadata,
    Column("RR_NO", BigInteger),
    Column("SURNAME", Unicode(50, "Latin1_General_CI_AS"), nullable=False),
    Column("FORENAME", Unicode(50, "Latin1_General_CI_AS")),
    Column("DATE_BIRTH", DateTime),
    Column("USE_AS_DEFAULT", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
    Column("SOUNDEX_FORENAME", String(5, "Latin1_General_CI_AS")),
    Column("BIRTH_NAME", Unicode(50, "Latin1_General_CI_AS")),
    Column("ALIAS_NAME", Unicode(50, "Latin1_General_CI_AS")),
    Column("SOUNDEX_SURNAME", String(5, "Latin1_General_CI_AS")),
)


t_AUDIT_QUARTERLY_TREATMENT = Table(
    "AUDIT_QUARTERLY_TREATMENT",
    Base.metadata,
    Column("RR_NO", BigInteger),
    Column("DATE_START", DateTime),
    Column("DATE_END", DateTime),
    Column("TREATMENT_MODALITY", Unicode(8, "Latin1_General_CI_AS")),
    Column("ADD_HAEMO_ON_PD", Unicode(1, "Latin1_General_CI_AS")),
    Column("TREATMENT_CENTRE", Unicode(8, "Latin1_General_CI_AS")),
    Column("CREATININE", Numeric(38, 4)),
    Column("UREA", Numeric(38, 4)),
    Column("HAEMOGLOBIN", Numeric(38, 4)),
    Column("FERRETIN", Numeric(38, 4)),
    Column("ALBUMIN", Numeric(38, 4)),
    Column("ALUMINIUM", Numeric(38, 4)),
    Column("HBA1C", Numeric(38, 4)),
    Column("CHOLESTEROL", Numeric(38, 4)),
    Column("IPTH", Numeric(38, 4)),
    Column("CALCIUM_UNCORR", Numeric(38, 4)),
    Column("CALCIUM_CORR", Numeric(38, 4)),
    Column("PHOSPHATE", Numeric(38, 4)),
    Column("BICARBONATE", Numeric(38, 4)),
    Column("SYSTOLIC_BP", Numeric(20, 0)),
    Column("DIASTOLIC_BP", Numeric(20, 0)),
    Column("WEIGHT", Numeric(38, 4)),
    Column("UREA_REDUCTION_RATIO", Numeric(38, 4)),
    Column("EPO_USE", Unicode(1, "Latin1_General_CI_AS")),
    Column("HOSP_CENTRE", Unicode(8, "Latin1_General_CI_AS")),
    Column("HD_SUPERVISON", Unicode(4, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
    Column("DIALYSER_USED", Unicode(8, "Latin1_General_CI_AS")),
    Column("FLOW_RATE", Numeric(20, 0)),
    Column("DIAL_REUSE", Unicode(1, "Latin1_General_CI_AS")),
    Column("TIMES_PER_WEEK", Numeric(20, 0)),
    Column("DIAL_TIME", Numeric(38, 4)),
    Column("BICARB_DIAL", Unicode(1, "Latin1_General_CI_AS")),
    Column("WEEKLY_FLUID_VOL", Numeric(38, 4)),
    Column("BAG_SIZE", Numeric(38, 4)),
    Column("CENTRE_PRI", Unicode(1, "Latin1_General_CI_AS")),
    Column("POST_SYSTOLIC_BP", Numeric(20, 0)),
    Column("POST_DIASTOLIC_BP", Numeric(20, 0)),
    Column("PD_DIALYSATE_KTV", Numeric(38, 4)),
    Column("PD_URINE_KTV", Numeric(38, 4)),
    Column("PD_NPCR", Numeric(38, 4)),
    Column("CRP", Numeric(38, 4)),
    Column("LDL_CHOLESTEROL", Numeric(38, 4)),
    Column("HDL_CHOLESTEROL", Numeric(38, 4)),
    Column("TRIGLYCERIDES", Numeric(38, 4)),
    Column("SODIUM", Numeric(38, 4)),
    Column("WAITING_LIST_STATUS", Unicode(3, "Latin1_General_CI_AS")),
    Column("CREATININE_FIRST_MONTH", Numeric(38, 4)),
    Column("CREATININE_SECOND_MONTH", Numeric(38, 4)),
    Column("PERCENT_HYPOCHROMIC", Numeric(38, 4)),
    Column("MCH", Numeric(38, 4)),
    Column("B12", Numeric(38, 4)),
    Column("RED_CELL_FOLATE", Numeric(38, 4)),
    Column("TRANSFERRIN_SATURATION", Numeric(38, 4)),
    Column("SERUM_POTASSIUM", Numeric(38, 4)),
    Column("PROTEIN_CREATININE_RATIO", Numeric(38, 4)),
    Column("ALBUMIN_CREATININE_RATIO", Numeric(38, 4)),
    Column("SERUM_CELL_FOLATE", Numeric(38, 4)),
    Column("ACE_INHIBITOR", Unicode(1, "Latin1_General_CI_AS")),
    Column("RENAGEL", Unicode(1, "Latin1_General_CI_AS")),
    Column("LANTHANUM", Unicode(1, "Latin1_General_CI_AS")),
    Column("CINACALCET", Unicode(1, "Latin1_General_CI_AS")),
    Column("CALCIUM_BASED_BINDER", Unicode(1, "Latin1_General_CI_AS")),
    Column("ALUCAPS", Unicode(1, "Latin1_General_CI_AS")),
    Column("SERUM_URATE", Numeric(38, 4)),
    Column("STATIN_DRUG_USE", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("HBA1C_MMOL", Numeric(38, 4)),
    Column("ALKALINE_PHOSPHATASE", Numeric(38, 4)),
)


t_AUDIT_RESIDENCY = Table(
    "AUDIT_RESIDENCY",
    Base.metadata,
    Column("CENTRE_CODE", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_NO", BigInteger),
    Column("DATE_START", DateTime),
    Column("DATE_END", DateTime),
    Column("ADDRESS_1", Unicode(60, "Latin1_General_CI_AS")),
    Column("ADDRESS_2", Unicode(60, "Latin1_General_CI_AS")),
    Column("ADDRESS_3", Unicode(60, "Latin1_General_CI_AS")),
    Column("POST_CODE", Unicode(8, "Latin1_General_CI_AS")),
    Column("CENTRE_PRI", Unicode(1, "Latin1_General_CI_AS")),
    Column("NHS_CODE", Unicode(3, "Latin1_General_CI_AS")),
    Column("NHS_NAME", Unicode(60, "Latin1_General_CI_AS")),
    Column("STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("SENT_ADD_1", Unicode(60, "Latin1_General_CI_AS")),
    Column("SENT_ADD_2", Unicode(60, "Latin1_General_CI_AS")),
    Column("SENT_ADD_3", Unicode(60, "Latin1_General_CI_AS")),
    Column("SENT_POST_CODE", Unicode(8, "Latin1_General_CI_AS")),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
    Column("ADDRESS_4", Unicode(60, "Latin1_General_CI_AS")),
    Column("SENT_ADD_4", Unicode(60, "Latin1_General_CI_AS")),
)


t_AUDIT_RR_CODES = Table(
    "AUDIT_RR_CODES",
    Base.metadata,
    Column("ID", Unicode(10, "Latin1_General_CI_AS"), nullable=False),
    Column("RR_CODE", Unicode(10, "Latin1_General_CI_AS"), nullable=False),
    Column("DESCRIPTION_1", Unicode(255, "Latin1_General_CI_AS")),
    Column("DESCRIPTION_2", Unicode(70, "Latin1_General_CI_AS")),
    Column("DESCRIPTION_3", Unicode(60, "Latin1_General_CI_AS")),
    Column("OLD_VALUE", Unicode(10, "Latin1_General_CI_AS")),
    Column("OLD_VALUE_2", Unicode(10, "Latin1_General_CI_AS")),
    Column("NEW_VALUE", Unicode(10, "Latin1_General_CI_AS")),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_RR_CODE_LISTS = Table(
    "AUDIT_RR_CODE_LISTS",
    Base.metadata,
    Column("ID", Unicode(10, "Latin1_General_CI_AS"), nullable=False),
    Column("NAME", Unicode(70, "Latin1_General_CI_AS")),
    Column("UPLOAD_KEYS", Unicode(70, "Latin1_General_CI_AS")),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_RR_COUNTS_CONFIG = Table(
    "AUDIT_RR_COUNTS_CONFIG",
    Base.metadata,
    Column("id", Integer, Identity(start=1, increment=1), nullable=False),
    Column("listgroup", Integer, nullable=False),
    Column("tagname", String(5, "Latin1_General_CI_AS"), nullable=False),
    Column("display", NCHAR(1, "Latin1_General_CI_AS"), nullable=False),
    Column("description", String(100, "Latin1_General_CI_AS")),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_RR_DATA_DEFINITION = Table(
    "AUDIT_RR_DATA_DEFINITION",
    Base.metadata,
    Column("UPLOAD_KEY", Unicode(5, "Latin1_General_CI_AS")),
    Column("TABLE_NAME", Unicode(30, "Latin1_General_CI_AS"), nullable=False),
    Column("FIELD_NAME", Unicode(30, "Latin1_General_CI_AS"), nullable=False),
    Column("CODE_ID", Unicode(10, "Latin1_General_CI_AS")),
    Column("MANDATORY", Numeric(1, 0)),
    Column("TYPE", Unicode(1, "Latin1_General_CI_AS")),
    Column("ALT_CONSTRAINT", Unicode(30, "Latin1_General_CI_AS")),
    Column("ALT_DESC", Unicode(30, "Latin1_General_CI_AS")),
    Column("EXTRA_VAL", Unicode(1, "Latin1_General_CI_AS")),
    Column("ERROR_TYPE", Integer),
    Column("PAED_MAND", Numeric(1, 0)),
    Column("CKD5_MAND", Numeric(1, 0)),
    Column("DEPENDANT_FIELD", Unicode(30, "Latin1_General_CI_AS")),
    Column("ALT_VALIDATION", Unicode(30, "Latin1_General_CI_AS")),
    Column("FILE_PREFIX", Unicode(20, "Latin1_General_CI_AS")),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
    Column("MIN", Numeric(38, 4)),
    Column("MAX", Numeric(38, 4)),
    Column("LOAD_MIN", Numeric(38, 4)),
    Column("LOAD_MAX", Numeric(38, 4)),
    Column("REMOVE_MIN", Numeric(38, 4)),
    Column("REMOVE_MAX", Numeric(38, 4)),
    Column("IN_MONTH", Numeric(1, 0)),
    Column("AKI_MAND", Numeric(1, 0)),
    Column("RRT_MAND", Numeric(1, 0)),
    Column("CONS_MAND", Numeric(1, 0)),
    Column("CKD4_MAND", Numeric(1, 0)),
    Column("VALID_BEFORE_DOB", Numeric(1, 0)),
    Column("VALID_AFTER_DOD", Numeric(1, 0)),
    Column("IN_QUARTER", Numeric(1, 0)),
)


t_AUDIT_RR_ERROR_LOG = Table(
    "AUDIT_RR_ERROR_LOG",
    Base.metadata,
    Column("ERROR_TIMESTAMP", DateTime, nullable=False),
    Column("ERROR_TYPE", Unicode(collation="Latin1_General_CI_AS")),
    Column("ERROR_TEXT", Unicode(collation="Latin1_General_CI_AS")),
    Column("ERROR_DETAILS", Unicode(collation="Latin1_General_CI_AS")),
    Column("UPLOAD_FILE", Unicode(collation="Latin1_General_CI_AS")),
    Column("SQL", Unicode(collation="Latin1_General_CI_AS")),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_RR_HIST_COUNTS = Table(
    "AUDIT_RR_HIST_COUNTS",
    Base.metadata,
    Column("ID", Integer, Identity(start=1, increment=1), nullable=False),
    Column("PROCESS_DATE", DateTime),
    Column("FILESITE", Unicode(8, "Latin1_General_CI_AS")),
    Column("FILEQUARTER", Integer),
    Column("Tag", Unicode(255, "Latin1_General_CI_AS")),
    Column("COUNT", Integer),
    Column("M1_COUNT", Integer),
    Column("M2_COUNT", Integer),
    Column("M3_COUNT", Integer),
    Column("QUA_EQ_COUNT", Integer),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_RR_MONTH_TO_QUARTER_FIELD_MAP = Table(
    "AUDIT_RR_MONTH_TO_QUARTER_FIELD_MAP",
    Base.metadata,
    Column("monthly_name", Unicode(50, "Latin1_General_CI_AS")),
    Column("quarterly_equiv", Unicode(50, "Latin1_General_CI_AS")),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_RR_NOLOAD = Table(
    "AUDIT_RR_NOLOAD",
    Base.metadata,
    Column("SITE", Unicode(8, "Latin1_General_CI_AS")),
    Column("QUARTER", Integer),
    Column("LOCAL_HOSP_NO", Unicode(15, "Latin1_General_CI_AS")),
    Column("SURNAME", Unicode(50, "Latin1_General_CI_AS")),
    Column("FORENAME", Unicode(50, "Latin1_General_CI_AS")),
    Column("DATE_BIRTH", DateTime),
    Column("NEW_NHS_NO", BigInteger),
    Column("CODED_REASON", Unicode(15, "Latin1_General_CI_AS")),
    Column("REASON_FREETEXT", Unicode(60, "Latin1_General_CI_AS")),
    Column("EXTRA_COMMENT", Unicode(60, "Latin1_General_CI_AS")),
    Column("INITIALS", Unicode(4, "Latin1_General_CI_AS")),
    Column("RR_NO", BigInteger),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("OTHER_SITE_CODE", Unicode(10, "Latin1_General_CI_AS")),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_RR_NOMATCH_PATIENTS = Table(
    "AUDIT_RR_NOMATCH_PATIENTS",
    Base.metadata,
    Column("RR_NO", BigInteger, nullable=False),
    Column("MISMATCH_RR_NO", BigInteger, nullable=False),
    Column("COMMENTS", Unicode(128, "Latin1_General_CI_AS")),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_RR_NOMATCH_UKT = Table(
    "AUDIT_RR_NOMATCH_UKT",
    Base.metadata,
    Column("RR_NO", BigInteger, nullable=False),
    Column("MISMATCH_UKTSSA_NO", BigInteger, nullable=False),
    Column("COMMENTS", Unicode(128, "Latin1_General_CI_AS")),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_RR_NO_ALLOCATION = Table(
    "AUDIT_RR_NO_ALLOCATION",
    Base.metadata,
    Column("ALLOC_YEAR", Integer),
    Column("NEXT_RR_NO", Integer),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_RR_QUARTERS = Table(
    "AUDIT_RR_QUARTERS",
    Base.metadata,
    Column("QUARTERNUMBER", BigInteger),
    Column("QUARTERSTARTDATE", DateTime),
    Column("QUARTERENDDATE", DateTime),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_SYS_TAKEON = Table(
    "AUDIT_SYS_TAKEON",
    Base.metadata,
    Column("TREATMENT_MODALITY", String(50, "Latin1_General_CI_AS")),
    Column("TREATMENT_CENTRE", String(50, "Latin1_General_CI_AS")),
    Column("DATE_START", DateTime),
    Column("RR_NO", BigInteger),
    Column("HOSP_CENTRE", String(50, "Latin1_General_CI_AS")),
    Column("YEAR_END_SEQ", Integer),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_TBL_VWE_UKT_RR_PATIENTS = Table(
    "AUDIT_TBL_VWE_UKT_RR_PATIENTS",
    Base.metadata,
    Column("UNDELETED_RR_NO", BigInteger),
    Column("RR_NO", BigInteger),
    Column("UKT_UKTSSA_NO", BigInteger),
    Column("SURNAME", Unicode(50, "Latin1_General_CI_AS")),
    Column("FORENAME", Unicode(50, "Latin1_General_CI_AS")),
    Column("DATE_BIRTH", DateTime),
    Column("DATE_DEATH", DateTime),
    Column("TRACING_DATE_DEATH", DateTime),
    Column("NEW_NHS_NO", BigInteger),
    Column("CHI_NO", BigInteger),
    Column("SCOT_REG_NO", Unicode(10, "Latin1_General_CI_AS")),
    Column("LOCAL_HOSP_NO", Unicode(15, "Latin1_General_CI_AS")),
    Column("HOSP_CENTRE", Unicode(8, "Latin1_General_CI_AS")),
    Column("UKTSSA_NO", BigInteger),
    Column("PATIENT_TYPE", String(26, "Latin1_General_CI_AS"), nullable=False),
    Column("SOUNDEX_SURNAME", String(5, "Latin1_General_CI_AS")),
    Column("SOUNDEX_FORENAME", String(5, "Latin1_General_CI_AS")),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_TRANSPLANT = Table(
    "AUDIT_TRANSPLANT",
    Base.metadata,
    Column("RR_NO", BigInteger, nullable=False),
    Column("HOSP_CENTRE", String(20, "Latin1_General_CI_AS"), nullable=False),
    Column("TRANSPLANT_DATE", DateTime, nullable=False),
    Column("TRANSPLANT_NUMBER", Integer),
    Column("TRANSPLANT_FAILURE", String(1, "Latin1_General_CI_AS")),
    Column("FAILURE_DATE", DateTime),
    Column("FAILURE_CAUSE", Integer),
    Column("FAILURE_DESCRIPTION", Unicode(255, "Latin1_General_CI_AS")),
    Column("GRAFT_NEPHRECTOMY_DATE", DateTime),
    Column("UKT_TRANSPLANT_NUMBER", BigInteger),
    Column("PRE_GRAFT_TREATMENT", String(4, "Latin1_General_CI_AS")),
    Column("LISTED_DATE", DateTime),
    Column("TRANSPLANT_CENTRE", String(20, "Latin1_General_CI_AS")),
    Column("TRANSPLANT_ABROAD", String(50, "Latin1_General_CI_AS")),
    Column("REMAINING_KIDNEYS", Integer),
    Column("GRAFT_TYPE", Integer),
    Column("NHSBT_TYPE", String(5, "Latin1_General_CI_AS")),
    Column("RCMV_STATUS", String(3, "Latin1_General_CI_AS")),
    Column("REBV_STATUS", String(3, "Latin1_General_CI_AS")),
    Column("DONOR_AGE", Integer),
    Column("DONOR_SEX", String(1, "Latin1_General_CI_AS")),
    Column("DCMV_STATUS", String(3, "Latin1_General_CI_AS")),
    Column("DEBV_STATUS", String(3, "Latin1_General_CI_AS")),
    Column("MISMATCH_A", Integer),
    Column("MISMATCH_B", Integer),
    Column("MISMATCH_DR", Integer),
    Column("ABO_COMPATIBLE", String(1, "Latin1_General_CI_AS")),
    Column("PLASMA_EXCHANGE", String(1, "Latin1_General_CI_AS")),
    Column("IMMUNOADSORPTION", String(1, "Latin1_General_CI_AS")),
    Column("RITUXIMAB", String(1, "Latin1_General_CI_AS")),
    Column("IV_IMMUNOGLOBULIN", String(1, "Latin1_General_CI_AS")),
    Column("COLD_ISCHAEMIC_TIME", DECIMAL(18, 0)),
    Column("PRIMARY_FUNCTION", String(1, "Latin1_General_CI_AS")),
    Column("ANTICOAGULATION", Integer),
    Column("CMV_PROPHYLAXIS", Integer),
    Column("PNEUMOCYSTIS_PROPHYLAXIS", Integer),
    Column("FUNCTIONING", String(1, "Latin1_General_CI_AS")),
    Column("OTHER_ORGAN_TX_1", Integer),
    Column("OTHER_ORGAN_TX_2", Integer),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_TREATMENT = Table(
    "AUDIT_TREATMENT",
    Base.metadata,
    Column("RR_NO", BigInteger),
    Column("DATE_START", DateTime),
    Column("DATE_END", DateTime),
    Column("TREATMENT_MODALITY", Unicode(8, "Latin1_General_CI_AS")),
    Column("ADD_HAEMO_ON_PD", Unicode(1, "Latin1_General_CI_AS")),
    Column("CHANGE_TREATMENT", Unicode(8, "Latin1_General_CI_AS")),
    Column("HAEMO_DIAL_ACCESS", Unicode(8, "Latin1_General_CI_AS")),
    Column("FGS_SITE", Unicode(8, "Latin1_General_CI_AS")),
    Column("HD_CATHETER_SITE", Unicode(8, "Latin1_General_CI_AS")),
    Column("DIALYSER_USED", Unicode(8, "Latin1_General_CI_AS")),
    Column("FLOW_RATE", Numeric(38, 4)),
    Column("DIAL_REUSE", Unicode(1, "Latin1_General_CI_AS")),
    Column("TIMES_PER_WEEK", Numeric(20, 0)),
    Column("DIAL_TIME", Numeric(38, 4)),
    Column("BICARB_DIAL", Unicode(1, "Latin1_General_CI_AS")),
    Column("TREATMENT_CENTRE", Unicode(8, "Latin1_General_CI_AS")),
    Column("HD_SUPERVISON", Unicode(4, "Latin1_General_CI_AS")),
    Column("WEEKLY_FLUID_VOL", Numeric(38, 4)),
    Column("BAG_SIZE", Numeric(38, 4)),
    Column("HOSP_CENTRE", Unicode(8, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("LOAD_IND", Unicode(1, "Latin1_General_CI_AS")),
    Column("DISPLAY_SEQ", Numeric(38, 4)),
    Column("YEAR_END_SEQ", Numeric(38, 4)),
    Column("TRANSFER_IN_FROM", Unicode(10, "Latin1_General_CI_AS")),
    Column("TRANSFER_OUT_TO", Unicode(10, "Latin1_General_CI_AS")),
)


t_AUDIT_TREATMENT_CHANGE_REASONS = Table(
    "AUDIT_TREATMENT_CHANGE_REASONS",
    Base.metadata,
    Column("CODE", Integer, nullable=False),
    Column("MODALITY_GROUP", String(4, "Latin1_General_CI_AS"), nullable=False),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_UKT_PATIENTS = Table(
    "AUDIT_UKT_PATIENTS",
    Base.metadata,
    Column("UKTSSA_NO", BigInteger, nullable=False),
    Column("SURNAME", Unicode(50, "Latin1_General_CI_AS")),
    Column("FORENAME", Unicode(50, "Latin1_General_CI_AS")),
    Column("SEX", Unicode(1, "Latin1_General_CI_AS")),
    Column("POST_CODE", Unicode(10, "Latin1_General_CI_AS")),
    Column("NEW_NHS_NO", BigInteger),
    Column("CHI_NO", BigInteger),
    Column("HSC_NO", BigInteger),
    Column("RR_NO", BigInteger),
    Column("UKT_DATE_DEATH", DateTime),
    Column("UKT_DATE_BIRTH", DateTime),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
    Column("SOUNDEX_FORENAME", String(5, "Latin1_General_CI_AS")),
    Column("SOUNDEX_SURNAME", String(5, "Latin1_General_CI_AS")),
)


t_AUDIT_UKT_SITES = Table(
    "AUDIT_UKT_SITES",
    Base.metadata,
    Column("SITE_NAME", Unicode(50, "Latin1_General_CI_AS"), nullable=False),
    Column("RR_CODE", Unicode(8, "Latin1_General_CI_AS"), nullable=False),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
)


t_AUDIT_UKT_TRANSPLANTS = Table(
    "AUDIT_UKT_TRANSPLANTS",
    Base.metadata,
    Column("UKTSSA_NO", BigInteger, nullable=False),
    Column("TRANSPLANT_ID", BigInteger),
    Column("TRANSPLANT_TYPE", Unicode(10, "Latin1_General_CI_AS")),
    Column("TRANSPLANT_ORGAN", Unicode(50, "Latin1_General_CI_AS")),
    Column("TRANSPLANT_UNIT", Unicode(50, "Latin1_General_CI_AS")),
    Column("RR_NO", BigInteger),
    Column("TRANSPLANT_DATE", DateTime),
    Column("UKT_FAIL_DATE", DateTime),
    Column("REGISTRATION_ID", Unicode(12, "Latin1_General_CI_AS"), nullable=False),
    Column("REGISTRATION_DATE", DateTime),
    Column("REGISTRATION_DATE_TYPE", Unicode(12, "Latin1_General_CI_AS")),
    Column("REGISTRATION_END_DATE", DateTime),
    Column("REGISTRATION_END_STATUS", Unicode(12, "Latin1_General_CI_AS")),
    Column("TRANSPLANT_CONSIDERATION", Unicode(20, "Latin1_General_CI_AS")),
    Column("TRANSPLANT_DIALYSIS", Unicode(12, "Latin1_General_CI_AS")),
    Column("TRANSPLANT_RELATIONSHIP", Unicode(20, "Latin1_General_CI_AS")),
    Column("TRANSPLANT_SEX", Unicode(12, "Latin1_General_CI_AS")),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
    Column("CAUSE_OF_FAILURE", String(10, "Latin1_General_CI_AS")),
    Column("CAUSE_OF_FAILURE_TEXT", String(500, "Latin1_General_CI_AS")),
    Column("CIT_MINS", String(10, "Latin1_General_CI_AS")),
    Column("HLA_MISMATCH", String(10, "Latin1_General_CI_AS")),
    Column("UKT_SUSPENSION", Boolean),
)


t_AUDIT_UPLOAD_LOG = Table(
    "AUDIT_UPLOAD_LOG",
    Base.metadata,
    Column("RUN_DATE", DateTime),
    Column("SITE", Unicode(10, "Latin1_General_CI_AS")),
    Column("TYPE", Unicode(10, "Latin1_General_CI_AS")),
    Column("FILENAME", Unicode(260, "Latin1_General_CI_AS")),
    Column("PAT_COUNT", BigInteger),
    Column("SQL_COUNT", BigInteger),
    Column("AUDIT_STATUS", Unicode(1, "Latin1_General_CI_AS")),
    Column("AUDIT_DATE", DateTime),
    Column("AUDIT_TIME", Unicode(8, "Latin1_General_CI_AS")),
    Column("USER_REF", Unicode(31, "Latin1_General_CI_AS")),
    Column("QRT_NO", Integer),
)


class CKD(Base):
    __tablename__ = "CKD"
    __table_args__ = (PrimaryKeyConstraint("RR_NO", "HOSP_CENTRE", name="PK_CKD"),)

    RR_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    HOSP_CENTRE: Mapped[str] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS"), primary_key=True
    )
    FIRST_TREAT_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    FIRST_TREAT_WEIGHT: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    FIRST_TREAT_CREATININE: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    PRIMARY_DISEASE_CODE: Mapped[Optional[str]] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS")
    )
    EDTA_DISEASE_CODE: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    SECONDARY_ESRF_1: Mapped[Optional[str]] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS")
    )
    SECONDARY_ESRF_2: Mapped[Optional[str]] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS")
    )
    SECONDARY_ESRF_3: Mapped[Optional[str]] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS")
    )
    PRIMARY_DISEASE_TEXT: Mapped[Optional[str]] = mapped_column(
        Unicode(70, "Latin1_General_CI_AS")
    )
    ANGINA: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    PREV_MI_LE3M: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    PREV_MI_GT3M: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    PREV_CAGB: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    SMOKER: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    COPD: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    SYMPT_CEREBRO_VASC: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    DIABETES_NON_ESRF: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    MALIGNANCY: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    LIVER_DISEASE: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    CLAUDICATION: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    ISCH_NEUROPATH_ULCERS: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    ANGIOPLASTY_NC: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    PVD_AMPUTATION: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    ANTENATAL_DIAG: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    ANTENATAL_TREAT: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    PRETERM: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    CEREBRAL_PALSY: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    DEVEL_EDUC_HANDICAP: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    CONGEN_HEART_DISEASE: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    OTHER_CONGEN_ABNORM: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    DOWNS_SYNDROME: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    OTHER_CHROMO_ABNORM: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    OTHER_SYNDROME: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    NEURAL_TUBE_DEFECT: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    DATE_CREAT_PRIOR_TO_ESRF: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime
    )
    CREAT_PRIOR_TO_ESRF: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    DATE_HB_PRIOR_TO_ESRF: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    HB_PRIOR_TO_ESRF: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    ACCESS_USED_AT_FIRST_DIALYSIS: Mapped[Optional[str]] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS")
    )
    EPISODE_OF_HEART_FAILURE: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    EDTA_NEW_DISEASE_CODE: Mapped[Optional[str]] = mapped_column(
        Unicode(20, "Latin1_General_CI_AS")
    )
    EDTA_NEW_DISEASE_CODE_CONV: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    CKD5_REACHED_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    SECONDARY_DISEASE_CODE: Mapped[Optional[str]] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS")
    )
    FIRST_REPLACEMENT_MODALITY: Mapped[Optional[str]] = mapped_column(
        Unicode(4, "Latin1_General_CI_AS")
    )
    BMI_AT_START_OF_RRT: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    ACCESS_AT_3_MONTHS: Mapped[Optional[str]] = mapped_column(
        Unicode(5, "Latin1_General_CI_AS")
    )
    FIRST_TREATMENT_CENTRE: Mapped[Optional[str]] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS")
    )
    TRANSPLANT_SUITABILITY: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    CONNECTION_DECISION_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime
    )
    FIRST_HEIGHT: Mapped[Optional[float]] = mapped_column(Float(53))
    ON_RRT: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    REASON_NO_RRT: Mapped[Optional[str]] = mapped_column(
        Unicode(150, "Latin1_General_CI_AS")
    )
    PRESUMED_INHERITENCE: Mapped[Optional[int]] = mapped_column(Integer)
    GENETIC_DISEASE: Mapped[Optional[int]] = mapped_column(Integer)
    GENETIC_DISEASE_DETAILS: Mapped[Optional[str]] = mapped_column(
        Unicode(150, "Latin1_General_CI_AS")
    )
    OTHER_CONGENITAL_DETAILS: Mapped[Optional[str]] = mapped_column(
        Unicode(150, "Latin1_General_CI_AS")
    )
    OTHER_ORGAN_TRANSPLANT_1: Mapped[Optional[str]] = mapped_column(
        Unicode(20, "Latin1_General_CI_AS")
    )
    OTHER_ORGAN_TRANSPLANT_2: Mapped[Optional[str]] = mapped_column(
        Unicode(20, "Latin1_General_CI_AS")
    )
    OTHER_ORGAN_TRANSPLANT_3: Mapped[Optional[str]] = mapped_column(
        Unicode(20, "Latin1_General_CI_AS")
    )
    FIRST_MALIGNANCY_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(
        DATETIME2
    )
    OTHER_FAMILY_ERF: Mapped[Optional[int]] = mapped_column(Integer)
    CKD_EGFR_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    CKD_EGFR: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    CKD_EGFR_CREATININE: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )


class CMVANTIBODY(Base):
    __tablename__ = "CMV_ANTIBODY"
    __table_args__ = (
        PrimaryKeyConstraint("RR_NO", "CMV_ANTIBODY_DATE", name="PK_CMV_ANTIBODY"),
    )

    RR_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    CMV_ANTIBODY_DATE: Mapped[datetime.datetime] = mapped_column(
        DateTime, primary_key=True
    )
    CMV_ANTIBODY_STATUS: Mapped[Optional[str]] = mapped_column(
        Unicode(5, "Latin1_General_CI_AS")
    )


class CMVANTIGENAEMIA(Base):
    __tablename__ = "CMV_ANTIGENAEMIA"
    __table_args__ = (
        PrimaryKeyConstraint(
            "RR_NO", "CMV_ANTIGENAEMIA_DATE", name="PK_CMV_ANTIGENAEMIA"
        ),
    )

    RR_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    CMV_ANTIGENAEMIA_DATE: Mapped[datetime.datetime] = mapped_column(
        DateTime, primary_key=True
    )
    CMV_ANTIGENAEMIA: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 0))


class CMVPCR(Base):
    __tablename__ = "CMV_PCR"
    __table_args__ = (PrimaryKeyConstraint("RR_NO", "CMV_PCR_DATE", name="PK_CMV_PCR"),)

    RR_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    CMV_PCR_DATE: Mapped[datetime.datetime] = mapped_column(DateTime, primary_key=True)
    CMV_PCR: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 0))


class COMORBIDITY(Base):
    __tablename__ = "COMORBIDITY"
    __table_args__ = (
        PrimaryKeyConstraint("RR_NO", "HOSP_CENTRE", name="PK_COMORBIDITY_1"),
    )

    RR_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    HOSP_CENTRE: Mapped[str] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS"), primary_key=True
    )
    CABG: Mapped[Optional[str]] = mapped_column(String(1, "Latin1_General_CI_AS"))
    HEART_FAILURE: Mapped[Optional[str]] = mapped_column(
        String(1, "Latin1_General_CI_AS")
    )
    COPD: Mapped[Optional[str]] = mapped_column(String(1, "Latin1_General_CI_AS"))
    LIVER_DISEASE: Mapped[Optional[str]] = mapped_column(
        String(1, "Latin1_General_CI_AS")
    )
    CLAUDICATION: Mapped[Optional[str]] = mapped_column(
        String(1, "Latin1_General_CI_AS")
    )
    IN_ULCERS: Mapped[Optional[str]] = mapped_column(String(1, "Latin1_General_CI_AS"))
    STENT: Mapped[Optional[str]] = mapped_column(String(1, "Latin1_General_CI_AS"))
    AMPUTATION_FOR_PVD: Mapped[Optional[str]] = mapped_column(
        String(1, "Latin1_General_CI_AS")
    )
    DIABETES: Mapped[Optional[str]] = mapped_column(Unicode(10, "Latin1_General_CI_AS"))
    DIABETES_DIAGNOSED_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(
        DATETIME2
    )
    HEART_DISEASE: Mapped[Optional[str]] = mapped_column(
        String(1, "Latin1_General_CI_AS")
    )
    ST_SEGMENT_ELEVATION_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(
        DATETIME2
    )
    NON_ST_SEG_ELEVATION_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(
        DATETIME2
    )
    ANGINA_DIAGNOSED_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(
        DATETIME2
    )
    CABG_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DATETIME2)
    HEART_FAILURE_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DATETIME2)
    ATRIAL_FIBRILLATION_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(
        DATETIME2
    )
    MALIGNANCY: Mapped[Optional[str]] = mapped_column(String(1, "Latin1_General_CI_AS"))
    MALIGNANCY_SITE: Mapped[Optional[int]] = mapped_column(SmallInteger)
    MALIGNANCY_DIAGNOSED_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(
        DATETIME2
    )
    CEREBROVASCULAR_DISEASE: Mapped[Optional[str]] = mapped_column(
        String(1, "Latin1_General_CI_AS")
    )
    TIA_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DATETIME2)
    CVE_STROKE_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DATETIME2)
    SMOKING: Mapped[Optional[str]] = mapped_column(Unicode(20, "Latin1_General_CI_AS"))
    COPD_DIAGNOSED_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DATETIME2)
    LIVER_DISEASE_DIAGNOSED_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(
        DATETIME2
    )
    PVD_DIAGNOSED_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DATETIME2)
    CLAUDICATION_DIAGNOSED_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(
        DATETIME2
    )
    ULCERS_DIAGNOSED_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(
        DATETIME2
    )
    STENT_DIAGNOSED_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DATETIME2)
    PVD_AMPUTATION_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DATETIME2)
    DEMENTIA_DIAGNOSED_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(
        DATETIME2
    )
    PVD: Mapped[Optional[str]] = mapped_column(String(1, "Latin1_General_CI_AS"))
    DEMENTIA: Mapped[Optional[str]] = mapped_column(String(1, "Latin1_General_CI_AS"))
    ATRIAL_FIBRILLATION: Mapped[Optional[str]] = mapped_column(
        String(1, "Latin1_General_CI_AS")
    )


class CONSTRAINTTABLE(Base):
    __tablename__ = "CONSTRAINT_TABLE"
    __table_args__ = (PrimaryKeyConstraint("FIELD_NAME", name="PK_CONSTRAINT_TABLE"),)

    FIELD_NAME: Mapped[str] = mapped_column(
        Unicode(30, "Latin1_General_CI_AS"), primary_key=True
    )
    FIELD_ID: Mapped[Optional[str]] = mapped_column(Unicode(5, "Latin1_General_CI_AS"))
    LOWER_LIMIT: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    UPPER_LIMIT: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    LOWER_WARN: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    UPPER_WARN: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))


t_DATA_ITEM_SUBMISSION = Table(
    "DATA_ITEM_SUBMISSION",
    Base.metadata,
    Column("HOSP_CENTRE", Unicode(8, "Latin1_General_CI_AS")),
    Column("QUARTER", BigInteger),
    Column("DATA_ITEM", Unicode(30, "Latin1_General_CI_AS")),
)


class DELETEDPATIENTS(Base):
    __tablename__ = "DELETED_PATIENTS"
    __table_args__ = (
        PrimaryKeyConstraint("RR_NO", name="PK_DELETED_PATIENTS"),
        Index("_dta_index_DELETED_PATIENTS_7_1184827383__K1", "RR_NO"),
        Index(
            "_dta_index_DELETED_PATIENTS_7_1184827383__K16_K5_K9_K6_K14_K19_K1_K56_K55_3_4",
            "NEW_NHS_NO",
            "DATE_BIRTH",
            "HOSP_CENTRE",
            "LOCAL_HOSP_NO",
            "CHI_NO",
            "SCOT_REG_NO",
            "RR_NO",
            "SOUNDEX_SURNAME",
            "SOUNDEX_FORENAME",
        ),
        Index(
            "_dta_index_DELETED_PATIENTS_7_1184827383__K1_K5_K16_K9_K6_K55_K56_K52_K19_K48_K13_K14",
            "RR_NO",
            "DATE_BIRTH",
            "NEW_NHS_NO",
            "HOSP_CENTRE",
            "LOCAL_HOSP_NO",
            "SOUNDEX_FORENAME",
            "SOUNDEX_SURNAME",
            "DUPLICATE_RR_NO",
            "SCOT_REG_NO",
            "TRACING_NHS_NO",
            "UKTSSA_NO",
            "CHI_NO",
        ),
        Index(
            "_dta_index_DELETED_PATIENTS_7_1184827383__K52_K9_K6_K13_K14_K16_K48_K19_K1_K56_K55_K5",
            "DUPLICATE_RR_NO",
            "HOSP_CENTRE",
            "LOCAL_HOSP_NO",
            "UKTSSA_NO",
            "CHI_NO",
            "NEW_NHS_NO",
            "TRACING_NHS_NO",
            "SCOT_REG_NO",
            "RR_NO",
            "SOUNDEX_SURNAME",
            "SOUNDEX_FORENAME",
            "DATE_BIRTH",
        ),
    )

    RR_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    SURNAME: Mapped[str] = mapped_column(Unicode(50, "Latin1_General_CI_AS"))
    FORENAME: Mapped[str] = mapped_column(Unicode(50, "Latin1_General_CI_AS"))
    DATE_BIRTH: Mapped[datetime.datetime] = mapped_column(DateTime)
    LOCAL_HOSP_NO: Mapped[str] = mapped_column(Unicode(15, "Latin1_General_CI_AS"))
    HOSP_CENTRE: Mapped[str] = mapped_column(Unicode(8, "Latin1_General_CI_AS"))
    SURNAME_SOUNDEX: Mapped[Optional[str]] = mapped_column(
        Unicode(4, "Latin1_General_CI_AS")
    )
    DATE_REGISTERED: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    SEX: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    MIN_DATA_IND: Mapped[Optional[str]] = mapped_column(
        Unicode(2, "Latin1_General_CI_AS")
    )
    ESRF_IND: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    PAEDIATRIC_IND: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    UKTSSA_NO: Mapped[Optional[int]] = mapped_column(BigInteger)
    CHI_NO: Mapped[Optional[int]] = mapped_column(BigInteger)
    SUPER_CHI_NO: Mapped[Optional[str]] = mapped_column(
        Unicode(15, "Latin1_General_CI_AS")
    )
    NEW_NHS_NO: Mapped[Optional[int]] = mapped_column(BigInteger)
    OLD_NHS_NO: Mapped[Optional[str]] = mapped_column(
        Unicode(15, "Latin1_General_CI_AS")
    )
    MRC_NO: Mapped[Optional[str]] = mapped_column(Unicode(10, "Latin1_General_CI_AS"))
    SCOT_REG_NO: Mapped[Optional[str]] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS")
    )
    MARITAL_STATUS: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    ETHGR_CODE: Mapped[Optional[str]] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS")
    )
    ADULT_HEIGHT: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    FIRST_SEEN_HEIGHT: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    FIRST_SEEN_WEIGHT: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    FIRST_SEEN_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    FIRST_SEEN_CREATININE: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    DATE_DEATH: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    COD_READ: Mapped[Optional[str]] = mapped_column(Unicode(8, "Latin1_General_CI_AS"))
    COD_EDTA1: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    COD_EDTA2: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    COD_TEXT: Mapped[Optional[str]] = mapped_column(Unicode(70, "Latin1_General_CI_AS"))
    TRANSFER_IND: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    TRANSFER_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    CENTRE_PRI: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    GP_POSTCODE: Mapped[Optional[str]] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS")
    )
    DATE_STAT: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    BLOOD_GROUP: Mapped[Optional[str]] = mapped_column(
        Unicode(2, "Latin1_General_CI_AS")
    )
    BLOOD_GROUP_RHESUS: Mapped[Optional[str]] = mapped_column(
        Unicode(3, "Latin1_General_CI_AS")
    )
    OPT_OUT_FLAG: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    YEAR_OF_BIRTH: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    UNIQUE_IDENTIFIER: Mapped[Optional[str]] = mapped_column(
        Unicode(20, "Latin1_General_CI_AS")
    )
    TRACING_DATE_DEATH: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    TRACING_DATE_BIRTH: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    DOMINANT_ARM: Mapped[Optional[str]] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS")
    )
    REFERRAL_CODE: Mapped[Optional[str]] = mapped_column(
        Unicode(20, "Latin1_General_CI_AS")
    )
    REFERRAL_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    REFERRING_GP_CODE: Mapped[Optional[str]] = mapped_column(
        Unicode(20, "Latin1_General_CI_AS")
    )
    TRACING_NHS_NO: Mapped[Optional[int]] = mapped_column(BigInteger)
    AUDIT_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    AUDIT_TIME: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(8, 0))
    DESCRIPTION: Mapped[Optional[str]] = mapped_column(
        Unicode(1000, "Latin1_General_CI_AS")
    )
    DUPLICATE_RR_NO: Mapped[Optional[int]] = mapped_column(BigInteger)
    USERNAME: Mapped[Optional[str]] = mapped_column(Unicode(20, "Latin1_General_CI_AS"))
    AUTHORISED_BY: Mapped[Optional[str]] = mapped_column(
        Unicode(20, "Latin1_General_CI_AS")
    )
    SOUNDEX_FORENAME: Mapped[Optional[str]] = mapped_column(
        String(5, "Latin1_General_CI_AS"),
        Computed("(soundex([dbo].[normalise_forename2]([FORENAME])))", persisted=True),
    )
    SOUNDEX_SURNAME: Mapped[Optional[str]] = mapped_column(
        String(5, "Latin1_General_CI_AS"),
        Computed("(soundex([dbo].[normalise_surname2]([SURNAME])))", persisted=True),
    )
    HSC_NO: Mapped[Optional[int]] = mapped_column(BigInteger)
    ALIAS_NAME: Mapped[Optional[str]] = mapped_column(
        Unicode(50, "Latin1_General_CI_AS")
    )
    BAPN_NO: Mapped[Optional[str]] = mapped_column(Unicode(20, "Latin1_General_CI_AS"))
    BIRTH_NAME: Mapped[Optional[str]] = mapped_column(
        Unicode(50, "Latin1_General_CI_AS")
    )
    CKD5_GE_90: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    CKD5_START: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    DATE_CKD5_GE_90: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    DATE_CKD5_START: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    DATE_LAST_TRACED: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    GP_CODE: Mapped[Optional[str]] = mapped_column(Unicode(10, "Latin1_General_CI_AS"))
    REFERRING_GP_PRACTICE_CODE: Mapped[Optional[str]] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS")
    )
    RPV_FLAG: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    RR_DATE_FIRST_AKI: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    RR_DATE_FIRST_CKD4: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    RR_DATE_FIRST_CKD5: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    RR_DATE_FIRST_CONS: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    RR_DATE_FIRST_ESRF: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    UKT_UKTSSA_NO: Mapped[Optional[int]] = mapped_column(BigInteger)
    TRACING_RESPONSE: Mapped[Optional[str]] = mapped_column(
        Unicode(2, "Latin1_General_CI_AS")
    )
    RR_DATE_FIRST_CKD1: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    RR_DATE_FIRST_CKD2: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    RR_DATE_FIRST_CKD3: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


class DIALYSISACCESSDETAIL(Base):
    __tablename__ = "DIALYSIS_ACCESS_DETAIL"
    __table_args__ = (
        PrimaryKeyConstraint(
            "RR_NO",
            "HOSP_CENTRE",
            "ACCESS_DATE",
            "ACCESS_TYPE",
            "ANATOMICAL_SIDE",
            "VASCULAR_SITE_ACCESS",
            name="PK_DIALYSIS_ACCESS_DETAILS",
        ),
    )

    RR_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    HOSP_CENTRE: Mapped[str] = mapped_column(
        String(20, "Latin1_General_CI_AS"), primary_key=True
    )
    ACCESS_DATE: Mapped[datetime.datetime] = mapped_column(DateTime, primary_key=True)
    ACCESS_TYPE: Mapped[str] = mapped_column(
        String(3, "Latin1_General_CI_AS"), primary_key=True
    )
    ANATOMICAL_SIDE: Mapped[str] = mapped_column(
        String(1, "Latin1_General_CI_AS"), primary_key=True
    )
    VASCULAR_SITE_ACCESS: Mapped[str] = mapped_column(
        String(2, "Latin1_General_CI_AS"), primary_key=True
    )
    FIRST_ACCESS_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    ACCESS_FAILURE_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    REMOVAL_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    HD_REMOVAL_REASON: Mapped[Optional[int]] = mapped_column(Integer)
    PD_INSERTION_TECHNIQUE: Mapped[Optional[int]] = mapped_column(Integer)
    PD_REMOVAL_REASON: Mapped[Optional[int]] = mapped_column(Integer)


class DIALYSISACCESSEVENT(Base):
    __tablename__ = "DIALYSIS_ACCESS_EVENT"
    __table_args__ = (
        PrimaryKeyConstraint(
            "RR_NO",
            "ACCESS_DATE",
            "ACCESS_TYPE",
            "LOCATION",
            "COMPLICATION_DATE",
            "HD_COMPLICATION",
            "HOSP_CENTRE",
            name="PK_DIALYSIS_ACCESS_EVENT",
        ),
    )

    RR_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    ACCESS_DATE: Mapped[datetime.datetime] = mapped_column(DateTime, primary_key=True)
    ACCESS_TYPE: Mapped[str] = mapped_column(
        String(5, "Latin1_General_CI_AS"), primary_key=True
    )
    LOCATION: Mapped[str] = mapped_column(
        String(5, "Latin1_General_CI_AS"), primary_key=True
    )
    COMPLICATION_DATE: Mapped[datetime.datetime] = mapped_column(
        DateTime, primary_key=True
    )
    HD_COMPLICATION: Mapped[int] = mapped_column(Integer, primary_key=True)
    HOSP_CENTRE: Mapped[str] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS"), primary_key=True
    )
    TENCKHOFF_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    PD_COMPLICATION: Mapped[Optional[int]] = mapped_column(Integer)
    PERITONITIS_ORGANISM_1: Mapped[Optional[int]] = mapped_column(Integer)
    PERITONITIS_ORGANISM_2: Mapped[Optional[int]] = mapped_column(Integer)
    PERITONITIS_ORGANISM_3: Mapped[Optional[int]] = mapped_column(Integer)
    SWITCH_FROM_PD_REASON: Mapped[Optional[int]] = mapped_column(Integer)
    SWITCH_FROM_PD_REASON_2: Mapped[Optional[int]] = mapped_column(Integer)
    SWITCH_FROM_PD_REASON_3: Mapped[Optional[int]] = mapped_column(Integer)


class EPODOSAGE(Base):
    __tablename__ = "EPO_DOSAGE"
    __table_args__ = (
        PrimaryKeyConstraint(
            "RR_NO", "DATE_START", "HOSP_CENTRE", name="PK_EPO_DOSAGE_1"
        ),
    )

    RR_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    DATE_START: Mapped[datetime.datetime] = mapped_column(DateTime, primary_key=True)
    HOSP_CENTRE: Mapped[str] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS"), primary_key=True
    )
    DATE_END: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    UNITS_TRANSFUSED: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    PARENTERAL_IRON: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    EPO_DRUG_NAME: Mapped[Optional[str]] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS")
    )
    EPO_DOSAGE: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    EPO_WEEKLY_DOSAGE: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    EPO_ADMIN_ROUTE: Mapped[Optional[str]] = mapped_column(
        Unicode(20, "Latin1_General_CI_AS")
    )
    EPO_FREQUENCY: Mapped[Optional[str]] = mapped_column(
        Unicode(20, "Latin1_General_CI_AS")
    )
    EPO_WEEKLY_RAW: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))


class ESRF(Base):
    __tablename__ = "ESRF"
    __table_args__ = (
        PrimaryKeyConstraint("RR_NO", "HOSP_CENTRE", name="PK_ESRF"),
        Index("_dta_index_ESRF_7_1975782196__K1_2", "RR_NO"),
    )

    RR_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    HOSP_CENTRE: Mapped[str] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS"), primary_key=True
    )
    FIRST_TREAT_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    FIRST_TREAT_WEIGHT: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    FIRST_TREAT_CREATININE: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    PRIMARY_DISEASE_CODE: Mapped[Optional[str]] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS")
    )
    EDTA_DISEASE_CODE: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    SECONDARY_ESRF_1: Mapped[Optional[str]] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS")
    )
    SECONDARY_ESRF_2: Mapped[Optional[str]] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS")
    )
    SECONDARY_ESRF_3: Mapped[Optional[str]] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS")
    )
    PRIMARY_DISEASE_TEXT: Mapped[Optional[str]] = mapped_column(
        Unicode(70, "Latin1_General_CI_AS")
    )
    ANGINA: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    PREV_MI_LE3M: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    PREV_MI_GT3M: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    PREV_CAGB: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    SMOKER: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    COPD: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    SYMPT_CEREBRO_VASC: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    DIABETES_NON_ESRF: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    MALIGNANCY: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    LIVER_DISEASE: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    CLAUDICATION: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    ISCH_NEUROPATH_ULCERS: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    ANGIOPLASTY_NC: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    PVD_AMPUTATION: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    ANTENATAL_DIAG: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    ANTENATAL_TREAT: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    PRETERM: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    CEREBRAL_PALSY: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    DEVEL_EDUC_HANDICAP: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    CONGEN_HEART_DISEASE: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    OTHER_CONGEN_ABNORM: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    DOWNS_SYNDROME: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    OTHER_CHROMO_ABNORM: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    OTHER_SYNDROME: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    NEURAL_TUBE_DEFECT: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    DATE_CREAT_PRIOR_TO_ESRF: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime
    )
    CREAT_PRIOR_TO_ESRF: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    DATE_HB_PRIOR_TO_ESRF: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    HB_PRIOR_TO_ESRF: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    ACCESS_USED_AT_FIRST_DIALYSIS: Mapped[Optional[str]] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS")
    )
    EPISODE_OF_HEART_FAILURE: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    EDTA_NEW_DISEASE_CODE_CONV: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    EDTA_NEW_DISEASE_CODE: Mapped[Optional[str]] = mapped_column(
        Unicode(20, "Latin1_General_CI_AS")
    )
    CKD5_REACHED_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    SECONDARY_DISEASE_CODE: Mapped[Optional[str]] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS")
    )
    FIRST_REPLACEMENT_MODALITY: Mapped[Optional[str]] = mapped_column(
        Unicode(4, "Latin1_General_CI_AS")
    )
    BMI_AT_START_OF_RRT: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    ACCESS_AT_3_MONTHS: Mapped[Optional[str]] = mapped_column(
        Unicode(5, "Latin1_General_CI_AS")
    )
    FIRST_TREATMENT_CENTRE: Mapped[Optional[str]] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS")
    )
    TRANSPLANT_SUITABILITY: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    CONNECTION_DECISION_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime
    )
    FIRST_HEIGHT: Mapped[Optional[float]] = mapped_column(Float(53))
    ON_RRT: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    REASON_NO_RRT: Mapped[Optional[str]] = mapped_column(
        Unicode(150, "Latin1_General_CI_AS")
    )
    PRESUMED_INHERITENCE: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    GENETIC_DISEASE: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    GENETIC_DISEASE_DETAILS: Mapped[Optional[str]] = mapped_column(
        Unicode(150, "Latin1_General_CI_AS")
    )
    OTHER_CONGENITAL_DETAILS: Mapped[Optional[str]] = mapped_column(
        Unicode(150, "Latin1_General_CI_AS")
    )
    OTHER_ORGAN_TRANSPLANT_1: Mapped[Optional[str]] = mapped_column(
        Unicode(20, "Latin1_General_CI_AS")
    )
    OTHER_ORGAN_TRANSPLANT_2: Mapped[Optional[str]] = mapped_column(
        Unicode(20, "Latin1_General_CI_AS")
    )
    OTHER_ORGAN_TRANSPLANT_3: Mapped[Optional[str]] = mapped_column(
        Unicode(20, "Latin1_General_CI_AS")
    )
    FIRST_MALIGNANCY_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(
        DATETIME2
    )
    OTHER_FAMILY_ERF: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    CKD_EGFR_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    CKD_EGFR: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    CKD_EGFR_CREATININE: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )


class EXTERNALCOMM(Base):
    __tablename__ = "EXTERNAL_COMM"
    __table_args__ = (PrimaryKeyConstraint("RR_NO", name="PK_EXTERNAL_COMM"),)

    RR_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    UKTSSA_DATA: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    EDTA_DATA: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))


class FOLLOWUP(Base):
    __tablename__ = "FOLLOW_UP"
    __table_args__ = (
        PrimaryKeyConstraint(
            "RR_NO", "TRANSPLANT_NO", "DATE_FILE", name="PK_FOLLOW_UP"
        ),
    )

    RR_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    DATE_FILE: Mapped[datetime.datetime] = mapped_column(DateTime, primary_key=True)
    TRANSPLANT_NO: Mapped[decimal.Decimal] = mapped_column(
        Numeric(20, 0), primary_key=True
    )
    CLINICAL_ASSESS: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    DATE_LAST_ASSESS: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    CREATININE: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    DATE_CREATININE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    AZATHIOPRINE_PROPHLAXIS: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    AZATHIOPRINE_ACUTE_REJECT: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    CYCLOSPORIN_PROPHLAXIS: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    CYCLOSPORIN_ACUTE_REJECT: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    STEROID_PROPHLAXIS: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    STEROID_ACUTE_REJECT: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    OKT3_PROPHLAXIS: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    OKT3_ACUTE_REJECT: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    ATG_PROPHLAXIS: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    ATG_ACUTE_REJECT: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    ALG_PROPHLAXIS: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    ALG_ACUTE_REJECT: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    TACROLIMUS_PROPHLAXIS: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    TACROLIMUS_ACUTE_REJECT: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    RS61443_PROPHLAXIS: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    RS61443_ACUTE_REJECT: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    OTHER_PROPHLAXIS: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    OTHER_ACUTE_REJECT: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    DATE_LAST_IMMSUP: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    REDIR_ADDRESS_1: Mapped[Optional[str]] = mapped_column(
        Unicode(40, "Latin1_General_CI_AS")
    )
    REDIR_ADDRESS_2: Mapped[Optional[str]] = mapped_column(
        Unicode(40, "Latin1_General_CI_AS")
    )
    REDIR_TOWN: Mapped[Optional[str]] = mapped_column(
        Unicode(40, "Latin1_General_CI_AS")
    )
    REDIR_POST_CODE: Mapped[Optional[str]] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS")
    )
    ORGAN_TRANSPLANT: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    TRANSPLANT_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    TRANSPLANT_FAILURE: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    DATE_FAILURE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    CAUSE_FAILURE: Mapped[Optional[str]] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS")
    )
    FAILURE_TEXT: Mapped[Optional[str]] = mapped_column(
        Unicode(70, "Latin1_General_CI_AS")
    )
    DATE_END_DIAL: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    DATE_RETURN_DIAL: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    DATE_GRAFT_NEPHRECTOMY: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime
    )
    IMM_SUP_SIROLIMUS: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )


class GPADDRESS(Base):
    __tablename__ = "GP_ADDRESS"
    __table_args__ = (
        PrimaryKeyConstraint(
            "RR_NO", "CENTRE_CODE", "DATE_START", name="PK_GP_ADDRESS"
        ),
    )

    CENTRE_CODE: Mapped[str] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS"), primary_key=True
    )
    RR_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    DATE_START: Mapped[datetime.datetime] = mapped_column(DateTime, primary_key=True)
    DATE_END: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    ADDRESS_1: Mapped[Optional[str]] = mapped_column(
        Unicode(60, "Latin1_General_CI_AS")
    )
    ADDRESS_2: Mapped[Optional[str]] = mapped_column(
        Unicode(60, "Latin1_General_CI_AS")
    )
    ADDRESS_3: Mapped[Optional[str]] = mapped_column(
        Unicode(60, "Latin1_General_CI_AS")
    )
    ADDRESS_4: Mapped[Optional[str]] = mapped_column(
        Unicode(60, "Latin1_General_CI_AS")
    )
    POST_CODE: Mapped[Optional[str]] = mapped_column(Unicode(8, "Latin1_General_CI_AS"))
    CENTRE_PRI: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    NHS_CODE: Mapped[Optional[str]] = mapped_column(Unicode(3, "Latin1_General_CI_AS"))
    NHS_NAME: Mapped[Optional[str]] = mapped_column(Unicode(60, "Latin1_General_CI_AS"))


class HAEMODIALYSISPRESCRIPTION(Base):
    __tablename__ = "HAEMODIALYSIS_PRESCRIPTION"
    __table_args__ = (
        PrimaryKeyConstraint(
            "RR_NO",
            "HOSP_CENTRE",
            "DIALYSIS_PRESC_DATE",
            "TIMES_PER_WEEK",
            "TIME_DIALYSED",
            name="PK_HAEMODIALYSIS_PRESCRIPTION",
        ),
    )

    RR_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    HOSP_CENTRE: Mapped[str] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS"), primary_key=True
    )
    DIALYSIS_PRESC_DATE: Mapped[datetime.datetime] = mapped_column(
        DateTime, primary_key=True
    )
    TIMES_PER_WEEK: Mapped[int] = mapped_column(Integer, primary_key=True)
    TIME_DIALYSED: Mapped[int] = mapped_column(Integer, primary_key=True)
    BLOOD_FLOW_RATE: Mapped[Optional[int]] = mapped_column(Integer)
    SODIUM_IN_DIALYSATE: Mapped[Optional[int]] = mapped_column(Integer)


class HAEMODIALYSISSESSION(Base):
    __tablename__ = "HAEMODIALYSIS_SESSION"
    __table_args__ = (
        PrimaryKeyConstraint(
            "RR_NO", "HD_SESSION_DATE", "SESSION_TYPE", name="PK_HAEMODIALYSIS_SESSION"
        ),
    )

    RR_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    HD_SESSION_DATE: Mapped[datetime.datetime] = mapped_column(
        DateTime, primary_key=True
    )
    SESSION_TYPE: Mapped[str] = mapped_column(
        NCHAR(10, "Latin1_General_CI_AS"),
        primary_key=True,
        server_default=text("('HD')"),
    )
    START_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    END_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    PRE_HD_WEIGHT: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    PRE_HD_SYSTOLIC_BP: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    PRE_HD_DIASTOLIC_BP: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    POST_HD_WEIGHT: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    POST_HD_SYSTOLIC_BP: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    POST_HD_DIASTOLIC_BP: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    SYMPTOMATIC_HYPOTENSION: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    VASCULAR_ACCESS: Mapped[Optional[str]] = mapped_column(
        Unicode(3, "Latin1_General_CI_AS")
    )
    VASCULAR_ACCESS_SITE: Mapped[Optional[str]] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS")
    )
    SESSION_START_TIME: Mapped[Optional[str]] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS"), server_default=text("(NULL)")
    )
    COUNTER: Mapped[Optional[int]] = mapped_column(Integer)
    ACCESS_IN_TWO_SITES: Mapped[Optional[str]] = mapped_column(
        NCHAR(1, "Latin1_General_CI_AS")
    )
    BLOOD_FLOW_RATE: Mapped[Optional[int]] = mapped_column(Integer)
    TIME_DIALYSED: Mapped[Optional[int]] = mapped_column(Integer)
    HOSP_CENTRE: Mapped[Optional[str]] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS")
    )
    NEEDLING_METHOD: Mapped[Optional[str]] = mapped_column(
        String(1, "Latin1_General_CI_AS")
    )
    DIALYSATE_SODIUM: Mapped[Optional[int]] = mapped_column(Integer)


class HBVANTIBODY(Base):
    __tablename__ = "HBV_ANTIBODY"
    __table_args__ = (
        PrimaryKeyConstraint("RR_NO", "HBV_ANTIBODY_DATE", name="PK_HBV_ANTIBODY"),
    )

    RR_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    HBV_ANTIBODY_DATE: Mapped[datetime.datetime] = mapped_column(
        DateTime, primary_key=True
    )
    HBV_ANTIBODY_STATUS: Mapped[Optional[str]] = mapped_column(
        Unicode(5, "Latin1_General_CI_AS")
    )


class HBVSANTIGEN(Base):
    __tablename__ = "HBV_S_ANTIGEN"
    __table_args__ = (
        PrimaryKeyConstraint("RR_NO", "HBV_S_ANTIGEN_DATE", name="PK_HBV_S_ANTIGEN"),
    )

    RR_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    HBV_S_ANTIGEN_DATE: Mapped[datetime.datetime] = mapped_column(
        DateTime, primary_key=True
    )
    HBV_S_ANTIGEN_STATUS: Mapped[Optional[str]] = mapped_column(
        Unicode(5, "Latin1_General_CI_AS")
    )


class HCVANTIBODY(Base):
    __tablename__ = "HCV_ANTIBODY"
    __table_args__ = (
        PrimaryKeyConstraint("RR_NO", "HCV_ANTIBODY_DATE", name="PK_HCV_ANTIBODY"),
    )

    RR_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    HCV_ANTIBODY_DATE: Mapped[datetime.datetime] = mapped_column(
        DateTime, primary_key=True
    )
    HCV_ANTIBODY_STATUS: Mapped[Optional[str]] = mapped_column(
        Unicode(5, "Latin1_General_CI_AS")
    )


class HIVANTIGEN(Base):
    __tablename__ = "HIV_ANTIGEN"
    __table_args__ = (
        PrimaryKeyConstraint("RR_NO", "HIV_ANTIGEN_DATE", name="PK_HIV_ANTIGEN"),
    )

    RR_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    HIV_ANTIGEN_DATE: Mapped[datetime.datetime] = mapped_column(
        DateTime, primary_key=True
    )
    HIV_ANTIGEN: Mapped[Optional[str]] = mapped_column(
        Unicode(5, "Latin1_General_CI_AS")
    )


class KTV(Base):
    __tablename__ = "KTV"
    __table_args__ = (
        PrimaryKeyConstraint("RR_NO", "DATE_START", "HOSP_CENTRE", name="PK_KTV"),
    )

    RR_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    DATE_START: Mapped[datetime.datetime] = mapped_column(DateTime, primary_key=True)
    HOSP_CENTRE: Mapped[str] = mapped_column(
        String(20, "Latin1_General_CI_AS"), primary_key=True
    )
    DATE_END: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    PRE_DIAL_UREA: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    POST_DIAL_UREA: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    PRE_DIAL_WEIGHT: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    POST_DIAL_WEIGHT: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    BLOOD_FLOW_RATE: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    DIAL_FLOW_RATE: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    DIAL_MAKE: Mapped[Optional[str]] = mapped_column(
        Unicode(100, "Latin1_General_CI_AS")
    )
    DIAL_TIME: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    RESIDUAL_RENAL_CLEAR: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(20, 0)
    )
    PRE_POST_IND_FOR_WT: Mapped[Optional[str]] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS")
    )
    WEIGHT_FOR_PD_CALC: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    DIALYSATE_UREA: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    URINE_UREA: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    BLOOD_UREA: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    DIALYSATE_KTV: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    URINE_KTV: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    DIALYSATE_EFFLUENT_VOL: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    URINE_VOLUME: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    COMBINED_KTV: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    URINE_IND: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    NORMALISED_PROTEIN_CATABOLIC: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    PROTEIN_LOSS_24_HOUR: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    DIALYSATE_CREATININE: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    URINE_CREATININE: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    SERUM_CREATININE: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    WEEKLY_NORMALISED_CREAT: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    CREAT_DIALYSATE_PLASMA_RATIO: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    DIALYSATE_GLUCOSE: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))


class LOCATIONS(Base):
    __tablename__ = "LOCATIONS"
    __table_args__ = (
        PrimaryKeyConstraint("CENTRE_CODE", name="PK__LOCATION__6E8232E9B58FCEF5"),
    )

    CENTRE_CODE: Mapped[str] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS"), primary_key=True
    )
    CENTRE_NAME: Mapped[str] = mapped_column(Unicode(255, "Latin1_General_CI_AS"))
    COUNTRY_CODE: Mapped[str] = mapped_column(Unicode(6, "Latin1_General_CI_AS"))
    PAED_UNIT: Mapped[int] = mapped_column(Integer)
    REGION_CODE: Mapped[Optional[str]] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS")
    )


class MEDICATION(Base):
    __tablename__ = "MEDICATION"
    __table_args__ = (
        PrimaryKeyConstraint(
            "RR_NO",
            "START_DATE",
            "DRUG_NAME",
            "DRUG_BRAND",
            "UNIT",
            "DOSE",
            "HOSP_CENTRE",
            name="PK_MEDICATION",
        ),
    )

    RR_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    START_DATE: Mapped[datetime.datetime] = mapped_column(DateTime, primary_key=True)
    DRUG_NAME: Mapped[str] = mapped_column(
        Unicode(100, "Latin1_General_CI_AS"), primary_key=True
    )
    DRUG_BRAND: Mapped[str] = mapped_column(
        Unicode(100, "Latin1_General_CI_AS"), primary_key=True
    )
    UNIT: Mapped[str] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS"), primary_key=True
    )
    DOSE: Mapped[int] = mapped_column(Integer, primary_key=True)
    HOSP_CENTRE: Mapped[str] = mapped_column(
        String(20, "Latin1_General_CI_AS"), primary_key=True
    )
    END_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    ROUTE: Mapped[Optional[int]] = mapped_column(Integer)
    FREQUENCY: Mapped[Optional[str]] = mapped_column(
        Unicode(50, "Latin1_General_CI_AS")
    )
    COMMENTS: Mapped[Optional[str]] = mapped_column(
        Unicode(250, "Latin1_General_CI_AS")
    )


class MODALITYCODES(Base):
    __tablename__ = "MODALITY_CODES"
    __table_args__ = (PrimaryKeyConstraint("REGISTRY_CODE", name="PK_MODALITY_CODES"),)

    REGISTRY_CODE: Mapped[str] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS"), primary_key=True
    )
    REGISTRY_CODE_TYPE: Mapped[str] = mapped_column(Unicode(3, "Latin1_General_CI_AS"))
    ACUTE: Mapped[bool] = mapped_column(Boolean)
    TRANSFER_IN: Mapped[bool] = mapped_column(Boolean)
    CKD_: Mapped[bool] = mapped_column("CKD", Boolean)
    CONS: Mapped[bool] = mapped_column(Boolean)
    RRT: Mapped[bool] = mapped_column(Boolean)
    END_OF_CARE: Mapped[bool] = mapped_column(Boolean)
    IS_IMPRECISE: Mapped[bool] = mapped_column(Boolean)
    REGISTRY_CODE_DESC: Mapped[Optional[str]] = mapped_column(
        Unicode(100, "Latin1_General_CI_AS")
    )
    EQUIV_MODALITY: Mapped[Optional[str]] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS")
    )
    NHSBT_TRANSPLANT_TYPE: Mapped[Optional[str]] = mapped_column(
        Unicode(4, "Latin1_General_CI_AS")
    )
    TRANSFER_OUT: Mapped[Optional[bool]] = mapped_column(Boolean)


class MONTHLYTREATMENT(Base):
    __tablename__ = "MONTHLY_TREATMENT"
    __table_args__ = (
        PrimaryKeyConstraint(
            "RR_NO",
            "START_DATE",
            "HOSP_CENTRE",
            "TREATMENT_MODALITY",
            "TREATMENT_CENTRE",
            name="PK_MONTHLY_TREATMENT_1",
        ),
    )

    RR_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    START_DATE: Mapped[datetime.datetime] = mapped_column(DateTime, primary_key=True)
    HOSP_CENTRE: Mapped[str] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS"), primary_key=True
    )
    TREATMENT_MODALITY: Mapped[str] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS"), primary_key=True
    )
    TREATMENT_CENTRE: Mapped[str] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS"), primary_key=True
    )
    END_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    ADD_HAEMO_ON_PD: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    HD_SUPERVISION: Mapped[Optional[str]] = mapped_column(
        Unicode(6, "Latin1_General_CI_AS")
    )
    CENTRE_PRI: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    SERUM_CREATININE_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    SERUM_CREATININE: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    SERUM_UREA: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    SERUM_BICARBONATE_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime
    )
    SERUM_BICARBONATE: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    SERUM_SODIUM_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    SERUM_SODIUM: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    SERUM_POTASSIUM_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    SERUM_POTASSIUM: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    LAB_CALCULATED_EGFR: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    SERUM_URIC_ACID_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    SERUM_URIC_ACID: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    SERUM_PHOSPHATE_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    SERUM_PHOSPHATE: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    SERUM_CALCIUM: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    SERUM_CALCIUM_CORRECTED: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    SERUM_ALKA_PHOSPHATASE_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime
    )
    SERUM_ALKA_PHOSPHATASE: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    SERUM_ALBUMIN_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    SERUM_ALBUMIN: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    SERUM_IPTH_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    SERUM_IPTH: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    UPC_RATIO_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    UPC_RATIO: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    UAC_RATIO_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    UAC_RATIO: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    SERUM_CHOLESTEROL_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime
    )
    SERUM_CHOLESTEROL: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    SERUM_HDL_CHOLESTEROL: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    SERUM_LDL_CHOLESTEROL: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    SERUM_TRIGLYCERIDES: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    CRP_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    CRP: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    HBA1C_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    HBA1C_PERCENT: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    HAEMOGLOBIN_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    HAEMOGLOBIN: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    MCH: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    PLATELETS: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    WBC: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    SERUM_FERRITIN_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    SERUM_FERRITIN: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    TRANSFERRIN_SATURATION_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime
    )
    TRANSFERRIN_SATURATION: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    HYPOCHROMIC_RED_CELLS_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime
    )
    HYPOCHROMIC_RED_CELLS: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    SERUM_B12_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    SERUM_B12: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    SERUM_FOLATE_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    SERUM_FOLATE: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    RED_CELL_FOLATE_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    RED_CELL_FOLATE: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    SERUM_ALUMINIUM_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    SERUM_ALUMINIUM: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    WEIGHT_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    WEIGHT: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    BP_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    SYSTOLIC_BP: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    DIASTOLIC_BP: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    POST_BP_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    POST_SYSTOLIC_BP: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    POST_DIASTOLIC_BP: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    URR_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    URR: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    BLOOD_FLOW_RATE: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    HD_TIMES_PER_WEEK: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    DIALYSIS_TIME: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    WEEKLY_FLUID_VOL: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    BAG_SIZE: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    STATIN_DRUG_USE: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    ACE_INHIBITOR: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    ANGIOTENSIN_RECEPTOR_BLOCKER: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    ORAL_B_BLOCKER: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    RENAGEL: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    LANTHANUM: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    CINACALCET: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    CALCIUM_BASED_BINDER: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    ALUCAPS: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    HBA1C_VALUE: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    SHARED_CARE: Mapped[Optional[int]] = mapped_column(SmallInteger)
    SERUM_UREA_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    LAB_CALCULATED_EGFR_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime
    )
    SERUM_CALCIUM_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    SERUM_CALCIUM_CORRECTED_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime
    )
    IPTH_ASSAY_METHOD: Mapped[Optional[str]] = mapped_column(
        Unicode(30, "Latin1_General_CI_AS")
    )
    SERUM_HDL_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    SERUM_LDL_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    SERUM_TRIGLYCERIDES_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime
    )
    MCH_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    PLATELETS_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    WBC_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    HAEMOGLOBIN_GL: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    TACROLIMUS_LEVEL: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    TACROLIMUS_LEVEL_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    SIROLIMUS_LEVEL: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    SIROLIMUS_LEVEL_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    CICLOSPORIN_LEVEL: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    CICLOSPORIN_LEVEL_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime
    )
    MYCOPHENOLATE_LEVEL: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    MYCOPHENOLATE_LEVEL_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime
    )
    HEIGHT: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    HEIGHT_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    LAST_APPT_ATTENDED_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime
    )
    ACCESS_USED: Mapped[Optional[str]] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS")
    )
    KTV_: Mapped[Optional[decimal.Decimal]] = mapped_column("KTV", Numeric(38, 4))
    KTV_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    HBV_ANTIBODY: Mapped[Optional[str]] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS")
    )
    HBV_ANTIBODY_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    HBV_ANTIGEN: Mapped[Optional[str]] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS")
    )
    HBV_ANTIGEN_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    HCV_ANTIBODY: Mapped[Optional[str]] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS")
    )
    HCV_ANTIBODY_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    CMV_ANTIBODY: Mapped[Optional[str]] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS")
    )
    CMV_ANTIBODY_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    CMV_PCR_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    CMV_PCR: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    HIV_TEST_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    HIV_ANTIGEN: Mapped[Optional[str]] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS")
    )
    EBV_STATUS: Mapped[Optional[str]] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS")
    )
    EBV_PCR_COUNT: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    EBV_TEST_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    URINE_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    URINE_VOL: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    URINARY_CREATININE: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    SELF_CARE: Mapped[Optional[str]] = mapped_column(String(1, "Latin1_General_CI_AS"))
    TRANSPLANTED_KIDNEY_DRAINAGE: Mapped[Optional[int]] = mapped_column(Integer)
    NON_RENAL_GRAFT_1: Mapped[Optional[str]] = mapped_column(
        Unicode(20, "Latin1_General_CI_AS")
    )
    NON_RENAL_GRAFT_2: Mapped[Optional[str]] = mapped_column(
        Unicode(20, "Latin1_General_CI_AS")
    )
    NON_RENAL_GRAFT_3: Mapped[Optional[str]] = mapped_column(
        Unicode(20, "Latin1_General_CI_AS")
    )
    DIAGNOSED_PTLD: Mapped[Optional[str]] = mapped_column(
        String(1, "Latin1_General_CI_AS")
    )
    MENTAL_DISABILITY: Mapped[Optional[int]] = mapped_column(Integer)
    PHYSICAL_DISABILITY: Mapped[Optional[int]] = mapped_column(Integer)
    VISUAL_DISABILITY: Mapped[Optional[int]] = mapped_column(Integer)
    AUDITORY_DISABILITY: Mapped[Optional[int]] = mapped_column(Integer)
    PTH_ULN: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 0))
    PTH_ULN_RATIO: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 0))
    ALT: Mapped[Optional[int]] = mapped_column(Integer)
    ANC: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 0))
    ALC: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 0))
    VARICELLA: Mapped[Optional[str]] = mapped_column(String(3, "Latin1_General_CI_AS"))
    VARICELLA_TEST_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    MYOPATHY: Mapped[Optional[str]] = mapped_column(String(1, "Latin1_General_CI_AS"))
    ANTHROPATHY: Mapped[Optional[str]] = mapped_column(
        String(1, "Latin1_General_CI_AS")
    )
    CENTRAL_NERVOUS_COM: Mapped[Optional[str]] = mapped_column(
        Unicode(150, "Latin1_General_CI_AS")
    )
    RESPIRATORY_COM: Mapped[Optional[str]] = mapped_column(
        Unicode(150, "Latin1_General_CI_AS")
    )
    CARDIOVASCULAR_COM: Mapped[Optional[str]] = mapped_column(
        Unicode(150, "Latin1_General_CI_AS")
    )
    GASTRO_INTESTINAL_COM: Mapped[Optional[str]] = mapped_column(
        Unicode(150, "Latin1_General_CI_AS")
    )
    HEPATIC_COM: Mapped[Optional[str]] = mapped_column(
        Unicode(150, "Latin1_General_CI_AS")
    )
    GENITO_URINARY_COM: Mapped[Optional[str]] = mapped_column(
        Unicode(150, "Latin1_General_CI_AS")
    )
    ENDOCRINE_COM: Mapped[Optional[str]] = mapped_column(
        Unicode(150, "Latin1_General_CI_AS")
    )
    SOCIAL_PSYCHIATRIC_COM: Mapped[Optional[str]] = mapped_column(
        Unicode(150, "Latin1_General_CI_AS")
    )
    PUBERTY_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    DATE_UNIT_CALC_EGFR: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    EGFR_CALC_BY_UNIT: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))


class NHSTRACINGMISMATCHES(Base):
    __tablename__ = "NHS_TRACING_MISMATCHES"
    __table_args__ = (
        PrimaryKeyConstraint("RR_NO", "NHS_NO", name="PK__NHS_TRAC__F767E7BB6F3D3B0D"),
    )

    RR_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    NHS_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    NOTES: Mapped[str] = mapped_column(Unicode(collation="Latin1_General_CI_AS"))


class PATIENTS(Base):
    __tablename__ = "PATIENTS"
    __table_args__ = (
        PrimaryKeyConstraint("RR_NO", name="PK_PATIENTS"),
        Index("Missing_IXNC_PATIENTS_DATE_DEATH_B7FAA", "DATE_DEATH"),
        Index(
            "_dta_index_PATIENTS_7_1616828922__K3_K4_K5_1_6_25_55",
            "SURNAME",
            "FORENAME",
            "DATE_BIRTH",
        ),
        Index("_dta_index_PATIENTS_7_880826300__K1", "RR_NO"),
        Index(
            "_dta_index_PATIENTS_7_880826300__K13_K1_K6_K9_K51_K56_K55_K17_K5_K3_K4_57_58",
            "UKTSSA_NO",
            "RR_NO",
            "LOCAL_HOSP_NO",
            "HOSP_CENTRE",
            "UKT_UKTSSA_NO",
            "CHI_NO",
            "NEW_NHS_NO",
            "SCOT_REG_NO",
            "DATE_BIRTH",
            "SURNAME",
            "FORENAME",
        ),
        Index(
            "_dta_index_PATIENTS_7_880826300__K17_K1_K6_K9_K13_K51_K56_K55_K5_K3_K4_57_58",
            "SCOT_REG_NO",
            "RR_NO",
            "LOCAL_HOSP_NO",
            "HOSP_CENTRE",
            "UKTSSA_NO",
            "UKT_UKTSSA_NO",
            "CHI_NO",
            "NEW_NHS_NO",
            "DATE_BIRTH",
            "SURNAME",
            "FORENAME",
        ),
        Index(
            "_dta_index_PATIENTS_7_880826300__K1_K3_K4_K57_K58",
            "RR_NO",
            "SURNAME",
            "FORENAME",
            "SOUNDEX_FORENAME",
            "SOUNDEX_SURNAME",
        ),
        Index(
            "_dta_index_PATIENTS_7_880826300__K1_K3_K4_K5_K55_K9_K6_K13_K40_K25",
            "RR_NO",
            "SURNAME",
            "FORENAME",
            "DATE_BIRTH",
            "NEW_NHS_NO",
            "HOSP_CENTRE",
            "LOCAL_HOSP_NO",
            "UKTSSA_NO",
            "TRACING_DATE_DEATH",
            "DATE_DEATH",
        ),
        Index(
            "_dta_index_PATIENTS_7_880826300__K1_K57_K58_K9_K6_K51_K56_K55_K17_K5_K3_K4",
            "RR_NO",
            "SOUNDEX_FORENAME",
            "SOUNDEX_SURNAME",
            "HOSP_CENTRE",
            "LOCAL_HOSP_NO",
            "UKT_UKTSSA_NO",
            "CHI_NO",
            "NEW_NHS_NO",
            "SCOT_REG_NO",
            "DATE_BIRTH",
            "SURNAME",
            "FORENAME",
        ),
        Index("_dta_index_PATIENTS_7_880826300__K51_K1", "UKT_UKTSSA_NO", "RR_NO"),
        Index(
            "_dta_index_PATIENTS_7_880826300__K51_K1_3_4_5_8_25_55",
            "UKT_UKTSSA_NO",
            "RR_NO",
        ),
        Index(
            "_dta_index_PATIENTS_7_880826300__K55_K1_K6_K9_K13_K51_K56_K17_K5_K3_K4_57_58",
            "NEW_NHS_NO",
            "RR_NO",
            "LOCAL_HOSP_NO",
            "HOSP_CENTRE",
            "UKTSSA_NO",
            "UKT_UKTSSA_NO",
            "CHI_NO",
            "SCOT_REG_NO",
            "DATE_BIRTH",
            "SURNAME",
            "FORENAME",
        ),
        Index(
            "_dta_index_PATIENTS_7_880826300__K56_K1_K6_K9_K13_K51_K55_K17_K5_K3_K4_57_58",
            "CHI_NO",
            "RR_NO",
            "LOCAL_HOSP_NO",
            "HOSP_CENTRE",
            "UKTSSA_NO",
            "UKT_UKTSSA_NO",
            "NEW_NHS_NO",
            "SCOT_REG_NO",
            "DATE_BIRTH",
            "SURNAME",
            "FORENAME",
        ),
        Index("_dta_index_PATIENTS_7_880826300__K5_K1", "DATE_BIRTH", "RR_NO"),
        Index("_dta_index_PATIENTS_7_880826300__K8_4", "SEX"),
        Index(
            "_dta_index_PATIENTS_7_880826300__K9_K6_K5_K55_K56_K17_K51_K13_K1",
            "HOSP_CENTRE",
            "LOCAL_HOSP_NO",
            "DATE_BIRTH",
            "NEW_NHS_NO",
            "CHI_NO",
            "SCOT_REG_NO",
            "UKT_UKTSSA_NO",
            "UKTSSA_NO",
            "RR_NO",
        ),
    )

    RR_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    SURNAME: Mapped[str] = mapped_column(Unicode(50, "Latin1_General_CI_AS"))
    FORENAME: Mapped[str] = mapped_column(Unicode(50, "Latin1_General_CI_AS"))
    DATE_BIRTH: Mapped[datetime.datetime] = mapped_column(DateTime)
    LOCAL_HOSP_NO: Mapped[str] = mapped_column(Unicode(15, "Latin1_General_CI_AS"))
    HOSP_CENTRE: Mapped[str] = mapped_column(Unicode(8, "Latin1_General_CI_AS"))
    SURNAME_SOUNDEX: Mapped[Optional[str]] = mapped_column(
        Unicode(4, "Latin1_General_CI_AS")
    )
    DATE_REGISTERED: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    SEX: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    MIN_DATA_IND: Mapped[Optional[str]] = mapped_column(
        Unicode(2, "Latin1_General_CI_AS")
    )
    ESRF_IND: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    PAEDIATRIC_IND: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    UKTSSA_NO: Mapped[Optional[int]] = mapped_column(BigInteger)
    SUPER_CHI_NO: Mapped[Optional[str]] = mapped_column(
        Unicode(15, "Latin1_General_CI_AS")
    )
    OLD_NHS_NO: Mapped[Optional[str]] = mapped_column(
        Unicode(15, "Latin1_General_CI_AS")
    )
    MRC_NO: Mapped[Optional[str]] = mapped_column(Unicode(10, "Latin1_General_CI_AS"))
    SCOT_REG_NO: Mapped[Optional[str]] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS")
    )
    MARITAL_STATUS: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    ETHGR_CODE: Mapped[Optional[str]] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS")
    )
    ADULT_HEIGHT: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    FIRST_SEEN_HEIGHT: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    FIRST_SEEN_WEIGHT: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    FIRST_SEEN_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    FIRST_SEEN_CREATININE: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    DATE_DEATH: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    COD_READ: Mapped[Optional[str]] = mapped_column(Unicode(8, "Latin1_General_CI_AS"))
    COD_EDTA1: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    COD_EDTA2: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    COD_TEXT: Mapped[Optional[str]] = mapped_column(Unicode(70, "Latin1_General_CI_AS"))
    TRANSFER_IND: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    TRANSFER_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    CENTRE_PRI: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    GP_POSTCODE: Mapped[Optional[str]] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS")
    )
    DATE_STAT: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    BLOOD_GROUP: Mapped[Optional[str]] = mapped_column(
        Unicode(2, "Latin1_General_CI_AS")
    )
    BLOOD_GROUP_RHESUS: Mapped[Optional[str]] = mapped_column(
        Unicode(3, "Latin1_General_CI_AS")
    )
    OPT_OUT_FLAG: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    YEAR_OF_BIRTH: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    UNIQUE_IDENTIFIER: Mapped[Optional[str]] = mapped_column(
        Unicode(20, "Latin1_General_CI_AS")
    )
    TRACING_DATE_DEATH: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    TRACING_DATE_BIRTH: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    DOMINANT_ARM: Mapped[Optional[str]] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS")
    )
    REFERRAL_CODE: Mapped[Optional[str]] = mapped_column(
        Unicode(20, "Latin1_General_CI_AS")
    )
    REFERRAL_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    REFERRING_GP_CODE: Mapped[Optional[str]] = mapped_column(
        Unicode(20, "Latin1_General_CI_AS")
    )
    TRACING_NHS_NO: Mapped[Optional[int]] = mapped_column(BigInteger)
    DATE_CKD5_START: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    CKD5_START: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    DATE_CKD5_GE_90: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    CKD5_GE_90: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    UKT_UKTSSA_NO: Mapped[Optional[int]] = mapped_column(BigInteger)
    TRACING_RESPONSE: Mapped[Optional[str]] = mapped_column(
        Unicode(2, "Latin1_General_CI_AS")
    )
    BAPN_NO: Mapped[Optional[str]] = mapped_column(Unicode(20, "Latin1_General_CI_AS"))
    DATE_LAST_TRACED: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    NEW_NHS_NO: Mapped[Optional[int]] = mapped_column(BigInteger)
    CHI_NO: Mapped[Optional[int]] = mapped_column(BigInteger)
    BIRTH_NAME: Mapped[Optional[str]] = mapped_column(
        Unicode(50, "Latin1_General_CI_AS")
    )
    ALIAS_NAME: Mapped[Optional[str]] = mapped_column(
        Unicode(50, "Latin1_General_CI_AS")
    )
    HSC_NO: Mapped[Optional[int]] = mapped_column(BigInteger)
    GP_CODE: Mapped[Optional[str]] = mapped_column(Unicode(10, "Latin1_General_CI_AS"))
    RPV_FLAG: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    REFERRING_GP_PRACTICE_CODE: Mapped[Optional[str]] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS")
    )
    RR_DATE_FIRST_CKD4: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    RR_DATE_FIRST_CKD5: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    RR_DATE_FIRST_AKI: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    RR_DATE_FIRST_ESRF: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    RR_DATE_FIRST_CONS: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    RR_DATE_FIRST_CKD2: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    RR_DATE_FIRST_CKD3: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    RR_DATE_FIRST_CKD1: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    RR_DATE_FIRST_PAED: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    SOUNDEX_FORENAME: Mapped[Optional[str]] = mapped_column(
        String(5, "Latin1_General_CI_AS"),
        Computed("(soundex([dbo].[normalise_forename2]([FORENAME])))", persisted=True),
    )
    SOUNDEX_SURNAME: Mapped[Optional[str]] = mapped_column(
        String(5, "Latin1_General_CI_AS"),
        Computed("(soundex([dbo].[normalise_surname2]([SURNAME])))", persisted=True),
    )


class PATIENTDEMOG(Base):
    __tablename__ = "PATIENT_DEMOG"
    __table_args__ = (
        PrimaryKeyConstraint("RR_NO", "HOSP_CENTRE", name="PK_PATIENT_DEMOG"),
    )

    RR_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    HOSP_CENTRE: Mapped[str] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS"), primary_key=True
    )
    LOCAL_HOSP_NO: Mapped[str] = mapped_column(Unicode(15, "Latin1_General_CI_AS"))
    SURNAME: Mapped[str] = mapped_column(Unicode(50, "Latin1_General_CI_AS"))
    FORENAME: Mapped[str] = mapped_column(Unicode(50, "Latin1_General_CI_AS"))
    DATE_BIRTH: Mapped[datetime.datetime] = mapped_column(DateTime)
    DATE_DEATH: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    NEW_NHS_NO: Mapped[Optional[int]] = mapped_column(BigInteger)
    CHI_NO: Mapped[Optional[int]] = mapped_column(BigInteger)
    FIRST_SEEN_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    ETHGR_CODE: Mapped[Optional[str]] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS")
    )
    UKTSSA_NO: Mapped[Optional[int]] = mapped_column(BigInteger)
    BIRTH_NAME: Mapped[Optional[str]] = mapped_column(
        Unicode(50, "Latin1_General_CI_AS")
    )
    ALIAS_NAME: Mapped[Optional[str]] = mapped_column(
        Unicode(50, "Latin1_General_CI_AS")
    )
    HSC_NO: Mapped[Optional[int]] = mapped_column(BigInteger)


class PATIENTNOTES(Base):
    __tablename__ = "PATIENT_NOTES"
    __table_args__ = (PrimaryKeyConstraint("RR_NO", name="PK_PATIENT_NOTES"),)

    RR_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    NOTES: Mapped[Optional[str]] = mapped_column(Unicode(4000, "Latin1_General_CI_AS"))


class PATIENTXREF(Base):
    __tablename__ = "PATIENT_XREF"
    __table_args__ = (
        PrimaryKeyConstraint(
            "RR_NO", "SURNAME", "FORENAME", "DATE_BIRTH", name="PK_PATIENT_XREF"
        ),
        Index("NonClusteredIndex-20150219-123721", "SURNAME", "FORENAME", "DATE_BIRTH"),
        Index("_dta_index_PATIENT_XREF_7_816826072__K1", "RR_NO"),
        Index(
            "_dta_index_PATIENT_XREF_7_816826072__K1_K2_K3_6_7",
            "RR_NO",
            "SURNAME",
            "FORENAME",
        ),
    )

    RR_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    SURNAME: Mapped[str] = mapped_column(
        Unicode(50, "Latin1_General_CI_AS"), primary_key=True
    )
    FORENAME: Mapped[str] = mapped_column(
        Unicode(50, "Latin1_General_CI_AS"), primary_key=True
    )
    DATE_BIRTH: Mapped[datetime.datetime] = mapped_column(DateTime, primary_key=True)
    USE_AS_DEFAULT: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    BIRTH_NAME: Mapped[Optional[str]] = mapped_column(
        Unicode(50, "Latin1_General_CI_AS")
    )
    ALIAS_NAME: Mapped[Optional[str]] = mapped_column(
        Unicode(50, "Latin1_General_CI_AS")
    )
    SOUNDEX_FORENAME: Mapped[Optional[str]] = mapped_column(
        String(5, "Latin1_General_CI_AS"),
        Computed("(soundex([dbo].[normalise_FORENAME2]([FORENAME])))", persisted=True),
    )
    SOUNDEX_SURNAME: Mapped[Optional[str]] = mapped_column(
        String(5, "Latin1_General_CI_AS"),
        Computed("(soundex([dbo].[normalise_surname2]([SURNAME])))", persisted=True),
    )


class QUARTERLYTREATMENT(Base):
    __tablename__ = "QUARTERLY_TREATMENT"
    __table_args__ = (
        PrimaryKeyConstraint(
            "RR_NO",
            "DATE_START",
            "TREATMENT_MODALITY",
            "HOSP_CENTRE",
            "TREATMENT_CENTRE",
            name="PK_QUARTERLY_TREATMENT",
        ),
        Index("IX_QUARTERLY_TREATMENT_2154_2153", "DATE_START"),
        Index(
            "_dta_index_QUARTERLY_TREATMENT_7_276300144__K1_K20_K2D_K4",
            "RR_NO",
            "HOSP_CENTRE",
            "DATE_START",
            "TREATMENT_MODALITY",
        ),
        Index(
            "_dta_index_QUARTERLY_TREATMENT_7_276300144__K1_K2D_K16_K20_K4",
            "RR_NO",
            "DATE_START",
            "TREATMENT_CENTRE",
            "HOSP_CENTRE",
            "TREATMENT_MODALITY",
        ),
        Index("_dta_index_QUARTERLY_TREATMENT_7_84299460__K25", "HOSP_CENTRE"),
        Index(
            "_dta_index_QUARTERLY_TREATMENT_7_84299460__K4_1_2_6_7_8_9_10_11_12_13_25_54",
            "TREATMENT_MODALITY",
        ),
    )

    RR_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    DATE_START: Mapped[datetime.datetime] = mapped_column(DateTime, primary_key=True)
    TREATMENT_MODALITY: Mapped[str] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS"), primary_key=True
    )
    TREATMENT_CENTRE: Mapped[str] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS"), primary_key=True
    )
    HOSP_CENTRE: Mapped[str] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS"), primary_key=True
    )
    DATE_END: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    ADD_HAEMO_ON_PD: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    CREATININE: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    UREA: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    HAEMOGLOBIN: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    FERRETIN: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    ALBUMIN: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    ALUMINIUM: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    HBA1C: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    CHOLESTEROL: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    IPTH: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    CALCIUM_UNCORR: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    CALCIUM_CORR: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    PHOSPHATE: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    BICARBONATE: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    SYSTOLIC_BP: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    DIASTOLIC_BP: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    WEIGHT: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    UREA_REDUCTION_RATIO: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    EPO_USE: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    HD_SUPERVISON: Mapped[Optional[str]] = mapped_column(
        Unicode(4, "Latin1_General_CI_AS")
    )
    DIALYSER_USED: Mapped[Optional[str]] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS")
    )
    FLOW_RATE: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    DIAL_REUSE: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    TIMES_PER_WEEK: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    DIAL_TIME: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    BICARB_DIAL: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    WEEKLY_FLUID_VOL: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    BAG_SIZE: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    CENTRE_PRI: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    POST_SYSTOLIC_BP: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    POST_DIASTOLIC_BP: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    SODIUM: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    PD_DIALYSATE_KTV: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    PD_URINE_KTV: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    PD_NPCR: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    CRP: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    LDL_CHOLESTEROL: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    HDL_CHOLESTEROL: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    TRIGLYCERIDES: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    WAITING_LIST_STATUS: Mapped[Optional[str]] = mapped_column(
        Unicode(3, "Latin1_General_CI_AS")
    )
    CREATININE_FIRST_MONTH: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    CREATININE_SECOND_MONTH: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    PERCENT_HYPOCHROMIC: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    MCH: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    B12: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    RED_CELL_FOLATE: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    TRANSFERRIN_SATURATION: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    SERUM_POTASSIUM: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    PROTEIN_CREATININE_RATIO: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    ALBUMIN_CREATININE_RATIO: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )
    SERUM_CELL_FOLATE: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    ACE_INHIBITOR: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    RENAGEL: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    LANTHANUM: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    CINACALCET: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    CALCIUM_BASED_BINDER: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    ALUCAPS: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    SERUM_URATE: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    STATIN_DRUG_USE: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    HBA1C_MMOL: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(3, 0))
    ALKALINE_PHOSPHATASE: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(38, 4)
    )


t_REGISTRY_CODES = Table(
    "REGISTRY_CODES",
    Base.metadata,
    Column("REGISTRY_CODE", Unicode(8, "Latin1_General_CI_AS"), nullable=False),
    Column("REGISTRY_CODE_DESC", Unicode(100, "Latin1_General_CI_AS")),
    Column("REGISTRY_CODE_TYPE", Unicode(3, "Latin1_General_CI_AS"), nullable=False),
    Column("ACUTE", Boolean, nullable=False),
    Column("TRANSFER_IN", Boolean, nullable=False),
    Column("CKD", Boolean, nullable=False),
    Column("CONS", Boolean, nullable=False),
    Column("RRT", Boolean, nullable=False),
    Column("EQUIV_MODALITY", Unicode(8, "Latin1_General_CI_AS")),
    Column("END_OF_CARE", Boolean, nullable=False),
)


class RESIDENCY(Base):
    __tablename__ = "RESIDENCY"
    __table_args__ = (
        PrimaryKeyConstraint("RR_NO", "DATE_START", "CENTRE_CODE", name="PK_RESIDENCY"),
        Index(
            "_dta_index_RESIDENCY_7_116299574__K1_K2_K4",
            "CENTRE_CODE",
            "RR_NO",
            "DATE_END",
        ),
        Index("_dta_index_RESIDENCY_7_116299574__K2_K3D_8", "RR_NO", "DATE_START"),
        Index(
            "_dta_index_RESIDENCY_7_116299574__K4_K2_K1_8",
            "DATE_END",
            "RR_NO",
            "CENTRE_CODE",
        ),
    )

    CENTRE_CODE: Mapped[str] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS"), primary_key=True
    )
    RR_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    DATE_START: Mapped[datetime.datetime] = mapped_column(DateTime, primary_key=True)
    DATE_END: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    ADDRESS_1: Mapped[Optional[str]] = mapped_column(
        Unicode(60, "Latin1_General_CI_AS")
    )
    ADDRESS_2: Mapped[Optional[str]] = mapped_column(
        Unicode(60, "Latin1_General_CI_AS")
    )
    ADDRESS_3: Mapped[Optional[str]] = mapped_column(
        Unicode(60, "Latin1_General_CI_AS")
    )
    ADDRESS_4: Mapped[Optional[str]] = mapped_column(
        Unicode(60, "Latin1_General_CI_AS")
    )
    POST_CODE: Mapped[Optional[str]] = mapped_column(Unicode(8, "Latin1_General_CI_AS"))
    CENTRE_PRI: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    NHS_CODE: Mapped[Optional[str]] = mapped_column(Unicode(3, "Latin1_General_CI_AS"))
    NHS_NAME: Mapped[Optional[str]] = mapped_column(Unicode(60, "Latin1_General_CI_AS"))
    STATUS: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    SENT_ADD_1: Mapped[Optional[str]] = mapped_column(
        Unicode(60, "Latin1_General_CI_AS")
    )
    SENT_ADD_2: Mapped[Optional[str]] = mapped_column(
        Unicode(60, "Latin1_General_CI_AS")
    )
    SENT_ADD_3: Mapped[Optional[str]] = mapped_column(
        Unicode(60, "Latin1_General_CI_AS")
    )
    SENT_ADD_4: Mapped[Optional[str]] = mapped_column(
        Unicode(60, "Latin1_General_CI_AS")
    )
    SENT_POST_CODE: Mapped[Optional[str]] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS")
    )


class RRCODES(Base):
    __tablename__ = "RR_CODES"
    __table_args__ = (PrimaryKeyConstraint("ID", "RR_CODE", name="PK_RR_CODES_1"),)

    ID: Mapped[str] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS"), primary_key=True
    )
    RR_CODE: Mapped[str] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS"), primary_key=True
    )
    DESCRIPTION_1: Mapped[Optional[str]] = mapped_column(
        Unicode(255, "Latin1_General_CI_AS")
    )
    DESCRIPTION_2: Mapped[Optional[str]] = mapped_column(
        Unicode(70, "Latin1_General_CI_AS")
    )
    DESCRIPTION_3: Mapped[Optional[str]] = mapped_column(
        Unicode(60, "Latin1_General_CI_AS")
    )
    OLD_VALUE: Mapped[Optional[str]] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS")
    )
    OLD_VALUE_2: Mapped[Optional[str]] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS")
    )
    NEW_VALUE: Mapped[Optional[str]] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS")
    )


class RRCODELISTS(Base):
    __tablename__ = "RR_CODE_LISTS"
    __table_args__ = (PrimaryKeyConstraint("ID", name="PK_RR_CODE_LISTS"),)

    ID: Mapped[str] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS"), primary_key=True
    )
    NAME: Mapped[Optional[str]] = mapped_column(Unicode(70, "Latin1_General_CI_AS"))
    UPLOAD_KEYS: Mapped[Optional[str]] = mapped_column(
        Unicode(70, "Latin1_General_CI_AS")
    )


t_RR_COUNTS_CONFIG = Table(
    "RR_COUNTS_CONFIG",
    Base.metadata,
    Column("id", Integer, Identity(start=1, increment=1), nullable=False),
    Column("listgroup", Integer, nullable=False),
    Column("tagname", String(5, "Latin1_General_CI_AS"), nullable=False),
    Column("display", NCHAR(1, "Latin1_General_CI_AS"), nullable=False),
    Column("description", String(100, "Latin1_General_CI_AS")),
    Index("unique_items", "listgroup", "tagname", unique=True),
)


t_RR_DATA_DEFINITION = Table(
    "RR_DATA_DEFINITION",
    Base.metadata,
    Column("UPLOAD_KEY", Unicode(5, "Latin1_General_CI_AS")),
    Column("TABLE_NAME", Unicode(30, "Latin1_General_CI_AS"), nullable=False),
    Column("FIELD_NAME", Unicode(30, "Latin1_General_CI_AS"), nullable=False),
    Column("CODE_ID", Unicode(10, "Latin1_General_CI_AS")),
    Column("MANDATORY", Numeric(1, 0)),
    Column("TYPE", Unicode(1, "Latin1_General_CI_AS")),
    Column("ALT_CONSTRAINT", Unicode(30, "Latin1_General_CI_AS")),
    Column("ALT_DESC", Unicode(30, "Latin1_General_CI_AS")),
    Column("EXTRA_VAL", Unicode(1, "Latin1_General_CI_AS")),
    Column("ERROR_TYPE", Integer),
    Column("PAED_MAND", Numeric(1, 0)),
    Column("CKD5_MAND", Numeric(1, 0)),
    Column("DEPENDANT_FIELD", Unicode(30, "Latin1_General_CI_AS")),
    Column("ALT_VALIDATION", Unicode(30, "Latin1_General_CI_AS")),
    Column("FILE_PREFIX", Unicode(20, "Latin1_General_CI_AS")),
    Column("LOAD_MIN", Numeric(38, 4)),
    Column("LOAD_MAX", Numeric(38, 4)),
    Column("REMOVE_MIN", Numeric(38, 4)),
    Column("REMOVE_MAX", Numeric(38, 4)),
    Column("IN_MONTH", Numeric(1, 0)),
    Column("AKI_MAND", Numeric(1, 0)),
    Column("RRT_MAND", Numeric(1, 0)),
    Column("CONS_MAND", Numeric(1, 0)),
    Column("CKD4_MAND", Numeric(1, 0)),
    Column("VALID_BEFORE_DOB", Numeric(1, 0)),
    Column("VALID_AFTER_DOD", Numeric(1, 0)),
    Column("IN_QUARTER", Numeric(1, 0)),
)


class RRERRORLOG(Base):
    __tablename__ = "RR_ERROR_LOG"
    __table_args__ = (PrimaryKeyConstraint("ERROR_TIMESTAMP", name="PK_RR_ERROR_LOG"),)

    ERROR_TIMESTAMP: Mapped[datetime.datetime] = mapped_column(
        DateTime, primary_key=True
    )
    ERROR_TYPE: Mapped[Optional[str]] = mapped_column(
        Unicode(collation="Latin1_General_CI_AS")
    )
    ERROR_TEXT: Mapped[Optional[str]] = mapped_column(
        Unicode(collation="Latin1_General_CI_AS")
    )
    ERROR_DETAILS: Mapped[Optional[str]] = mapped_column(
        Unicode(collation="Latin1_General_CI_AS")
    )
    UPLOAD_FILE: Mapped[Optional[str]] = mapped_column(
        Unicode(collation="Latin1_General_CI_AS")
    )
    SQL: Mapped[Optional[str]] = mapped_column(
        Unicode(collation="Latin1_General_CI_AS")
    )


t_RR_HIST_COUNTS = Table(
    "RR_HIST_COUNTS",
    Base.metadata,
    Column("ID", Integer, Identity(start=1, increment=1), nullable=False),
    Column("PROCESS_DATE", DateTime),
    Column("FILESITE", Unicode(8, "Latin1_General_CI_AS")),
    Column("FILEQUARTER", Integer),
    Column("Tag", Unicode(255, "Latin1_General_CI_AS")),
    Column("COUNT", Integer),
    Column("M1_COUNT", Integer),
    Column("M2_COUNT", Integer),
    Column("M3_COUNT", Integer),
    Column("QUA_EQ_COUNT", Integer),
)


t_RR_MONTH_TO_QUARTER_FIELD_MAP = Table(
    "RR_MONTH_TO_QUARTER_FIELD_MAP",
    Base.metadata,
    Column("monthly_name", Unicode(50, "Latin1_General_CI_AS")),
    Column("quarterly_equiv", Unicode(50, "Latin1_General_CI_AS")),
)


class RRNOLOAD(Base):
    __tablename__ = "RR_NOLOAD"
    __table_args__ = (
        PrimaryKeyConstraint("SITE", "QUARTER", "LOCAL_HOSP_NO", name="PK_RR_NOLOAD"),
        Index(
            "_dta_index_RR_NOLOAD_7_212299916__K12_K2_K7_K1_K8_K9_K3",
            "RR_NO",
            "QUARTER",
            "NEW_NHS_NO",
            "SITE",
            "CODED_REASON",
            "REASON_FREETEXT",
            "LOCAL_HOSP_NO",
        ),
        Index(
            "_dta_index_RR_NOLOAD_7_212299916__K7_K2_K12_K1_K8_K9_K3",
            "NEW_NHS_NO",
            "QUARTER",
            "RR_NO",
            "SITE",
            "CODED_REASON",
            "REASON_FREETEXT",
            "LOCAL_HOSP_NO",
        ),
    )

    SITE: Mapped[str] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS"), primary_key=True
    )
    QUARTER: Mapped[int] = mapped_column(Integer, primary_key=True)
    LOCAL_HOSP_NO: Mapped[str] = mapped_column(
        Unicode(15, "Latin1_General_CI_AS"), primary_key=True
    )
    SURNAME: Mapped[Optional[str]] = mapped_column(Unicode(50, "Latin1_General_CI_AS"))
    FORENAME: Mapped[Optional[str]] = mapped_column(Unicode(50, "Latin1_General_CI_AS"))
    DATE_BIRTH: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    NEW_NHS_NO: Mapped[Optional[int]] = mapped_column(BigInteger)
    CODED_REASON: Mapped[Optional[str]] = mapped_column(
        Unicode(15, "Latin1_General_CI_AS")
    )
    REASON_FREETEXT: Mapped[Optional[str]] = mapped_column(
        Unicode(60, "Latin1_General_CI_AS")
    )
    EXTRA_COMMENT: Mapped[Optional[str]] = mapped_column(
        Unicode(60, "Latin1_General_CI_AS")
    )
    INITIALS: Mapped[Optional[str]] = mapped_column(Unicode(4, "Latin1_General_CI_AS"))
    RR_NO: Mapped[Optional[int]] = mapped_column(BigInteger)
    OTHER_SITE_CODE: Mapped[Optional[str]] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS")
    )


class RRNOMATCHPATIENTS(Base):
    __tablename__ = "RR_NOMATCH_PATIENTS"
    __table_args__ = (
        PrimaryKeyConstraint("RR_NO", "MISMATCH_RR_NO", name="PK_RR_NOMATCH_PATIENTS"),
    )

    RR_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    MISMATCH_RR_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    COMMENTS: Mapped[Optional[str]] = mapped_column(
        Unicode(128, "Latin1_General_CI_AS")
    )


class RRNOMATCHUKT(Base):
    __tablename__ = "RR_NOMATCH_UKT"
    __table_args__ = (
        PrimaryKeyConstraint("RR_NO", "MISMATCH_UKTSSA_NO", name="PK_RR_NOMATCH_UKT"),
    )

    RR_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    MISMATCH_UKTSSA_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    COMMENTS: Mapped[Optional[str]] = mapped_column(
        Unicode(128, "Latin1_General_CI_AS")
    )


class RRNOALLOCATION(Base):
    __tablename__ = "RR_NO_ALLOCATION"
    __table_args__ = (PrimaryKeyConstraint("ALLOC_YEAR", name="PK_RR_NO_ALLOCATION"),)

    ALLOC_YEAR: Mapped[int] = mapped_column(Integer, primary_key=True)
    NEXT_RR_NO: Mapped[int] = mapped_column(Integer)


t_RR_QUARTERS = Table(
    "RR_QUARTERS",
    Base.metadata,
    Column("QUARTERNUMBER", BigInteger),
    Column("QUARTERSTARTDATE", DateTime),
    Column("QUARTERENDDATE", DateTime),
)


class RRVALIDATIONERROR(Base):
    __tablename__ = "RR_VALIDATION_ERROR"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="PK_RR_VALIDATION_ERROR"),
        Index("IX_RR_SEVERITY_ERROR_INDEX", "id", unique=True),
    )

    id: Mapped[int] = mapped_column(
        Integer, Identity(start=1, increment=1), primary_key=True
    )
    severity: Mapped[int] = mapped_column(SmallInteger)
    error: Mapped[str] = mapped_column(String(1000, "Latin1_General_CI_AS"))
    file_field: Mapped[Optional[str]] = mapped_column(
        String(10, "Latin1_General_CI_AS")
    )
    db_field: Mapped[Optional[str]] = mapped_column(String(50, "Latin1_General_CI_AS"))
    db_table: Mapped[Optional[str]] = mapped_column(String(50, "Latin1_General_CI_AS"))

    RR_VALIDATION_ERROR_LOG: Mapped[List["RRVALIDATIONERRORLOG"]] = relationship(
        "RRVALIDATIONERRORLOG", back_populates="RR_VALIDATION_ERROR"
    )


class RRVALIDATIONLOG(Base):
    __tablename__ = "RR_VALIDATION_LOG"
    __table_args__ = (PrimaryKeyConstraint("id", name="PK_RR_VALIDATION_LOG"),)

    id: Mapped[int] = mapped_column(
        Integer, Identity(start=1, increment=1), primary_key=True
    )
    site: Mapped[str] = mapped_column(Unicode(8, "Latin1_General_CI_AS"))
    quarter: Mapped[int] = mapped_column(SmallInteger)
    is_loading: Mapped[bool] = mapped_column(Boolean, server_default=text("((0))"))
    updated: Mapped[datetime.datetime] = mapped_column(DATETIME2)

    RR_VALIDATION_ERROR_LOG: Mapped[List["RRVALIDATIONERRORLOG"]] = relationship(
        "RRVALIDATIONERRORLOG", back_populates="RR_VALIDATION_LOG"
    )


class STUDYPATIENTS(Base):
    __tablename__ = "STUDY_PATIENTS"
    __table_args__ = (
        PrimaryKeyConstraint(
            "STUDY_ID", "STUDY_PATIENT_ID", name="PK_STUDY_PATIENTS_1"
        ),
    )

    STUDY_ID: Mapped[str] = mapped_column(
        String(50, "Latin1_General_CI_AS"), primary_key=True
    )
    STUDY_PATIENT_ID: Mapped[str] = mapped_column(
        String(50, "Latin1_General_CI_AS"), primary_key=True
    )
    RR_NO: Mapped[Optional[int]] = mapped_column(BigInteger)
    NHS_NO: Mapped[Optional[int]] = mapped_column(BigInteger)
    MATCH_RANK: Mapped[Optional[str]] = mapped_column(NCHAR(10, "Latin1_General_CI_AS"))


t_SYS_TAKEON = Table(
    "SYS_TAKEON",
    Base.metadata,
    Column("TREATMENT_MODALITY", String(50, "Latin1_General_CI_AS")),
    Column("TREATMENT_CENTRE", String(50, "Latin1_General_CI_AS")),
    Column("DATE_START", DateTime),
    Column("RR_NO", BigInteger),
    Column("HOSP_CENTRE", String(50, "Latin1_General_CI_AS")),
    Column("YEAR_END_SEQ", Integer),
)


t_TBL_PATIENT_ALIASES = Table(
    "TBL_PATIENT_ALIASES",
    Base.metadata,
    Column("RR_NO", BigInteger, nullable=False),
    Column("SURNAME", Unicode(50, "Latin1_General_CI_AS"), nullable=False),
    Column("FORENAME", Unicode(50, "Latin1_General_CI_AS"), nullable=False),
    Column("DATE_BIRTH", DateTime, nullable=False),
    Column("SOUNDEX_SURNAME", String(5, "Latin1_General_CI_AS")),
    Column("SOUNDEX_FORENAME", String(5, "Latin1_General_CI_AS")),
)


t_TBL_VWE_UKT_RR_PATIENTS = Table(
    "TBL_VWE_UKT_RR_PATIENTS",
    Base.metadata,
    Column("UNDELETED_RR_NO", BigInteger),
    Column("RR_NO", BigInteger),
    Column("UKT_UKTSSA_NO", BigInteger),
    Column("SURNAME", Unicode(50, "Latin1_General_CI_AS")),
    Column("FORENAME", Unicode(50, "Latin1_General_CI_AS")),
    Column("DATE_BIRTH", DateTime),
    Column("DATE_DEATH", DateTime),
    Column("TRACING_DATE_DEATH", DateTime),
    Column("NEW_NHS_NO", BigInteger),
    Column("CHI_NO", BigInteger),
    Column("SCOT_REG_NO", Unicode(10, "Latin1_General_CI_AS")),
    Column("LOCAL_HOSP_NO", Unicode(15, "Latin1_General_CI_AS")),
    Column("HOSP_CENTRE", Unicode(8, "Latin1_General_CI_AS")),
    Column("UKTSSA_NO", BigInteger),
    Column("PATIENT_TYPE", String(26, "Latin1_General_CI_AS"), nullable=False),
    Column("SOUNDEX_SURNAME", String(5, "Latin1_General_CI_AS")),
    Column("SOUNDEX_FORENAME", String(5, "Latin1_General_CI_AS")),
)


t_TEMP_TREATMENTS = Table(
    "TEMP_TREATMENTS",
    Base.metadata,
    Column("RR_NO", Integer),
    Column("FROM_TIME", DateTime),
    Column("ADMITREASONCODE", String(3, "Latin1_General_CI_AS")),
    Column("HEALTHCAREFACILITYCODE", String(10, "Latin1_General_CI_AS")),
    Column("TO_TIME", DateTime),
    Column("DISCHARGEREASONCODE", String(3, "Latin1_General_CI_AS")),
    Column("DISCHARGELOCATION", String(10, "Latin1_General_CI_AS")),
)


class TRANSPLANT(Base):
    __tablename__ = "TRANSPLANT"
    __table_args__ = (
        PrimaryKeyConstraint(
            "RR_NO", "HOSP_CENTRE", "TRANSPLANT_DATE", name="PK_TRANSPLANT"
        ),
    )

    RR_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    HOSP_CENTRE: Mapped[str] = mapped_column(
        String(20, "Latin1_General_CI_AS"), primary_key=True
    )
    TRANSPLANT_DATE: Mapped[datetime.datetime] = mapped_column(
        DateTime, primary_key=True
    )
    TRANSPLANT_NUMBER: Mapped[Optional[int]] = mapped_column(Integer)
    TRANSPLANT_FAILURE: Mapped[Optional[str]] = mapped_column(
        String(1, "Latin1_General_CI_AS")
    )
    FAILURE_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    FAILURE_CAUSE: Mapped[Optional[int]] = mapped_column(Integer)
    FAILURE_DESCRIPTION: Mapped[Optional[str]] = mapped_column(
        Unicode(255, "Latin1_General_CI_AS")
    )
    GRAFT_NEPHRECTOMY_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime
    )
    UKT_TRANSPLANT_NUMBER: Mapped[Optional[int]] = mapped_column(BigInteger)
    PRE_GRAFT_TREATMENT: Mapped[Optional[str]] = mapped_column(
        String(4, "Latin1_General_CI_AS")
    )
    LISTED_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    TRANSPLANT_CENTRE: Mapped[Optional[str]] = mapped_column(
        String(20, "Latin1_General_CI_AS")
    )
    TRANSPLANT_ABROAD: Mapped[Optional[str]] = mapped_column(
        String(50, "Latin1_General_CI_AS")
    )
    REMAINING_KIDNEYS: Mapped[Optional[int]] = mapped_column(Integer)
    GRAFT_TYPE: Mapped[Optional[int]] = mapped_column(Integer)
    NHSBT_TYPE: Mapped[Optional[str]] = mapped_column(String(5, "Latin1_General_CI_AS"))
    RCMV_STATUS: Mapped[Optional[str]] = mapped_column(
        String(3, "Latin1_General_CI_AS")
    )
    REBV_STATUS: Mapped[Optional[str]] = mapped_column(
        String(3, "Latin1_General_CI_AS")
    )
    DONOR_AGE: Mapped[Optional[int]] = mapped_column(Integer)
    DONOR_SEX: Mapped[Optional[str]] = mapped_column(String(1, "Latin1_General_CI_AS"))
    DCMV_STATUS: Mapped[Optional[str]] = mapped_column(
        String(3, "Latin1_General_CI_AS")
    )
    DEBV_STATUS: Mapped[Optional[str]] = mapped_column(
        String(3, "Latin1_General_CI_AS")
    )
    MISMATCH_A: Mapped[Optional[int]] = mapped_column(Integer)
    MISMATCH_B: Mapped[Optional[int]] = mapped_column(Integer)
    MISMATCH_DR: Mapped[Optional[int]] = mapped_column(Integer)
    ABO_COMPATIBLE: Mapped[Optional[str]] = mapped_column(
        String(1, "Latin1_General_CI_AS")
    )
    PLASMA_EXCHANGE: Mapped[Optional[str]] = mapped_column(
        String(1, "Latin1_General_CI_AS")
    )
    IMMUNOADSORPTION: Mapped[Optional[str]] = mapped_column(
        String(1, "Latin1_General_CI_AS")
    )
    RITUXIMAB: Mapped[Optional[str]] = mapped_column(String(1, "Latin1_General_CI_AS"))
    IV_IMMUNOGLOBULIN: Mapped[Optional[str]] = mapped_column(
        String(1, "Latin1_General_CI_AS")
    )
    COLD_ISCHAEMIC_TIME: Mapped[Optional[decimal.Decimal]] = mapped_column(
        DECIMAL(18, 0)
    )
    PRIMARY_FUNCTION: Mapped[Optional[str]] = mapped_column(
        String(1, "Latin1_General_CI_AS")
    )
    ANTICOAGULATION: Mapped[Optional[int]] = mapped_column(Integer)
    CMV_PROPHYLAXIS: Mapped[Optional[int]] = mapped_column(Integer)
    PNEUMOCYSTIS_PROPHYLAXIS: Mapped[Optional[int]] = mapped_column(Integer)
    FUNCTIONING: Mapped[Optional[str]] = mapped_column(
        String(1, "Latin1_General_CI_AS")
    )
    OTHER_ORGAN_TX_1: Mapped[Optional[int]] = mapped_column(Integer)
    OTHER_ORGAN_TX_2: Mapped[Optional[int]] = mapped_column(Integer)


class TREATMENT(Base):
    __tablename__ = "TREATMENT"
    __table_args__ = (
        PrimaryKeyConstraint(
            "RR_NO",
            "DATE_START",
            "TREATMENT_MODALITY",
            "HOSP_CENTRE",
            "TREATMENT_CENTRE",
            name="PK_TREATMENT",
        ),
        Index("IX_TREATMENT_8_7", "DATE_START"),
        Index("Missing_IXNC_TREATMENT_TREATMENT_MODALITY_487EB", "TREATMENT_MODALITY"),
        Index(
            "_dta_index_TREATMENT_7_276300144__K1_K20_K2D_K4",
            "RR_NO",
            "HOSP_CENTRE",
            "DATE_START",
            "TREATMENT_MODALITY",
        ),
        Index(
            "_dta_index_TREATMENT_7_276300144__K1_K2D_K16_K20_K4",
            "RR_NO",
            "DATE_START",
            "TREATMENT_CENTRE",
            "HOSP_CENTRE",
            "TREATMENT_MODALITY",
        ),
        Index(
            "_dta_index_TREATMENT_7_276300144__K20_K4_K2_K1_K16",
            "HOSP_CENTRE",
            "TREATMENT_MODALITY",
            "DATE_START",
            "RR_NO",
            "TREATMENT_CENTRE",
        ),
    )

    RR_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    DATE_START: Mapped[datetime.datetime] = mapped_column(DateTime, primary_key=True)
    TREATMENT_MODALITY: Mapped[str] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS"), primary_key=True
    )
    TREATMENT_CENTRE: Mapped[str] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS"), primary_key=True
    )
    HOSP_CENTRE: Mapped[str] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS"), primary_key=True
    )
    DATE_END: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    ADD_HAEMO_ON_PD: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    CHANGE_TREATMENT: Mapped[Optional[str]] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS")
    )
    HAEMO_DIAL_ACCESS: Mapped[Optional[str]] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS")
    )
    FGS_SITE: Mapped[Optional[str]] = mapped_column(Unicode(8, "Latin1_General_CI_AS"))
    HD_CATHETER_SITE: Mapped[Optional[str]] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS")
    )
    DIALYSER_USED: Mapped[Optional[str]] = mapped_column(
        Unicode(8, "Latin1_General_CI_AS")
    )
    FLOW_RATE: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    DIAL_REUSE: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    TIMES_PER_WEEK: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    DIAL_TIME: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    BICARB_DIAL: Mapped[Optional[str]] = mapped_column(
        Unicode(1, "Latin1_General_CI_AS")
    )
    HD_SUPERVISON: Mapped[Optional[str]] = mapped_column(
        Unicode(4, "Latin1_General_CI_AS")
    )
    WEEKLY_FLUID_VOL: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    BAG_SIZE: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    LOAD_IND: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    DISPLAY_SEQ: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    YEAR_END_SEQ: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(38, 4))
    TRANSFER_IN_FROM: Mapped[Optional[str]] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS")
    )
    TRANSFER_OUT_TO: Mapped[Optional[str]] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS")
    )


class TREATMENTCHANGEREASONS(Base):
    __tablename__ = "TREATMENT_CHANGE_REASONS"
    __table_args__ = (
        PrimaryKeyConstraint("CODE", name="PK__TREATMEN__AA1D4378857516B0"),
    )

    CODE: Mapped[int] = mapped_column(Integer, primary_key=True)
    MODALITY_GROUP: Mapped[str] = mapped_column(String(4, "Latin1_General_CI_AS"))


class UKTPATIENTS(Base):
    __tablename__ = "UKT_PATIENTS"
    __table_args__ = (
        PrimaryKeyConstraint("UKTSSA_NO", name="PK_UKT_PATIENTS"),
        Index("IX_UKT_PATIENTS_RR_NO_UKT_NO", "RR_NO"),
        Index("_dta_index_UKT_PATIENTS_7_960826585__K1_7", "UKTSSA_NO"),
        Index("_dta_index_UKT_PATIENTS_7_960826585__K7", "RR_NO"),
        Index(
            "_dta_index_UKT_PATIENTS_7_960826585__K7_K1_2_6_9_10_11",
            "RR_NO",
            "UKTSSA_NO",
        ),
    )

    UKTSSA_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    SURNAME: Mapped[Optional[str]] = mapped_column(Unicode(50, "Latin1_General_CI_AS"))
    FORENAME: Mapped[Optional[str]] = mapped_column(Unicode(50, "Latin1_General_CI_AS"))
    SEX: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    POST_CODE: Mapped[Optional[str]] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS")
    )
    NEW_NHS_NO: Mapped[Optional[int]] = mapped_column(BigInteger)
    CHI_NO: Mapped[Optional[int]] = mapped_column(BigInteger)
    HSC_NO: Mapped[Optional[int]] = mapped_column(BigInteger)
    RR_NO: Mapped[Optional[int]] = mapped_column(BigInteger)
    UKT_DATE_DEATH: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    UKT_DATE_BIRTH: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    SOUNDEX_FORENAME: Mapped[Optional[str]] = mapped_column(
        String(5, "Latin1_General_CI_AS"),
        Computed("(soundex([dbo].[normalise_forename2]([FORENAME])))", persisted=True),
    )
    SOUNDEX_SURNAME: Mapped[Optional[str]] = mapped_column(
        String(5, "Latin1_General_CI_AS"),
        Computed("(soundex([dbo].[normalise_surname2]([SURNAME])))", persisted=True),
    )


class UKTPATIENTS20231129(Base):
    __tablename__ = "UKT_PATIENTS_20231129"
    __table_args__ = (
        PrimaryKeyConstraint("UKTSSA_NO", name="PK_UKT_PATIENTS_20231129"),
    )

    UKTSSA_NO: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    SURNAME: Mapped[Optional[str]] = mapped_column(Unicode(50, "Latin1_General_CI_AS"))
    FORENAME: Mapped[Optional[str]] = mapped_column(Unicode(50, "Latin1_General_CI_AS"))
    SEX: Mapped[Optional[str]] = mapped_column(Unicode(1, "Latin1_General_CI_AS"))
    POST_CODE: Mapped[Optional[str]] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS")
    )
    NEW_NHS_NO: Mapped[Optional[int]] = mapped_column(BigInteger)
    CHI_NO: Mapped[Optional[int]] = mapped_column(BigInteger)
    HSC_NO: Mapped[Optional[int]] = mapped_column(BigInteger)
    RR_NO: Mapped[Optional[int]] = mapped_column(BigInteger)
    UKT_DATE_DEATH: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    UKT_DATE_BIRTH: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    SOUNDEX_FORENAME: Mapped[Optional[str]] = mapped_column(
        String(5, "Latin1_General_CI_AS"),
        Computed("(soundex([dbo].[normalise_forename2]([FORENAME])))", persisted=True),
    )
    SOUNDEX_SURNAME: Mapped[Optional[str]] = mapped_column(
        String(5, "Latin1_General_CI_AS"),
        Computed("(soundex([dbo].[normalise_surname2]([SURNAME])))", persisted=True),
    )


class UKTSITES(Base):
    __tablename__ = "UKT_SITES"
    __table_args__ = (PrimaryKeyConstraint("SITE_NAME", name="PK_UKT_SITES"),)

    SITE_NAME: Mapped[str] = mapped_column(
        Unicode(50, "Latin1_General_CI_AS"), primary_key=True
    )
    RR_CODE: Mapped[str] = mapped_column(Unicode(8, "Latin1_General_CI_AS"))


class UKTTRANSPLANTS(Base):
    __tablename__ = "UKT_TRANSPLANTS"
    __table_args__ = (
        PrimaryKeyConstraint("REGISTRATION_ID", name="PK_UKT_TRANSPLANTS"),
        Index(
            "_dta_index_UKT_TRANSPLANTS_7_324300315__K1_K7_K5",
            "UKTSSA_NO",
            "TRANSPLANT_DATE",
            "TRANSPLANT_UNIT",
        ),
        Index(
            "_dta_index_UKT_TRANSPLANTS_7_324300315__K5_K7_K1",
            "TRANSPLANT_UNIT",
            "TRANSPLANT_DATE",
            "UKTSSA_NO",
        ),
        Index(
            "_dta_index_UKT_TRANSPLANTS_7_324300315__K6_K7_K1_3_4_8",
            "RR_NO",
            "TRANSPLANT_DATE",
            "UKTSSA_NO",
        ),
    )

    UKTSSA_NO: Mapped[int] = mapped_column(BigInteger)
    REGISTRATION_ID: Mapped[str] = mapped_column(
        Unicode(12, "Latin1_General_CI_AS"), primary_key=True
    )
    TRANSPLANT_ID: Mapped[Optional[int]] = mapped_column(BigInteger)
    TRANSPLANT_TYPE: Mapped[Optional[str]] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS")
    )
    TRANSPLANT_ORGAN: Mapped[Optional[str]] = mapped_column(
        Unicode(50, "Latin1_General_CI_AS")
    )
    TRANSPLANT_UNIT: Mapped[Optional[str]] = mapped_column(
        Unicode(50, "Latin1_General_CI_AS")
    )
    RR_NO: Mapped[Optional[int]] = mapped_column(BigInteger)
    TRANSPLANT_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    UKT_FAIL_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    REGISTRATION_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    REGISTRATION_DATE_TYPE: Mapped[Optional[str]] = mapped_column(
        Unicode(12, "Latin1_General_CI_AS")
    )
    REGISTRATION_END_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    REGISTRATION_END_STATUS: Mapped[Optional[str]] = mapped_column(
        Unicode(12, "Latin1_General_CI_AS")
    )
    TRANSPLANT_CONSIDERATION: Mapped[Optional[str]] = mapped_column(
        Unicode(20, "Latin1_General_CI_AS")
    )
    TRANSPLANT_DIALYSIS: Mapped[Optional[str]] = mapped_column(
        Unicode(12, "Latin1_General_CI_AS")
    )
    TRANSPLANT_RELATIONSHIP: Mapped[Optional[str]] = mapped_column(
        Unicode(20, "Latin1_General_CI_AS")
    )
    TRANSPLANT_SEX: Mapped[Optional[str]] = mapped_column(
        Unicode(12, "Latin1_General_CI_AS")
    )
    CAUSE_OF_FAILURE: Mapped[Optional[str]] = mapped_column(
        String(10, "Latin1_General_CI_AS")
    )
    CAUSE_OF_FAILURE_TEXT: Mapped[Optional[str]] = mapped_column(
        String(500, "Latin1_General_CI_AS")
    )
    CIT_MINS: Mapped[Optional[str]] = mapped_column(String(10, "Latin1_General_CI_AS"))
    HLA_MISMATCH: Mapped[Optional[str]] = mapped_column(
        String(10, "Latin1_General_CI_AS")
    )
    UKT_SUSPENSION: Mapped[Optional[bool]] = mapped_column(Boolean)


class UKTTRANSPLANTS20231129(Base):
    __tablename__ = "UKT_TRANSPLANTS_20231129"
    __table_args__ = (
        PrimaryKeyConstraint("REGISTRATION_ID", name="PK_UKT_TRANSPLANTS_20231129"),
    )

    UKTSSA_NO: Mapped[int] = mapped_column(BigInteger)
    REGISTRATION_ID: Mapped[str] = mapped_column(
        Unicode(12, "Latin1_General_CI_AS"), primary_key=True
    )
    TRANSPLANT_ID: Mapped[Optional[int]] = mapped_column(BigInteger)
    TRANSPLANT_TYPE: Mapped[Optional[str]] = mapped_column(
        Unicode(10, "Latin1_General_CI_AS")
    )
    TRANSPLANT_ORGAN: Mapped[Optional[str]] = mapped_column(
        Unicode(50, "Latin1_General_CI_AS")
    )
    TRANSPLANT_UNIT: Mapped[Optional[str]] = mapped_column(
        Unicode(50, "Latin1_General_CI_AS")
    )
    RR_NO: Mapped[Optional[int]] = mapped_column(BigInteger)
    TRANSPLANT_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    UKT_FAIL_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    REGISTRATION_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    REGISTRATION_DATE_TYPE: Mapped[Optional[str]] = mapped_column(
        Unicode(12, "Latin1_General_CI_AS")
    )
    REGISTRATION_END_DATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    REGISTRATION_END_STATUS: Mapped[Optional[str]] = mapped_column(
        Unicode(12, "Latin1_General_CI_AS")
    )
    TRANSPLANT_CONSIDERATION: Mapped[Optional[str]] = mapped_column(
        Unicode(20, "Latin1_General_CI_AS")
    )
    TRANSPLANT_DIALYSIS: Mapped[Optional[str]] = mapped_column(
        Unicode(12, "Latin1_General_CI_AS")
    )
    TRANSPLANT_RELATIONSHIP: Mapped[Optional[str]] = mapped_column(
        Unicode(20, "Latin1_General_CI_AS")
    )
    TRANSPLANT_SEX: Mapped[Optional[str]] = mapped_column(
        Unicode(12, "Latin1_General_CI_AS")
    )
    CAUSE_OF_FAILURE: Mapped[Optional[str]] = mapped_column(
        String(10, "Latin1_General_CI_AS")
    )
    CAUSE_OF_FAILURE_TEXT: Mapped[Optional[str]] = mapped_column(
        String(500, "Latin1_General_CI_AS")
    )
    CIT_MINS: Mapped[Optional[str]] = mapped_column(String(10, "Latin1_General_CI_AS"))
    HLA_MISMATCH: Mapped[Optional[str]] = mapped_column(
        String(10, "Latin1_General_CI_AS")
    )
    UKT_SUSPENSION: Mapped[Optional[bool]] = mapped_column(Boolean)


t_UPLOAD_LOG = Table(
    "UPLOAD_LOG",
    Base.metadata,
    Column("RUN_DATE", DateTime),
    Column("SITE", Unicode(10, "Latin1_General_CI_AS")),
    Column("TYPE", Unicode(10, "Latin1_General_CI_AS")),
    Column("FILENAME", Unicode(260, "Latin1_General_CI_AS")),
    Column("PAT_COUNT", BigInteger),
    Column("SQL_COUNT", BigInteger),
    Column("QRT_NO", Integer),
)


t_VWE_ACUTE_PATIENTS = Table(
    "VWE_ACUTE_PATIENTS",
    Base.metadata,
    Column("RR_NO", BigInteger, nullable=False),
    Column("SURNAME", Unicode(30, "Latin1_General_CI_AS"), nullable=False),
    Column("FORENAME", Unicode(30, "Latin1_General_CI_AS"), nullable=False),
    Column("DATE_BIRTH", DateTime, nullable=False),
    Column("FIRST_SEEN_DATE", DateTime),
    Column("LATEST_DATE_START", DateTime, nullable=False),
    Column("LATEST_MODALITY", Unicode(8, "Latin1_General_CI_AS"), nullable=False),
    Column("EARLIEST_DATE_START", DateTime, nullable=False),
    Column("EARLIEST_MODALITY", Unicode(8, "Latin1_General_CI_AS"), nullable=False),
    Column("FIRST_TREAT_DATE", DateTime),
)


t_VWE_BIOCHEM_COMPLETENESS = Table(
    "VWE_BIOCHEM_COMPLETENESS",
    Base.metadata,
    Column("HOSP_CENTRE", Unicode(8, "Latin1_General_CI_AS"), nullable=False),
    Column("REGISTRY_CODE_TYPE", Unicode(3, "Latin1_General_CI_AS")),
    Column("QUARTERNUMBER", BigInteger),
    Column("PATIENT_COUNT", Integer),
    Column("CHANGE_PATIENT_COUNT", Integer),
    Column("PERCENT_CREATININE", Integer),
    Column("CHANGE_PERCENT_CREATININE", Integer),
    Column("PERCENT_HBA1C", Integer),
    Column("CHANGE_PERCENT_HBA1C", Integer),
    Column("PERCENT_HBA1C_MMOL", Integer),
    Column("CHANGE_PERCENT_HBA1C_MMOL", Integer),
    Column("PERCENT_UREA", Integer),
    Column("CHANGE_PERCENT_UREA", Integer),
    Column("PERCENT_URR", Integer),
    Column("CHANGE_PERCENT_URR", Integer),
    Column("PERCENT_HAEMOGLOBIN", Integer),
    Column("CHANGE_PERCENT_HAEMOGLOBIN", Integer),
    Column("PERCENT_FERRETIN", Integer),
    Column("CHANGE_PERCENT_FERRETIN", Integer),
    Column("PERCENT_IPTH", Integer),
    Column("CHANGE_PERCENT_IPTH", Integer),
    Column("PERCENT_ALBUMIN", Integer),
    Column("CHANGE_PERCENT_ALBUMIN", Integer),
    Column("PERCENT_CHOLESTEROL", Integer),
    Column("CHANGE_PERCENT_CHOLESTEROL", Integer),
    Column("PERCENT_PHOSPHATE", Integer),
    Column("CHANGE_PERCENT_PHOSPHATE", Integer),
    Column("PERCENT_CALCIUM_CORR", Integer),
    Column("CHANGE_PERCENT_CALCIUM_CORR", Integer),
    Column("PERCENT_CALCIUM_UNCORR", Integer),
    Column("CHANGE_PERCENT_CALCIUM_UNCORR", Integer),
    Column("PERCENT_DIASTOLIC_BP", Integer),
    Column("CHANGE_PERCENT_DIASTOLIC_BP", Integer),
    Column("PERCENT_SYSTOLIC_BP", Integer),
    Column("CHANGE_PERCENT_SYSTOLIC_BP", Integer),
    Column("PERCENT_BICARBONATE", Integer),
    Column("CHANGE_PERCENT_BICARBONATE", Integer),
)


t_VWE_BP_READINGS_ONLY = Table(
    "VWE_BP_READINGS_ONLY",
    Base.metadata,
    Column("RR_NO", BigInteger, nullable=False),
    Column("DATE_START", DateTime, nullable=False),
    Column("HOSP_CENTRE", Unicode(8, "Latin1_General_CI_AS"), nullable=False),
    Column("QUARTERNUMBER", BigInteger),
    Column("CREATININE", Numeric(38, 4)),
    Column("UREA", Numeric(38, 4)),
    Column("HAEMOGLOBIN", Numeric(38, 4)),
    Column("FERRETIN", Numeric(38, 4)),
    Column("ALBUMIN", Numeric(38, 4)),
    Column("DIASTOLIC_BP", Numeric(20, 0)),
    Column("POST_DIASTOLIC_BP", Numeric(20, 0)),
    Column("SYSTOLIC_BP", Numeric(20, 0)),
    Column("POST_SYSTOLIC_BP", Numeric(20, 0)),
)


t_VWE_BUSY_TRANSPLANT_DAYS = Table(
    "VWE_BUSY_TRANSPLANT_DAYS",
    Base.metadata,
    Column("RR_NO", BigInteger, nullable=False),
    Column("DATE_START", DateTime, nullable=False),
    Column("DATE_END", DateTime),
    Column("TREATMENT_MODALITY", Unicode(8, "Latin1_General_CI_AS"), nullable=False),
    Column("ADD_HAEMO_ON_PD", Unicode(1, "Latin1_General_CI_AS")),
    Column("CHANGE_TREATMENT", Unicode(8, "Latin1_General_CI_AS")),
    Column("HAEMO_DIAL_ACCESS", Unicode(8, "Latin1_General_CI_AS")),
    Column("FGS_SITE", Unicode(8, "Latin1_General_CI_AS")),
    Column("HD_CATHETER_SITE", Unicode(8, "Latin1_General_CI_AS")),
    Column("DIALYSER_USED", Unicode(8, "Latin1_General_CI_AS")),
    Column("FLOW_RATE", Numeric(38, 4)),
    Column("DIAL_REUSE", Unicode(1, "Latin1_General_CI_AS")),
    Column("TIMES_PER_WEEK", Numeric(20, 0)),
    Column("DIAL_TIME", Numeric(38, 4)),
    Column("BICARB_DIAL", Unicode(1, "Latin1_General_CI_AS")),
    Column("TREATMENT_CENTRE", Unicode(8, "Latin1_General_CI_AS"), nullable=False),
    Column("HD_SUPERVISON", Unicode(4, "Latin1_General_CI_AS")),
    Column("WEEKLY_FLUID_VOL", Numeric(38, 4)),
    Column("BAG_SIZE", Numeric(38, 4)),
    Column("HOSP_CENTRE", Unicode(8, "Latin1_General_CI_AS"), nullable=False),
    Column("LOAD_IND", Unicode(1, "Latin1_General_CI_AS")),
    Column("DISPLAY_SEQ", Numeric(38, 4)),
    Column("YEAR_END_SEQ", Numeric(38, 4)),
)


t_VWE_DELETED_PATIENTS = Table(
    "VWE_DELETED_PATIENTS",
    Base.metadata,
    Column("RR_NO", BigInteger),
    Column("DELETED_RR_NO", BigInteger, nullable=False),
    Column("SURNAME", Unicode(30, "Latin1_General_CI_AS"), nullable=False),
    Column("FORENAME", Unicode(30, "Latin1_General_CI_AS"), nullable=False),
    Column("HOSP_CENTRE", Unicode(8, "Latin1_General_CI_AS"), nullable=False),
    Column("AUDIT_DATE", DateTime),
    Column("DESCRIPTION", Unicode(1000, "Latin1_General_CI_AS")),
)


t_VWE_ESRF_EARLIEST = Table(
    "VWE_ESRF_EARLIEST",
    Base.metadata,
    Column("RR_NO", BigInteger, nullable=False),
    Column("FIRST_TREAT_DATE", DateTime),
    Column("FIRST_TREAT_WEIGHT", Numeric(38, 4)),
    Column("FIRST_TREAT_CREATININE", Numeric(38, 4)),
    Column("PRIMARY_DISEASE_CODE", Unicode(8, "Latin1_General_CI_AS")),
    Column("EDTA_DISEASE_CODE", Numeric(20, 0)),
    Column("SECONDARY_ESRF_1", Unicode(8, "Latin1_General_CI_AS")),
    Column("SECONDARY_ESRF_2", Unicode(8, "Latin1_General_CI_AS")),
    Column("SECONDARY_ESRF_3", Unicode(8, "Latin1_General_CI_AS")),
    Column("PRIMARY_DISEASE_TEXT", Unicode(70, "Latin1_General_CI_AS")),
    Column("ANGINA", Unicode(1, "Latin1_General_CI_AS")),
    Column("PREV_MI_LE3M", Unicode(1, "Latin1_General_CI_AS")),
    Column("PREV_MI_GT3M", Unicode(1, "Latin1_General_CI_AS")),
    Column("PREV_CAGB", Unicode(1, "Latin1_General_CI_AS")),
    Column("SMOKER", Unicode(1, "Latin1_General_CI_AS")),
    Column("COPD", Unicode(1, "Latin1_General_CI_AS")),
    Column("SYMPT_CEREBRO_VASC", Unicode(1, "Latin1_General_CI_AS")),
    Column("DIABETES_NON_ESRF", Unicode(1, "Latin1_General_CI_AS")),
    Column("MALIGNANCY", Unicode(1, "Latin1_General_CI_AS")),
    Column("LIVER_DISEASE", Unicode(1, "Latin1_General_CI_AS")),
    Column("CLAUDICATION", Unicode(1, "Latin1_General_CI_AS")),
    Column("ISCH_NEUROPATH_ULCERS", Unicode(1, "Latin1_General_CI_AS")),
    Column("ANGIOPLASTY_NC", Unicode(1, "Latin1_General_CI_AS")),
    Column("PVD_AMPUTATION", Unicode(1, "Latin1_General_CI_AS")),
    Column("ANTENATAL_DIAG", Unicode(1, "Latin1_General_CI_AS")),
    Column("ANTENATAL_TREAT", Unicode(1, "Latin1_General_CI_AS")),
    Column("PRETERM", Unicode(1, "Latin1_General_CI_AS")),
    Column("CEREBRAL_PALSY", Unicode(1, "Latin1_General_CI_AS")),
    Column("DEVEL_EDUC_HANDICAP", Unicode(1, "Latin1_General_CI_AS")),
    Column("CONGEN_HEART_DISEASE", Unicode(1, "Latin1_General_CI_AS")),
    Column("OTHER_CONGEN_ABNORM", Unicode(1, "Latin1_General_CI_AS")),
    Column("DOWNS_SYNDROME", Unicode(1, "Latin1_General_CI_AS")),
    Column("OTHER_CHROMO_ABNORM", Unicode(1, "Latin1_General_CI_AS")),
    Column("OTHER_SYNDROME", Unicode(1, "Latin1_General_CI_AS")),
    Column("NEURAL_TUBE_DEFECT", Unicode(1, "Latin1_General_CI_AS")),
    Column("DATE_CREAT_PRIOR_TO_ESRF", DateTime),
    Column("CREAT_PRIOR_TO_ESRF", Numeric(38, 4)),
    Column("DATE_HB_PRIOR_TO_ESRF", DateTime),
    Column("HB_PRIOR_TO_ESRF", Numeric(38, 4)),
    Column("ACCESS_USED_AT_FIRST_DIALYSIS", Unicode(10, "Latin1_General_CI_AS")),
    Column("HOSP_CENTRE", Unicode(10, "Latin1_General_CI_AS"), nullable=False),
    Column("EPISODE_OF_HEART_FAILURE", Unicode(1, "Latin1_General_CI_AS")),
    Column("ROWNUMBER", BigInteger),
)


t_VWE_FORMSTORM_DEMOGRAPHICS = Table(
    "VWE_FORMSTORM_DEMOGRAPHICS",
    Base.metadata,
    Column("RR_NO", BigInteger, nullable=False),
    Column("SURNAME", Unicode(50, "Latin1_General_CI_AS"), nullable=False),
    Column("FORENAME", Unicode(50, "Latin1_General_CI_AS"), nullable=False),
    Column("SEX", Unicode(1, "Latin1_General_CI_AS")),
    Column("DATE_BIRTH", DateTime, nullable=False),
    Column("NHS_IDENTIFIER", String(10, "Latin1_General_CI_AS")),
    Column("POST_CODE", Unicode(8, "Latin1_General_CI_AS")),
)


t_VWE_FORMSTORM_DEMOGRAPHICS_NEW = Table(
    "VWE_FORMSTORM_DEMOGRAPHICS_NEW",
    Base.metadata,
    Column("RR_NO", BigInteger, nullable=False),
    Column("SURNAME", Unicode(50, "Latin1_General_CI_AS"), nullable=False),
    Column("FORENAME", Unicode(50, "Latin1_General_CI_AS"), nullable=False),
    Column("SEX", Unicode(1, "Latin1_General_CI_AS")),
    Column("DATE_BIRTH", DateTime, nullable=False),
    Column("NHS_IDENTIFIER", BigInteger),
    Column("POST_CODE", Unicode(8, "Latin1_General_CI_AS")),
)


t_VWE_PRIMARY_KEYS = Table(
    "VWE_PRIMARY_KEYS",
    Base.metadata,
    Column("TABLE_NAME", Unicode(128, "Latin1_General_CI_AS"), nullable=False),
    Column("COLUMN_NAME", Unicode(128, "Latin1_General_CI_AS")),
    Column("POSITION", Integer, nullable=False),
    Column("STATUS", Boolean),
    Column("OWNER", Unicode(128, "Latin1_General_CI_AS"), nullable=False),
)


t_VWE_TRACING_PATIENTS = Table(
    "VWE_TRACING_PATIENTS", Base.metadata, Column("RR_NO", BigInteger, nullable=False)
)


t_VWE_TREATMENT_EARLIEST = Table(
    "VWE_TREATMENT_EARLIEST",
    Base.metadata,
    Column("RR_NO", BigInteger, nullable=False),
    Column("START_DATE", DateTime),
    Column("TREATMENT_MODALITY", Unicode(8, "Latin1_General_CI_AS")),
    Column("HOSP_CENTRE", Unicode(8, "Latin1_General_CI_AS")),
    Column("TREATMENT_CENTRE", Unicode(8, "Latin1_General_CI_AS")),
)


t_VWE_TXT_BUSY_DAYS = Table(
    "VWE_TXT_BUSY_DAYS",
    Base.metadata,
    Column("HOSP_CENTRE", Unicode(8, "Latin1_General_CI_AS"), nullable=False),
    Column("TXT_DATE", DateTime, nullable=False),
    Column("TXT_COUNT", Integer),
    Column("TXT_AVG_PER_DAY", Integer),
)


t_VWE_TXT_DAYS = Table(
    "VWE_TXT_DAYS",
    Base.metadata,
    Column("HOSP_CENTRE", Unicode(8, "Latin1_General_CI_AS"), nullable=False),
    Column("TXT_DATE", DateTime, nullable=False),
    Column("TXT_COUNT", Integer),
)


t_VWE_TXT_YEARS = Table(
    "VWE_TXT_YEARS",
    Base.metadata,
    Column("HOSP_CENTRE", Unicode(8, "Latin1_General_CI_AS"), nullable=False),
    Column("TXT_YEAR", Integer),
    Column("TXT_AVG_PER_DAY", Integer),
)


t_VWE_UKT_TRANSPLANT_EXPORT = Table(
    "VWE_UKT_TRANSPLANT_EXPORT",
    Base.metadata,
    Column("UKT_UKTSSA_NO", BigInteger, nullable=False),
    Column("UKT_TRANSPLANT_ID", BigInteger),
    Column("UKT_TRANSPLANT_TYPE", Unicode(10, "Latin1_General_CI_AS")),
    Column("UKT_TRANSPLANT_ORGAN", Unicode(50, "Latin1_General_CI_AS")),
    Column("UKT_TRANSPLANT_UNIT", Unicode(50, "Latin1_General_CI_AS")),
    Column("RR_RR_NO", BigInteger),
    Column("UKT_TRANSPLANT_DATE", DateTime),
    Column("UKT_FAIL_DATE", DateTime),
    Column("UKT_REGISTRATION_ID", Unicode(12, "Latin1_General_CI_AS"), nullable=False),
    Column("UKT_REGISTRATION_DATE", DateTime),
    Column("UKT_REGISTRATION_DATE_TYPE", Unicode(12, "Latin1_General_CI_AS")),
    Column("UKT_REGISTRATION_END_DATE", DateTime),
    Column("UKT_REGISTRATION_END_STATUS", Unicode(12, "Latin1_General_CI_AS")),
    Column("UKT_TRANSPLANT_DIALYSIS", Unicode(12, "Latin1_General_CI_AS")),
    Column("UKT_TRANSPLANT_RELATIONSHIP", Unicode(20, "Latin1_General_CI_AS")),
    Column("UKT_TRANSPLANT_SEX", Unicode(12, "Latin1_General_CI_AS")),
    Column("RR_PRE_REG_BLOCK_START", DateTime),
    Column("RR_PRE_REG_HOSP_CENTRE", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_REG_TREATMENT_CENTRE", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_REG_TREATMENT_MODALITY", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_TRAN_BLOCK_START", DateTime),
    Column("RR_PRE_TRAN_HOSP_CENTRE", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_TRAN_TREATMENT_CENTRE", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_TRAN_TREATMENT_MODALITY", Unicode(8, "Latin1_General_CI_AS")),
)


t_VWE_UKT_TRANSPLANT_EXPORT_NEW = Table(
    "VWE_UKT_TRANSPLANT_EXPORT_NEW",
    Base.metadata,
    Column("UKT_UKTSSA_NO", BigInteger, nullable=False),
    Column("UKT_TRANSPLANT_ID", BigInteger),
    Column("UKT_TRANSPLANT_TYPE", Unicode(10, "Latin1_General_CI_AS")),
    Column("UKT_TRANSPLANT_ORGAN", Unicode(50, "Latin1_General_CI_AS")),
    Column("UKT_TRANSPLANT_UNIT", Unicode(50, "Latin1_General_CI_AS")),
    Column("RR_RR_NO", BigInteger),
    Column("UKT_TRANSPLANT_DATE", DateTime),
    Column("UKT_FAIL_DATE", DateTime),
    Column("UKT_REGISTRATION_ID", Unicode(12, "Latin1_General_CI_AS"), nullable=False),
    Column("UKT_REGISTRATION_DATE", DateTime),
    Column("UKT_REGISTRATION_DATE_TYPE", Unicode(12, "Latin1_General_CI_AS")),
    Column("UKT_REGISTRATION_END_DATE", DateTime),
    Column("UKT_REGISTRATION_END_STATUS", Unicode(12, "Latin1_General_CI_AS")),
    Column("UKT_TRANSPLANT_DIALYSIS", Unicode(12, "Latin1_General_CI_AS")),
    Column("UKT_TRANSPLANT_RELATIONSHIP", Unicode(20, "Latin1_General_CI_AS")),
    Column("UKT_TRANSPLANT_SEX", Unicode(12, "Latin1_General_CI_AS")),
    Column("RR_PRE_REG_BLOCK_START", DateTime),
    Column("RR_PRE_REG_HOSP_CENTRE", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_REG_TREATMENT_CENTRE", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_REG_TREATMENT_MODALITY", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_TRAN_BLOCK_START", DateTime),
    Column("RR_PRE_TRAN_HOSP_CENTRE", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_TRAN_TREATMENT_CENTRE", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_TRAN_TREATMENT_MODALITY", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_FIRST_HOSP_CENTRE", Unicode(8, "Latin1_General_CI_AS")),
    Column("FIRST_DATE_START", DateTime),
    Column("FIRST_MODALITY", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_RECENT_HOSP_CENTRE", Unicode(8, "Latin1_General_CI_AS")),
    Column("RECENT_DATE_START", DateTime),
    Column("RECENT_MODALITY", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_QUA_HOSP_CENTRE", Unicode(8, "Latin1_General_CI_AS")),
    Column("PRE_QUA_DATE_START", DateTime),
    Column("PRE_QUA_MODALITY", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_TXT_HOSP_CENTRE", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_TXT_TREATMENT_CENTRE", Unicode(8, "Latin1_General_CI_AS")),
    Column("PRE_TXT_DATE_START", DateTime),
    Column("PRE_TXT_MODALITY", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_PRE_QUA_HOSP_CENTRE", Unicode(8, "Latin1_General_CI_AS")),
    Column("PRE_PRE_QUA_DATE_START", DateTime),
    Column("PRE_PRE_QUA_MODALITY", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_REG_QUA_HOSP_CENTRE", Unicode(8, "Latin1_General_CI_AS")),
    Column("PRE_REG_QUA_DATE_START", DateTime),
    Column("PRE_REG_QUA_MODALITY", Unicode(8, "Latin1_General_CI_AS")),
)


t_VWE_UKT_TRANSPLANT_EXTRACT_NEW = Table(
    "VWE_UKT_TRANSPLANT_EXTRACT_NEW",
    Base.metadata,
    Column("RR_NO", BigInteger, nullable=False),
    Column("UKT_UKTSSA_NO", BigInteger),
    Column("UKTR_DDATE", Date),
    Column("RR_DDATE", Date),
    Column("DBS_DDATE", Date),
    Column("RR_FIRST_DIALYSIS_DATE", Date),
    Column("UKTR_DATE_ON1", Date),
    Column("UKTR_LIST_STATUS1", Unicode(12, "Latin1_General_CI_AS")),
    Column("UKTR_ENDSTAT1", Unicode(12, "Latin1_General_CI_AS")),
    Column("UKTR_TXT_LIST1", Unicode(50, "Latin1_General_CI_AS")),
    Column("UKTR_REMOVAL_DATE1", Date),
    Column("UKTR_TX_ID1", BigInteger),
    Column("UKTR_TXDATE1", Date),
    Column("UKTR_DGRP1", Unicode(10, "Latin1_General_CI_AS")),
    Column("UKTR_TX_UNIT1", Unicode(50, "Latin1_General_CI_AS")),
    Column("UKTR_FAILDATE1", Date),
    Column("UKTR_RELATIONSHIP1", Unicode(20, "Latin1_General_CI_AS")),
    Column("UKTR_DSEX1", Unicode(12, "Latin1_General_CI_AS")),
    Column("RR_DIALYSIS_START_DATE1", Date),
    Column("RR_DIALYSIS_CENTRE1", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_DIALYSIS_MODALITY1", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_FIRST_HOSP_CENTRE1", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_RECENT_HOSP_CENTRE1", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_QUA_HOSP_CENTRE1", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_TXT_HOSP_CENTRE1", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_TXT_TREATMENT_CENTRE1", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_PRE_QUA_HOSP_CENTRE1", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_REG_QUA_HOSP_CENTRE1", Unicode(8, "Latin1_General_CI_AS")),
    Column("UKTR_DATE_ON2", Date),
    Column("UKTR_LIST_STATUS2", Unicode(12, "Latin1_General_CI_AS")),
    Column("UKTR_ENDSTAT2", Unicode(12, "Latin1_General_CI_AS")),
    Column("UKTR_TXT_LIST2", Unicode(50, "Latin1_General_CI_AS")),
    Column("UKTR_REMOVAL_DATE2", Date),
    Column("UKTR_TX_ID2", BigInteger),
    Column("UKTR_TXDATE2", Date),
    Column("UKTR_DGRP2", Unicode(10, "Latin1_General_CI_AS")),
    Column("UKTR_TX_UNIT2", Unicode(50, "Latin1_General_CI_AS")),
    Column("UKTR_FAILDATE2", Date),
    Column("UKTR_RELATIONSHIP2", Unicode(20, "Latin1_General_CI_AS")),
    Column("UKTR_DSEX2", Unicode(12, "Latin1_General_CI_AS")),
    Column("RR_DIALYSIS_START_DATE2", Date),
    Column("RR_DIALYSIS_CENTRE2", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_DIALYSIS_MODALITY2", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_FIRST_HOSP_CENTRE2", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_RECENT_HOSP_CENTRE2", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_QUA_HOSP_CENTRE2", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_TXT_HOSP_CENTRE2", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_TXT_TREATMENT_CENTRE2", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_PRE_QUA_HOSP_CENTRE2", Unicode(8, "Latin1_General_CI_AS")),
    Column("RRPRE_REG_QUA_HOSP_CENTRE2", Unicode(8, "Latin1_General_CI_AS")),
    Column("UKTR_DATE_ON3", Date),
    Column("UKTR_LIST_STATUS3", Unicode(12, "Latin1_General_CI_AS")),
    Column("UKTR_ENDSTAT3", Unicode(12, "Latin1_General_CI_AS")),
    Column("UKTR_TXT_LIST3", Unicode(50, "Latin1_General_CI_AS")),
    Column("UKTR_REMOVAL_DATE3", Date),
    Column("UKTR_TX_ID3", BigInteger),
    Column("UKTR_TXDATE3", Date),
    Column("UKTR_DGRP3", Unicode(10, "Latin1_General_CI_AS")),
    Column("UKTR_TX_UNIT3", Unicode(50, "Latin1_General_CI_AS")),
    Column("UKTR_FAILDATE3", Date),
    Column("UKTR_RELATIONSHIP3", Unicode(20, "Latin1_General_CI_AS")),
    Column("UKTR_DSEX3", Unicode(12, "Latin1_General_CI_AS")),
    Column("RR_DIALYSIS_START_DATE3", Date),
    Column("RR_DIALYSIS_CENTRE3", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_DIALYSIS_MODALITY3", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_FIRST_HOSP_CENTRE3", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_RECENT_HOSP_CENTRE3", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_QUA_HOSP_CENTRE3", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_TXT_HOSP_CENTRE3", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_TXT_TREATMENT_CENTRE3", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_PRE_QUA_HOSP_CENTRE3", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_REG_QUA_HOSP_CENTRE3", Unicode(8, "Latin1_General_CI_AS")),
    Column("UKTR_DATE_ON4", Date),
    Column("UKTR_LIST_STATUS4", Unicode(12, "Latin1_General_CI_AS")),
    Column("UKTR_ENDSTAT4", Unicode(12, "Latin1_General_CI_AS")),
    Column("UKTR_TXT_LIST4", Unicode(50, "Latin1_General_CI_AS")),
    Column("UKTR_REMOVAL_DATE4", Date),
    Column("UKTR_TX_ID4", BigInteger),
    Column("UKTR_TXDATE4", Date),
    Column("UKTR_DGRP4", Unicode(10, "Latin1_General_CI_AS")),
    Column("UKTR_TX_UNIT4", Unicode(50, "Latin1_General_CI_AS")),
    Column("UKTR_FAILDATE4", Date),
    Column("UKTR_RELATIONSHIP4", Unicode(20, "Latin1_General_CI_AS")),
    Column("UKTR_DSEX4", Unicode(12, "Latin1_General_CI_AS")),
    Column("RR_DIALYSIS_START_DATE4", Date),
    Column("RR_DIALYSIS_CENTRE4", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_DIALYSIS_MODALITY4", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_FIRST_HOSP_CENTRE4", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_RECENT_HOSP_CENTRE4", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_QUA_HOSP_CENTRE4", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_TXT_HOSP_CENTRE4", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_TXT_TREATMENT_CENTRE4", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_PRE_QUA_HOSP_CENTRE4", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_REG_QUA_HOSP_CENTRE4", Unicode(8, "Latin1_General_CI_AS")),
    Column("UKTR_DATE_ON5", Date),
    Column("UKTR_LIST_STATUS5", Unicode(12, "Latin1_General_CI_AS")),
    Column("UKTR_ENDSTAT5", Unicode(12, "Latin1_General_CI_AS")),
    Column("UKTR_TXT_LIST5", Unicode(50, "Latin1_General_CI_AS")),
    Column("UKTR_REMOVAL_DATE5", Date),
    Column("UKTR_TX_ID5", BigInteger),
    Column("UKTR_TXDATE5", Date),
    Column("UKTR_DGRP5", Unicode(10, "Latin1_General_CI_AS")),
    Column("UKTR_TX_UNIT5", Unicode(50, "Latin1_General_CI_AS")),
    Column("UKTR_FAILDATE5", Date),
    Column("UKTR_RELATIONSHIP5", Unicode(20, "Latin1_General_CI_AS")),
    Column("UKTR_DSEX5", Unicode(12, "Latin1_General_CI_AS")),
    Column("RR_DIALYSIS_START_DATE5", Date),
    Column("RR_DIALYSIS_CENTRE5", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_DIALYSIS_MODALITY5", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_FIRST_HOSP_CENTRE5", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_RECENT_HOSP_CENTRE5", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_QUA_HOSP_CENTRE5", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_TXT_HOSP_CENTRE5", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_TXT_TREATMENT_CENTRE5", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_PRE_QUA_HOSP_CENTRE5", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_PRE_REG_QUA_HOSP_CENTRE5", Unicode(8, "Latin1_General_CI_AS")),
    Column("UKTR_DATE_ON6", Date),
    Column("UKTR_LIST_STATUS6", Unicode(12, "Latin1_General_CI_AS")),
    Column("UKTR_ENDSTAT6", Unicode(12, "Latin1_General_CI_AS")),
    Column("UKTR_TXT_LIST6", Unicode(50, "Latin1_General_CI_AS")),
    Column("UKTR_REMOVAL_DATE6", Date),
    Column("UKTR_TX_ID6", BigInteger),
    Column("UKTR_TXDATE6", Date),
    Column("UKTR_DGRP6", Unicode(10, "Latin1_General_CI_AS")),
    Column("UKTR_TX_UNIT6", Unicode(50, "Latin1_General_CI_AS")),
    Column("UKTR_FAILDATE6", Date),
    Column("UKTR_RELATIONSHIP6", Unicode(20, "Latin1_General_CI_AS")),
    Column("UKTR_DSEX6", Unicode(12, "Latin1_General_CI_AS")),
    Column("RR_DIALYSIS_START_DATE6", Date),
    Column("RR_DIALYSIS_CENTRE6", Unicode(8, "Latin1_General_CI_AS")),
    Column("RR_DIALYSIS_MODALITY6", Unicode(8, "Latin1_General_CI_AS")),
)


t_patient_aliases = Table(
    "patient_aliases",
    Base.metadata,
    Column("RR_NO", BigInteger, nullable=False),
    Column("SURNAME", Unicode(30, "Latin1_General_CI_AS"), nullable=False),
    Column("FORENAME", Unicode(30, "Latin1_General_CI_AS"), nullable=False),
    Column("DATE_BIRTH", DateTime, nullable=False),
    Column("SOUNDEX_SURNAME", String(5, "Latin1_General_CI_AS")),
    Column("SOUNDEX_FORENAME", String(5, "Latin1_General_CI_AS")),
)


class Sysdiagrams(Base):
    __tablename__ = "sysdiagrams"
    __table_args__ = (
        PrimaryKeyConstraint("diagram_id", name="PK__sysdiagr__C2B05B615AFB08A5"),
        Index("UK_principal_name", "principal_id", "name", unique=True),
    )

    name: Mapped[str] = mapped_column(Unicode(128, "Latin1_General_CI_AS"))
    principal_id: Mapped[int] = mapped_column(Integer)
    diagram_id: Mapped[int] = mapped_column(
        Integer, Identity(start=1, increment=1), primary_key=True
    )
    version: Mapped[Optional[int]] = mapped_column(Integer)
    definition: Mapped[Optional[bytes]] = mapped_column(LargeBinary)


t_vwe_latest_involvement = Table(
    "vwe_latest_involvement",
    Base.metadata,
    Column("RR_NO", BigInteger, nullable=False),
    Column("HOSP_CENTRE", Unicode(8, "Latin1_General_CI_AS"), nullable=False),
    Column("LATEST_DATE_START", DateTime),
)


t_vwe_rr_patients = Table(
    "vwe_rr_patients",
    Base.metadata,
    Column("UNDELETED_RR_NO", BigInteger, nullable=False),
    Column("RR_NO", BigInteger),
    Column("UKTSSA_NO", BigInteger),
    Column("SURNAME", Unicode(30, "Latin1_General_CI_AS")),
    Column("FORENAME", Unicode(30, "Latin1_General_CI_AS")),
    Column("DATE_BIRTH", DateTime),
    Column("DATE_DEATH", DateTime),
    Column("TRACING_DATE_DEATH", DateTime),
    Column("NEW_NHS_NO", BigInteger),
    Column("CHI_NO", BigInteger),
    Column("SCOT_REG_NO", Unicode(10, "Latin1_General_CI_AS")),
    Column("LOCAL_HOSP_NO", Unicode(15, "Latin1_General_CI_AS")),
    Column("HOSP_CENTRE", Unicode(8, "Latin1_General_CI_AS")),
    Column("UKT_UKTSSA_NO", BigInteger),
    Column("SOUNDEX_SURNAME", String(5, "Latin1_General_CI_AS")),
    Column("SOUNDEX_FORENAME", String(5, "Latin1_General_CI_AS")),
)


t_vwe_sex_mismatch = Table(
    "vwe_sex_mismatch",
    Base.metadata,
    Column("Forename", String(255, "Latin1_General_CI_AS")),
    Column("Sex_A", Unicode(1, "Latin1_General_CI_AS")),
    Column("PatCount_A", Integer, nullable=False),
    Column("Sex_B", Unicode(1, "Latin1_General_CI_AS")),
    Column("PatCount_B", Integer, nullable=False),
)


t_vwe_ukt_rr_patients = Table(
    "vwe_ukt_rr_patients",
    Base.metadata,
    Column("UNDELETED_RR_NO", BigInteger),
    Column("RR_NO", BigInteger),
    Column("UKT_UKTSSA_NO", BigInteger),
    Column("SURNAME", Unicode(50, "Latin1_General_CI_AS")),
    Column("FORENAME", Unicode(50, "Latin1_General_CI_AS")),
    Column("DATE_BIRTH", DateTime),
    Column("DATE_DEATH", DateTime),
    Column("TRACING_DATE_DEATH", DateTime),
    Column("NEW_NHS_NO", BigInteger),
    Column("CHI_NO", BigInteger),
    Column("SCOT_REG_NO", Unicode(10, "Latin1_General_CI_AS")),
    Column("LOCAL_HOSP_NO", Unicode(15, "Latin1_General_CI_AS")),
    Column("HOSP_CENTRE", Unicode(8, "Latin1_General_CI_AS")),
    Column("UKTSSA_NO", BigInteger),
    Column("PATIENT_TYPE", String(26, "Latin1_General_CI_AS"), nullable=False),
    Column("SOUNDEX_SURNAME", String(5, "Latin1_General_CI_AS")),
    Column("SOUNDEX_FORENAME", String(5, "Latin1_General_CI_AS")),
    Column("HSC_NO", BigInteger),
)


class RRVALIDATIONERRORLOG(Base):
    __tablename__ = "RR_VALIDATION_ERROR_LOG"
    __table_args__ = (
        ForeignKeyConstraint(
            ["validation_error"],
            ["RR_VALIDATION_ERROR.id"],
            name="FK_RR_VALIDATION_ERROR_LOG_RR_VALIDATION_ERROR",
        ),
        ForeignKeyConstraint(
            ["validation_log"],
            ["RR_VALIDATION_LOG.id"],
            name="FK_RR_VALIDATION_ERROR_LOG_RR_VALIDATION_ERROR_LOG",
        ),
        PrimaryKeyConstraint("id", name="PK_RR_VALIDATION_ERROR_LOG"),
    )

    id: Mapped[int] = mapped_column(
        Integer, Identity(start=1, increment=1), primary_key=True
    )
    validation_log: Mapped[int] = mapped_column(Integer)
    validation_error: Mapped[int] = mapped_column(Integer)
    error_count: Mapped[int] = mapped_column(Integer, server_default=text("((0))"))

    RR_VALIDATION_ERROR: Mapped["RRVALIDATIONERROR"] = relationship(
        "RRVALIDATIONERROR", back_populates="RR_VALIDATION_ERROR_LOG"
    )
    RR_VALIDATION_LOG: Mapped["RRVALIDATIONLOG"] = relationship(
        "RRVALIDATIONLOG", back_populates="RR_VALIDATION_ERROR_LOG"
    )
