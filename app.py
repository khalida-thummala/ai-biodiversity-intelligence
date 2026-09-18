import streamlit as st
import json
import os
import io
from dotenv import load_dotenv

from src.engine import EnvironmentalScientistEngine
from src.knowledge_base import ScientificKnowledgeBase
from src.agent import BiodiversityAgent
from src.report_generator import generate_user_assessment_docx

load_dotenv()

st.set_page_config(
    page_title="Darukaa.Earth | AI Biodiversity Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1b4332;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #40916c;
        margin-bottom: 1.5rem;
    }
    .rec-card {
        background-color: #f8fafc;
        border-left: 5px solid #2d6a4f;
        padding: 18px 22px;
        border-radius: 8px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .clarify-card {
        background-color: #fffbeb;
        border-left: 5px solid #d97706;
        padding: 16px 20px;
        border-radius: 8px;
        margin-bottom: 16px;
    }
    .metric-pill {
        display: inline-block;
        background-color: #e2e8f0;
        color: #1e293b;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .citation-tag {
        font-size: 0.82rem;
        color: #475569;
        font-style: italic;
    }
    .chain-box {
        background-color: #ecfdf5;
        border: 1px solid #a7f3d0;
        color: #065f46;
        padding: 10px 14px;
        border-radius: 6px;
        font-size: 0.9rem;
        margin-top: 10px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "agent" not in st.session_state:
    st.session_state.agent = BiodiversityAgent()
if "kb" not in st.session_state:
    st.session_state.kb = ScientificKnowledgeBase()
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "latest_analysis" not in st.session_state:
    st.session_state.latest_analysis = None

# Sidebar
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?auto=format&fit=crop&w=600&q=80", use_container_width=True)
    st.title("Darukaa.Earth AI")
    st.caption("Biodiversity Intelligence Reasoning System")

    st.markdown("---")
    st.subheader("System Status")
    st.success("Knowledge Layer: RAG Active (8 Curated Benchmarks)")
    st.success("Reasoning Core: Multi-Metric Synthesizer Active")
    st.success("Gemini LLM Grounding: Connected")

    st.markdown("---")
    st.subheader("Quick Benchmarks")
    if st.button("Semi-Arid Monoculture Wheat (0.3% SOC)", use_container_width=True):
        st.session_state.preset_query = "What interventions can improve biodiversity and ecosystem resilience on my land?"
        st.session_state.preset_vars = {
            "soil_organic_carbon": "0.3%",
            "rainfall": "low",
            "crop": "monoculture wheat",
            "region": "semi-arid"
        }
        st.rerun()

    if st.button("Watershed & Slope Restoration", use_container_width=True):
        st.session_state.preset_query = "Severe runoff erosion, soil compaction, and zero earthworms on sloping arable land"
        st.session_state.preset_vars = {
            "soil_organic_carbon": "0.8%",
            "rainfall": "episodic intense",
            "tillage": "conventional moldboard",
            "region": "sloping arable"
        }
        st.rerun()

    if st.button("Reset Conversation", use_container_width=True):
        st.session_state.agent.reset()
        st.session_state.chat_messages = []
        st.session_state.latest_analysis = None
        if "preset_query" in st.session_state:
            del st.session_state.preset_query
        if "preset_vars" in st.session_state:
            del st.session_state.preset_vars
        st.rerun()

# Header
st.markdown('<div class="main-header">Darukaa.Earth: AI Biodiversity Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Scientific Multi-Metric Reasoning & Knowledge-Grounded Ecosystem Restoration</div>', unsafe_allow_html=True)

# Tabs
tab_chat, tab_structured, tab_rag, tab_report = st.tabs([
    "Conversational Scientist",
    "Structured Assessment (JSON)",
    "Knowledge Layer (RAG Inspector)",
    "Download Assessment Report"
])

def render_analysis(result):
    if result.is_clarifying_required:
        st.markdown("""
        <div class="clarify-card">
            <h4>Baseline Parameters Needed</h4>
            <p>An environmental scientist evaluates multiple ecosystem dimensions before recommending interventions. Please provide:</p>
        </div>
        """, unsafe_allow_html=True)
        for q in result.clarifying_questions:
            st.markdown(f"- **{q}**")
        if result.missing_critical_variables:
            st.caption("Missing dimensions: " + ", ".join(result.missing_critical_variables))
    else:
        st.success(f"**Ecosystem Diagnosis:** {result.synthesis_summary}")
        st.subheader("Actionable, Evidence-Backed Recommendations")
        
        for idx, rec in enumerate(result.recommendations, start=1):
            with st.container():
                st.markdown(f"""
                <div class="rec-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <h3 style="margin: 0; color: #1b4332;">{idx}. {rec.title}</h3>
                        <div>
                            <span class="metric-pill" style="background-color: #dbeafe; color: #1e40af;">Time: {rec.time_horizon}</span>
                            <span class="metric-pill" style="background-color: #dcfce7; color: #15803d;">Confidence: {rec.confidence_level}</span>
                        </div>
                    </div>
                    <p><strong>Targeted Action:</strong><br>{rec.recommendation}</p>
                    <p><strong>Scientific Mechanism (Why it works):</strong><br>{rec.scientific_reasoning}</p>
                    <div class="chain-box">
                        <strong>Multi-Metric Causal Chain (>=3 Variables):</strong><br>
                        {rec.multi_metric_chain}
                    </div>
                    <div style="margin-top: 10px;">
                        <strong>Quantified Metric Improvements:</strong><br>
                        {' '.join([f'<span class="metric-pill">{m}</span>' for m in rec.impacted_metrics])}
                    </div>
                    <div style="margin-top: 10px;" class="citation-tag">
                        <strong>Scientific Citations:</strong><br>
                        {'<br>- '.join([''] + rec.citations)}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# TAB 1: CHATBOT
with tab_chat:
    st.markdown("Consult with the AI Environmental Scientist. The system maintains conversation memory across turns and integrates soil, water, and vegetation dimensions.")

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "user":
                st.write(msg["content"])
            else:
                render_analysis(msg["analysis"])

    default_prompt = st.session_state.get("preset_query", "")
    preset_vars = st.session_state.get("preset_vars", {})

    if prompt := st.chat_input("Describe your land, soil conditions, or environmental challenge...", key="chat_input"):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Retrieving scientific benchmarks & synthesizing multi-metric evidence..."):
                analysis_result = st.session_state.agent.chat(prompt, structured_override=preset_vars)
                st.session_state.latest_analysis = analysis_result
                st.session_state.chat_messages.append({"role": "assistant", "analysis": analysis_result})
                render_analysis(analysis_result)
        st.rerun()

    elif default_prompt and not st.session_state.chat_messages:
        st.session_state.chat_messages.append({"role": "user", "content": default_prompt})
        analysis_result = st.session_state.agent.chat(default_prompt, structured_override=preset_vars)
        st.session_state.latest_analysis = analysis_result
        st.session_state.chat_messages.append({"role": "assistant", "analysis": analysis_result})
        st.rerun()

# TAB 2: STRUCTURED ASSESSMENT (JSON)
with tab_structured:
    st.subheader("Structured Input Assessment (JSON / Parameters)")
    st.markdown("Input environmental parameters directly or via structured JSON format.")

    col1, col2 = st.columns(2)
    with col1:
        soc_val = st.text_input("Soil Organic Carbon (SOC %)", value="0.3%")
        ph_val = st.text_input("Soil pH", value="7.4")
        rain_val = st.selectbox("Rainfall Pattern / Moisture", ["low (< 450mm / semi-arid)", "moderate (500-800mm)", "high / monsoonal", "episodic flash runoff"])
        crop_val = st.text_input("Primary Cropping System", value="monoculture wheat")
    
    with col2:
        region_val = st.selectbox("Region / Biome", ["semi-arid", "arid dryland", "Mediterranean", "sub-humid", "temperate"])
        tillage_val = st.selectbox("Tillage Practice", ["conventional moldboard plow", "reduced tillage", "no-till with residue"])
        lat_val = st.number_input("Latitude (Bonus Spatial)", value=31.5204, format="%.4f")
        lon_val = st.number_input("Longitude (Bonus Spatial)", value=74.3587, format="%.4f")

    engine = st.session_state.agent.engine
    spatial_preview = engine.infer_spatial_context(lat_val, lon_val)
    st.info(f"Inferred Biome Context: {spatial_preview['estimated_biome']}")

    structured_payload = {
        "soil_organic_carbon": soc_val,
        "soil_ph": ph_val,
        "rainfall": rain_val,
        "crop": crop_val,
        "region": region_val,
        "tillage": tillage_val,
        "latitude": lat_val,
        "longitude": lon_val
    }

    with st.expander("View / Edit Raw JSON Payload"):
        json_str = st.text_area("JSON Payload", value=json.dumps(structured_payload, indent=2), height=180)

    if st.button("Analyze Structured Assessment", type="primary", use_container_width=True):
        try:
            parsed_json = json.loads(json_str)
            with st.spinner("Analyzing multi-variable parameters against FAO/IPCC databases..."):
                structured_res = engine.analyze(
                    user_text="Provide targeted ecological restoration plan for this site.",
                    structured_vars=parsed_json
                )
                st.session_state.latest_analysis = structured_res
                render_analysis(structured_res)
        except Exception as e:
            st.error(f"Error parsing JSON or executing engine: {e}")

# TAB 3: RAG KNOWLEDGE INSPECTOR
with tab_rag:
    st.subheader("Retrievable Knowledge Layer (RAG System)")
    st.markdown(
        "Indexed peer-reviewed studies and guidelines from **FAO**, **IPCC**, and **IPBES** "
        "providing empirical grounding for all recommendations."
    )

    rag_search = st.text_input("Search Knowledge Base:", value="soil organic carbon semi-arid wheat")
    if rag_search:
        results = st.session_state.kb.retrieve(rag_search, top_k=3)
        st.write(f"**Retrieved {len(results)} Benchmark Records for Query:** `{rag_search}`")
        for r in results:
            with st.expander(f"[{r['id']}] {r['title']} - {r['domain']}"):
                st.markdown(f"**Climate Zones:** {', '.join(r.get('climate_zones', []))}")
                st.markdown(f"**Land Use Applicability:** {', '.join(r.get('land_use', []))}")
                st.markdown(f"**Intervention:** {r.get('intervention')}")
                st.markdown(f"**Mechanisms:** {r.get('scientific_mechanisms')}")
                st.markdown(f"**Causal Chain:** `{r.get('multi_metric_chain')}`")
                st.markdown("**Quantitative Impacts:**")
                for k, v in r.get("quantitative_impacts", {}).items():
                    st.markdown(f"- {k.replace('_', ' ').title()}: **{v}**")
                st.markdown("**Credible Citations:**")
                for c in r.get("citations", []):
                    st.markdown(f"- *{c}*")

# TAB 4: DOWNLOAD REPORT
with tab_report:
    st.subheader("Download Your Ecological Assessment Report")
    st.markdown("Export a comprehensive scientific report of your current consultation, including detected site parameters, diagnosis, and evidence-backed interventions.")

    latest = st.session_state.latest_analysis
    accum_vars = st.session_state.agent.accumulated_variables

    if not latest or not latest.recommendations:
        st.info("No active recommendations yet. Run an assessment in the Conversational Scientist tab or Structured Assessment tab to generate and download your personalized report.")
    else:
        st.success(f"Active Assessment Ready for Download: {len(latest.recommendations)} Interventions Formulated")
        
        with st.expander("View Report Summary Preview", expanded=True):
            st.markdown(f"**Ecosystem Diagnosis:** {latest.synthesis_summary}")
            st.markdown("**Interventions Included:**")
            for r in latest.recommendations:
                st.markdown(f"- **{r.title}** (Time: {r.time_horizon}, Confidence: {r.confidence_level})")
                st.caption(f"Citations: {', '.join(r.citations)}")

        report_file_path = "c:/Users/khali/AIChatbot/User_Biodiversity_Assessment_Report.docx"
        generate_user_assessment_docx(
            detected_vars=accum_vars or latest.detected_variables,
            synthesis_summary=latest.synthesis_summary,
            recommendations=latest.recommendations,
            output_path=report_file_path
        )

        with open(report_file_path, "rb") as f:
            docx_bytes = f.read()

        st.download_button(
            label="Download Ecological Assessment Report (.docx)",
            data=docx_bytes,
            file_name="Darukaa_Ecological_Assessment_Report.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            type="primary",
            use_container_width=True
        )
