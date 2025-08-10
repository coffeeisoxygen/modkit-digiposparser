"""Test implementation of the Adapter Pattern for response handling.

This demonstrates how the adapter pattern works with both JSON and plaintext
responses, including validation errors and custom exceptions.
"""

from app.exceptions.exc_digipos import (
    DigiposAuthenticationError,
    DigiposMemberNotFoundError,
    DigiposValidationError,
)
from app.response import (
    JsonResponseAdapter,
    PlaintextResponseAdapter,
    with_json_response,
    with_plaintext_response,
)
from fastapi import FastAPI, Query
from pydantic import BaseModel, field_validator

# Create test FastAPI app
app = FastAPI(title="Adapter Pattern Test")


# Test request model with validation
class TestRequest(BaseModel):
    """Test request model with validation rules."""

    memberid: str
    product: str
    amount: float

    @field_validator("memberid")
    @classmethod
    def validate_memberid(cls, v: str) -> str:
        """Validate member ID format."""
        if len(v) < 3:
            raise ValueError("Member ID must be at least 3 characters")
        return v

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        """Validate amount is positive."""
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v


# JSON Response Endpoints (for admin/monitoring)
@app.get("/admin/health")
@with_json_response
async def health_check():
    """Health check endpoint - returns JSON."""
    return {"status": "healthy", "service": "modkit-digiposparser"}


@app.post("/admin/test-validation")
@with_json_response
async def test_json_validation(data: TestRequest):
    """Test JSON validation errors."""
    return {"message": "Validation passed", "data": data.model_dump()}


@app.get("/admin/test-error")
@with_json_response
async def test_json_error():
    """Test JSON custom exception."""
    raise DigiposAuthenticationError("Invalid API key provided")


# Plaintext Response Endpoints (for Otomax)
@app.get("/digipos/health")
@with_plaintext_response
async def digipos_health():
    """Health check for Otomax - returns plaintext."""
    return "Service healthy and ready"


@app.post("/digipos/test-validation")
@with_plaintext_response
async def test_plaintext_validation(data: TestRequest):
    """Test plaintext validation errors."""
    return f"Validation passed for member {data.memberid}"


@app.get("/digipos/test-error")
@with_plaintext_response
async def test_plaintext_error():
    """Test plaintext custom exception."""
    raise DigiposMemberNotFoundError("Member WIR6289504 not found in system")


@app.get("/digipos/test-validation-error")
@with_plaintext_response
async def test_validation_error(memberid: str = Query(...)):
    """Test validation error handling."""
    if len(memberid) < 3:
        raise DigiposValidationError("memberid", "Must be at least 3 characters")
    return f"Member {memberid} is valid"


# Demonstration endpoints
@app.get("/demo/compare-responses")
async def compare_responses():
    """Demonstrate the difference between adapters."""
    test_data = {"message": "Success", "data": [1, 2, 3]}

    json_adapter = JsonResponseAdapter()
    plaintext_adapter = PlaintextResponseAdapter()

    return {
        "json_format": json_adapter.format_success(test_data).body.decode(),
        "plaintext_format": plaintext_adapter.format_success(test_data).body.decode(),
    }


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting Adapter Pattern Test Server...")
    print()
    print("📋 Test Endpoints:")
    print("   JSON Responses (Admin):")
    print("   • GET  /admin/health")
    print("   • POST /admin/test-validation")
    print("   • GET  /admin/test-error")
    print()
    print("   Plaintext Responses (Otomax):")
    print("   • GET  /digipos/health")
    print("   • POST /digipos/test-validation")
    print("   • GET  /digipos/test-error")
    print("   • GET  /digipos/test-validation-error?memberid=xx")
    print()
    print("   Comparison:")
    print("   • GET  /demo/compare-responses")
    print()

    uvicorn.run(app, host="0.0.0.0", port=8000)
