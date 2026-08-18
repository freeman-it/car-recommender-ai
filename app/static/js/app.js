/* Car Recommender AI 前端逻辑 */
(function () {
  "use strict";

  const form = document.getElementById("questionnaire-form");
  const formError = document.getElementById("form-error");
  const submitBtn = document.getElementById("submit-btn");
  const formSection = document.getElementById("form-section");
  const resultSection = document.getElementById("result-section");
  const resultList = document.getElementById("result-list");
  const adviceBox = document.getElementById("advice-box");
  const seatsSlider = document.getElementById("seats");
  const seatsValue = document.getElementById("seats-value");
  const budgetMin = document.getElementById("budget_min");
  const budgetMax = document.getElementById("budget_max");
  const budgetTip = document.getElementById("budget-tip");
  const brandGroup = document.getElementById("brand-group");
  const resetBtn = document.getElementById("reset-btn");

  const ENERGY_MAP = { 燃油: "fuel", 混动: "hybrid", 纯电: "ev" };

  /* ---------- 工具 ---------- */
  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text == null ? "" : String(text);
    return div.innerHTML;
  }

  function showError(msg) {
    formError.textContent = msg;
  }

  function clearError() {
    formError.textContent = "";
  }

  function setLoading(isLoading) {
    if (isLoading) {
      submitBtn.disabled = true;
      submitBtn.innerHTML =
        '<span class="loading"></span><span class="btn-text">正在计算...</span>';
    } else {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<span class="btn-text">生成推荐方案</span>';
    }
  }

  /* ---------- 初始化 ---------- */
  async function loadBrands() {
    try {
      const resp = await fetch("/api/cars");
      if (!resp.ok) throw new Error("加载车型失败");
      const cars = await resp.json();
      const brands = [...new Set(cars.map((c) => c.brand))].sort();
      if (brands.length === 0) {
        brandGroup.innerHTML = '<span class="hint">暂无品牌可选</span>';
        return;
      }
      brandGroup.innerHTML = brands
        .map(
          (b) =>
            '<label class="chip"><input type="checkbox" name="brand" value="' +
            escapeHtml(b) +
            '"><span>' +
            escapeHtml(b) +
            "</span></label>"
        )
        .join("");
    } catch (err) {
      brandGroup.innerHTML =
        '<span class="hint">品牌加载失败：' + escapeHtml(err.message) + "</span>";
    }
  }

  seatsSlider.addEventListener("input", function () {
    seatsValue.textContent = seatsSlider.value + " 座";
  });

  function updateBudgetTip() {
    const min = parseFloat(budgetMin.value) || 0;
    const max = parseFloat(budgetMax.value) || 0;
    if (max > 0 && max <= min) {
      budgetTip.textContent = "⚠ 预算上限需大于下限";
      budgetTip.style.color = "var(--danger)";
    } else {
      budgetTip.textContent = "建议下限不高于上限，相差越大可选车型越多";
      budgetTip.style.color = "";
    }
  }

  budgetMin.addEventListener("input", updateBudgetTip);
  budgetMax.addEventListener("input", updateBudgetTip);

  /* ---------- 表单收集 ---------- */
  function collectPayload() {
    const min = parseFloat(budgetMin.value);
    const max = parseFloat(budgetMax.value);
    if (isNaN(min) || isNaN(max) || min < 0 || max <= 0) {
      throw new Error("请填写有效的预算区间");
    }
    if (max <= min) {
      throw new Error("预算上限必须大于预算下限");
    }

    const energyType = Array.from(
      document.querySelectorAll('input[name="energy"]:checked')
    ).map((el) => el.value);

    const purposeEl = document.querySelector('input[name="purpose"]:checked');
    const priorityEl = document.querySelector('input[name="priority"]:checked');

    const brandPreferences = Array.from(
      document.querySelectorAll('input[name="brand"]:checked')
    ).map((el) => el.value);

    return {
      budget_min: min,
      budget_max: max,
      energy_type: energyType,
      purpose: purposeEl ? purposeEl.value : "家庭用车",
      seats: parseInt(seatsSlider.value, 10),
      brand_preferences: brandPreferences,
      priority: priorityEl ? priorityEl.value : "综合",
    };
  }

  /* ---------- 结果渲染 ---------- */
  function rankClass(i) {
    if (i === 0) return "top1";
    if (i === 1) return "top2";
    if (i === 2) return "top3";
    return "";
  }

  function renderResults(data) {
    resultList.innerHTML = "";
    if (!data.results || data.results.length === 0) {
      resultList.innerHTML =
        '<div class="empty-state">没有找到符合条件的车型，试试调整预算或条件</div>';
      return;
    }

    data.results.forEach(function (r, i) {
      const car = r.car;
      const item = document.createElement("div");
      item.className = "result-item";

      const reasonsHtml = (r.reasons || [])
        .map(function (reason) {
          return "<li>" + escapeHtml(reason) + "</li>";
        })
        .join("");

      const tagsHtml = (car.tags || [])
        .slice(0, 4)
        .map(function (t) {
          return '<span class="meta-tag">' + escapeHtml(t) + "</span>";
        })
        .join("");

      item.innerHTML =
        '<div class="result-rank ' +
        rankClass(i) +
        '">' +
        (i + 1) +
        "</div>" +
        '<div class="result-main">' +
        '<div class="result-title">' +
        "<h3>" +
        escapeHtml(car.name) +
        "</h3>" +
        '<span class="brand">' +
        escapeHtml(car.brand) +
        "</span>" +
        '<span class="result-score">' +
        r.score +
        "<small> /100</small></span>" +
        "</div>" +
        '<div class="result-meta">' +
        '<span class="meta-tag energy">' +
        escapeHtml(car.energy_type) +
        "</span>" +
        '<span class="meta-tag price">' +
        car.price +
        " 万元</span>" +
        '<span class="meta-tag">' +
        car.seats +
        " 座</span>" +
        '<span class="meta-tag">' +
        escapeHtml(car.segment) +
        "</span>" +
        tagsHtml +
        "</div>" +
        '<ul class="reasons">' +
        reasonsHtml +
        "</ul>" +
        "</div>";

      resultList.appendChild(item);
    });
  }

  function showAdvice(advice) {
    if (!advice) {
      adviceBox.hidden = true;
      return;
    }
    adviceBox.hidden = false;
    adviceBox.innerHTML =
      "<strong>AI 购车建议</strong>" + escapeHtml(advice);
  }

  /* ---------- 提交 ---------- */
  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    clearError();

    let payload;
    try {
      payload = collectPayload();
    } catch (err) {
      showError(err.message);
      return;
    }

    setLoading(true);
    try {
      const resp = await fetch("/api/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await resp.json();
      if (!resp.ok) {
        throw new Error(data.detail || "推荐失败，请稍后再试");
      }
      showAdvice(data.advice);
      renderResults(data);
      formSection.hidden = true;
      resultSection.hidden = false;
      resultSection.scrollIntoView({ behavior: "smooth" });
    } catch (err) {
      showError(err.message);
    } finally {
      setLoading(false);
    }
  });

  /* ---------- 重置 ---------- */
  resetBtn.addEventListener("click", function () {
    resultSection.hidden = true;
    formSection.hidden = false;
    formSection.scrollIntoView({ behavior: "smooth" });
  });

  /* ---------- 启动 ---------- */
  loadBrands();
  updateBudgetTip();
})();
