"use strict";
const { test } = require("node:test");
const assert = require("node:assert/strict");
const { calculateLace } = require("../web/app.js");

test("maximum and minimum component sums", () => {
  assert.deepEqual(calculateLace({
    lengthOfStayDays: 14, acuteAdmission: true, charlsonScore: 4, edVisits6Months: 4
  }), { lengthOfStay: 7, acute: 3, comorbidity: 5, emergency: 4, total: 19 });
  assert.equal(calculateLace({
    lengthOfStayDays: 0, acuteAdmission: false, charlsonScore: 0, edVisits6Months: 0
  }).total, 0);
});

test("published length-of-stay category boundaries", () => {
  const values = [[0,0],[1,1],[2,2],[3,3],[4,4],[6,4],[7,5],[13,5],[14,7]];
  for (const [days, expected] of values) {
    assert.equal(calculateLace({
      lengthOfStayDays: days, acuteAdmission: false, charlsonScore: 0, edVisits6Months: 0
    }).lengthOfStay, expected);
  }
});

test("rejects fractions, negative numbers, NaN, and invalid boolean", () => {
  const values = { lengthOfStayDays: 2, acuteAdmission: false, charlsonScore: 1, edVisits6Months: 2 };
  for (const [key, invalid] of [
    ["lengthOfStayDays", -1], ["charlsonScore", 1.5],
    ["edVisits6Months", NaN], ["acuteAdmission", 1],
    ["lengthOfStayDays", Number.MAX_SAFE_INTEGER + 1],
  ]) {
    assert.throws(() => calculateLace({ ...values, [key]: invalid }));
  }
});
