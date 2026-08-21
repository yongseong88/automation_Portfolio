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
      `<a class="auth-login" href="/mypage" data-testid="mypage-link">마이페이지</a>` +
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
  renderFooter();
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


/* ── 푸터 ───────────────────────────────────────────────────────
   사업자 정보 / 고객 연락처 / 정책 링크 / 저작권 / 소셜 링크.
   모든 페이지에서 initHeader() 를 호출하므로 여기서 한 번만 그린다.
   표기 내용은 데모용 더미 데이터다.
------------------------------------------------------------------ */
const FOOTER_INFO = {
  company: [
    ["상호명", "주식회사 마켓프레시"],
    ["대표자명", "김신선"],
    ["사업자등록번호", "123-45-67890"],
    ["통신판매업신고번호", "제2026-서울강남-01234호"],
    ["주소", "서울특별시 강남구 테헤란로 123, 마켓프레시빌딩 8층"],
  ],
  contact: [
    ["대표 전화", "1000-1234"],
    ["고객문의", "help@marketfresh.test"],
    ["팩스", "02-1234-5679"],
  ],
  policies: [
    ["개인정보처리방침", "/policy/privacy", "privacy"],
    ["이용안내", "/policy/guide", "guide"],
    ["서비스 이용약관", "/policy/terms", "terms"],
  ],
  socials: [
    ["공식 블로그", "https://blog.naver.com", "📝", "blog"],
    ["유튜브", "https://youtube.com", "▶️", "youtube"],
    ["인스타그램", "https://instagram.com", "📷", "instagram"],
    ["페이스북", "https://facebook.com", "👍", "facebook"],
  ],
};

function renderFooter() {
  if (document.querySelector("#site-footer")) return;   // 중복 렌더 방지

  const year = new Date().getFullYear();
  const dl = (rows) =>
    rows.map(([k, v]) => `<div class="foot-row"><dt>${k}</dt><dd>${v}</dd></div>`).join("");

  const footer = document.createElement("footer");
  footer.className = "site-footer";
  footer.id = "site-footer";
  footer.dataset.testid = "footer";
  footer.innerHTML = `
    <div class="footer-inner">
      <nav class="footer-policies" data-testid="footer-policies" aria-label="정책">
        ${FOOTER_INFO.policies
          .map(([label, href, key]) =>
            `<a href="${href}" target="_blank" rel="noreferrer"
                data-testid="footer-${key}">${label}</a>`)
          .join('<span class="foot-sep">|</span>')}
      </nav>

      <div class="footer-cols">
        <dl class="footer-col" data-testid="footer-company">
          <p class="foot-heading">사업자 정보</p>
          ${dl(FOOTER_INFO.company)}
        </dl>
        <dl class="footer-col" data-testid="footer-contact">
          <p class="foot-heading">고객센터</p>
          ${dl(FOOTER_INFO.contact)}
          <p class="foot-note">운영시간 평일 09:00 ~ 18:00 (주말·공휴일 휴무)</p>
        </dl>
      </div>

      <div class="footer-bottom">
        <p class="footer-copy" data-testid="footer-copyright">
          Copyright © ${year} MarketFresh Corp. All rights reserved.
        </p>
        <ul class="footer-social" data-testid="footer-social">
          ${FOOTER_INFO.socials
            .map(([label, href, icon, key]) =>
              `<li><a href="${href}" target="_blank" rel="noreferrer"
                     title="${label}" aria-label="${label}"
                     data-testid="social-${key}">${icon}</a></li>`)
            .join("")}
        </ul>
      </div>
    </div>`;
  document.body.appendChild(footer);
}