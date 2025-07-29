"""
EDI 835 (Electronic Remittance Advice) AST Definitions

This module defines the Abstract Syntax Tree nodes for EDI 835 
Electronic Remittance Advice transactions.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from ...base.edi_ast import Node


@dataclass
class FinancialInformation(Node):
    """Financial information from BPR segment."""
    total_paid: float
    payment_method: str
    payment_date: str

    # Backward compatibility properties
    @property
    def payment_amount(self):
        """Alias for total_paid for backward compatibility."""
        return self.total_paid

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_paid": self.total_paid,
            "payment_method": self.payment_method,
            "payment_date": self.payment_date,
        }


@dataclass
class Payer(Node):
    """Payer information from N1 segment."""
    name: str

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name}


@dataclass
class Payee(Node):
    """Payee information from N1 segment."""
    name: str
    npi: str
    tax_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "npi": self.npi, "tax_id": self.tax_id}


@dataclass
class Claim(Node):
    """Claim information from CLP segment."""
    claim_id: str
    status_code: str
    total_charge: float
    total_paid: float
    patient_responsibility: float
    payer_control_number: str
    adjustments: List['Adjustment'] = None
    services: List['Service'] = None
    
    def __post_init__(self):
        if self.adjustments is None:
            self.adjustments = []
        if self.services is None:
            self.services = []

    # Backward compatibility properties
    @property
    def charge_amount(self):
        """Alias for total_charge for backward compatibility."""
        return self.total_charge
    
    @property
    def payment_amount(self):
        """Alias for total_paid for backward compatibility."""
        return self.total_paid
    
    @property
    def patient_responsibility_amount(self):
        """Alias for patient_responsibility for backward compatibility."""
        return self.patient_responsibility

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "status_code": self.status_code,
            "total_charge": self.total_charge,
            "total_paid": self.total_paid,
            "patient_responsibility": self.patient_responsibility,
            "payer_control_number": self.payer_control_number,
            "adjustments": [adj.to_dict() for adj in self.adjustments],
            "services": [svc.to_dict() for svc in self.services],
        }


@dataclass
class Adjustment(Node):
    """Adjustment information from CAS segment."""
    group_code: str
    reason_code: str
    amount: float
    quantity: Optional[float] = None  # Can be None if not present

    def to_dict(self) -> Dict[str, Any]:
        return {
            "group_code": self.group_code,
            "reason_code": self.reason_code,
            "amount": self.amount,
            "quantity": self.quantity,
        }


@dataclass
class Service(Node):
    """Service information from SVC segment."""
    service_code: str
    charge_amount: float
    paid_amount: float
    revenue_code: str
    service_date: str
    
    # Additional fields for composite parsing
    procedure_code: Optional[str] = None
    modifier1: Optional[str] = None
    modifier2: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "service_code": self.service_code,
            "charge_amount": self.charge_amount,
            "paid_amount": self.paid_amount,
            "revenue_code": self.revenue_code,
            "service_date": self.service_date,
        }
        if self.procedure_code:
            data["procedure_code"] = self.procedure_code
        if self.modifier1:
            data["modifier1"] = self.modifier1
        if self.modifier2:
            data["modifier2"] = self.modifier2
        return data


@dataclass
class Transaction835(Node):
    """835 Electronic Remittance Advice Transaction."""
    header: Dict[str, str]
    financial_information: Optional[FinancialInformation] = None
    reference_numbers: List[Dict[str, str]] = None
    dates: List[Dict[str, str]] = None
    payer: Optional[Payer] = None
    payee: Optional[Payee] = None
    claims: List[Claim] = None
    
    # New fields for enhanced functionality
    plb: List[Dict[str, Any]] = None  # Provider Level Adjustments
    out_of_balance: bool = False
    balance_delta: Optional[float] = None
    segment_count_mismatch: bool = False
    
    def __post_init__(self):
        if self.reference_numbers is None:
            self.reference_numbers = []
        if self.dates is None:
            self.dates = []
        if self.claims is None:
            self.claims = []
        if self.plb is None:
            self.plb = []

    def to_dict(self) -> Dict[str, Any]:
        data = {"header": self.header}
        if self.financial_information:
            data["financial_information"] = self.financial_information.to_dict()
        if self.reference_numbers:
            data["reference_numbers"] = self.reference_numbers
        if self.dates:
            data["dates"] = self.dates
        if self.payer:
            data["payer"] = self.payer.to_dict()
        if self.payee:
            data["payee"] = self.payee.to_dict()
        if self.claims:
            data["claims"] = [claim.to_dict() for claim in self.claims]
        if self.plb:
            data["plb"] = self.plb
        data["out_of_balance"] = self.out_of_balance
        if self.balance_delta is not None:
            data["balance_delta"] = self.balance_delta
        data["segment_count_mismatch"] = self.segment_count_mismatch
        return data