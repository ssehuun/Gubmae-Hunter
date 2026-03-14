/**
 * STEP1 프론트엔드 스크립트.
 *
 * - 기본 API 연동 확인
 * - STEP6에서 실제 검색 폼 동작으로 확장 예정
 */

const loadButton = document.getElementById("load-button");
const resultElement = document.getElementById("result");

async function loadListings() {
  resultElement.textContent = "불러오는 중...";

  try {
    const response = await fetch("/api/listings");
    const data = await response.json();
    resultElement.textContent = JSON.stringify(data, null, 2);
  } catch (error) {
    resultElement.textContent = `요청 실패: ${error}`;
  }
}

loadButton.addEventListener("click", loadListings);
