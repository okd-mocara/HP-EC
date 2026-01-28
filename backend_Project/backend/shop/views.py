import json
import stripe
from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView

from .models import Product, Order, OrderItem
from .serializers import ProductSerializer, OrderCreateSerializer


class ProductListView(ListAPIView):
    queryset = Product.objects.filter(is_active=True).order_by("id")
    serializer_class = ProductSerializer


class ProductDetailView(RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer


@api_view(["POST"])
def create_checkout_session(request):
    """
    1) 注文を DB に pending で作る
    2) Stripe Checkout Session を作る
    3) Session URL を返す（Reactはそこへリダイレクト）
    """
    if not settings.STRIPE_SECRET_KEY:
        return Response({"error": "STRIPE_SECRET_KEY is not set"}, status=500)

    serializer = OrderCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    items = data["items"]

    # 商品ID検証＆合計計算（サーバ側で必ずやる）
    product_map = {p.id: p for p in Product.objects.filter(id__in=[i["product_id"] for i in items], is_active=True)}
    if len(product_map) != len({i["product_id"] for i in items}):
        return Response({"error": "Invalid product in items"}, status=status.HTTP_400_BAD_REQUEST)

    line_items = []
    total = 0
    for it in items:
        p = product_map[it["product_id"]]
        qty = it["quantity"]
        total += p.price_jpy * qty
        line_items.append({
            "price_data": {
                "currency": "jpy",
                "product_data": {"name": p.name},
                "unit_amount": p.price_jpy,  # JPYは最小単位=円
            },
            "quantity": qty,
        })

    stripe.api_key = settings.STRIPE_SECRET_KEY

    with transaction.atomic():
        order = Order.objects.create(
            customer_name=data["customer_name"],
            customer_email=data["customer_email"],
            customer_phone=data.get("customer_phone", ""),

            shipping_address1=data["shipping_address1"],
            shipping_address2=data.get("shipping_address2", ""),
            shipping_city=data["shipping_city"],
            shipping_prefecture=data["shipping_prefecture"],
            shipping_postal_code=data["shipping_postal_code"],
            total_jpy=total,
            status=Order.Status.PENDING,
        )

        # 明細保存（注文時点価格を保存）
        bulk = []
        for it in items:
            p = product_map[it["product_id"]]
            bulk.append(OrderItem(
                order=order,
                product=p,
                quantity=it["quantity"],
                unit_price_jpy=p.price_jpy,
            ))
        OrderItem.objects.bulk_create(bulk)

        # Checkout Session 作成
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=line_items,
            success_url=f"{settings.FRONTEND_BASE_URL}/success?order_id={order.id}",
            cancel_url=f"{settings.FRONTEND_BASE_URL}/cancel?order_id={order.id}",
            metadata={"order_id": str(order.id)},
        )

        order.stripe_checkout_session_id = session["id"]
        order.save(update_fields=["stripe_checkout_session_id"])

    return Response({"checkout_url": session["url"], "order_id": order.id})


@csrf_exempt
def stripe_webhook(request):
    """
    StripeからのWebhookを受けて注文をPAIDにする。
    **署名検証**が超重要。
    """
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    if not settings.STRIPE_WEBHOOK_SECRET:
        return HttpResponse("STRIPE_WEBHOOK_SECRET not set", status=500)

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )
    except Exception:
        return HttpResponse("Invalid signature", status=400)

    # 決済完了（Checkoutの場合ここが基本）
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        order_id = session.get("metadata", {}).get("order_id")
        payment_intent = session.get("payment_intent", "")

        if order_id:
            # 二重実行に耐える（idempotent）
            Order.objects.filter(id=order_id, status=Order.Status.PENDING).update(
                status=Order.Status.PAID,
                stripe_payment_intent_id=payment_intent or "",
            )

    return HttpResponse("ok", status=200)
