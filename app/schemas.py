from pydantic import BaseModel, Field


class ReceiptItem(BaseModel):
    name: str = Field(description="Product or service name exactly as it appears on the receipt when readable.")
    quantity: float | None = Field(
        description="Purchased quantity. Use 1 when the receipt clearly lists a single unit.",
    )
    price: float | None = Field(
        description="Line item total price after item-level discounts when readable.",
    )


class ReceiptData(BaseModel):
    merchant: str | None = Field(description="Store, merchant, or company name.")
    purchase_date: str | None = Field(
        description="Purchase date in ISO 8601 format YYYY-MM-DD when it can be inferred.",
    )
    items: list[ReceiptItem] = Field(description="Receipt line items. Use an empty array when no items are readable.")


class ErrorResponse(BaseModel):
    detail: str
