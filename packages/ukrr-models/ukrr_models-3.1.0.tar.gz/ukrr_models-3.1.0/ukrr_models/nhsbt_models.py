"""SQLAlchemy models for NHSBT"""

from sqlalchemy import Boolean, DateTime, Integer, MetaData, String
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, synonym

metadata = MetaData()
Base = declarative_base(metadata=metadata)


class UKTPatient(Base):
    __tablename__ = "UKT_PATIENTS"

    UKTSSA_NO: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=False
    )
    uktssa_no: Mapped[int] = synonym("UKTSSA_NO")

    SURNAME: Mapped[str] = mapped_column(String(50))
    surname: Mapped[str] = synonym("SURNAME")

    FORENAME: Mapped[str] = mapped_column(String(50))
    forename: Mapped[str] = synonym("FORENAME")

    SEX: Mapped[str] = mapped_column(String(1))
    sex: Mapped[str] = synonym("SEX")

    POST_CODE: Mapped[str] = mapped_column(String(10))
    post_code: Mapped[str] = synonym("POST_CODE")

    NEW_NHS_NO: Mapped[int] = mapped_column(Integer)
    new_nhs_no: Mapped[int] = synonym("NEW_NHS_NO")

    CHI_NO: Mapped[int] = mapped_column(Integer)
    chi_no: Mapped[int] = synonym("CHI_NO")

    HSC_NO: Mapped[int] = mapped_column(Integer)
    hsc_no: Mapped[int] = synonym("HSC_NO")

    RR_NO: Mapped[int] = mapped_column(Integer)
    rr_no: Mapped[int] = synonym("RR_NO")

    UKT_DATE_DEATH: Mapped[DateTime] = mapped_column(DateTime)
    ukt_date_death: Mapped[DateTime] = synonym("UKT_DATE_DEATH")

    UKT_DATE_BIRTH: Mapped[DateTime] = mapped_column(DateTime)
    ukt_date_birth: Mapped[DateTime] = synonym("UKT_DATE_BIRTH")


class UKTTransplant(Base):
    __tablename__ = "UKT_TRANSPLANTS"

    REGISTRATION_ID: Mapped[str] = mapped_column(String(12), primary_key=True)
    registration_id: Mapped[str] = synonym("REGISTRATION_ID")

    UKTSSA_NO: Mapped[int] = mapped_column(Integer)
    uktssa_no: Mapped[int] = synonym("UKTSSA_NO")

    TRANSPLANT_ID: Mapped[int] = mapped_column(Integer)
    transplant_id: Mapped[int] = synonym("TRANSPLANT_ID")

    TRANSPLANT_TYPE: Mapped[str] = mapped_column(String(10))
    transplant_type: Mapped[str] = synonym("TRANSPLANT_TYPE")

    TRANSPLANT_ORGAN: Mapped[str] = mapped_column(String(50))
    transplant_organ: Mapped[str] = synonym("TRANSPLANT_ORGAN")

    TRANSPLANT_UNIT: Mapped[str] = mapped_column(String(50))
    transplant_unit: Mapped[str] = synonym("TRANSPLANT_UNIT")

    RR_NO: Mapped[int] = mapped_column(Integer)
    rr_no: Mapped[int] = synonym("RR_NO")

    TRANSPLANT_DATE: Mapped[DateTime] = mapped_column(DateTime)
    transplant_date: Mapped[DateTime] = synonym("TRANSPLANT_DATE")

    UKT_FAIL_DATE: Mapped[DateTime] = mapped_column(DateTime)
    ukt_fail_date: Mapped[DateTime] = synonym("UKT_FAIL_DATE")

    REGISTRATION_DATE: Mapped[DateTime] = mapped_column(DateTime)
    registration_date: Mapped[DateTime] = synonym("REGISTRATION_DATE")

    REGISTRATION_DATE_TYPE: Mapped[str] = mapped_column(String(12))
    registration_date_type: Mapped[str] = synonym("REGISTRATION_DATE_TYPE")

    REGISTRATION_END_DATE: Mapped[DateTime] = mapped_column(DateTime)
    registration_end_date: Mapped[DateTime] = synonym("REGISTRATION_END_DATE")

    REGISTRATION_END_STATUS: Mapped[str] = mapped_column(String(12))
    registration_end_status: Mapped[str] = synonym("REGISTRATION_END_STATUS")

    TRANSPLANT_CONSIDERATION: Mapped[str] = mapped_column(String(20))
    transplant_consideration: Mapped[str] = synonym("TRANSPLANT_CONSIDERATION")

    TRANSPLANT_DIALYSIS: Mapped[str] = mapped_column(String(12))
    transplant_dialysis: Mapped[str] = synonym("TRANSPLANT_DIALYSIS")

    TRANSPLANT_RELATIONSHIP: Mapped[str] = mapped_column(String(20))
    transplant_relationship: Mapped[str] = synonym("TRANSPLANT_RELATIONSHIP")

    TRANSPLANT_SEX: Mapped[str] = mapped_column(String(12))
    transplant_sex: Mapped[str] = synonym("TRANSPLANT_SEX")

    CAUSE_OF_FAILURE: Mapped[str] = mapped_column(String(10))
    cause_of_failure: Mapped[str] = synonym("CAUSE_OF_FAILURE")

    CAUSE_OF_FAILURE_TEXT: Mapped[str] = mapped_column(String(500))
    cause_of_failure_text: Mapped[str] = synonym("CAUSE_OF_FAILURE_TEXT")

    CIT_MINS: Mapped[str] = mapped_column(String(10))
    cit_mins: Mapped[str] = synonym("CIT_MINS")

    HLA_MISMATCH: Mapped[str] = mapped_column(String(10))
    hla_mismatch: Mapped[str] = synonym("HLA_MISMATCH")

    UKT_SUSPENSION: Mapped[bool] = mapped_column(Boolean)
    ukt_suspension: Mapped[bool] = synonym("UKT_SUSPENSION")


class UKTSites(Base):
    __tablename__ = "UKT_SITES"

    SITE_NAME: Mapped[str] = mapped_column(String(50), primary_key=True)
    site_name: Mapped[str] = synonym("SITE_NAME")

    RR_CODE: Mapped[str] = mapped_column(String(8))
    rr_code: Mapped[str] = synonym("RR_CODE")
