# Receipt Processing API
An API service for analyzing receipt photos and returning JSON with the merchant, purchase date, and receipt items.

## Run

```bash
cp .env.example .env
docker compose up --build
```

API URL: `http://localhost:8000`.

## Endpoints

### Healthcheck

```bash
curl http://localhost:8000/health
```

### Receipt analysis

```bash
curl -X POST http://localhost:8000/v1/receipts/analyze \
  -F "file=@receipt.jpg"
```

Response example:

```json
{
  "merchant": "Example Market",
  "purchase_date": "2026-05-30",
  "items": [
    {
      "name": "Milk 1L",
      "quantity": 1,
      "price": 2.49
    }
  ]
}
```

## Settings

Environment variables:

- `OPENAI_API_KEY` - required API-key OpenAI.
- `OPENAI_MODEL` - default image analysis model `gpt-4.1-mini`.
- `MAX_IMAGE_BYTES` - maximum file size, default `15728640` bytes.

Supporting formats: JPEG, PNG, WEBP, GIF.

