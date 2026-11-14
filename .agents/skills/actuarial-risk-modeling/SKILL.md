---
name: actuarial-risk-modeling
description: Models workforce compensation distributions, Bühlmann-Kish empirical Bayes shrinkage, Total Cost to Employer (CTC) accruals, and cash flow risk bounds under hyperinflation.
---

# Actuarial Risk Modeling Skill

## Purpose
Formulate mathematically rigorous models for salary distribution shrinkage, total employment cost projection, turnover liability estimation, and compensation credibility.

## Key Formulations
1. **Total Cost to Employer (CTC)**:
   $$\text{CTC} = 12 \times \text{Gross} + 12 \times \text{SSO}_{\text{emp}} (23\%) + \text{Sanavat}_{\text{annual}} + \text{Eydi}_{\text{annual}} + \text{LeaveCarryover} + \text{Friction}$$
   *Rule*: Never accrue for 26 days of statutory annual leave in addition to 12 months salary; only accrue for expected unexercised carryover (up to 9 days $\times$ unutilized probability).
2. **Bühlmann-Kish Credibility Shrinkage**:
   $$Z_k = \frac{n_{\text{eff}}}{n_{\text{eff}} + K}, \quad K = \frac{\sigma^2_{\text{within}}}{\sigma^2_{\text{between}}}, \quad n_{\text{eff}} = \frac{(\sum w_i)^2}{\sum w_i^2}$$
   *Clamping*: Always enforce $K_{\min} \le K \le K_{\max}$ ($0.1 \le K \le 100.0$) to prevent division by zero or collapse when cluster variance is negligible.
3. **Net-to-Gross Analytical Solver**:
   Solve piecewise linear equation directly in $O(1)$:
   $$G = \frac{\text{Net} - \text{Intercept}_k}{1 - r_k (1 - s)}$$
   Verify boundary condition: $G \in [\text{SlabMin}_k, \text{SlabMax}_k]$.
