from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, Field


class AddressPrintDto(BaseModel):
    address: str = Field(default="", alias="Address")
    city: str = Field(default="", alias="City")
    state: str = Field(default="", alias="State")
    zip_code: str = Field(default="", alias="ZipCode")
    country: str = Field(default="", alias="Country")

    class Config:
        populate_by_name = True


class CompanyPrintDto(BaseModel):
    id: Optional[UUID] = Field(default=None, alias="Id")
    name: str = Field(default="", alias="Name")
    address: str = Field(default="", alias="Address")
    city: str = Field(default="", alias="City")
    state: str = Field(default="", alias="State")
    state_code: str = Field(default="", alias="StateCode")
    gstin: str = Field(default="", alias="GSTIN")
    zip_code: str = Field(default="", alias="ZipCode")
    country: str = Field(default="", alias="Country")
    phone: str = Field(default="", alias="Phone")
    email: str = Field(default="", alias="Email")
    website: str = Field(default="", alias="Website")
    tax_id: str = Field(default="", alias="TaxId")
    logo_url: str = Field(default="", alias="LogoUrl")
    currency: str = Field(default="", alias="Currency")

    class Config:
        populate_by_name = True


class PartyPrintDto(BaseModel):
    id: Optional[UUID] = Field(default=None, alias="Id")
    name: str = Field(default="", alias="Name")
    code: str = Field(default="", alias="Code")
    category: str = Field(default="", alias="Category")
    billing_address: AddressPrintDto = Field(default_factory=AddressPrintDto, alias="BillingAddress")
    shipping_address: AddressPrintDto = Field(default_factory=AddressPrintDto, alias="ShippingAddress")
    phone: str = Field(default="", alias="Phone")
    email: str = Field(default="", alias="Email")
    website: str = Field(default="", alias="Website")
    tax_id: str = Field(default="", alias="TaxId")

    class Config:
        populate_by_name = True


class TransactionHeaderDto(BaseModel):
    id: Optional[UUID] = Field(default=None, alias="Id")
    transaction_number: str = Field(default="", alias="TransactionNumber")
    invoice_number: str = Field(default="", alias="InvoiceNumber")
    transaction_date: datetime = Field(default_factory=datetime.now, alias="TransactionDate")
    due_date: datetime = Field(default_factory=datetime.now, alias="DueDate")
    type: str = Field(default="", alias="Type")
    status: str = Field(default="", alias="Status")
    notes: str = Field(default="", alias="Notes")
    reference_number: str = Field(default="", alias="ReferenceNumber")
    payment_method: str = Field(default="", alias="PaymentMethod")

    class Config:
        populate_by_name = True


class TransactionItemVariantPrintDto(BaseModel):
    id: Optional[UUID] = Field(default=None, alias="Id")
    product_variant_id: Optional[UUID] = Field(default=None, alias="ProductVariantId")
    variant_code: str = Field(default="", alias="VariantCode")
    variant_name: str = Field(default="", alias="VariantName")
    quantity: Decimal = Field(default=Decimal("0"), alias="Quantity")
    unit_price: Decimal = Field(default=Decimal("0"), alias="UnitPrice")
    selling_price: Decimal = Field(default=Decimal("0"), alias="SellingPrice")
    description: str = Field(default="", alias="Description")

    class Config:
        populate_by_name = True


class TransactionItemPrintDto(BaseModel):
    id: Optional[UUID] = Field(default=None, alias="Id")
    serial_number: int = Field(default=0, alias="SerialNumber")
    product_id: Optional[UUID] = Field(default=None, alias="ProductId")
    product_code: str = Field(default="", alias="ProductCode")
    product_name: str = Field(default="", alias="ProductName")
    description: str = Field(default="", alias="Description")
    unit: str = Field(default="", alias="Unit")
    sku: str = Field(default="", alias="SKU")
    barcode: str = Field(default="", alias="Barcode")
    quantity: Decimal = Field(default=Decimal("0"), alias="Quantity")
    unit_price: Decimal = Field(default=Decimal("0"), alias="UnitPrice")
    discount_rate: Decimal = Field(default=Decimal("0"), alias="DiscountRate")
    discount_amount: Decimal = Field(default=Decimal("0"), alias="DiscountAmount")
    line_total: Decimal = Field(default=Decimal("0"), alias="LineTotal")
    variants: List[TransactionItemVariantPrintDto] = Field(default_factory=list, alias="Variants")

    class Config:
        populate_by_name = True


class TransactionTaxComponentPrintDto(BaseModel):
    id: Optional[UUID] = Field(default=None, alias="Id")
    tax_component_id: Optional[UUID] = Field(default=None, alias="TaxComponentId")
    component_name: str = Field(default="", alias="ComponentName")
    component_type: str = Field(default="", alias="ComponentType")
    rate: Decimal = Field(default=Decimal("0"), alias="Rate")
    amount: Decimal = Field(default=Decimal("0"), alias="Amount")
    description: str = Field(default="", alias="Description")
    is_applied: bool = Field(default=False, alias="IsApplied")
    applied_date: Optional[datetime] = Field(default=None, alias="AppliedDate")
    reference_number: str = Field(default="", alias="ReferenceNumber")

    class Config:
        populate_by_name = True


class TransactionTaxPrintDto(BaseModel):
    id: Optional[UUID] = Field(default=None, alias="Id")
    serial_number: int = Field(default=0, alias="SerialNumber")
    tax_id: Optional[UUID] = Field(default=None, alias="TaxId")
    tax_name: str = Field(default="", alias="TaxName")
    tax_description: str = Field(default="", alias="TaxDescription")
    tax_category: str = Field(default="", alias="TaxCategory")
    hsn_code: str = Field(default="", alias="HSNCode")
    taxable_amount: Decimal = Field(default=Decimal("0"), alias="TaxableAmount")
    tax_amount: Decimal = Field(default=Decimal("0"), alias="TaxAmount")
    calculation_method: str = Field(default="", alias="CalculationMethod")
    is_applied: bool = Field(default=False, alias="IsApplied")
    applied_date: Optional[datetime] = Field(default=None, alias="AppliedDate")
    reference_number: str = Field(default="", alias="ReferenceNumber")
    description: str = Field(default="", alias="Description")
    components: List[TransactionTaxComponentPrintDto] = Field(default_factory=list, alias="Components")

    class Config:
        populate_by_name = True


class TaxComponentSummaryDto(BaseModel):
    component_type: str = Field(default="", alias="ComponentType")
    component_name: str = Field(default="", alias="ComponentName")
    taxable_amount: Decimal = Field(default=Decimal("0"), alias="TaxableAmount")
    rate: Decimal = Field(default=Decimal("0"), alias="Rate")
    amount: Decimal = Field(default=Decimal("0"), alias="Amount")

    class Config:
        populate_by_name = True


class TransactionSummaryDto(BaseModel):
    sub_total: Decimal = Field(default=Decimal("0"), alias="SubTotal")
    total_discount_amount: Decimal = Field(default=Decimal("0"), alias="TotalDiscountAmount")
    taxable_amount: Decimal = Field(default=Decimal("0"), alias="TaxableAmount")
    total_tax_amount: Decimal = Field(default=Decimal("0"), alias="TotalTaxAmount")
    freight: Decimal = Field(default=Decimal("0"), alias="Freight")
    is_freight_included: bool = Field(default=False, alias="IsFreightIncluded")
    round_off: Decimal = Field(default=Decimal("0"), alias="RoundOff")
    total: Decimal = Field(default=Decimal("0"), alias="Total")
    paid_amount: Decimal = Field(default=Decimal("0"), alias="PaidAmount")
    balance_due: Decimal = Field(default=Decimal("0"), alias="BalanceDue")
    is_paid: bool = Field(default=False, alias="IsPaid")
    tax_components_summary: List[TaxComponentSummaryDto] = Field(default_factory=list, alias="TaxComponentsSummary")

    class Config:
        populate_by_name = True


class TransactionPrintDto(BaseModel):
    company: CompanyPrintDto = Field(default_factory=CompanyPrintDto, alias="Company")
    party: PartyPrintDto = Field(default_factory=PartyPrintDto, alias="Party")
    transaction_header: TransactionHeaderDto = Field(default_factory=TransactionHeaderDto, alias="TransactionHeader")
    items: List[TransactionItemPrintDto] = Field(default_factory=list, alias="Items")
    taxes: List[TransactionTaxPrintDto] = Field(default_factory=list, alias="Taxes")
    summary: TransactionSummaryDto = Field(default_factory=TransactionSummaryDto, alias="Summary")

    class Config:
        populate_by_name = True
