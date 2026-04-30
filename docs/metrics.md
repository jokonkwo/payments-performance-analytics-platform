# Metrics Documentation

## Gross Payment Volume (GPV)
Definition:
SUM(transaction_amount)

Business Meaning:
Total processed transaction volume.

---

## Interchange Rate
Definition:
SUM(interchange_amount) / SUM(transaction_amount)

Business Meaning:
Percentage cost incurred from interchange processing fees.

---

## AVS Coverage %
Definition:
Transactions with AVS supplied / total transactions

Business Meaning:
Measures address verification adoption during transaction authorization.
