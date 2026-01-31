import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import io
from datetime import datetime
import base64
from scipy import stats
from scipy.interpolate import interp1d, UnivariateSpline
import warnings
warnings.filterwarnings('ignore')

# ==================== КОНФИГУРАЦИЯ ====================
st.set_page_config(
    page_title="BioLab Pro - Гормон Калибровкаси",
    page_icon="⚗️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/hormon-calibration',
        'Report a bug': "https://github.com/yourusername/hormon-calibration/issues",
        'About': "# Биолаборатория учун профессиональ гормон калибровка тизими"
    }
)

# ==================== CSS СТИЛЛАР ====================
def inject_custom_css():
    st.markdown("""
    <style>
    /* Асосий дизайн */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .sub-title {
        font-size: 1.2rem;
        opacity: 0.9;
        font-weight: 300;
    }
    
    /* Карточкалар */
    .custom-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        border: 1px solid #e0e0e0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .custom-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.15);
    }
    
    /* Тугмалар */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
    }
    
    .secondary-btn > button {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    }
    
    /* Таблар */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f8f9fa;
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
    }
    
    /* Статистика бокслар */
    .stat-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
    }
    
    .stat-label {
        font-size: 1rem;
        opacity: 0.9;
        margin: 0;
    }
    
    /* Даволаш таблицаси */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Прогресс бар */
    .stProgress > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Футер */
    .footer {
        text-align: center;
        padding: 2rem;
        margin-top: 3rem;
        color: #666;
        border-top: 1px solid #e0e0e0;
    }
    
    /* Иконкалар */
    .icon {
        font-size: 1.5rem;
        margin-right: 10px;
    }
    
    /* Адаптивлик */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2rem;
        }
        .custom-card {
            padding: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# ==================== КЭШ ФУНКЦИЯЛАРИ ====================
@st.cache_data(ttl=3600)
def load_sample_data():
    """Намуна маълумотларни юклаш"""
    sample_standards = {
        "Кортизол": {
            "optic_density": [0.1, 0.2, 0.3, 0.4, 0.5],
            "concentration": [10, 20, 30, 40, 50],
            "unit": "нг/мл"
        },
        "ТТГ": {
            "optic_density": [0.05, 0.15, 0.25, 0.35, 0.45],
            "concentration": [0.5, 1.5, 2.5, 3.5, 4.5],
            "unit": "мкМЕ/мл"
        },
        "Тестостерон": {
            "optic_density": [0.2, 0.3, 0.4, 0.5, 0.6],
            "concentration": [2, 4, 6, 8, 10],
            "unit": "нг/мл"
        }
    }
    return sample_standards

# ==================== ХЕЛПЕР ФУНКЦИЯЛАРИ ====================
def create_download_link(df, filename, text):
    """CSV файл учун юклаш линки яратиш"""
    csv = df.to_csv(index=False, encoding='utf-8-sig')
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">{text}</a>'
    return href

def calculate_regression(x, y):
    """Регрессия ҳисоблаш"""
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    return {
        'slope': slope,
        'intercept': intercept,
        'r_squared': r_value**2,
        'p_value': p_value,
        'std_err': std_err
    }

# ==================== АСОСИЙ КЛАССЛАР ====================
class HormoneCalibrator:
    """Гормон калибратор класси"""
    
    def __init__(self):
        self.standards = {}
        self.patients = {}
        self.results = {}
        self.calibration_data = {}
    
    def add_standard(self, name, optic_density, concentration, unit):
        """Стандарт қўшиш"""
        self.standards[name] = {
            'optic_density': optic_density,
            'concentration': concentration,
            'unit': unit,
            'timestamp': datetime.now()
        }
    
    def calibrate(self, hormone_name, method='linear'):
        """Калибровка қилиш"""
        if hormone_name not in self.standards:
            raise ValueError(f"{hormone_name} учун стандарт маълумотлари мавжуд эмас")
        
        std = self.standards[hormone_name]
        x = np.array(std['optic_density'])
        y = np.array(std['concentration'])
        
        # Интерполяция функцияси
        if method == 'linear':
            f = interp1d(x, y, fill_value="extrapolate")
        elif method == 'cubic':
            f = interp1d(x, y, kind='cubic', fill_value="extrapolate")
        elif method == 'spline':
            f = UnivariateSpline(x, y, s=0, ext='extrapolate')
        else:
            raise ValueError(f"Номаълум метод: {method}")
        
        self.calibration_data[hormone_name] = {
            'function': f,
            'method': method,
            'range': (min(x), max(x)),
            'regression': calculate_regression(x, y)
        }
        
        return self.calibration_data[hormone_name]
    
    def predict(self, hormone_name, optic_density_values):
        """Концентрацияни прогноз қилиш"""
        if hormone_name not in self.calibration_data:
            self.calibrate(hormone_name)
        
        calib = self.calibration_data[hormone_name]
        f = calib['function']
        
        od_array = np.array(optic_density_values)
        predictions = f(od_array)
        
        # Диапазон текшириш
        status = np.zeros_like(predictions, dtype=int)
        min_od, max_od = calib['range']
        
        status[od_array < min_od] = -1  # Пастки диапазон
        status[od_array > max_od] = 1   # Юкори диапазон
        
        return predictions, status

# ==================== СТРИМЛИТ ВИДЖЕТЛАРИ ====================
def show_sidebar():
    """Сайдбарни кўрсатиш"""
    with st.sidebar:
        st.image("https://via.placeholder.com/250x80/667eea/ffffff?text=BioLab+Pro", use_column_width=True)
        
        st.markdown("---")
        st.markdown("### ⚙️ Настройкалар")
        
        # Интерполяция усули
        method = st.selectbox(
            "📊 Интерполяция усули",
            ["linear", "cubic", "spline"],
            index=0,
            help="Линей - содда, Кубик - аниқ, Сплайн - мураккаб"
        )
        
        # Статистика қўрсатиш
        show_stats = st.checkbox("📈 Батафсил статистика", value=True)
        
        # Автосақлаш
        auto_save = st.checkbox("💾 Автосақлаш", value=True)
        
        st.markdown("---")
        
        # Намуна маълумотлар
        st.markdown("### 📂 Намуна маълумотлар")
        sample_data = load_sample_data()
        sample_hormone = st.selectbox(
            "Намуна гормонни танланг",
            list(sample_data.keys())
        )
        
        if st.button("📥 Намунани юклаш", use_container_width=True):
            data = sample_data[sample_hormone]
            st.session_state['standards'] = data
            st.success(f"{sample_hormone} намунаси юкланди!")
        
        st.markdown("---")
        
        # Файл юклаш
        st.markdown("### 📁 Маълумотларни юклаш")
        uploaded_file = st.file_uploader(
            "JSON ёки CSV файл юкланг",
            type=['json', 'csv'],
            help="Стандартлар ёки беморлар маълумотлари"
        )
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.json'):
                    data = json.load(uploaded_file)
                    st.session_state.update(data)
                else:
                    data = pd.read_csv(uploaded_file)
                    st.session_state['patient_data'] = data.to_dict('records')
                
                st.success("Файл муваффақиятли юкланди!")
            except Exception as e:
                st.error(f"Юклашда хатолик: {str(e)}")
        
        st.markdown("---")
        st.markdown("**👨‍💻 Ишлаб чиқувчи:** Лаборатория D")
        st.markdown("**📧 Контакт:** info@biolab.uz")
        st.markdown("**🌐 Вебсайт:** [biolab.uz](https://biolab.uz)")

def show_dashboard():
    """Дашбордни кўрсатиш"""
    st.markdown('<div class="main-header"><h1 class="main-title">⚗️ BioLab Pro</h1><p class="sub-title">Профессионал гормон калибровка ва таҳлил тизими</p></div>', unsafe_allow_html=True)
    
    # Статистика карточкалари
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="stat-box"><p class="stat-value">🎯</p><p class="stat-label">Калибровка</p></div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="stat-box"><p class="stat-value">📊</p><p class="stat-label">Таҳлил</p></div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="stat-box"><p class="stat-value">✅</p><p class="stat-label">Тасдиқ</p></div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="stat-box"><p class="stat-value">🚀</p><p class="stat-label">Суръат</p></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Тезишли функциялар
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Калибровка", 
        "👥 Беморлар", 
        "📈 График", 
        "📊 Статистика", 
        "📁 Экспорт"
    ])
    
    return tab1, tab2, tab3, tab4, tab5

def calibration_tab(tab):
    """Калибровка таби"""
    with tab:
        st.markdown('<div class="custom-card"><h3>🎯 Стандартларни киритиш</h3></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            hormone_name = st.text_input("Гормон номи", "Кортизол")
            unit = st.text_input("Ўлчов бирлиги", "нг/мл")
            
            num_standards = st.number_input(
                "Стандартлар сони",
                min_value=3,
                max_value=10,
                value=5,
                step=1
            )
        
        with col2:
            st.markdown("**Стандарт қийматлари:**")
            
            standards_data = []
            for i in range(num_standards):
                cols = st.columns(2)
                with cols[0]:
                    od = st.number_input(
                        f"Оптик зичлик {i+1}",
                        min_value=0.0,
                        value=float(i+1)*0.1,
                        format="%.3f",
                        key=f"od_{i}"
                    )
                with cols[1]:
                    conc = st.number_input(
                        f"Концентрация {i+1}",
                        min_value=0.0,
                        value=float(i+1)*10.0,
                        format="%.2f",
                        key=f"conc_{i}"
                    )
                standards_data.append({
                    '№': i+1,
                    'Оптик зичлик': od,
                    f'Концентрация ({unit})': conc
                })
        
        if standards_data:
            df_standards = pd.DataFrame(standards_data)
            st.dataframe(df_standards, use_container_width=True)
            
            # Калибровка қилиш
            if st.button("🎯 Калибровкани бажариш", use_container_width=True, type="primary"):
                with st.spinner("Калибровка жараёни давом этаёт..."):
                    optic_density = [row['Оптик зичлик'] for row in standards_data]
                    concentration = [row[f'Концентрация ({unit})'] for row in standards_data]
                    
                    st.session_state['calibration'] = {
                        'hormone': hormone_name,
                        'unit': unit,
                        'optic_density': optic_density,
                        'concentration': concentration,
                        'standards_df': df_standards
                    }
                    
                    st.success(f"✅ {hormone_name} учун калибровка муваффақиятли амалга оширилди!")
        
        # Сақланган калибровкалар
        if 'calibration' in st.session_state:
            st.markdown('<div class="custom-card"><h3>💾 Сақланган калибровкалар</h3></div>', unsafe_allow_html=True)
            
            calib = st.session_state['calibration']
            cols = st.columns(3)
            
            with cols[0]:
                st.metric("Гормон", calib['hormone'])
            with cols[1]:
                st.metric("Ўлчов бирлиги", calib['unit'])
            with cols[2]:
                st.metric("Стандартлар", len(calib['optic_density']))

def patients_tab(tab):
    """Беморлар таби"""
    with tab:
        st.markdown('<div class="custom-card"><h3>👥 Беморлар маълумотлари</h3></div>', unsafe_allow_html=True)
        
        # Беморлар сони
        num_patients = st.number_input(
            "Беморлар сони",
            min_value=1,
            max_value=100,
            value=10,
            step=1
        )
        
        # Беморларни киритиш
        patients_data = []
        
        # Автоматик генерация
        if st.button("🎲 Намуна беморлар яратиш", use_container_width=True):
            np.random.seed(42)
            for i in range(num_patients):
                patients_data.append({
                    'ID': f"P{i+1:03d}",
                    'Оптик зичлик': round(np.random.uniform(0.1, 0.6), 3),
                    'Изоҳ': f"Намуна бемор {i+1}"
                })
            st.session_state['patients'] = patients_data
            st.success(f"{num_patients} та намуна бемор яратилди!")
        
        # Қўлда киритиш
        st.markdown("**Қўлда киритиш:**")
        
        edit_cols = st.columns([3, 1, 1])
        
        if 'patients' not in st.session_state:
            st.session_state['patients'] = []
        
        for i in range(num_patients):
            cols = st.columns([1, 2, 3])
            with cols[0]:
                patient_id = st.text_input(f"ID {i+1}", value=f"P{i+1:03d}", key=f"pid_{i}")
            with cols[1]:
                optic_density = st.number_input(
                    f"Оптик зичлик {i+1}",
                    min_value=0.0,
                    value=0.2 + i*0.05,
                    format="%.3f",
                    key=f"p_od_{i}"
                )
            with cols[2]:
                note = st.text_input(f"Изоҳ {i+1}", key=f"note_{i}")
            
            if i < len(st.session_state['patients']):
                st.session_state['patients'][i] = {
                    'ID': patient_id,
                    'Оптик зичлик': optic_density,
                    'Изоҳ': note
                }
            else:
                st.session_state['patients'].append({
                    'ID': patient_id,
                    'Оптик зичлик': optic_density,
                    'Изоҳ': note
                })
        
        if st.session_state['patients']:
            df_patients = pd.DataFrame(st.session_state['patients'])
            st.dataframe(df_patients, use_container_width=True)
            
            # Статистика
            st.markdown('<div class="custom-card"><h3>📊 Беморлар статистикаси</h3></div>', unsafe_allow_html=True)
            
            optic_values = [p['Оптик зичлик'] for p in st.session_state['patients']]
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Жами беморлар", len(optic_values))
            with col2:
                st.metric("Ўртача зичлик", f"{np.mean(optic_values):.3f}")
            with col3:
                st.metric("Минимал", f"{min(optic_values):.3f}")
            with col4:
                st.metric("Максимал", f"{max(optic_values):.3f}")

def visualization_tab(tab):
    """График таби"""
    with tab:
        st.markdown('<div class="custom-card"><h3>📈 Визуализация ва график</h3></div>', unsafe_allow_html=True)
        
        if 'calibration' not in st.session_state:
            st.warning("Аввал калибровка маълумотларини киритинг!")
            return
        
        calib = st.session_state['calibration']
        
        # Калибровка графиги
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Калибровка қийшиқ чизиғи',
                'Регрессия таҳлили',
                'Концентрация тақсимоти',
                'Қолдиқлар таҳлили'
            ),
            vertical_spacing=0.15,
            horizontal_spacing=0.15
        )
        
        # 1. Калибровка қийшиқ чизиғи
        fig.add_trace(
            go.Scatter(
                x=calib['optic_density'],
                y=calib['concentration'],
                mode='lines+markers',
                name='Стандартлар',
                marker=dict(size=12, color='#667eea', symbol='circle'),
                line=dict(color='#667eea', width=3),
                hovertemplate='Оптик: %{x:.3f}<br>Конц: %{y:.2f}'
            ),
            row=1, col=1
        )
        
        # Регрессия чизиғи
        x_range = np.linspace(min(calib['optic_density']), max(calib['optic_density']), 100)
        slope, intercept, r, p, std_err = stats.linregress(
            calib['optic_density'], 
            calib['concentration']
        )
        y_range = slope * x_range + intercept
        
        fig.add_trace(
            go.Scatter(
                x=x_range,
                y=y_range,
                mode='lines',
                name=f'Регрессия (R²={r**2:.3f})',
                line=dict(color='#f093fb', width=2, dash='dash'),
                hovertemplate='R² = %{customdata:.3f}',
                customdata=[r**2]*len(x_range)
            ),
            row=1, col=1
        )
        
        # 2. Регрессия диаграммаси
        fig.add_trace(
            go.Scatter(
                x=calib['optic_density'],
                y=calib['concentration'],
                mode='markers',
                name='Мaълумотлар',
                marker=dict(
                    size=10,
                    color=calib['concentration'],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Концентрация")
                )
            ),
            row=1, col=2
        )
        
        # 3. Гистограмма
        fig.add_trace(
            go.Histogram(
                x=calib['concentration'],
                name='Тақсимот',
                marker_color='#43e97b',
                nbinsx=10,
                opacity=0.7
            ),
            row=2, col=1
        )
        
        # 4. Q-Q plot (нормаллик текшириш)
        residuals = calib['concentration'] - (slope * np.array(calib['optic_density']) + intercept)
        fig.add_trace(
            go.Scatter(
                x=np.sort(residuals),
                y=np.sort(np.random.normal(0, 1, len(residuals))),
                mode='markers',
                name='Q-Q plot',
                marker=dict(size=8, color='#ff6b6b')
            ),
            row=2, col=2
        )
        
        # Лейаутни сўнғириш
        fig.update_layout(
            height=800,
            showlegend=True,
            template='plotly_white',
            title_text=f"{calib['hormone']} калибровка таҳлили",
            hovermode='closest'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Илова графиклар
        if 'patients' in st.session_state and st.session_state['patients']:
            st.markdown('<div class="custom-card"><h3>👥 Беморлар таҳлили</h3></div>', unsafe_allow_html=True)
            
            # Беморлар концентрациясини ҳисоблаш
            calibrator = HormoneCalibrator()
            calibrator.add_standard(
                calib['hormone'],
                calib['optic_density'],
                calib['concentration'],
                calib['unit']
            )
            calibrator.calibrate(calib['hormone'])
            
            patient_od = [p['Оптик зичлик'] for p in st.session_state['patients']]
            predictions, status = calibrator.predict(calib['hormone'], patient_od)
            
            # Беморлар графиги
            fig_patients = go.Figure()
            
            colors = ['#43e97b', '#ff6b6b', '#ffd93d']
            status_labels = ['Нормал', 'Пастки', 'Юкори']
            
            for stat_val, color, label in zip([0, -1, 1], colors, status_labels):
                mask = status == stat_val
                if np.any(mask):
                    fig_patients.add_trace(go.Scatter(
                        x=np.array(patient_od)[mask],
                        y=predictions[mask],
                        mode='markers',
                        name=f'Беморлар ({label})',
                        marker=dict(size=15, color=color, line=dict(width=2, color='white')),
                        text=[st.session_state['patients'][i]['ID'] for i in range(len(mask)) if mask[i]],
                        hovertemplate='ID: %{text}<br>Оптик: %{x:.3f}<br>Конц: %{y:.2f}'
                    ))
            
            fig_patients.update_layout(
                title="Беморлар концентрацияси",
                xaxis_title="Оптик зичлик",
                yaxis_title=f"Концентрация ({calib['unit']})",
                template='plotly_white',
                height=500
            )
            
            st.plotly_chart(fig_patients, use_container_width=True)

def statistics_tab(tab):
    """Статистика таби"""
    with tab:
        st.markdown('<div class="custom-card"><h3>📊 Батафсил статистика</h3></div>', unsafe_allow_html=True)
        
        if 'calibration' not in st.session_state:
            st.warning("Аввал калибровка маълумотларини киритинг!")
            return
        
        calib = st.session_state['calibration']
        
        # Регрессия статистикаси
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            calib['optic_density'], 
            calib['concentration']
        )
        
        # Статистика карточкалари
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("R² (детерминация)", f"{r_value**2:.4f}")
        with col2:
            st.metric("Регрессия коэффициенти", f"{slope:.4f}")
        with col3:
            st.metric("p-қиймат", f"{p_value:.6f}")
        with col4:
            st.metric("Стандарт хатолик", f"{std_err:.4f}")
        
        # Батафсил статистика
        st.markdown('<div class="custom-card"><h3>📈 Дескриптив статистика</h3></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Оптик зичлик:**")
            df_od = pd.DataFrame(calib['optic_density'], columns=['Оптик зичлик'])
            st.dataframe(df_od.describe(), use_container_width=True)
        
        with col2:
            st.markdown(f"**Концентрация ({calib['unit']}):**")
            df_conc = pd.DataFrame(calib['concentration'], columns=['Концентрация'])
            st.dataframe(df_conc.describe(), use_container_width=True)
        
        # Корреляция матрицаси
        st.markdown('<div class="custom-card"><h3>🔗 Корреляция таҳлили</h3></div>', unsafe_allow_html=True)
        
        df_corr = pd.DataFrame({
            'Оптик зичлик': calib['optic_density'],
            'Концентрация': calib['concentration']
        }).corr()
        
        fig_corr = px.imshow(
            df_corr,
            text_auto=True,
            color_continuous_scale='RdBu',
            title='Корреляция матрицаси'
        )
        st.plotly_chart(fig_corr, use_container_width=True)
        
        # Беморлар статистикаси
        if 'patients' in st.session_state and st.session_state['patients']:
            st.markdown('<div class="custom-card"><h3>👥 Беморлар статистикаси</h3></div>', unsafe_allow_html=True)
            
            patient_od = [p['Оптик зичлик'] for p in st.session_state['patients']]
            
            # Ҳисоблаш
            calibrator = HormoneCalibrator()
            calibrator.add_standard(
                calib['hormone'],
                calib['optic_density'],
                calib['concentration'],
                calib['unit']
            )
            calibrator.calibrate(calib['hormone'])
            predictions, status = calibrator.predict(calib['hormone'], patient_od)
            
            # Статистика
            stats_data = {
                'Жами беморлар': len(predictions),
                'Нормал диапазон': int(np.sum(status == 0)),
                'Пастки диапазон': int(np.sum(status == -1)),
                'Юкори диапазон': int(np.sum(status == 1)),
                'Ўртача концентрация': f"{np.nanmean(predictions):.2f}",
                'Стандарт оғиш': f"{np.nanstd(predictions):.2f}",
                'Минимал': f"{np.nanmin(predictions):.2f}",
                'Максимал': f"{np.nanmax(predictions):.2f}"
            }
            
            df_stats = pd.DataFrame(list(stats_data.items()), columns=['Кўрсаткич', 'Қиймат'])
            st.dataframe(df_stats, use_container_width=True, hide_index=True)

def export_tab(tab):
    """Экспорт таби"""
    with tab:
        st.markdown('<div class="custom-card"><h3>📁 Маълумотларни экспорт қилиш</h3></div>', unsafe_allow_html=True)
        
        export_options = st.multiselect(
            "Экспорт қилинадиган маълумотлар",
            [
                "Калибровка маълумотлари",
                "Беморлар рўйхати", 
                "Ҳисобланган натижалар",
                "Статистика ҳисоботи",
                "График расмлари"
            ],
            default=["Калибровка маълумотлари", "Беморлар рўйхати"]
        )
        
        # Формат танлаш
        col1, col2 = st.columns(2)
        with col1:
            export_format = st.radio(
                "Файл формати",
                ["CSV", "Excel", "JSON", "PDF"],
                horizontal=True
            )
        
        with col2:
            encoding = st.selectbox(
                "Кодировка",
                ["utf-8", "utf-8-sig", "cp1251"],
                index=1
            )
        
        # Маълумотларни тайёрлаш
        export_data = {}
        
        if 'calibration' in st.session_state and "Калибровка маълумотлари" in export_options:
            calib = st.session_state['calibration']
            export_data['calibration'] = {
                'hormone': calib['hormone'],
                'unit': calib['unit'],
                'standards': calib['standards_df'].to_dict('records'),
                'timestamp': datetime.now().isoformat()
            }
        
        if 'patients' in st.session_state and "Беморлар рўйхати" in export_options:
            export_data['patients'] = st.session_state['patients']
        
        # Ҳисобланган натижалар
        if 'calibration' in st.session_state and 'patients' in st.session_state:
            if "Ҳисобланган натижалар" in export_options:
                calibrator = HormoneCalibrator()
                calibrator.add_standard(
                    st.session_state['calibration']['hormone'],
                    st.session_state['calibration']['optic_density'],
                    st.session_state['calibration']['concentration'],
                    st.session_state['calibration']['unit']
                )
                calibrator.calibrate(st.session_state['calibration']['hormone'])
                
                patient_od = [p['Оптик зичлик'] for p in st.session_state['patients']]
                predictions, status = calibrator.predict(
                    st.session_state['calibration']['hormone'], 
                    patient_od
                )
                
                results = []
                for i, (pred, stat) in enumerate(zip(predictions, status)):
                    results.append({
                        'ID': st.session_state['patients'][i]['ID'],
                        'Оптик зичлик': patient_od[i],
                        f'Концентрация ({st.session_state["calibration"]["unit"]})': pred,
                        'Ҳолат': 'Нормал' if stat == 0 else 'Пастки' if stat == -1 else 'Юкори',
                        'Изоҳ': st.session_state['patients'][i]['Изоҳ']
                    })
                
                export_data['results'] = results
        
        # Экспорт қилиш
        if export_data:
            st.markdown('<div class="custom-card"><h3>📥 Юклаб олиш</h3></div>', unsafe_allow_html=True)
            
            if export_format == "CSV":
                for name, data in export_data.items():
                    if name == 'calibration':
                        df = pd.DataFrame(data['standards'])
                        csv = df.to_csv(index=False, encoding=encoding)
                    elif name == 'patients':
                        df = pd.DataFrame(data)
                        csv = df.to_csv(index=False, encoding=encoding)
                    elif name == 'results':
                        df = pd.DataFrame(data)
                        csv = df.to_csv(index=False, encoding=encoding)
                    
                    b64 = base64.b64encode(csv.encode()).decode()
                    href = f'<a href="data:file/csv;base64,{b64}" download="{name}.csv">📥 {name}.csv юклаб олиш</a>'
                    st.markdown(href, unsafe_allow_html=True)
            
            elif export_format == "Excel":
                with pd.ExcelWriter('экспорт.xlsx', engine='openpyxl') as writer:
                    for name, data in export_data.items():
                        if name == 'calibration':
                            pd.DataFrame(data['standards']).to_excel(
                                writer, 
                                sheet_name='Калибровка',
                                index=False
                            )
                        elif name == 'patients':
                            pd.DataFrame(data).to_excel(
                                writer,
                                sheet_name='Беморлар',
                                index=False
                            )
                        elif name == 'results':
                            pd.DataFrame(data).to_excel(
                                writer,
                                sheet_name='Натижалар',
                                index=False
                            )
                
                with open('экспорт.xlsx', 'rb') as f:
                    excel_data = f.read()
                
                b64 = base64.b64encode(excel_data).decode()
                href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="калибровка_экспорт.xlsx">📥 Excel файлини юклаб олиш</a>'
                st.markdown(href, unsafe_allow_html=True)
            
            elif export_format == "JSON":
                json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
                b64 = base64.b64encode(json_str.encode()).decode()
                href = f'<a href="data:application/json;base64,{b64}" download="калибровка.json">📥 JSON файлини юклаб олиш</a>'
                st.markdown(href, unsafe_allow_html=True)

# ==================== АСОСИЙ ДАСТУР ====================
def main():
    # CSS стилларини ижро этиш
    inject_custom_css()
    
    # Сайдбарни кўрсатиш
    show_sidebar()
    
    # Асосий дашборд
    tab1, tab2, tab3, tab4, tab5 = show_dashboard()
    
    # Табларни кўрсатиш
    calibration_tab(tab1)
    patients_tab(tab2)
    visualization_tab(tab3)
    statistics_tab(tab4)
    export_tab(tab5)
    
    # Футер
    st.markdown("---")
    st.markdown("""
    <div class="footer">
        <p>© 2024 BioLab Pro | Лаборатория маълумотларини идора қилиш тизими</p>
        <p>📧 info@biolab.uz | 🌐 biolab.uz | 📞 +998 71 123 45 67</p>
        <p style="font-size: 0.8rem; opacity: 0.7;">Илова версияси: 2.1.0 | Охиңги янгиланиш: 2024-01-31</p>
    </div>
    """, unsafe_allow_html=True)

# ==================== ИЖРО ====================
if __name__ == "__main__":
    main()
