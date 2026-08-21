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
- /api/reset 으로 테스트마다 상태(상품/장바구니/회원) 초기화 → 테스트 격리
- 404(없는 상품) / 422(잘못된 수량) / 409(품절·중복가입) 등 음성 케이스를 명확히 노출
- 장바구니 합계/무료배송 임계값 계산 → 데이터 단언(assertion) 연습용
"""

from __future__ import annotations
import asyncio
import re                                # ← [회원가입] 비밀번호 규칙 검증용
import secrets
from copy import deepcopy
from datetime import datetime            # ← [수정②] import datetime → from datetime import datetime
from fastapi import Cookie, FastAPI, HTTPException, Query, Response  # ← [수정⑤] 중복 import 정리
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator   # ← [회원가입] field_validator 추가
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

# 장바구니: 소유자별로 분리해서 보관한다.
#   {"__guest__": {product_id: qty}, "demo": {product_id: qty}, ...}
# 로그인 사용자는 자기 장바구니가 유지되고, 비회원 장바구니는 로그인 시 병합된다.
GUEST_CART_KEY = "__guest__"
carts: dict[str, dict[int, int]] = {}

# --- 로그인 계정 / 세션 ----------------------------------------------------
# 데모 계정 시드 (username -> 프로필). 회원가입 시 USERS 에 추가된다.
# 비밀번호는 회원가입 규칙(영문+특수문자, 8자 이상)을 데모 계정도 따르도록 맞춤.
SEED_USERS = {
    "demo": {
        "password": "demo1234!",
        "name": "김데모",
        "phone": "010-1111-2222",
        "email": "demo@marketfresh.com",
        "address": "서울시 강남구 테헤란로 1",
    },
    "test": {
        "password": "test1234!",
        "name": "이테스트",
        "phone": "010-3333-4444",
        "email": "test@marketfresh.com",
        "address": "서울시 마포구 월드컵로 2",
    },
}
# 실제 사용되는 회원 저장소 (가입 시 여기에 추가됨)
USERS: dict[str, dict] = deepcopy(SEED_USERS)

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


# 허용 특수문자 집합 (아이디/비밀번호 공통)
SPECIAL_CHARS = r"!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?~`"

# 회원가입 입력 규칙
#  - 아이디  : 영문/숫자/특수문자 4~10자 (공백·한글 불가)
#  - 비밀번호: 영문/숫자/특수문자 8~16자, 특수문자 1개 이상 필수 (공백·한글 불가)
#  - 이메일  : 아이디@도메인.최상위도메인 (공백·한글 불가, @ 및 마침표 필수)
#  - 연락처  : 3자리-4자리-4자리 (숫자와 하이픈만)
USERNAME_PATTERN = rf"^[A-Za-z0-9{SPECIAL_CHARS}]{{4,10}}$"
PASSWORD_PATTERN = rf"^[A-Za-z0-9{SPECIAL_CHARS}]{{8,16}}$"
EMAIL_PATTERN = r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$"
PHONE_PATTERN = r"^\d{3}-\d{4}-\d{4}$"


class SignupIn(BaseModel):
    """회원가입 입력.

    문자 종류/길이는 pattern 으로, '특수문자 1개 이상 포함' 같은 복합 조건은
    field_validator 로 검사한다.
    (Pydantic 의 pattern 은 Rust 정규식이라 look-ahead 를 지원하지 않는다)
    """
    username: str = Field(pattern=USERNAME_PATTERN)
    password: str = Field(pattern=PASSWORD_PATTERN)
    name: str = Field(min_length=1, max_length=40)
    phone: str = Field(pattern=PHONE_PATTERN)
    email: str = Field(pattern=EMAIL_PATTERN, max_length=100)
    address: str = Field(min_length=1, max_length=200)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(f"[{re.escape(SPECIAL_CHARS)}]", v):
            raise ValueError("비밀번호에 특수문자가 포함되어야 합니다.")
        return v


class OrderIn(BaseModel):
    # 주문자 정보 (추가)
    orderer_name: str = Field(min_length=1, max_length=40)
    orderer_phone: str = Field(min_length=1, max_length=20)
    orderer_email: str = Field(min_length=1, max_length=100, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    # 배송지 (기존)
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


def cart_owner(session: str | None) -> str:
    """현재 요청의 장바구니 소유자 키 (로그인 사용자명 또는 비회원 키)."""
    user = current_user(session)
    return user if user else GUEST_CART_KEY


def get_cart(session: str | None) -> dict[int, int]:
    """소유자의 장바구니를 돌려준다 (없으면 새로 만들어 반환)."""
    return carts.setdefault(cart_owner(session), {})


def cart_summary(session: str | None = None) -> dict:
    cart = get_cart(session)
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


@app.get("/policy/{key}", include_in_schema=False)
def page_policy(key: str):
    """약관/정책 문서 (privacy | guide | terms). 문서 내용은 정적 페이지에 담겨 있다."""
    return FileResponse(files.read_filepath("static", "policy.html"))


@app.get("/cart", include_in_schema=False)
def page_cart():
    return FileResponse(files.read_filepath("static", "cart.html"))


@app.get("/login", include_in_schema=False)
def page_login():
    return FileResponse(files.read_filepath("static", "login.html"))


@app.get("/signup", include_in_schema=False)          # ← [회원가입] 페이지 라우트
def page_signup():
    return FileResponse(files.read_filepath("static", "signup.html"))


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
    global products, order_seq, USERS     # ← [회원가입] USERS 도 초기화 대상
    products = deepcopy(SEED_PRODUCTS)
    USERS = deepcopy(SEED_USERS)          # ← [회원가입] 가입 계정 초기화 (테스트 격리)
    carts.clear()                         # ← 모든 소유자의 장바구니 초기화
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


def only_digits(value: str) -> str:
    """비교용으로 숫자만 남긴다 (010-1234-5678 과 01012345678 을 같게 취급)."""
    return re.sub(r"\D", "", value or "")


def find_duplicate(payload: SignupIn) -> dict | None:
    """이미 사용 중인 항목이 있으면 {"field","message"} 를, 없으면 None 을 반환."""
    if payload.username in USERS:
        return {"field": "username", "message": "이미 사용 중인 아이디입니다."}

    phone_digits = only_digits(payload.phone)
    email_lower = payload.email.lower()

    for user in USERS.values():
        if user.get("email", "").lower() == email_lower:
            return {"field": "email", "message": "이미 사용 중인 이메일입니다."}
        if only_digits(user.get("phone", "")) == phone_digits:
            return {"field": "phone", "message": "이미 사용 중인 연락처입니다."}
    return None


@app.post("/api/signup", status_code=201)
def signup(payload: SignupIn) -> dict:
    """회원가입.

    입력 형식 위반은 422(SignupIn 이 처리), 이미 사용 중인 값은 409 로 응답한다.
    409 응답의 detail 에는 어느 항목이 중복인지 담아 화면이 해당 필드에 표시할 수 있게 한다.
    """
    duplicated = find_duplicate(payload)
    if duplicated:
        raise HTTPException(status_code=409, detail=duplicated)

    USERS[payload.username] = {
        "password": payload.password,
        "name": payload.name,
        "phone": payload.phone,
        "email": payload.email,
        "address": payload.address,
    }
    return {
        "username": payload.username,
        "name": payload.name,
        "email": payload.email,
    }


def merge_guest_cart(username: str) -> int:
    """비회원 장바구니를 로그인 사용자 장바구니에 합치고, 비회원 것은 비운다.

    같은 상품이면 수량을 더한다(최대 99). 병합된 상품 종류 수를 돌려준다.
    """
    guest_cart = carts.get(GUEST_CART_KEY, {})
    if not guest_cart:
        return 0

    user_cart = carts.setdefault(username, {})
    for pid, qty in guest_cart.items():
        user_cart[pid] = min(user_cart.get(pid, 0) + qty, 99)

    merged = len(guest_cart)
    guest_cart.clear()
    return merged


@app.post("/api/login")
def login(payload: LoginIn, response: Response) -> dict:
    user = USERS.get(payload.username)                       # ← [회원가입] dict 구조 대응
    if user and user["password"] == payload.password:        # ← [회원가입] dict 구조 대응
        token = secrets.token_hex(16)
        _sessions[token] = payload.username
        # httponly 쿠키 → JS로 못 읽지만 브라우저가 자동으로 들고 다님
        response.set_cookie("session", token, httponly=True, samesite="lax")

        # 비회원 상태에서 담아둔 상품을 로그인 계정 장바구니로 옮긴다
        merged = merge_guest_cart(payload.username)

        return {"user": {"username": payload.username}, "merged_cart_items": merged}
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
    profile = USERS.get(user, {})              # ← [회원가입] 프로필까지 반환
    return {
        "username": user,
        "name": profile.get("name", ""),
        "phone": profile.get("phone", ""),
        "email": profile.get("email", ""),
        "address": profile.get("address", ""),
    }


# --- 라우트: 주문 ----------------------------------------------------------
@app.post("/api/orders", status_code=201)
def create_order(payload: OrderIn, session: str | None = Cookie(default=None)) -> dict:
    summary = cart_summary(session)
    if not summary["items"]:
        raise HTTPException(status_code=409, detail="장바구니가 비어 있습니다.")

    global order_seq                       # ← [수정①] _order_seq → order_seq (선언과 이름 일치)
    order_seq += 1
    order = {
        "order_id": order_seq,
        "order_no": f"ORD-{order_seq:05d}",
        "user": current_user(session),  # 비회원이면 None

        # 주문자 정보
        "orderer_name": payload.orderer_name,
        "orderer_phone": payload.orderer_phone,
        "orderer_email": payload.orderer_email,

        "items": summary["items"],
        "subtotal": summary["subtotal"],
        "shipping": summary["shipping"],
        "total": summary["total"],
        "recipient_name": payload.recipient_name,
        "phone": payload.phone,
        "address": payload.address,
        "delivery_request": payload.delivery_request,
        "payment_method": payload.payment_method,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "status": "결제완료",
    }
    orders.append(order)
    get_cart(session).clear()  # 주문 후 해당 소유자의 장바구니만 비움
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


SECTION_SIZE = 20        # 구좌당 내려줄 상품 수 (화면은 5개씩 넘겨서 본다)


def section_products(key: str) -> list[dict]:
    """구좌 키에 해당하는 상품 목록을 정책에 맞게 골라 돌려준다."""
    available = [p for p in products if p["stock"] > 0]

    if key == "deal":
        # 특가: 정가 대비 할인이 있는 상품을 할인율 높은 순으로
        picked = [p for p in available if (p.get("original_price") or 0) > p["price"]]
        picked.sort(
            key=lambda p: (p["original_price"] - p["price"]) / p["original_price"],
            reverse=True,
        )
    elif key == "popular":
        # 인기: 판매량 많은 순
        picked = sorted(available, key=lambda p: p.get("sales_count", 0), reverse=True)
    elif key == "new":
        # 신상: badge 가 '신상' 인 상품 (최근 등록 = id 큰 순)
        picked = [p for p in available if p.get("badge") == "신상"]
        picked.sort(key=lambda p: p["id"], reverse=True)
    elif key == "limited":
        # 한정: badge 가 '한정' 인 상품 (재고 적은 순 → 희소성)
        picked = [p for p in available if p.get("badge") == "한정"]
        picked.sort(key=lambda p: p["stock"])
    elif key == "budget":
        # 알뜰: 가격이 낮은 순
        picked = sorted(available, key=lambda p: p["price"])
    else:
        picked = []

    return [serialize(p) for p in picked[:SECTION_SIZE]]


SECTION_META = [
    {"key": "deal", "title": "이번 주 특가", "emoji": "🔥",
     "description": "지금 가장 크게 할인 중인 상품"},
    {"key": "popular", "title": "지금 인기 상품", "emoji": "👀",
     "description": "많이 구매한 순서로 모았어요"},
    {"key": "new", "title": "새로 들어왔어요", "emoji": "✨",
     "description": "이번에 새로 입고된 신상품"},
    {"key": "limited", "title": "한정 수량", "emoji": "⏰",
     "description": "수량이 얼마 남지 않았어요"},
    {"key": "budget", "title": "알뜰 쇼핑", "emoji": "💰",
     "description": "가벼운 가격으로 채우는 장바구니"},
]


@app.get("/api/sections")
def list_sections() -> dict:
    """홈 화면 구좌(큐레이션 섹션) 목록.

    구좌 정의를 서버가 갖고 있어 화면과 교차 검증할 수 있다.
    (화면에 뜬 상품이 API 가 내려준 것과 같은지 확인 가능)
    """
    items = []
    for m in SECTION_META:
        picked = section_products(m["key"])
        items.append({**m, "total": len(picked), "products": picked})
    return {"items": items}


@app.get("/api/products")
async def list_products(
    category: str = Query(default=""),
    q: str = Query(default=""),
    sort: str = Query(default="id", pattern="^(id|name|price|sales_count)$"),
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


@app.get("/api/checkout")
def checkout(session: str | None = Cookie(default=None)) -> dict:
    """주문서 진입 시 필요한 정보를 한 번에 반환 (컬리 checkout 스타일).
    운용 중인 항목(상품/금액/할인/배송비/결제수단)만 묶어서 제공.
    """
    summary = cart_summary(session)

    # 상품할인 합계 = Σ(정가 - 할인가) × 수량
    discount_total = 0
    for item in summary["items"]:
        original = item.get("original_price") or 0
        if original > item["price"]:
            discount_total += (original - item["price"]) * item["qty"]

    return {
        "items": summary["items"],
        "subtotal": summary["subtotal"] + discount_total,   # 정가 기준 상품금액
        "discount_total": discount_total,                    # 상품할인 합계
        "shipping": summary["shipping"],
        "total": summary["total"],                           # 최종 결제 금액
        "free_shipping_threshold": FREE_SHIPPING_THRESHOLD,
        "payment_methods": ["card", "bank", "easy"],
    }


@app.get("/api/cart")
def read_cart(session: str | None = Cookie(default=None)) -> dict:
    return cart_summary(session)


@app.post("/api/cart")
def add_to_cart(payload: CartAddIn, session: str | None = Cookie(default=None)) -> dict:
    p = find(payload.product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    if p["stock"] == 0:
        raise HTTPException(status_code=409, detail="Sold out")
    cart = get_cart(session)
    cart[payload.product_id] = cart.get(payload.product_id, 0) + payload.qty
    return cart_summary(session)


@app.patch("/api/cart/{product_id}")
def update_cart(product_id: int, payload: CartUpdateIn,
                session: str | None = Cookie(default=None)) -> dict:
    cart = get_cart(session)
    if product_id not in cart:
        raise HTTPException(status_code=404, detail="Not in cart")
    cart[product_id] = payload.qty
    return cart_summary(session)


@app.delete("/api/cart/{product_id}")
def remove_from_cart(product_id: int, session: str | None = Cookie(default=None)) -> dict:
    get_cart(session).pop(product_id, None)
    return cart_summary(session)