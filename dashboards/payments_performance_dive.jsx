// Payments Performance Analytics — MotherDuck Dive
// Live dashboard: https://app.motherduck.com/dives/b88b73e6-c16e-4459-bd20-ed72e6b4ae3c
// Built with React + Recharts + MotherDuck useSQLQuery hook
// Queries the payments_performance MotherDuck database gold layer

import { useState } from "react";
import { useSQLQuery } from "@motherduck/react-sql-query";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";

const N = (v) => (v != null ? Number(v) : 0);
const PRIORITY_COLOR = { high: "#bc1200", medium: "#e18727", low: "#2d7a00" };
const FUNDING_COLOR = { commercial: "#bd4e35", credit: "#0777b3", prepaid: "#e18727", debit: "#2d7a00" };

export const REQUIRED_DATABASES = [
  { type: "share", path: "md:_share/payments_performance_jokonkwo/5ffa01f6-e26b-4e86-b999-79c010cdc71d", alias: "payments_performance" }
];

export default function PaymentsPerformance() {
  const [selectedInteraction, setSelectedInteraction] = useState("all");

  const kpiQuery = useSQLQuery(`
    SELECT
      COUNT(DISTINCT merchant_account_id) as merchant_count,
      SUM(transaction_attempts) as total_attempts,
      ROUND(AVG(auth_rate) * 100, 1) as avg_auth_rate,
      ROUND(SUM(potential_revenue_at_risk_cents) / 100.0, 0) as total_revenue_at_risk
    FROM "payments_performance"."main"."mart_auth_rate_performance"
  `);

  const authGapSQL = selectedInteraction === "all"
    ? `SELECT a.merchant_account_id, m.merchant_name, a.shopper_interaction,
        ROUND(AVG(a.auth_rate) * 100, 1) as avg_auth_rate_pct,
        ROUND(AVG(a.auth_rate_vs_benchmark) * 100, 1) as gap_pct,
        SUM(a.transaction_attempts) as total_attempts,
        ROUND(SUM(a.potential_revenue_at_risk_cents) / 100.0, 0) as revenue_at_risk_usd
       FROM "payments_performance"."main"."mart_auth_rate_performance" a
       JOIN "payments_performance"."main"."dim_merchant" m ON a.merchant_account_id = m.merchant_account_id
       GROUP BY 1,2,3 ORDER BY gap_pct ASC LIMIT 12`
    : `SELECT a.merchant_account_id, m.merchant_name, a.shopper_interaction,
        ROUND(AVG(a.auth_rate) * 100, 1) as avg_auth_rate_pct,
        ROUND(AVG(a.auth_rate_vs_benchmark) * 100, 1) as gap_pct,
        SUM(a.transaction_attempts) as total_attempts,
        ROUND(SUM(a.potential_revenue_at_risk_cents) / 100.0, 0) as revenue_at_risk_usd
       FROM "payments_performance"."main"."mart_auth_rate_performance" a
       JOIN "payments_performance"."main"."dim_merchant" m ON a.merchant_account_id = m.merchant_account_id
       WHERE a.shopper_interaction = '${selectedInteraction}'
       GROUP BY 1,2,3 ORDER BY gap_pct ASC LIMIT 12`;

  const authGapQuery = useSQLQuery(authGapSQL, { enabled: true });

  const interchangeQuery = useSQLQuery(`
    SELECT card_funding, shopper_interaction,
      SUM(transaction_count) as total_txns,
      ROUND(AVG(avg_interchange_rate_bps), 1) as avg_rate_bps,
      ROUND(SUM(total_interchange_cents) / 100.0, 0) as total_interchange_usd
    FROM "payments_performance"."main"."mart_interchange_performance"
    GROUP BY 1, 2 ORDER BY avg_rate_bps DESC LIMIT 12
  `);

  const recoQuery = useSQLQuery(`
    SELECT recommendation_type, priority,
      COUNT(*) as merchant_count,
      SUM(affected_transaction_count) as total_affected,
      ROUND(SUM(estimated_annual_impact_cents) / 100.0, 0) as annual_impact_usd
    FROM "payments_performance"."main"."mart_payment_optimization_recommendations"
    GROUP BY 1, 2 ORDER BY annual_impact_usd DESC LIMIT 9
  `);

  const kpiRows = Array.isArray(kpiQuery.data) ? kpiQuery.data : [];
  const kpi = kpiRows[0] || {};
  const authRows = Array.isArray(authGapQuery.data) ? authGapQuery.data : [];
  const authChartData = authRows.map(r => ({
    name: String(r.merchant_name || "").replace("Merchant_", "").replace(/_/g, " "),
    channel: String(r.shopper_interaction || ""),
    gap: N(r.gap_pct),
  }));
  const icRows = Array.isArray(interchangeQuery.data) ? interchangeQuery.data : [];
  const icChartData = icRows.map(r => ({
    name: `${r.card_funding} / ${r.shopper_interaction}`,
    funding: String(r.card_funding || ""),
    rate_bps: N(r.avg_rate_bps),
  }));
  const recoRows = Array.isArray(recoQuery.data) ? recoQuery.data : [];

  const fmt = (n) => n >= 1_000_000 ? `$${(n/1_000_000).toFixed(1)}M`
    : n >= 1_000 ? `$${(n/1_000).toFixed(0)}K` : `$${n}`;
  const fmtNum = (n) => n >= 1_000_000 ? `${(n/1_000_000).toFixed(1)}M`
    : n >= 1_000 ? `${(n/1_000).toFixed(0)}K` : String(n);

  return (
    <div style={{ background: "#f8f8f8", minHeight: "100vh", padding: "24px", fontFamily: "system-ui, sans-serif", color: "#231f20" }}>
      <div style={{ marginBottom: "24px" }}>
        <h1 style={{ fontSize: "22px", fontWeight: 700, margin: 0 }}>Payments Performance Analytics</h1>
        <p style={{ fontSize: "13px", color: "#6a6a6a", margin: "4px 0 0" }}>8.25M authorization attempts · 50 merchants · 2024</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "32px", marginBottom: "32px" }}>
        {[
          { label: "Merchants", value: kpiQuery.isLoading ? "—" : fmtNum(N(kpi.merchant_count)) },
          { label: "Total Attempts", value: kpiQuery.isLoading ? "—" : fmtNum(N(kpi.total_attempts)) },
          { label: "Avg Auth Rate", value: kpiQuery.isLoading ? "—" : `${N(kpi.avg_auth_rate)}%` },
          { label: "Revenue at Risk", value: kpiQuery.isLoading ? "—" : fmt(N(kpi.total_revenue_at_risk)), highlight: true },
        ].map((k, i) => (
          <div key={i}>
            {kpiQuery.isLoading
              ? <div style={{ height: "48px", width: "120px", background: "#e0e0e0", borderRadius: "4px" }} />
              : <p style={{ fontSize: "36px", fontWeight: 700, margin: 0, color: k.highlight ? "#bc1200" : "#231f20" }}>{k.value}</p>
            }
            <p style={{ fontSize: "12px", color: "#6a6a6a", margin: "4px 0 0" }}>{k.label}</p>
          </div>
        ))}
      </div>

      <div style={{ marginBottom: "32px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
          <div>
            <h2 style={{ fontSize: "15px", fontWeight: 600, margin: 0 }}>Authorization Rate Gap vs Benchmark</h2>
            <p style={{ fontSize: "12px", color: "#6a6a6a", margin: "2px 0 0" }}>Negative values = below benchmark. Sorted worst first.</p>
          </div>
          <select value={selectedInteraction} onChange={e => setSelectedInteraction(e.target.value)}
            style={{ fontSize: "12px", padding: "4px 8px", border: "1px solid #ccc", borderRadius: "4px", background: "#fff" }}>
            {["all", "ecommerce", "recurring", "pos", "moto"].map(v => (
              <option key={v} value={v}>{v === "all" ? "All channels" : v}</option>
            ))}
          </select>
        </div>
        {authGapQuery.isLoading
          ? <div style={{ height: "220px", background: "#e8e8e8", borderRadius: "4px" }} />
          : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={authChartData} layout="vertical" margin={{ left: 120, right: 60, top: 4, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#eee" horizontal={false} />
                <XAxis type="number" tickFormatter={v => `${v}pp`} fontSize={11} domain={[-12, 2]} />
                <YAxis type="category" dataKey="name" fontSize={10} width={115} />
                <Tooltip formatter={(v) => [`${v}pp`, "Gap vs benchmark"]} />
                <Bar dataKey="gap" radius={[0, 2, 2, 0]}>
                  {authChartData.map((entry, i) => (
                    <Cell key={i} fill={entry.gap < -5 ? "#bc1200" : entry.gap < 0 ? "#e18727" : "#2d7a00"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )
        }
      </div>

      <div style={{ marginBottom: "32px" }}>
        <h2 style={{ fontSize: "15px", fontWeight: 600, margin: "0 0 4px" }}>Interchange Rate by Funding Source & Channel</h2>
        <p style={{ fontSize: "12px", color: "#6a6a6a", margin: "0 0 12px" }}>Basis points (bps). 100 bps = 1.00% of transaction value.</p>
        {interchangeQuery.isLoading
          ? <div style={{ height: "200px", background: "#e8e8e8", borderRadius: "4px" }} />
          : (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={icChartData} margin={{ left: 8, right: 8, top: 4, bottom: 40 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
                <XAxis dataKey="name" fontSize={10} angle={-35} textAnchor="end" interval={0} />
                <YAxis tickFormatter={v => `${v}bps`} fontSize={11} domain={[0, 300]} />
                <Tooltip formatter={(v) => [`${v} bps`, "Avg interchange rate"]} />
                <Bar dataKey="rate_bps" radius={[2, 2, 0, 0]}>
                  {icChartData.map((entry, i) => (
                    <Cell key={i} fill={FUNDING_COLOR[entry.funding] || "#638CAD"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )
        }
      </div>

      <div>
        <h2 style={{ fontSize: "15px", fontWeight: 600, margin: "0 0 4px" }}>Optimization Recommendations</h2>
        <p style={{ fontSize: "12px", color: "#6a6a6a", margin: "0 0 12px" }}>Ranked by estimated annual impact across merchant portfolio.</p>
        {recoQuery.isLoading
          ? <div style={{ height: "180px", background: "#e8e8e8", borderRadius: "4px" }} />
          : (
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "12px" }}>
              <thead>
                <tr style={{ borderBottom: "2px solid #ddd" }}>
                  {["Recommendation", "Priority", "Merchants", "Affected Txns", "Annual Impact"].map(h => (
                    <th key={h} style={{ padding: "6px 8px", textAlign: "left", color: "#6a6a6a", fontWeight: 600 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {recoRows.map((r, i) => (
                  <tr key={i} style={{ borderBottom: "1px solid #eee" }}>
                    <td style={{ padding: "6px 8px", fontWeight: 500 }}>{String(r.recommendation_type || "").replace(/_/g, " ")}</td>
                    <td style={{ padding: "6px 8px" }}>
                      <span style={{ background: PRIORITY_COLOR[r.priority] || "#aaa", color: "#fff", padding: "2px 6px", borderRadius: "3px", fontSize: "11px", fontWeight: 600 }}>
                        {String(r.priority || "").toUpperCase()}
                      </span>
                    </td>
                    <td style={{ padding: "6px 8px", color: "#6a6a6a" }}>{N(r.merchant_count)}</td>
                    <td style={{ padding: "6px 8px", color: "#6a6a6a" }}>{fmtNum(N(r.total_affected))}</td>
                    <td style={{ padding: "6px 8px", fontWeight: 700, color: "#2d7a00" }}>{fmt(N(r.annual_impact_usd))}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )
        }
      </div>
    </div>
  );
}
