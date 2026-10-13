"use strict";

// Original LACE point rubric: van Walraven et al., CMAJ 2010, Table 3.
// Not a CMS HWR calculation and not an individualized predicted probability.
function calculateLace({ lengthOfStayDays, acuteAdmission, charlsonScore, edVisits6Months }) {
  const values = { lengthOfStayDays, charlsonScore, edVisits6Months };
  for (const [name, value] of Object.entries(values)) {
    if (!Number.isSafeInteger(value) || value < 0) {
      throw new RangeError(name + " must be a nonnegative integer");
    }
  }
  if (typeof acuteAdmission !== "boolean") {
    throw new TypeError("acuteAdmission must be a boolean");
  }
  const lengthOfStay = lengthOfStayDays === 0 ? 0 :
    lengthOfStayDays <= 3 ? lengthOfStayDays :
    lengthOfStayDays <= 6 ? 4 :
    lengthOfStayDays <= 13 ? 5 : 7;
  const acute = acuteAdmission ? 3 : 0;
  const comorbidity = charlsonScore <= 3 ? charlsonScore : 5;
  const emergency = Math.min(edVisits6Months, 4);
  return {
    lengthOfStay, acute, comorbidity, emergency,
    total: lengthOfStay + acute + comorbidity + emergency
  };
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { calculateLace };
}

if (typeof document !== "undefined") {
  document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("lace-form");
    const result = document.getElementById("result");
    const feedback = document.getElementById("feedback");

    function getInteger(id) {
      const input = document.getElementById(id);
      if (input.value.trim() === "") throw new RangeError("All numeric fields are required.");
      const value = Number(input.value);
      if (!Number.isSafeInteger(value) || value < 0) {
        throw new RangeError("Enter nonnegative whole numbers only.");
      }
      return value;
    }

    form.addEventListener("submit", (event) => {
      event.preventDefault();
      result.hidden = true;
      feedback.textContent = "";
      try {
        const scores = calculateLace({
          lengthOfStayDays: getInteger("length-of-stay"),
          acuteAdmission: document.getElementById("acute-admission").checked,
          charlsonScore: getInteger("charlson-score"),
          edVisits6Months: getInteger("ed-visits"),
        });
        document.getElementById("total").textContent = String(scores.total);
        document.getElementById("los-points").textContent = String(scores.lengthOfStay);
        document.getElementById("acute-points").textContent = String(scores.acute);
        document.getElementById("cci-points").textContent = String(scores.comorbidity);
        document.getElementById("ed-points").textContent = String(scores.emergency);
        result.hidden = false;
      } catch (error) {
        feedback.textContent = error.message || "Invalid input.";
      }
    });
    form.addEventListener("reset", () => {
      result.hidden = true;
      feedback.textContent = "";
    });
  });
}
