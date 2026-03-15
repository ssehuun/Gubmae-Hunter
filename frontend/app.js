/**
 * STEP6 프론트엔드 스크립트.
 *
 * - 검색 폼 -> /api/listings 쿼리 파라미터 생성
 * - 결과 테이블 렌더링
 */

const searchForm = document.getElementById("search-form");
const resetButton = document.getElementById("reset-button");
const statusElement = document.getElementById("status");
const resultBody = document.getElementById("result-body");

function formatDiscountRate(value) {
  if (value === null || value === undefined) {
    return "-";
  }
  return Number(value).toFixed(2);
}

function buildQueryFromForm(form) {
  const formData = new FormData(form);
  const params = new URLSearchParams();

  for (const [key, rawValue] of formData.entries()) {
    const value = String(rawValue).trim();
    if (value !== "") {
      params.set(key, value);
    }
  }

  return params;
}

function renderRows(items) {
  if (!items.length) {
    resultBody.innerHTML = '<tr><td colspan="8" class="empty">검색 결과가 없습니다.</td></tr>';
    return;
  }

  const rows = items
    .map((item) => {
      const quickSaleText = item.is_quick_sale ? "✅ 급매" : "-";
      const link = item.detail_url
        ? `<a href="${item.detail_url}" target="_blank" rel="noopener noreferrer">바로가기</a>`
        : "-";

      return `
        <tr>
          <td>${item.apt_name ?? "-"}</td>
          <td>${item.district ?? "-"}</td>
          <td>${item.area_m2 ?? "-"}</td>
          <td>${item.price_text ?? "-"}</td>
          <td>${item.floor_info ?? "-"}</td>
          <td>${quickSaleText}</td>
          <td>${formatDiscountRate(item.discount_rate)}</td>
          <td>${link}</td>
        </tr>
      `;
    })
    .join("");

  resultBody.innerHTML = rows;
}

async function searchListings(event) {
  event.preventDefault();

  statusElement.textContent = "검색 중...";

  try {
    const params = buildQueryFromForm(searchForm);
    const response = await fetch(`/api/listings?${params.toString()}`);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    const items = data.items ?? [];

    renderRows(items);
    statusElement.textContent = `총 ${items.length}건을 조회했습니다.`;
  } catch (error) {
    statusElement.textContent = `요청 실패: ${error}`;
    resultBody.innerHTML = '<tr><td colspan="8" class="empty">데이터를 불러오지 못했습니다.</td></tr>';
  }
}

function resetForm() {
  searchForm.reset();
  resultBody.innerHTML = '<tr><td colspan="8" class="empty">데이터가 없습니다.</td></tr>';
  statusElement.textContent = "검색 조건을 입력한 뒤 검색 버튼을 누르세요.";
}

searchForm.addEventListener("submit", searchListings);
resetButton.addEventListener("click", resetForm);
