"""
QA Harness Demo - E-commerce SUT (컬리 스타일 데모)
자동화 연습/포트폴리오용 데모 백엔드.
- 페이지 4종을 서빙: 홈 / 카테고리 / 상품 상세 / 장바구니
- UI/API 자동화 모두 가능한 JSON API 제공

실행:
    pip install -r requirements.txt
    uvicorn app:app --reload --port 8000
    → http://localhost:8000

설계 의도(자동화 관점):
- /api/products 는 일부러 지연(latency)을 둬서 "명시적 대기 전략"을 강제
- /api/reset 으로 테스트마다 상태(상품/장바구니) 초기화 → 테스트 격리
- 404(없는 상품) / 422(잘못된 수량) / 409(품절) 등 음성 케이스를 명확히 노출
- 장바구니 합계/무료배송 임계값 계산 → 데이터 단언(assertion) 연습용
"""

from __future__ import annotations
import asyncio
import secrets
from copy import deepcopy
from datetime import datetime            # ← [수정②] import datetime → from datetime import datetime
from fastapi import Cookie, FastAPI, HTTPException, Query, Response  # ← [수정⑤] 중복 import 정리
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from utilities.File_read import Filereadutil


app = FastAPI(title="Market Fresh Demo API", version="2.0.0")

# 경로 계산/파일 읽기는 utilities 공통 유틸로 위임 (프로젝트 루트 기준 절대경로)
files = Filereadutil()
app.mount("/static", StaticFiles(directory=files.read_filepath("", "static")), name="static")

FREE_SHIPPING_THRESHOLD = 40000
SHIPPING_FEE = 3000

# --- 카테고리 / 시드 상품 (config/*.json 에서 로드) -----------------------
CATEGORIES = files.read_file(files.read_filepath("config", "categories.json"))
SEED_PRODUCTS = files.read_file(files.read_filepath("config", "products.json"))
products: list[dict] = deepcopy(SEED_PRODUCTS)

# 장바구니: {product_id: qty} (데모용 단일 전역 장바구니)
cart: dict[int, int] = {}

# --- 로그인 계정 / 세션 ----------------------------------------------------
# 데모 계정 (username -> password)
USERS = {
    "demo": "demo1234",
    "test": "test1234",
}
# 활성 세션: {token: username}
_sessions: dict[str, str] = {}

# 주문: 서버에 저장되는 주문 목록 (로그인 사용자는 user 로 귀속)
orders: list[dict] = []
order_seq: int = 0


# --- 모델 ------------------------------------------------------------------
class CartAddIn(BaseModel):
    product_id: int
    qty: int = Field(default=1, ge=1, le=99)


class CartUpdateIn(BaseModel):
    qty: int = Field(ge=1, le=99)


class LoginIn(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class OrderIn(BaseModel):
    recipient_name: str = Field(min_length=1, max_length=40)
    phone: str = Field(min_length=1, max_length=20)
    address: str = Field(min_length=1, max_length=200)
    delivery_request: str = Field(default="", max_length=200)
    payment_method: str = Field(default="card", pattern="^(card|bank|easy)$")


# --- 헬퍼 ------------------------------------------------------------------
def find(product_id: int) -> dict | None:
    return next((p for p in products if p["id"] == product_id), None)


def serialize(p: dict) -> dict:
    """응답용: 할인율/품절여부를 계산해서 붙임."""
    out = dict(p)
    if p["original_price"]:
        out["discount_pct"] = round(
            (p["original_price"] - p["price"]) / p["original_price"] * 100
        )
    else:
        out["discount_pct"] = 0

    out["sold_out"] = p["stock"] == 0
    return out


def cart_summary() -> dict:
    items = []
    subtotal = 0
    for pid, qty in cart.items():
        p = find(pid)
        if not p:
            continue
        line_total = p["price"] * qty
        subtotal += line_total
        items.append({**serialize(p), "qty": qty, "line_total": line_total})

    shipping = 0 if subtotal == 0 or subtotal >= FREE_SHIPPING_THRESHOLD else SHIPPING_FEE

    return {
        "items": items,
        "count": sum(cart.values()),
        "subtotal": subtotal,
        "shipping": shipping,
        "total": subtotal + shipping,
        "free_shipping_threshold": FREE_SHIPPING_THRESHOLD,
    }


# --- 라우트: 페이지 --------------------------------------------------------
@app.get("/", include_in_schema=False)
def page_home():
    return FileResponse(files.read_filepath("static", "home.html"))


@app.get("/category/{slug}", include_in_schema=False)
def page_category(slug: str):
    return FileResponse(files.read_filepath("static", "category.html"))


@app.get("/product/{product_id}", include_in_schema=False)
def page_product(product_id: int):
    return FileResponse(files.read_filepath("static", "product.html"))


@app.get("/cart", include_in_schema=False)
def page_cart():
    return FileResponse(files.read_filepath("static", "cart.html"))


@app.get("/login", include_in_schema=False)
def page_login():
    return FileResponse(files.read_filepath("static", "login.html"))


@app.get("/order", include_in_schema=False)
def page_order():
    return FileResponse(files.read_filepath("static", "order.html"))


@app.get("/order/complete/{order_id}", include_in_schema=False)
def page_order_complete(order_id: int):
    return FileResponse(files.read_filepath("static", "order_complete.html"))


@app.get("/mypage", include_in_schema=False)
def page_mypage():
    return FileResponse(files.read_filepath("static", "mypage.html"))


@app.get("/mypage/orders", include_in_schema=False)   # ← [수정④] 빠져있던 주문내역 라우트 추가
def page_orders():
    return FileResponse(files.read_filepath("static", "orders.html"))


# --- 라우트: API -----------------------------------------------------------
@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/reset")
def reset_state() -> dict:
    global products, order_seq            # ← [수정③] order_seq 도 초기화 대상
    products = deepcopy(SEED_PRODUCTS)
    cart.clear()
    _sessions.clear()                     # ← [수정③] 세션 초기화
    orders.clear()                        # ← [수정③] 주문 초기화
    order_seq = 0                         # ← [수정③] 주문 시퀀스 초기화
    return {"reset": True, "products": len(products)}


# --- 라우트: 인증 ----------------------------------------------------------
def current_user(session: str | None = Cookie(default=None)) -> str | None:
    """세션 쿠키로 현재 로그인 사용자명을 돌려줌(없으면 None)."""
    if session and session in _sessions:
        return _sessions[session]
    return None


@app.post("/api/login")
def login(payload: LoginIn, response: Response) -> dict:
    if USERS.get(payload.username) == payload.password:
        token = secrets.token_hex(16)
        _sessions[token] = payload.username
        # httponly 쿠키 → JS로 못 읽지만 브라우저가 자동으로 들고 다님
        response.set_cookie("session", token, httponly=True, samesite="lax")
        return {"user": {"username": payload.username}}
    raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다.")


@app.post("/api/logout")
def logout(response: Response, session: str | None = Cookie(default=None)) -> dict:
    if session:
        _sessions.pop(session, None)
    response.delete_cookie("session")
    return {"ok": True}


@app.get("/api/me")
def me(session: str | None = Cookie(default=None)) -> dict:
    user = current_user(session)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"username": user}


# --- 라우트: 주문 ----------------------------------------------------------
@app.post("/api/orders", status_code=201)
def create_order(payload: OrderIn, session: str | None = Cookie(default=None)) -> dict:
    summary = cart_summary()
    if not summary["items"]:
        raise HTTPException(status_code=409, detail="장바구니가 비어 있습니다.")

    global order_seq                       # ← [수정①] _order_seq → order_seq (선언과 이름 일치)
    order_seq += 1
    order = {
        "order_id": order_seq,
        "order_no": f"ORD-{order_seq:05d}",
        "user": current_user(session),     # 비회원이면 None
        "items": summary["items"],
        "subtotal": summary["subtotal"],
        "shipping": summary["shipping"],
        "total": summary["total"],
        "recipient_name": payload.recipient_name,
        "phone": payload.phone,
        "address": payload.address,
        "delivery_request": payload.delivery_request,
        "payment_method": payload.payment_method,
        "created_at": datetime.now().isoformat(timespec="seconds"),  # ← [수정②] datetime.now() 정상 동작
        "status": "결제완료",
    }
    orders.append(order)
    cart.clear()  # 주문 후 장바구니 비움
    return order


@app.get("/api/orders")
def list_orders(session: str | None = Cookie(default=None)) -> dict:
    """로그인 사용자의 주문 목록(최신순). 미로그인은 401."""
    user = current_user(session)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    mine = sorted(
        (o for o in orders if o["user"] == user),
        key=lambda o: o["order_id"],
        reverse=True,
    )
    return {"items": mine, "count": len(mine)}


@app.get("/api/orders/{order_id}")
def get_order(order_id: int) -> dict:
    for o in orders:
        if o["order_id"] == order_id:
            return o
    raise HTTPException(status_code=404, detail="Order not found")


@app.get("/api/categories")
def list_categories() -> dict:
    return {"items": CATEGORIES}


@app.get("/api/products")
async def list_products(
    category: str = Query(default=""),
    q: str = Query(default=""),
    sort: str = Query(default="id", pattern="^(id|name|price)$"),
    order: str = Query(default="asc", pattern="^(asc|desc)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=50),
    delay_ms: int = Query(default=400, ge=0, le=3000),
) -> dict:
    # 일부러 지연 → 명시적 대기 전략 강제
    if delay_ms:
        await asyncio.sleep(delay_ms / 1000)

    items = products
    if category:
        items = [p for p in items if p["category"] == category]
    if q:
        needle = q.lower()
        items = [p for p in items if needle in p["name"].lower()]

    items = sorted(items, key=lambda p: p[sort], reverse=(order == "desc"))

    total = len(items)
    start = (page - 1) * page_size
    page_items = [serialize(p) for p in items[start:start + page_size]]

    return {
        "items": page_items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, (total + page_size - 1) // page_size),
    }


@app.get("/api/products/{product_id}")
def get_product(product_id: int) -> dict:
    p = find(product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return serialize(p)


@app.get("/api/cart")
def get_cart() -> dict:
    return cart_summary()


@app.post("/api/cart")
def add_to_cart(payload: CartAddIn) -> dict:
    p = find(payload.product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    if p["stock"] == 0:
        raise HTTPException(status_code=409, detail="Sold out")
    cart[payload.product_id] = cart.get(payload.product_id, 0) + payload.qty
    return cart_summary()


@app.patch("/api/cart/{product_id}")
def update_cart(product_id: int, payload: CartUpdateIn) -> dict:
    if product_id not in cart:
        raise HTTPException(status_code=404, detail="Not in cart")
    cart[product_id] = payload.qty
    return cart_summary()


@app.delete("/api/cart/{product_id}")
def remove_from_cart(product_id: int) -> dict:
    cart.pop(product_id, None)
    return cart_summary()