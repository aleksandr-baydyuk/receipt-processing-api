import base64
import os

from fastapi import FastAPI, File, HTTPException, UploadFile
from openai import OpenAI, OpenAIError

from app.schemas import ErrorResponse, ReceiptData


ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}
MAX_IMAGE_BYTES = int(os.getenv("MAX_IMAGE_BYTES", str(15 * 1024 * 1024)))
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")


app = FastAPI(
    title="Receipt Photo JSON API",
    version="1.0.0",
    description="Extract merchant, purchase date, and receipt items from a receipt photo.",
)


def _client() -> OpenAI:
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not configured.")
    return OpenAI()


def _to_data_url(content: bytes, content_type: str) -> str:
    encoded = base64.b64encode(content).decode("utf-8")
    return f"data:{content_type};base64,{encoded}"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/v1/receipts/analyze",
    response_model=ReceiptData,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}, 502: {"model": ErrorResponse}},
)
async def analyze_receipt(file: UploadFile = File(...)) -> ReceiptData:
    content_type = file.content_type or ""
    if content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Upload JPEG, PNG, WEBP, or non-animated GIF.",
        )

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(content) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=400, detail=f"Image is too large. Limit is {MAX_IMAGE_BYTES} bytes.")

    prompt = (
        "Extract structured JSON data from this receipt photo. "
        "Return only data visible or strongly inferable from the receipt. "
        "For merchant use the store/company name. "
        "For purchase_date use YYYY-MM-DDTHH:MM:SS. If the year is missing, infer it only when obvious; otherwise use null. "
        "For items, include purchasable goods/services only, not subtotals, taxes, totals, payment lines, or change. "
        "For each item, name should preserve the receipt wording, quantity should be numeric, "
        "and price should be the line total price. Use null for unreadable values."
    )

    try:
        response = _client().responses.parse(
            model=OPENAI_MODEL,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {
                            "type": "input_image",
                            "image_url": _to_data_url(content, content_type),
                            "detail": "high",
                        },
                    ],
                }
            ],
            text_format=ReceiptData,
        )
    except OpenAIError as exc:
        raise HTTPException(status_code=502, detail=f"OpenAI API error: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Receipt analysis failed: {exc}") from exc

    if response.output_parsed is None:
        raise HTTPException(status_code=502, detail="Model did not return a parseable receipt JSON object.")

    return response.output_parsed
