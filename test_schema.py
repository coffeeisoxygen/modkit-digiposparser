#!/usr/bin/env python3

from app.feature.member.sch_memberauth import MemberTrxRequestModel

# Test schema
r = MemberTrxRequestModel(memberid='test', pin='123', password='abc')
print(f'Pin type: {type(r.pin)}, value: {r.pin}')
print(f'Password type: {type(r.password)}, value: {r.password}')
print('Schema works with string values!')
