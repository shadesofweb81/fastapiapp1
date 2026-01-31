from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, Field


class AddressPrintDto(BaseModel):
    address: str = Field(default="", alias="address")
    city: str = Field(default="", alias="city")
    state: str = Field(default="", alias="state")
    zip_code: str = Field(default="", alias="zipCode")
    country: str = Field(default="", alias="country")

    class Config:
        populate_by_name = True


class CompanyPrintDto(BaseModel):
    id: Optional[UUID] = Field(default=None, alias="id")
    name: str = Field(default="", alias="name")
    address: str = Field(default="", alias="address")
    city: str = Field(default="", alias="city")
    state: str = Field(default="", alias="state")
    state_code: str = Field(default="", alias="stateCode")
    gstin: str = Field(default="", alias="gstin")
    zip_code: str = Field(default="", alias="zipCode")
    country: str = Field(default="", alias="country")
    phone: str = Field(default="", alias="phone")
    email: str = Field(default="", alias="email")
    website: str = Field(default="", alias="website")
    tax_id: str = Field(default="", alias="taxId")
    logo_url: str = Field(default="", alias="logoUrl")
    currency: str = Field(default="", alias="currency")

    class Config:
        populate_by_name = True


class PartyPrintDto(BaseModel):
    id: Optional[UUID] = Field(default=None, alias="id")
    name: str = Field(default="", alias="name")
    code: str = Field(default="", alias="code")
    category: str = Field(default="", alias="category")
    billing_address: AddressPrintDto = Field(default_factory=AddressPrintDto, alias="billingAddress")
    shipping_address: AddressPrintDto = Field(default_factory=AddressPrintDto, alias="shippingAddress")
    phone: str = Field(default="", alias="phone")
    email: str = Field(default="", alias="email")
    website: str = Field(default="", alias="website")
    tax_id: str = Field(default="", alias="taxId")

    class Config:
        populate_by_name = True


class TransactionHeaderDto(BaseModel):
    id: Optional[UUID] = Field(default=None, alias="id")
    transaction_number: str = Field(default="", alias="transactionNumber")
    invoice_number: str = Field(default="", alias="invoiceNumber")
    transaction_date: datetime = Field(default_factory=datetime.now, alias="transactionDate")
    due_date: datetime = Field(default_factory=datetime.now, alias="dueDate")
    type: str = Field(default="", alias="type")
    status: str = Field(default="", alias="status")
    notes: str = Field(default="", alias="notes")
    reference_number: str = Field(default="", alias="referenceNumber")
    payment_method: str = Field(default="", alias="paymentMethod")
    place_of_supply: str = Field(default="", alias="placeOfSupply")

    class Config:
        populate_by_name = True


class TransactionItemVariantPrintDto(BaseModel):
    id: Optional[UUID] = Field(default=None, alias="id")
    product_variant_id: Optional[UUID] = Field(default=None, alias="productVariantId")
    variant_code: str = Field(default="", alias="variantCode")
    variant_name: str = Field(default="", alias="variantName")
    quantity: Decimal = Field(default=Decimal("0"), alias="quantity")
    unit_price: Decimal = Field(default=Decimal("0"), alias="unitPrice")
    selling_price: Decimal = Field(default=Decimal("0"), alias="sellingPrice")
    description: str = Field(default="", alias="description")

    class Config:
        populate_by_name = True


class TransactionItemPrintDto(BaseModel):
    id: Optional[UUID] = Field(default=None, alias="id")
    serial_number: int = Field(default=0, alias="serialNumber")
    product_id: Optional[UUID] = Field(default=None, alias="productId")
    product_code: str = Field(default="", alias="productCode")
    product_name: str = Field(default="", alias="productName")
    description: str = Field(default="", alias="description")
    hsn_code: str = Field(default="", alias="hsnCode")
    unit: str = Field(default="", alias="unit")
    sku: str = Field(default="", alias="sku")
    barcode: str = Field(default="", alias="barcode")
    quantity: Decimal = Field(default=Decimal("0"), alias="quantity")
    unit_price: Decimal = Field(default=Decimal("0"), alias="unitPrice")
    discount_rate: Decimal = Field(default=Decimal("0"), alias="discountRate")
    discount_amount: Decimal = Field(default=Decimal("0"), alias="discountAmount")
    line_total: Decimal = Field(default=Decimal("0"), alias="lineTotal")
    variants: List[TransactionItemVariantPrintDto] = Field(default_factory=list, alias="variants")

    class Config:
        populate_by_name = True


class TransactionTaxComponentPrintDto(BaseModel):
    id: Optional[UUID] = Field(default=None, alias="id")
    tax_component_id: Optional[UUID] = Field(default=None, alias="taxComponentId")
    component_name: str = Field(default="", alias="componentName")
    component_type: str = Field(default="", alias="componentType")
    rate: Decimal = Field(default=Decimal("0"), alias="rate")
    amount: Decimal = Field(default=Decimal("0"), alias="amount")
    description: str = Field(default="", alias="description")
    is_applied: bool = Field(default=False, alias="isApplied")
    applied_date: Optional[datetime] = Field(default=None, alias="appliedDate")
    reference_number: str = Field(default="", alias="referenceNumber")

    class Config:
        populate_by_name = True


class TransactionTaxPrintDto(BaseModel):
    id: Optional[UUID] = Field(default=None, alias="id")
    serial_number: int = Field(default=0, alias="serialNumber")
    tax_id: Optional[UUID] = Field(default=None, alias="taxId")
    tax_name: str = Field(default="", alias="taxName")
    tax_description: str = Field(default="", alias="taxDescription")
    tax_category: str = Field(default="", alias="taxCategory")
    hsn_code: str = Field(default="", alias="hsnCode")
    taxable_amount: Decimal = Field(default=Decimal("0"), alias="taxableAmount")
    tax_amount: Decimal = Field(default=Decimal("0"), alias="taxAmount")
    calculation_method: str = Field(default="", alias="calculationMethod")
    is_applied: bool = Field(default=False, alias="isApplied")
    applied_date: Optional[datetime] = Field(default=None, alias="appliedDate")
    reference_number: str = Field(default="", alias="referenceNumber")
    description: str = Field(default="", alias="description")
    components: List[TransactionTaxComponentPrintDto] = Field(default_factory=list, alias="components")

    class Config:
        populate_by_name = True


class TaxComponentSummaryDto(BaseModel):
    component_type: str = Field(default="", alias="componentType")
    component_name: str = Field(default="", alias="componentName")
    taxable_amount: Decimal = Field(default=Decimal("0"), alias="taxableAmount")
    rate: Decimal = Field(default=Decimal("0"), alias="rate")
    amount: Decimal = Field(default=Decimal("0"), alias="amount")

    class Config:
        populate_by_name = True


class TransactionSummaryDto(BaseModel):
    sub_total: Decimal = Field(default=Decimal("0"), alias="subTotal")
    total_discount_amount: Decimal = Field(default=Decimal("0"), alias="totalDiscountAmount")
    taxable_amount: Decimal = Field(default=Decimal("0"), alias="taxableAmount")
    total_tax_amount: Decimal = Field(default=Decimal("0"), alias="totalTaxAmount")
    freight: Decimal = Field(default=Decimal("0"), alias="freight")
    is_freight_included: bool = Field(default=False, alias="isFreightIncluded")
    round_off: Decimal = Field(default=Decimal("0"), alias="roundOff")
    total: Decimal = Field(default=Decimal("0"), alias="total")
    paid_amount: Decimal = Field(default=Decimal("0"), alias="paidAmount")
    balance_due: Decimal = Field(default=Decimal("0"), alias="balanceDue")
    is_paid: bool = Field(default=False, alias="isPaid")
    tax_components_summary: List[TaxComponentSummaryDto] = Field(default_factory=list, alias="taxComponentsSummary")

    class Config:
        populate_by_name = True


class TransportPrintDto(BaseModel):
    gr_number: str = Field(default="", alias="grNumber")
    transporter_name: str = Field(default="", alias="transporterName")
    eway_bill_no: str = Field(default="", alias="ewayBillNo")
    vehicle_number: str = Field(default="", alias="vehicleNumber")
    loading_station: str = Field(default="", alias="loadingStation")

    class Config:
        populate_by_name = True


class BankDetailsPrintDto(BaseModel):
    bank_name: str = Field(default="", alias="bankName")
    account_name: str = Field(default="", alias="accountName")
    account_number: str = Field(default="", alias="accountNumber")
    ifsc_code: str = Field(default="", alias="ifscCode")
    branch: str = Field(default="", alias="branch")
    upi_id: str = Field(default="", alias="upiId")

    class Config:
        populate_by_name = True


class TransactionPrintDto(BaseModel):
    company: CompanyPrintDto = Field(default_factory=CompanyPrintDto, alias="company")
    party: PartyPrintDto = Field(default_factory=PartyPrintDto, alias="party")
    transaction_header: TransactionHeaderDto = Field(default_factory=TransactionHeaderDto, alias="transactionHeader")
    items: List[TransactionItemPrintDto] = Field(default_factory=list, alias="items")
    taxes: List[TransactionTaxPrintDto] = Field(default_factory=list, alias="taxes")
    summary: TransactionSummaryDto = Field(default_factory=TransactionSummaryDto, alias="summary")
    transport: TransportPrintDto = Field(default_factory=TransportPrintDto, alias="transport")
    bank_details: BankDetailsPrintDto = Field(default_factory=BankDetailsPrintDto, alias="bankDetails")
    terms: str = Field(default="", alias="terms")

    class Config:
        populate_by_name = True


class PrintSettings(BaseModel):
    paper_size: str = Field(default="A4", alias="paperSize")
    paper_copies: str = Field(default="1", alias="paperCopies")
    document_type: List[str] = Field(default_factory=list, alias="documentType")
    save_path: str = Field(default="", alias="savePath")
    template: str = Field(default="default", alias="template")  # default, template_1, etc.

    class Config:
        populate_by_name = True
