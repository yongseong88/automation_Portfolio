// 공통 헬퍼 (모든 페이지 공유)

const won = (n) => `${Number(n).toLocaleString("ko-KR")}원`;

function toast(msg, type = "ok") {
  let wrap = document.querySelector(".toast-wrap");
  if (!wrap) {
    wrap = document.createElement("div");
    wrap.className = "toast-wrap";
    wrap.setAttribute("data-testid", "toast-wrap");
    wrap.setAttribute("aria-live", "polite");
    document.body.appendChild(wrap);
  }
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  el.setAttribute("data-testid", `toast-${type}`);
  el.setAttribute("role", "status");
  el.textContent = msg;
  wrap.appendChild(el);
  setTimeout(() => el.remove(), 3000);
}

async function refreshCartCount() {
  const res = await fetch("/api/cart");
  const data = await res.json();
  const el = document.querySelector("#cart-count");
  if (!el) return;
  el.textContent = data.count;
  el.classList.toggle("hidden", data.count === 0);
}

async function loadCategoryNav() {
  const nav = document.querySelector("#cat-nav");
  if (!nav) return;
  const res = await fetch("/api/categories");
  const data = await res.json();
  nav.innerHTML = data.items
    .map(
      (c) =>
        `<a href="/category/${c.slug}" data-testid="cat-${c.slug}">${c.emoji} ${c.name}</a>`
    )
    .join("");
}

async function renderAuth() {
  const area = document.querySelector("#auth-area");
  if (!area) return;
  const res = await fetch("/api/me");
  if (res.ok) {
    const me = await res.json();
    area.innerHTML =
      `<span class="auth-user" data-testid="auth-user">${me.username}님</span>` +
      `<button class="auth-logout" id="logout-btn" data-testid="logout">로그아웃</button>`;
    document.querySelector("#logout-btn").addEventListener("click", async () => {
      await fetch("/api/logout", { method: "POST" });
      window.location.href = "/";
    });
  } else {
    area.innerHTML =
      `<a class="auth-login" href="/login" data-testid="login-link">로그인</a>`;
  }
}

function wireSearch() {
  const input = document.querySelector("#site-search");
  if (!input) return;
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && input.value.trim()) {
      window.location.href = `/?q=${encodeURIComponent(input.value.trim())}`;
    }
  });
}

function initHeader() {
  loadCategoryNav();
  refreshCartCount();
  renderAuth();
  wireSearch();
}

// 상품 카드 HTML (홈/카테고리 공용)
function productCardHTML(p) {
  const priceBlock = p.discount_pct
    ? `<span class="discount" data-testid="discount">${p.discount_pct}%</span>
       <span class="price" data-testid="price">${won(p.price)}</span>
       <span class="original">${won(p.original_price)}</span>`
    : `<span class="price" data-testid="price">${won(p.price)}</span>`;
  const badge = p.badge ? `<span class="badge" data-testid="badge">${p.badge}</span>` : "";
  const soldOut = p.sold_out
    ? `<span class="sold-out-mask" data-testid="sold-out">품절</span>`
    : "";
  return `
    <a class="card" href="/product/${p.id}" data-testid="product-card" data-id="${p.id}">
      <div class="thumb" style="background:${p.color}">
        ${badge}<span aria-hidden="true">${p.emoji}</span>${soldOut}
      </div>
      <p class="pname" data-testid="card-name">${p.name}</p>
      <span class="punit">${p.unit}</span>
      <div class="price-row">${priceBlock}</div>
    </a>`;
}
