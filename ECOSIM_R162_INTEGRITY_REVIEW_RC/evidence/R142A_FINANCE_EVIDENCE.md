# R142A finance — client evidence and limits

**Spendable budget and actual lending limit: UNKNOWN.** R141's 865,588 ECU is a prior UI-observed p1 net result, not cash available for projects. R140B reports manual p10 default ECU, p14 yearly maintenance, p19 automatic borrowing and repayment before reserve; these are document statements from the prior audit, not independently inspected manual pages in this bundle. Static slices independently support the client computations below, not actual server settlement.

Long loan: open(t)=0 when t<=0 else prior close; borrow=max(decision change,0); repayment change=clamp(change,−open,0); close=open+borrow+repayment change; interest=close × market.loans.long.interest for period. Thus this branch prevents repayment exceeding opening balance and allows positive change without a numerical upper bound in the formula. The field is presented as a decision with no explicit limit argument at this call site, but shared setup or backend may limit it. No claim of unlimited lending follows. Variable-maturity borrowing=max(decision,0), repayment=−min(decision,0); bonds are another decision. Rates include market.loans.short.interestRate, long.interest and variableLength.interestRate, plus other market finance inputs.

Short borrowing is max(0, the negative of a computed subtotal of operating income, other borrowing and other revenue less listed operating expenses, interest, repayments and other items). The branch has no numerical maximum or explicit insufficient-funds rejection; other validation and server limits remain unknown. Next-period short repayment is max(previous short borrow,0), with interest previous borrow × prior short rate. Reserve formation is 0 for t<=0 and otherwise total revenue including borrowing minus listed expense, interest, repayment and other items. It has no explicit nonnegative clamp; the computed short borrowing algebra normally closes the included deficit, subject to inputs and branch assumptions. Prior-year cash is market.finance.prevYearEndCash at t=0 and reserve(t−1) thereafter, hence client prior cash at t=1 is zero because reserve(0)=0. This does not establish real cash lost, free reserves or settlement.

Shared active Q(t) and new T(t) distinguish repeatable projects (main window below). Client project expense = sum over T of startCost + invest, plus sum of runCost for active nonrepeatable projects. Signed runCost can reduce the client sum; it is not guaranteed cash income. Repeatable runCost is omitted from this particular reduction only. New project support is summed separately in company development-funding income, alongside market finance input and another component; timing in the client period is not proof of advance availability, eligibility, actual payment or sequencing. The separate income/expense representation confirms the relevant R139 claim; R140B's accounting sequence remains a reported manual statement, not a proven server behavior. A future annual maintenance burden and running projects' existing obligations must be checked.

All windows below are 180 raw bytes, [start,end), SHA-256; full source hashes are in status. No JS was executed.

| Purpose | Byte range [start,end) | SHA-256 of 180 bytes |
|---|---:|---|
| Loan rates/open/close | 3340–3520 | `3ad0a586255ccd3d14087f1ca63d9cf493692d830e9d0f8dc807c34b464d7804` |
| Repayment clamp | 3599–3779 | `ac99a13c043500ff12f699ff35f2b63423891eced50420e0237b213817106935` |
| Company support | 23503–23683 | `7e5230cce6eaaa3134dc8b19fb3ba24d0037c6489cb71c98d86fa2703b7146ec` |
| Interest and repayments | 43189–43369 | `0ad9af23489920e1f0384430dd1362509201198f3871904375757629a4f6576c` |
| Reserve formation | 43632–43812 | `5222be1242aecdcf21310bd5c4ce73d55b48005a49dd60bc891bffd087f946a4` |
| Short borrowing | 46107–46287 | `9813d81f417bea49b403dbfdc596aaec2b70a3eb94b5048ef888a688763e3527` |
| Prior cash | 46590–46770 | `6323488c368ead35faf3d311ed79a93f7a06faa993ab5d3a2b841b9e34849442` |
| Project expense | 70269–70449 | `d7907875056baf55fbe7d25283f5c4b03fa1acd44d750335b40e4f57847fa3c2` |

| Purpose | Byte range [start,end) | SHA-256 of 180 bytes |
|---|---:|---|
| Effect aggregation | 968672–968852 | `60afc3388157874609c7e51f5f3f144230a3e79b636008524787dffd9863c8da` |
| Support and active/new sets | 969210–969390 | `9231b967795c922683eff4eb9282544685bb0e7fbefd2165756b81becead6c4a` |
