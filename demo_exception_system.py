# """Quick manual test for exception system.

# This demonstrates that all components work together correctly.
# """

# import asyncio

# from app.exceptions.canvas.exc_adapter import (
#     JsonResponseAdapter,
#     PlaintextResponseAdapter,
# )
# from app.exceptions.canvas.exc_base import AppExceptionError, ServiceError
# from app.exceptions.canvas.exc_handler import (
#     with_json_response,
#     with_plaintext_response,
# )


# @with_json_response
# async def demo_json_success():
#     return {"message": "JSON success!", "data": [1, 2, 3]}


# @with_json_response
# async def demo_json_error():
#     raise ServiceError(message="Service is down for maintenance")


# @with_plaintext_response
# async def demo_plaintext_success():
#     return "Plain text success message"


# @with_plaintext_response
# async def demo_plaintext_error():
#     raise AppExceptionError(
#         message="Custom error occurred",
#         context={"user_id": "123", "operation": "test"},
#     )


# async def main():
#     print("=== Exception System Demo ===\n")

#     # Test JSON success
#     print("1. JSON Success Response:")
#     response = await demo_json_success()
#     print(f"   Status: {response.status_code}")
#     print(f"   Type: {type(response).__name__}\n")

#     # Test JSON error
#     print("2. JSON Error Response:")
#     response = await demo_json_error()
#     print(f"   Status: {response.status_code}")
#     print(f"   Type: {type(response).__name__}\n")

#     # Test Plaintext success
#     print("3. Plaintext Success Response:")
#     response = await demo_plaintext_success()
#     print(f"   Status: {response.status_code}")
#     print(f"   Type: {type(response).__name__}\n")

#     # Test Plaintext error
#     print("4. Plaintext Error Response:")
#     response = await demo_plaintext_error()
#     print(f"   Status: {response.status_code}")
#     print(f"   Type: {type(response).__name__}\n")

#     # Test adapters directly
#     print("5. Direct Adapter Testing:")
#     json_adapter = JsonResponseAdapter()
#     plaintext_adapter = PlaintextResponseAdapter()

#     error = AppExceptionError("Direct adapter test")

#     json_resp = json_adapter.format_error(error)
#     plain_resp = plaintext_adapter.format_error(error)

#     print(
#         f"   JSON adapter response: {type(json_resp).__name__} - {json_resp.status_code}"
#     )
#     print(
#         f"   Plaintext adapter response: {type(plain_resp).__name__} - {plain_resp.status_code}"
#     )

#     # Test HTML method
#     print("\n6. HTML Fragment Generation:")
#     html_fragment = error.to_html()
#     print(f"   HTML contains 'alert': {'alert' in html_fragment}")
#     print(f"   HTML contains error message: {'Direct adapter test' in html_fragment}")

#     print("\n=== All tests completed successfully! ===")


# if __name__ == "__main__":
#     asyncio.run(main())
