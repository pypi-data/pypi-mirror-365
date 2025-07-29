"""
# File       : api_ios支付.py
# Time       ：2025/7/28 14:34
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：前端下单 -> 后端创建订单(order_number) -> 前端支付(receipt) -> 记录订单与收据或transaction_id
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional, Callable, Awaitable

from svc_order_zxw.db import get_db
from svc_order_zxw.db.crud2_products import get_product
from svc_order_zxw.db.crud3_orders import (
    create_order,
    get_order,
    PYD_OrderCreate,
)
from svc_order_zxw.db.crud4_payments import (
    create_payment,
    get_payment,
    update_payment,
    PYD_PaymentUpdate,
    PYD_PaymentCreate,
)
from svc_order_zxw.异常代码 import 订单_异常代码, 商品_异常代码, 支付_异常代码, 其他_异常代码
from svc_order_zxw.config import AliPayConfig
from svc_order_zxw.apis.schemas_payments import OrderStatus, PaymentMethod

from svc_order_zxw.apis.api_支付_苹果内购.func_生成订单号 import 生成订单号

from app_tools_zxw.SDK_苹果应用服务.sdk_支付验证 import 苹果内购支付服务_官方库
from app_tools_zxw.SDK_苹果应用服务.sdk_促销优惠管理 import 苹果内购优惠管理服务
from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW
from app_tools_zxw.Funcs.fastapi_logger import setup_logger

logger = setup_logger(__name__)


class 请求_IPA_创建订单(BaseModel):
    user_id: str
    product_id: int
    payment_price: float
    quantity: int = Field(default=1)


class 返回_IPA_订单信息(BaseModel):
    user_id: str
    product_id: int
    order_number: str

    total_price: float  # 总金额
    payment_price: float  # 实际支付金额
    quantity: int
    status: str


class 请求_IPA_验证收据(BaseModel):
    order_number: str | None
    收据: str | None


class 返回_IPA_支付信息(BaseModel):
    order_number: str
    payment_status: str  # 理论上是OrderStatus类型, 在schemas_payments中
    payment_price: float
    quantity: int
    order_id: int
    product_name: str
    app_name: str
    qr_uri: Optional[str] = None


async def 创建订单(request: 请求_IPA_创建订单, db: AsyncSession = Depends(get_db)):
    # 验证产品是否存在
    product = await get_product(db, request.product_id)
    if not product:
        raise HTTPException_AppToolsSZXW(
            error_code=商品_异常代码.商品不存在.value,
            detail="商品不存在",
            http_status_code=404
        )

    # 创建新订单
    new_order = await create_order(db, PYD_OrderCreate(
        order_number=生成订单号(),
        user_id=request.user_id,
        total_price=product.price * request.quantity,
        quantity=request.quantity,
        product_id=request.product_id,
    ))

    # 创建支付单
    new_payment = await create_payment(db, PYD_PaymentCreate(
        order_id=new_order.id,
        payment_price=request.payment_price,
        payment_method=PaymentMethod.ALIPAY_QR,
        payment_status=OrderStatus.PENDING,
        callback_url=AliPayConfig.回调路径_root + AliPayConfig.回调路径_prefix,
        payment_url=None,
    ))

    return 返回_支付宝url_订单信息(
        order_number=new_order.order_number,
        user_id=new_order.user_id,
        product_id=new_order.product_id,
        total_price=new_order.total_price,
        payment_price=new_payment.payment_price,
        quantity=new_order.quantity,
        status=new_payment.payment_status.value
    )


async def 查询支付状态(order_number: str, db: AsyncSession = Depends(get_db)):
    # 查询支付记录
    payment = await get_payment(
        db,
        order_number=order_number,
        include_order=True)
    logger.info(f"payment 查询结果 = {payment}")
    if not payment:
        raise HTTPException_AppToolsSZXW(
            error_code=支付_异常代码.支付单号不存在.value,
            detail="Payment not found",
            http_status_code=404
        )

    if not payment.order:
        raise HTTPException_AppToolsSZXW(
            error_code=订单_异常代码.订单号不存在.value,
            detail="Order not found for this payment",
            http_status_code=404
        )

    # 检查支付状态
    ...
