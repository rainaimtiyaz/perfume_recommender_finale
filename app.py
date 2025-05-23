import streamlit as st
import pandas as pd
from perfume_recommender import PerfumeRecommender

st.markdown("""
    <style>
        .st-emotion-cache-1qrv4ga, 
        .st-emotion-cache-1qrv4ga:hover,
        .st-emotion-cache-1qrv4ga:active,
        .st-emotion-cache-1qrv4ga:focus {
            color: black !important;
        }
        .st-emotion-cache-1qrv4ga:hover {
            font-weight: bold !important;
        }
        .st-emotion-cache-1qrv4ga[aria-expanded="true"] {
            font-weight: bold !important;
            color: black !important;
        }
        .stButton>button {
            background-color: #1E90FF;
            color: white;
            border-radius: 5px;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 500;
            width: 100%;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #0066CC;
            color: white !important;
        }
        .stButton>button:active {
            background-color: #004080;
            color: white !important;
        }
        .st-emotion-cache-5rimss.e1nzilvr5 {
            margin-bottom: 1rem;
        }
        .tooltip {
            display: inline-block;
            position: relative;
            cursor: pointer;
            font-weight: bold;
            font-size: 1rem;
            color: #1E90FF;
            margin-left: 4px;
        }

        .tooltip .tooltiptext {
            visibility: hidden;
            width: 320px;
            background-color: #f9f9f9;
            color: #333;
            text-align: left;
            border-radius: 6px;
            border: 1px solid #ccc;
            padding: 10px;
            position: absolute;
            z-index: 1;
            top: 120%;
            left: 50%;
            transform: translateX(-50%);
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 0.85rem;
            box-shadow: 0px 0px 6px rgba(0,0,0,0.1);
        }

        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }
    </style>
""", unsafe_allow_html=True)

recommender_jaccard = PerfumeRecommender('perfume_dataset_final.csv')

st.title('Aromaku: Sistem Rekomendasi Parfum')

st.markdown("""
Temukan parfum yang sesuai untuk Anda berdasarkan preferensi pribadi! ✨
""")

col_guide, col_data = st.columns(2)

with col_guide:
    with st.expander("📖 Panduan Penggunaan", expanded=True):
        st.markdown("""
        1. Pilih gender parfum yang diinginkan
        2. Pilih waktu penggunaan
        3. Deskripsikan parfum yang Anda cari (Penulisan notes gunakan bahasa Inggris)
        4. Tulis pengecualian aroma (Jika tidak ada silakan isi dengan '-')
        5. Klik "Dapatkan Rekomendasi"
        """)

with col_data:
    with st.expander("📊 Tentang Dataset", expanded=True):
        st.markdown(f"""
        - Total Parfum: {len(recommender_jaccard.df)}
        - Parfum Wanita: {len(recommender_jaccard.df[recommender_jaccard.df['Gender'] == 'wanita'])}
        - Parfum Pria: {len(recommender_jaccard.df[recommender_jaccard.df['Gender'] == 'pria'])}
        - Parfum Unisex: {len(recommender_jaccard.df[recommender_jaccard.df['Gender'] == 'unisex'])}
        """)

st.markdown("""
<div style="display: inline-flex; align-items: center; gap: 4px; margin-bottom: 0rem;">
    <span style="font-size: 1.7rem; font-weight: 600.1;">🔍 Masukkan Preferensi Anda</span>
    <div class="tooltip">ℹ
        <span class="tooltiptext">
            Rekomendasi dihasilkan berdasarkan perhitungan Jaccard Similarity<br>
            <br>
            Jaccard Similarity: <strong>Melihat berapa banyak keyword yang benar-benar sama antara input user dengan master data.</strong>
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    gender = st.selectbox(
        "👩🏻‍🤝‍👨🏽 Untuk siapa parfum ini?",
        options=['wanita', 'pria', 'unisex']
    )

with col2:
    time_usage = st.selectbox(
        "⏱️ Waktu penggunaan parfum",
        options=['siang', 'malam', 'siang dan malam']
    )

with st.container():
    st.markdown("""
    <div style='margin-bottom: -0.5rem; font-weight: normal; font-size: 0.9rem;'>✍️ Deskripsi aroma yang diinginkan&nbsp;
    <span title="Khusus penulisan aroma (notes) parfum gunakan bahasa Inggris">[❗️]</span></div>
    """, unsafe_allow_html=True)
    description = st.text_input(
        label=" ",
        placeholder="Contoh: Saya ingin parfum lokal yang beraroma fruity apple",
        label_visibility="collapsed"
    )

with st.container():
    st.markdown("""
    <div style='margin-bottom: -0.5rem; font-weight: normal; font-size: 0.9rem;'>🚫 Pengecualian Aroma&nbsp;
    <span title="Khusus penulisan aroma (notes) parfum gunakan bahasa Inggris">[❗️]</span></div>
    """, unsafe_allow_html=True)
    exclusions = st.text_input(
        label=" ",
        placeholder="Contoh: Jangan ada wangi tuberose dan woody",
        label_visibility="collapsed"
    )

if st.button("Dapatkan Rekomendasi"):
    if not description:
        st.warning("⚠️ Silakan deskripsikan parfum yang Anda inginkan")
    else:
        with st.spinner('🔍 Mencari rekomendasi terbaik untuk Anda...'):
            recommender = recommender_jaccard
            similarity_label = "Skor kesamaan Jaccard"

            recommendations = recommender.get_recommendations(
            gender=gender,
            time_usage=time_usage,
            description=description,
            exclusions=exclusions
            )

            if recommendations is None or recommendations.empty:
                st.error("Maaf, tidak ditemukan rekomendasi yang sesuai 😞")
            else:
                st.success("🎉 Berikut rekomendasi parfum untuk Anda:")
                    
                for idx, row in recommendations.iterrows():
                    with st.expander(f"✨️{row['Brand']} - {row['Perfume Name']} ({similarity_label}: {row['similarity']:.4f})"):
                        st.markdown(f"""
                        - **Gender:** {row['Gender'].capitalize()}
                        - **Rating:** {row['Rating']}
                        - **Waktu Penggunaan:** {row['Time Usage'].capitalize()}
                        - **Olfactory Family:** {row['Olfactory Family']}
                        - **Top Notes:** {row['Top Notes']}
                        - **Middle Notes:** {row['Middle Notes']}
                        - **Base Notes:** {row['Base Notes']}
                        - **Negara:** {row['Negara']}
                        """)
