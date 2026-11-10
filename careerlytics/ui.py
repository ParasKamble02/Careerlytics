"""Visual layer: CSS theme (matches the reference dashboard design), small HTML components and Plotly helpers."""
from __future__ import annotations

import html as _html

import streamlit as st

PRIMARY, PRIMARY_SOFT, GRAY_BAR = "#4F5BD5", "#E6E8FA", "#DDE0EC"
DONUT = ["#4F5BD5", "#8E96E6", "#C3C7F0", "#E3E5F8"]
GREEN, RED, ORANGE, CYAN, PURPLE = "#2FB36D", "#E5484D", "#FFA53B", "#3CC4DF", "#7C7FDB"
AVATARS = ["#4F5BD5", "#FFA53B", "#3CC4DF", "#E5648B", "#2FB36D", "#7C7FDB"]

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap');
:root{--primary:#4F5BD5;--soft:#E6E8FA;--ink:#2B2F4A;--muted:#9AA0B8;--line:#EDEEF5;--side:#F3F4FA;
      --green:#2FB36D;--red:#E5484D;--orange:#FFA53B;--cyan:#3CC4DF}
html, body, .stApp, .stApp * {font-family:'Poppins','Segoe UI',sans-serif;}
.stApp{background:#fff;color:var(--ink)}
.material-symbols-rounded, [data-testid="stIconMaterial"]{font-family:'Material Symbols Rounded'!important}
header[data-testid="stHeader"]{background:transparent}
[data-testid="stAppDeployButton"],[data-testid="stMainMenu"],[data-testid="stToolbarActions"],[data-testid="stDecoration"],#MainMenu,footer{display:none!important}
/* sidebar open/close toggles: always visible, small round icon */
[data-testid="stExpandSidebarButton"],[data-testid="stSidebarCollapsedControl"] button,[data-testid="stSidebarCollapseButton"] button{
  color:var(--primary)!important;opacity:1!important;visibility:visible!important;background:var(--soft);border-radius:50%}
[data-testid="stSidebarCollapsedControl"],[data-testid="stExpandSidebarButton"]{z-index:1000}
.block-container{padding:1.1rem 2.4rem 3rem!important;max-width:100%!important}
h1,h2,h3{font-weight:500!important;color:var(--ink)}

/* sidebar */
section[data-testid="stSidebar"]{background:var(--side);border-right:0}
section[data-testid="stSidebar"][aria-expanded="true"]{min-width:250px;max-width:250px}
[data-testid="stSidebarContent"]{padding:1.4rem .8rem}
# .brand{display:flex;align-items:center;gap:10px;font-weight:600;font-size:12.5px;letter-spacing:.06em;margin:2px 0 26px 10px;color:var(--ink)}
# .brand .logo{width:24px;height:24px;border-radius:50%;background:var(--primary);color:#fff;display:flex;align-items:center;justify-content:center;font-size:12px}
.brand{display:flex;align-items:center;gap:11px;margin:2px 0 24px 8px}
.brand svg{flex:none;filter:drop-shadow(0 3px 6px rgba(79,91,213,.28))}
.brand .name{font-weight:600;font-size:13px;letter-spacing:.07em;color:var(--ink);line-height:1.1}
.brand .tag{font-weight:400;font-size:9.5px;line-height:1.35;color:var(--muted);margin-top:3px;letter-spacing:.01em}
.menu-label{font-size:10px;letter-spacing:.1em;color:#B3B7CB;margin:20px 0 8px 14px}
[class*="st-key-nav_"] .stButton, [class*="st-key-navon_"] .stButton,
[class*="st-key-nav_"] button, [class*="st-key-navon_"] button{width:100%}
[class*="st-key-nav_"] button, [class*="st-key-navon_"] button{justify-content:flex-start;border:0;background:transparent;
  color:#8E93AC;padding:.5rem .9rem;border-radius:8px;box-shadow:none;min-height:0}
[class*="st-key-nav_"] button p, [class*="st-key-navon_"] button p{font-size:13px;margin:0}
[class*="st-key-nav_"] button:hover{background:#E9EBF8;color:var(--primary)}
[class*="st-key-navon_"] button{background:var(--soft);color:var(--primary)}
[class*="st-key-navon_"] button p{font-weight:500}
[data-testid="stSidebar"] .stElementContainer{margin-bottom:-.35rem}

/* top bar */
[class*="st-key-search"] input{background:#F4F5FA;border:0;font-size:13px;color:var(--ink)}
[class*="st-key-search"] [data-baseweb="input"], [class*="st-key-search"] [data-baseweb="base-input"]{background:#F4F5FA;border:0;border-radius:8px}
.user-chip{display:flex;align-items:center;justify-content:flex-end;gap:10px;font-size:12.5px;font-weight:500;height:40px}
.avatar{width:30px;height:30px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;color:#fff;font-weight:600;font-size:11px;flex:none}
[class*="st-key-bell"] button{border:0;background:transparent;box-shadow:none;min-height:0;padding:.35rem .5rem}
.page-title{font-size:18px;font-weight:500;margin:18px 0 18px;padding-top:6px;border-top:1px solid var(--line)}

/* cards */
[class*="st-key-card_"]{background:#fff;border:1px solid var(--line);border-radius:12px;padding:20px 24px 14px}
.c-label{font-size:13px;font-weight:500;color:#464B69}
.c-big{font-size:22px;font-weight:600;line-height:1.25;margin:4px 0 0}
.c-sub{font-size:11px;color:var(--muted);margin-top:8px}
.c-delta{font-size:11px;font-weight:600;margin-top:4px}
.c-delta.up{color:var(--green)} .c-delta.down{color:var(--red)} .c-delta .m{color:var(--muted);font-weight:400}
.legend{display:flex;gap:18px;flex-wrap:wrap;font-size:11px;color:#8A8FA8;margin-top:4px}
.legend .dot{width:7px;height:7px;border-radius:50%;display:inline-block;margin-right:6px}
.legend b{color:var(--ink);font-weight:500}
[class*="st-key-vr_"]{display:flex;justify-content:flex-end}
[class*="st-key-vr_"] button{border:1px solid #E7E9F4;background:#fff;color:var(--primary);min-height:0;padding:.2rem .95rem;
  border-radius:6px;box-shadow:0 3px 10px rgba(79,91,213,.10)}
[class*="st-key-vr_"] button p{font-size:12px;font-weight:500;margin:0}

/* list rows (top recommended jobs, actions) */
.row{display:flex;align-items:center;gap:12px;padding:12px 0;border-bottom:1px solid var(--line);font-size:12px}
.row:last-child{border-bottom:0}
.row .grow{flex:1;min-width:0}.row .t{font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.row .s{color:var(--muted);font-size:11px}.row .r{text-align:right;font-weight:600;font-size:12.5px}
.row .num,.step .num{width:26px;height:26px;border-radius:50%;background:var(--soft);color:var(--primary);display:flex;align-items:center;justify-content:center;font-weight:600;font-size:11px;flex:none}
.pdot{width:9px;height:9px;border-radius:50%;flex:none}

/* chips & bars */
.chip{display:inline-block;padding:3px 10px;border-radius:999px;font-size:11.5px;margin:0 6px 6px 0;font-weight:500}
.chip.ok{background:#E8F7EF;color:#1E8E59}.chip.miss{background:#FDECEC;color:#C0343A}.chip.neutral{background:var(--soft);color:var(--primary)}
.chip.high{background:#FDECEC;color:#C0343A}.chip.medium{background:#FFF1DD;color:#B26A00}.chip.low{background:#E8F7EF;color:#1E8E59}
.chip.strong{background:#E8F7EF;color:#1E8E59}.chip.good{background:var(--soft);color:var(--primary)}.chip.stretch{background:#F1F2F7;color:#7C819B}
.bar-row{display:flex;align-items:center;gap:12px;font-size:12px;margin:9px 0}
.bar-row .n{width:130px;color:#464B69;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bar-row .b{flex:1;height:8px;background:#F1F2F8;border-radius:6px;overflow:hidden}.bar-row .b i{display:block;height:100%;border-radius:6px}
.bar-row .v{width:42px;text-align:right;color:var(--muted)}
.step{display:flex;gap:14px;padding:12px 0;border-bottom:1px dashed var(--line);font-size:12.5px;align-items:center}
.step:last-child{border-bottom:0}
.note{background:var(--soft);color:#3B44A8;border-radius:10px;padding:10px 16px;font-size:12.5px;margin-bottom:14px}
.kpi{font-size:12px;color:var(--muted)}.kpi b{display:block;font-size:22px;color:var(--ink);font-weight:600;margin-top:2px}
.feed-item{display:flex;gap:10px;align-items:flex-start;padding:10px 0;border-bottom:1px solid var(--line);font-size:12.5px}
.feed-item .t{color:var(--muted);font-size:11px}
div[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:10px}
button[kind="primary"]{background:var(--primary);border-color:var(--primary)}
"""

def inject_css() -> None:
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

def html(s: str) -> None:
    """Render an HTML snippet (newlines/indentation collapsed so Markdown never treats it as code)."""
    st.markdown(" ".join(line.strip() for line in s.strip().splitlines()), unsafe_allow_html=True)

def esc(x) -> str:
    return _html.escape(str(x))

#small components
LOGO_SVG = (
    '<svg width="36" height="36" viewBox="0 0 34 34" xmlns="http://www.w3.org/2000/svg">'
    '<defs><linearGradient id="clg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#4F5BD5"/>'
    '<stop offset="1" stop-color="#8E96E6"/></linearGradient></defs>'
    '<rect width="34" height="34" rx="10" fill="url(#clg)"/>'
    '<rect x="8" y="19" width="4.5" height="7" rx="1.5" fill="#fff" opacity=".75"/>'
    '<rect x="14.8" y="14" width="4.5" height="12" rx="1.5" fill="#fff" opacity=".9"/>'
    '<rect x="21.6" y="8.5" width="4.5" height="17.5" rx="1.5" fill="#fff"/>'
    '<circle cx="25" cy="6.5" r="3" fill="#FFA53B" stroke="#fff" stroke-width="1.5"/></svg>'
)

def brand_html(style: str = "") -> str:
    """Logo + name + subtitle, used in the sidebar and on the login screen."""
    return (f'<div class="brand" style="{style}">{LOGO_SVG}<div><div class="name">CAREERLYTICS</div>'
            '<div class="tag">AI-Powered Career Intelligence &amp; Job Discovery</div></div></div>')

def page_title(text: str) -> None:
    html(f'<div class="page-title">{esc(text)}</div>')

def initials(text: str) -> str:
    parts = [p for p in str(text).replace("-", " ").split() if p]
    return (parts[0][0] + (parts[1][0] if len(parts) > 1 else "")).upper() if parts else "?"

def avatar(text: str, idx: int = 0) -> str:
    return f'<span class="avatar" style="background:{AVATARS[idx % len(AVATARS)]}">{esc(initials(text))}</span>'

def delta_html(pct: float, suffix: str = "vs previous period") -> str:
    up = pct >= 0
    return f'<div class="c-delta {"up" if up else "down"}">{"↑" if up else "↓"} {abs(pct):.1f}% <span class="m">{esc(suffix)}</span></div>'

def card_header(label: str, big: str | None = None, delta: str = "", sub: str = "") -> None:
    parts = [f'<div class="c-label">{esc(label)}</div>']
    if big is not None:
        parts.append(f'<div class="c-big">{esc(big)}</div>')
    parts.append(delta)
    if sub:
        parts.append(f'<div class="c-sub">{esc(sub)}</div>')
    html("".join(parts))

def legend(items) -> None:
    """items: [(color, label, value_or_None)]"""
    html('<div class="legend">' + "".join(
        f'<span><span class="dot" style="background:{c}"></span>{esc(l)}' + (f' &nbsp;<b>{esc(v)}</b>' if v is not None else "") + "</span>"
        for c, l, v in items) + "</div>")

def chips(items, kind: str = "neutral") -> str:
    return "".join(f'<span class="chip {kind}">{esc(i)}</span>' for i in items)

def progress_rows(rows, color: str = PRIMARY) -> None:
    """rows: [(label, value 0-100, display_text, color_or_None)]"""
    html("".join(
        f'<div class="bar-row"><span class="n">{esc(n)}</span><span class="b"><i style="width:{max(0, min(100, v)):.0f}%;background:{c or color}"></i></span>'
        f'<span class="v">{esc(t)}</span></div>' for n, v, t, c in rows))

def bubbles_svg(items) -> str:
    """Three overlapping bubbles like the reference 'Your Rating' card. items: [(label, value 0-100, color)] (3 items)."""
    pos = [(105, 78), (92, 200), (232, 140)]
    out = ['<svg viewBox="0 0 340 280" width="100%" height="260" xmlns="http://www.w3.org/2000/svg">']
    for (label, value, color), (cx, cy) in zip(items, pos):
        r = 30 + value * 0.36
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r + 6:.0f}" fill="none" stroke="{color}" stroke-opacity=".45" stroke-width="1.5"/>')
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r:.0f}" fill="{color}"/>')
        out.append(f'<text x="{cx}" y="{cy + 2}" text-anchor="middle" fill="#fff" font-size="21" font-weight="500" font-family="Poppins,sans-serif">{value:.0f}%</text>')
        out.append(f'<text x="{cx}" y="{cy + 20}" text-anchor="middle" fill="#fff" font-size="11" font-family="Poppins,sans-serif">{esc(label)}</text>')
    out.append("</svg>")
    return "".join(out)

def tier_chip(tier: str) -> str:
    return f'<span class="chip {tier.lower()}">{esc(tier)}</span>'

#plotly helpers
def style(fig, height: int = 230, legend_on: bool = False, grid: bool = True):
    fig.update_layout(
        height=height, margin=dict(l=0, r=0, t=8, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Poppins, sans-serif", size=11, color="#9AA0B8"), showlegend=legend_on, bargap=0.38,
        hoverlabel=dict(bgcolor="#2B2F4A", font_color="#fff", font_size=12),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, showline=False, tickfont=dict(size=10, color="#B3B7CB"))
    fig.update_yaxes(showgrid=grid, gridcolor="#F1F2F8", zeroline=False, showline=False, tickfont=dict(size=10, color="#B3B7CB"))
    return fig

def show(fig, key: str) -> None:
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key=key)

def paired_bars(labels, now, prev, name_now="Current", name_prev="Previous", height=210):
    import plotly.graph_objects as go
    fig = go.Figure()
    fig.add_bar(x=labels, y=now, name=name_now, marker_color=PRIMARY)
    fig.add_bar(x=labels, y=prev, name=name_prev, marker_color=GRAY_BAR)
    fig.update_layout(barmode="group", bargroupgap=0.1)
    return style(fig, height)

def donut(labels, values, center_title: str, center_sub: str, height=190, colors=None, unit="jobs"):
    import plotly.graph_objects as go
    fig = go.Figure(go.Pie(labels=labels, values=values, hole=0.66, sort=False, marker=dict(colors=colors or DONUT[: len(values)]),
                           textinfo="none", hovertemplate="%{label}<br>%{value} " + unit + " (%{percent})<extra></extra>"))
    fig.add_annotation(text=f"<b>{center_title}</b><br><span style='font-size:10px;color:#9AA0B8'>{center_sub}</span>", showarrow=False, font=dict(size=17, color="#2B2F4A"))
    return style(fig, height, grid=False)

def line_compare(x, now, prev, name_now="This week", name_prev="Last week", height=190):
    import plotly.graph_objects as go
    fig = go.Figure()
    fig.add_scatter(x=x, y=prev, name=name_prev, mode="lines", line=dict(color="#D5D8E6", width=2, shape="spline"))
    fig.add_scatter(x=x, y=now, name=name_now, mode="lines+markers", line=dict(color=PRIMARY, width=2.6, shape="spline"), marker=dict(size=5))
    return style(fig, height)

def hbar(labels, values, colors=None, height=320, fmt="{:.0%}"):
    import plotly.graph_objects as go
    fig = go.Figure(go.Bar(x=values, y=labels, orientation="h", marker_color=colors or PRIMARY,
                           text=[fmt.format(v) for v in values], textposition="outside", cliponaxis=False,
                           hovertemplate="%{y}: %{text}<extra></extra>"))
    fig.update_yaxes(autorange="reversed", showgrid=False)
    fig.update_xaxes(visible=False, range=[0, (max(values) * 1.2) if len(values) else 1])
    fig.update_layout(bargap=0.3)
    return style(fig, height, grid=False)
