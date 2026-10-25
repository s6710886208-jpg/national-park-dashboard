from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="เที่ยวอุทยานไทย | Dashboard", page_icon="🌿", layout="wide")
MONTHS = ["ต.ค.", "พ.ย.", "ธ.ค.", "ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย."]
COLORS = ["#18735a", "#e4ad4c", "#63a994", "#344b40", "#a2cbbb"]
SOURCE = "https://data.go.th/th/dataset/gdpublish-stat-tourism"


@st.cache_data
def load_data():
    frame = pd.read_csv(Path(__file__).parent / "data" / "tourism_2567.csv")
    frame["เดือน"] = pd.Categorical(frame["เดือน"], categories=MONTHS, ordered=True)
    return frame


def style_chart(fig):
    fig.update_layout(font=dict(family="Tahoma, sans-serif", size=13, color="#254438"),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      margin=dict(t=20, b=25, l=15, r=20), hoverlabel=dict(font_size=14))
    fig.update_yaxes(gridcolor="#e6ece7")
    return fig


st.markdown("""<style>
.stApp {background:#f6f8f3;color:#254438}
.block-container {padding-top:2.3rem;max-width:1480px}
h1,h2,h3 {color:#183e30}
[data-testid="stMetric"] {background:white;border:1px solid #e0e8df;border-radius:16px;padding:18px}
[data-testid="stSidebar"] {background:#eaf0e6}
.hero {background:#193f32;padding:26px 30px;border-radius:20px;color:#fff;margin-bottom:25px}
.hero h1 {color:#fff;font-size:2rem;margin:8px 0}
.hero p {color:#d6e5d8;margin:0}
.eyebrow {font-size:.8rem;letter-spacing:2px;color:#d9bd7f}
</style>
<div class="hero"><div class="eyebrow">THAILAND NATIONAL PARKS</div>
<h1>เที่ยวอุทยานไทย 🌿</h1><p>สำรวจจำนวนนักท่องเที่ยว อุทยานยอดนิยม และช่วงเวลาที่คนเดินทาง</p></div>
""", unsafe_allow_html=True)

df = load_data()
with st.sidebar:
    st.header("เลือกข้อมูล")
    st.caption("ปีงบประมาณ 2567 · ต.ค. 2566 – ก.ย. 2567")
    offices = st.multiselect("สังกัด", sorted(df["สังกัด"].unique()), placeholder="ทุกสังกัด")
    available = df[df["สังกัด"].isin(offices)] if offices else df
    parks = st.multiselect("อุทยานแห่งชาติ", sorted(available["อุทยานแห่งชาติ"].unique()), placeholder="ทุกอุทยาน")
    months = st.multiselect("เดือน", MONTHS, default=MONTHS)
    top_n = st.slider("จำนวนอุทยานในกราฟอันดับ", 5, 20, 10)
    st.caption("ช่องสังกัดและอุทยานที่ว่าง = เลือกทั้งหมด")
    st.divider()
    st.markdown(f"[แหล่งข้อมูล: data.go.th]({SOURCE})")
    st.caption("กรมอุทยานแห่งชาติ สัตว์ป่า และพันธุ์พืช")

filtered = available.copy()
if parks:
    filtered = filtered[filtered["อุทยานแห่งชาติ"].isin(parks)]
filtered = filtered[filtered["เดือน"].isin(months)]
if filtered.empty:
    st.info("ไม่มีข้อมูลตามตัวกรอง กรุณาเลือกอย่างน้อยหนึ่งเดือน หรือปรับสังกัดและอุทยาน")
    st.stop()

monthly = filtered.groupby("เดือน", observed=True)["นักท่องเที่ยว"].sum().reset_index().sort_values("เดือน")
ranking = filtered.groupby("อุทยานแห่งชาติ")["นักท่องเที่ยว"].sum().sort_values(ascending=False)
peak = monthly.loc[monthly["นักท่องเที่ยว"].idxmax()]
total = int(filtered["นักท่องเที่ยว"].sum())
st.caption(f"ปีงบประมาณ 2567 · เลือก {len(months)} เดือน · {filtered['อุทยานแห่งชาติ'].nunique()} อุทยาน")
a, b, c, d = st.columns(4)
a.metric("นักท่องเที่ยวรวม (คน)", f"{total:,}")
b.metric("อุทยานที่เลือก (แห่ง)", f"{filtered['อุทยานแห่งชาติ'].nunique():,}")
c.metric("เดือนที่มีนักท่องเที่ยวสูงสุด", str(peak["เดือน"]), f"{int(peak['นักท่องเที่ยว']):,} คน", delta_color="off")
d.metric("อุทยานยอดนิยม", ranking.index[0], f"{int(ranking.iloc[0]):,} คน", delta_color="off")
st.write("")

left, right = st.columns([1.1, 1])
with left:
    st.subheader("การเดินทางตลอดปี")
    st.caption("จำนวนนักท่องเที่ยวรวมรายเดือน ตามตัวกรอง")
    fig = px.area(monthly, x="เดือน", y="นักท่องเที่ยว", markers=True, color_discrete_sequence=COLORS)
    fig.update_traces(line_width=3, hovertemplate="%{x}<br>%{y:,.0f} คน<extra></extra>")
    st.plotly_chart(style_chart(fig), width="stretch")
with right:
    st.subheader(f"{min(top_n, len(ranking))} อุทยานยอดนิยม")
    st.caption("เรียงตามจำนวนนักท่องเที่ยวในเดือนที่เลือก")
    top = ranking.head(top_n).sort_values().rename_axis("อุทยานแห่งชาติ").reset_index()
    fig = px.bar(top, x="นักท่องเที่ยว", y="อุทยานแห่งชาติ", orientation="h", color_discrete_sequence=COLORS)
    fig.update_traces(hovertemplate="%{y}<br>%{x:,.0f} คน<extra></extra>")
    st.plotly_chart(style_chart(fig), width="stretch")

st.subheader("แต่ละอุทยานคึกคักช่วงไหน")
st.caption(f"เปรียบเทียบรายเดือนของ {min(top_n, len(ranking))} อุทยานอันดับแรก หน่วย: คน")
heat = filtered[filtered["อุทยานแห่งชาติ"].isin(ranking.head(top_n).index)].pivot_table(
    index="อุทยานแห่งชาติ", columns="เดือน", values="นักท่องเที่ยว", aggfunc="sum", observed=True)
heat = heat.reindex(index=ranking.head(top_n).index, columns=[m for m in MONTHS if m in months])
fig = px.imshow(heat, aspect="auto", color_continuous_scale=["#edf3e9", "#a8cdb6", "#18735a"], labels={"color":"คน"})
fig.update_traces(hovertemplate="%{y}<br>%{x}: %{z:,.0f} คน<extra></extra>")
fig.update_layout(height=max(360, len(heat)*26))
st.plotly_chart(style_chart(fig), width="stretch")

with st.expander("ตารางข้อมูลและดาวน์โหลด"):
    table = filtered.copy()
    table["เดือน"] = table["เดือน"].astype(str)
    st.dataframe(table, hide_index=True, width="stretch")
    st.download_button("ดาวน์โหลดข้อมูลที่เลือก (CSV)", table.to_csv(index=False).encode("utf-8-sig"),
                       "national_park_tourism_2567.csv", "text/csv")
st.divider()
st.markdown(f"ข้อมูล: [จำนวนนักท่องเที่ยวในอุทยานแห่งชาติ ปีงบประมาณ พ.ศ. 2567]({SOURCE}) · กรมอุทยานแห่งชาติ สัตว์ป่า และพันธุ์พืช")
st.caption("ข้อมูลต้นทาง tourism67.xlsx ปรับปรุง 2 ธันวาคม 2567 · จำนวนตามที่หน่วยงานรายงาน ไม่ใช่จำนวนบุคคลไม่ซ้ำ · ค่าศูนย์คงไว้ตามต้นทาง ไม่ได้แปลว่าเปิดให้บริการครบทุกเดือน")
