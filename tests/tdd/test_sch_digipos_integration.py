import pytest
from app.feature.digipos.sch_digipos import (
    DigiposCatAsProdEnum,
    DigiposRequestBuy,
    DigiposRequestCheck,
    DigiposRequestList,
    DigposActionEnum,
)


@pytest.mark.integration
@pytest.mark.parametrize(
    "product,action_cls",
    [
        (DigiposCatAsProdEnum.DATA, DigiposRequestList),
        (DigiposCatAsProdEnum.VOICE_SMS, DigiposRequestList),
        (DigiposCatAsProdEnum.DIGITAL_GAME, DigiposRequestList),
    ],
)
def test_digipos_request_list_should_accept_valid_product(product, action_cls):
    # Arrange
    payload = {
        "memberid": "M123",
        "product": product.value,
        "dest": "08123456789",
        "refid": "REF001",
        "sign": "SIGN",
        "pin": "1234",
        "password": "pass",
        "action": DigposActionEnum.LIST,
        "markup": 10,
        "minday": 1,
        "maxday": 10,
        "minprice": 1000,
        "maxprice": 5000,
    }
    # Act
    obj = action_cls(**payload)
    # Assert
    assert obj.product == product.value, (
        f"Expected product {product.value}, got {obj.product}"
    )


@pytest.mark.integration
@pytest.mark.parametrize(
    "minday,maxday,minprice,maxprice",
    [
        (1, 10, 1000, 5000),  # normal
        (None, None, None, None),  # all None
        (0, 0, 0, 0),  # edge: zero values
    ],
)
def test_digipos_request_list_should_accept_valid_ranges(
    minday, maxday, minprice, maxprice
):
    # Arrange
    payload = {
        "memberid": "M123",
        "product": DigiposCatAsProdEnum.DATA.value,
        "dest": "08123456789",
        "refid": "REF001",
        "sign": "SIGN",
        "pin": "1234",
        "password": "pass",
        "action": DigposActionEnum.LIST,
        "markup": 0,
        "minday": minday,
        "maxday": maxday,
        "minprice": minprice,
        "maxprice": maxprice,
    }
    # Act
    obj = DigiposRequestList(**payload)
    # Assert
    assert obj.minday == minday, f"Expected minday {minday}, got {obj.minday}"
    assert obj.maxday == maxday, f"Expected maxday {maxday}, got {obj.maxday}"
    assert obj.minprice == minprice, f"Expected minprice {minprice}, got {obj.minprice}"
    assert obj.maxprice == maxprice, f"Expected maxprice {maxprice}, got {obj.maxprice}"


@pytest.mark.integration
@pytest.mark.parametrize(
    "minday,maxday",
    [
        (10, 1),  # minday > maxday
        (5, 2),  # minday > maxday
    ],
)
def test_digipos_request_list_should_raise_when_minday_gt_maxday(minday, maxday):
    # Arrange
    payload = {
        "memberid": "M123",
        "product": DigiposCatAsProdEnum.DATA.value,
        "dest": "08123456789",
        "refid": "REF001",
        "sign": "SIGN",
        "pin": "1234",
        "password": "pass",
        "action": DigposActionEnum.LIST,
        "minday": minday,
        "maxday": maxday,
    }
    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        DigiposRequestList(**payload)
    assert "minday must be <= maxday" in str(exc_info.value), (
        f"Expected ValueError with 'minday must be <= maxday', got '{exc_info.value}'"
    )


@pytest.mark.integration
@pytest.mark.parametrize(
    "minprice,maxprice",
    [
        (5000, 1000),  # minprice > maxprice
        (100, 99),  # minprice > maxprice
    ],
)
def test_digipos_request_list_should_raise_when_minprice_gt_maxprice(
    minprice, maxprice
):
    # Arrange
    payload = {
        "memberid": "M123",
        "product": DigiposCatAsProdEnum.DATA.value,
        "dest": "08123456789",
        "refid": "REF001",
        "sign": "SIGN",
        "pin": "1234",
        "password": "pass",
        "action": DigposActionEnum.LIST,
        "minprice": minprice,
        "maxprice": maxprice,
    }
    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        DigiposRequestList(**payload)
    assert "minprice must be <= maxprice" in str(exc_info.value), (
        f"Expected ValueError with 'minprice must be <= maxprice', got '{exc_info.value}'"
    )


@pytest.mark.integration
@pytest.mark.parametrize(
    "product",
    [
        "INVALID",
        "data",  # case sensitive
        "VOICE",  # not in enum
    ],
)
def test_digipos_request_base_should_raise_when_invalid_product(product):
    # Arrange
    payload = {
        "memberid": "M123",
        "product": product,
        "dest": "08123456789",
        "refid": "REF001",
        "sign": "SIGN",
        "pin": "1234",
        "password": "pass",
        "action": DigposActionEnum.LIST,
    }
    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        DigiposRequestList(**payload)
    assert "product must be one of:" in str(exc_info.value), (
        f"Expected ValueError with product enum message, got '{exc_info.value}'"
    )


@pytest.mark.integration
def test_digipos_request_check_should_require_productid():
    # Arrange
    payload = {
        "memberid": "M123",
        "product": DigiposCatAsProdEnum.DATA.value,
        "dest": "08123456789",
        "refid": "REF001",
        "sign": "SIGN",
        "pin": "1234",
        "password": "pass",
        "action": DigposActionEnum.CHECK,
        "productid": "PROD123",
    }
    # Act
    obj = DigiposRequestCheck(**payload)
    # Assert
    assert obj.productid == "PROD123", (
        f"Expected productid 'PROD123', got {obj.productid}"
    )


@pytest.mark.integration
def test_digipos_request_buy_should_require_productid():
    # Arrange
    payload = {
        "memberid": "M123",
        "product": DigiposCatAsProdEnum.DATA.value,
        "dest": "08123456789",
        "refid": "REF001",
        "sign": "SIGN",
        "pin": "1234",
        "password": "pass",
        "action": DigposActionEnum.BUY,
        "productid": "PROD456",
    }
    # Act
    obj = DigiposRequestBuy(**payload)
    # Assert
    assert obj.productid == "PROD456", (
        f"Expected productid 'PROD456', got {obj.productid}"
    )


@pytest.mark.integration
@pytest.mark.parametrize(
    "field,value",
    [
        ("minday", -1),
        ("maxday", -5),
        ("minprice", -100),
        ("maxprice", -200),
    ],
)
def test_digipos_request_list_should_raise_on_negative_values(field, value):
    # Arrange
    payload = {
        "memberid": "M123",
        "product": DigiposCatAsProdEnum.DATA.value,
        "dest": "08123456789",
        "refid": "REF001",
        "sign": "SIGN",
        "pin": "1234",
        "password": "pass",
        "action": DigposActionEnum.LIST,
        field: value,
    }
    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        DigiposRequestList(**payload)
    assert "value must be >= 0" in str(exc_info.value), (
        f"Expected ValueError with 'value must be >= 0', got '{exc_info.value}'"
    )
