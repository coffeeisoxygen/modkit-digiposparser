#!/usr/bin/env python3

from app.feature.member.sch_memberauth import MemberTrxRequestModel

# Test basic schema functionality
print("Testing MemberTrxRequestModel...")

# Test with string PIN
request1 = MemberTrxRequestModel(
    memberid="TEST001", pin="123456", password="password123"
)
print(f"String PIN: {request1.pin}")

# Test with int PIN
request2 = MemberTrxRequestModel(memberid="TEST001", pin=123456, password=789012)
print(f"Int PIN: {request2.pin}")

# Test with None values
request3 = MemberTrxRequestModel(memberid="TEST001", pin=None, password=None)
print(f"None PIN: {request3.pin}")

print("Schema tests passed!")
