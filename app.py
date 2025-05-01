import streamlit as st
import time
import json
import re
import os
import base64
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import geckodriver_autoinstaller
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_card import card
from streamlit_lottie import st_lottie
import requests
import matplotlib.pyplot as plt
import networkx as nx
import io

# Custom JSON encoder to handle Timestamp objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date, pd.Timestamp)):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)

# Function to save data to file with custom encoder
def save_data_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4, cls=DateTimeEncoder)
    return True

# Styling for a more appealing UI
st.set_page_config(
    page_title="Persian Data Crawler | ربات داده کاوی",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
def add_custom_css():
    st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
        color: #333;
        direction: rtl;
    }
    .stButton button {
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: none;
        transition: all 0.3s;
    }
    .stButton button:hover {
        background-color: #ff2b2b;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    .css-1d391kg, .css-12oz5g7 {
        padding-top: 2rem;
    }
    .stProgress > div > div > div > div {
        background-color: #ff4b4b;
    }
    h1, h2, h3 {
        color: #333;
        text-align: right;
    }
    .card {
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        background-color: white;
        transition: all 0.3s;
        direction: rtl;
        text-align: right;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    .highlight {
        color: #ff4b4b;
        font-weight: bold;
    }
    div[data-testid="stVerticalBlock"] {
        direction: rtl;
    }
    .stDataFrame {
        direction: rtl;
    }
    div[data-testid="stMetricValue"] {
        direction: ltr;
    }
    .stPlotlyChart {
        direction: rtl;
    }
    .css-1544g2n {
        padding-right: 1rem;
    }
    .input-section {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .section-title {
        color: #ff4b4b;
        font-size: 1.2rem;
        margin-bottom: 10px;
        border-bottom: 2px solid #f0f0f0;
        padding-bottom: 5px;
    }
    .accent-border {
        border-right: 4px solid #ff4b4b;
        padding-right: 10px;
    }
    /* Fix slider styles */
    .stSlider {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    .stSlider > div {
        margin-bottom: 0 !important;
    }
    /* Improve button styling */
    .submit-btn {
        margin-top: 5px;
        margin-bottom: 5px;
    }
    .param-title {
        font-weight: bold;
        margin-bottom: 6px !important;
        font-size: 0.95rem;
    }
    /* Fix metrics layout for RTL */
    div[data-testid="metric-container"] {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center !important;
    }
    
    div[data-testid="metric-container"] > div:nth-child(1) {
        width: 100%;
        text-align: center !important;
    }
    
    div[data-testid="metric-container"] > div:nth-child(2) {
        width: 100%;
        text-align: center !important;
    }
    
    div[data-testid="stMetricValue"] {
        width: 100%;
        text-align: center !important;
        direction: ltr;
    }
    
    div[data-testid="stMetricLabel"] {
        width: 100%;
        text-align: center !important;
    }
    
    /* Create a better metrics card style */
    .metric-card {
        background-color: white;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .metrics-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    
    @media (max-width: 1200px) {
        .metrics-container {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    
    @media (max-width: 600px) {
        .metrics-container {
            grid-template-columns: 1fr;
        }
    }
    
    /* Sexy header styling */
    .app-header {
        background: linear-gradient(135deg, #ff3366 0%, #ff6b3d 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(255, 51, 102, 0.15);
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .app-header::before {
        content: "";
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0) 60%);
        opacity: 0.4;
        z-index: 0;
    }
    
    .app-header h1 {
        margin: 0;
        font-size: 2.2rem;
        position: relative;
        z-index: 1;
        font-weight: 600;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .app-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        position: relative;
        z-index: 1;
        opacity: 0.9;
    }
    
    .app-icon {
        font-size: 1.8rem;
        margin-right: 0.5rem;
        vertical-align: middle;
        display: inline-block;
    }
    
    .app-header-accent {
        position: absolute;
        bottom: -30px;
        right: -30px;
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.15);
        z-index: 0;
    }
    
    .app-header-accent-2 {
        position: absolute;
        top: -20px;
        left: -20px;
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.1);
        z-index: 0;
    }
    </style>
    """, unsafe_allow_html=True)

add_custom_css()

# Functions from crawler.py
def remove_tags(text):
    TAG_RE = re.compile(r'<[^>]+>')
    text = text.replace('&nbsp;', ' ')
    return TAG_RE.sub('', text)

def extract_all_phrase_contexts(text, phrase, start_words=["آقای", "خانم"], words_after=5, fallback_words_before=10):
    contexts = []
    try:
        # Clean text once
        cleaned_text = re.sub(r'\s+', ' ', text).strip()
        # Create padded versions for reliable searching
        padded_start_words = [f" {word} " for word in start_words]

        # Find all occurrences of the main phrase
        for phrase_match in re.finditer(re.escape(phrase), cleaned_text, re.IGNORECASE):
            phrase_start_index = phrase_match.start()
            phrase_end_index = phrase_match.end()
            text_before_phrase = cleaned_text[:phrase_start_index]

            # Find the last occurrence of any start word before the phrase
            best_start_word_index = -1
            for i, padded_word in enumerate(padded_start_words):
                found_index = text_before_phrase.rfind(padded_word)
                if found_index > best_start_word_index:
                    best_start_word_index = found_index
                    # Adjust index to get the actual word start (remove leading space)
                    best_start_word_index += 1

            context_start_index = -1
            if best_start_word_index != -1:
                context_start_index = best_start_word_index
            else:
                # Fallback: approximate start based on words if no start word found
                words_in_before_text = text_before_phrase.split()
                fallback_start_word_num = max(0, len(words_in_before_text) - fallback_words_before)
                # Try to find the start index of that word in the original cleaned text
                if fallback_start_word_num < len(words_in_before_text):
                     # This is approximate, joining words back might not match original spacing
                     approx_start_phrase = " ".join(words_in_before_text[fallback_start_word_num:])
                     # Search for the beginning of this approximate phrase near the end of text_before_phrase
                     search_start_fallback = max(0, phrase_start_index - len(approx_start_phrase) - 50) # Search window
                     context_start_index = cleaned_text.find(words_in_before_text[fallback_start_word_num], search_start_fallback, phrase_start_index)
                     if context_start_index == -1: context_start_index = max(0, phrase_start_index - 70) # Final fallback: char count
                else:
                     context_start_index = max(0, phrase_start_index - 70) # Fallback: char count if few/no words before

            # Capture text from calculated start up to the end of the phrase
            context_part1 = cleaned_text[context_start_index:phrase_end_index]

            # Capture words after the phrase using regex
            text_after_phrase = cleaned_text[phrase_end_index:]
            pattern_after = rf'^(\s*(?:\S+\s*){{0,{words_after}}})' # Match from beginning of the after-text
            match_after = re.search(pattern_after, text_after_phrase)
            context_part2 = match_after.group(1).strip() if match_after else ""

            # Combine parts
            final_context = (context_part1 + " " + context_part2).strip()
            if final_context:
                 contexts.append(final_context)

    except Exception as e:
        st.error(f"Error during context extraction: {e}")

    return contexts

# Function to load Lottie animations
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception as e:
        st.warning(f"Failed to load animation: {e}")
        return None

# Load a default Lottie animation or from URL
def get_lottie_animation():
    # First try to load from URL
    lottie_url = "https://lottie.host/b62b1154-a853-4042-852f-1eee577e95d0/XdHCLcn0JT.json"
    lottie_animation = load_lottieurl(lottie_url)
    
    # If URL fails, use a default animation
    if lottie_animation is None:
        # Default spider/data animation in JSON format
        lottie_animation = {
            "v":"5.5.7",
            "fr":30,
            "ip":0,
            "op":60,
            "w":200,
            "h":200,
            "nm":"Data Animation",
            "ddd":0,
            "assets":[],
            "layers":[
                {
                    "ddd":0,
                    "ind":1,
                    "ty":4,
                    "nm":"Circle",
                    "sr":1,
                    "ks":{
                        "o":{"a":0,"k":100},
                        "r":{"a":1,"k":[{"t":0,"s":[0]},{"t":60,"s":[360]}]},
                        "p":{"a":0,"k":[100,100]},
                        "a":{"a":0,"k":[0,0]},
                        "s":{"a":0,"k":[100,100]}
                    },
                    "shapes":[
                        {
                            "ty":"gr",
                            "it":[
                                {
                                    "d":1,
                                    "ty":"el",
                                    "s":{"a":0,"k":[80,80]},
                                    "p":{"a":0,"k":[0,0]},
                                    "nm":"Ellipse Path 1",
                                    "mn":"ADBE Vector Shape - Ellipse"
                                },
                                {
                                    "ty":"st",
                                    "c":{"a":0,"k":[0.941,0.294,0.294,1]},
                                    "o":{"a":0,"k":100},
                                    "w":{"a":0,"k":10},
                                    "lc":2,
                                    "lj":1,
                                    "ml":4,
                                    "bm":0,
                                    "nm":"Stroke 1",
                                    "mn":"ADBE Vector Graphic - Stroke"
                                },
                                {
                                    "ty":"tr",
                                    "p":{"a":0,"k":[0,0]},
                                    "a":{"a":0,"k":[0,0]},
                                    "s":{"a":0,"k":[100,100]},
                                    "r":{"a":0,"k":0},
                                    "o":{"a":0,"k":100},
                                    "sk":{"a":0,"k":0},
                                    "sa":{"a":0,"k":0},
                                    "nm":"Transform"
                                }
                            ],
                            "nm":"Ellipse 1",
                            "np":2,
                            "cix":2,
                            "bm":0,
                            "ix":1,
                            "mn":"ADBE Vector Group"
                        }
                    ],
                    "ip":0,
                    "op":60,
                    "st":0,
                    "bm":0
                }
            ],
            "markers":[]
        }
    
    return lottie_animation

# Display animation
lottie_crawler = get_lottie_animation()

# App header
st.markdown("""
<div class="app-header">
    <div class="app-header-accent"></div>
    <div class="app-header-accent-2"></div>
    <h1>استخراج هوشمند داده از روزنامه رسمی🔍</h1>
    <p>سیستم پیشرفته استخراج و تحلیل اطلاعات شرکت‌ها و مدیران</p>
</div>
""", unsafe_allow_html=True)

# Tab navigation
colored_header(
    label="منابع اطلاعاتی",
    description="انتخاب کنید از کدام منبع داده استخراج شود",
    color_name="red-70",
)

# Create tabs
tab1, tab2, tab3 = st.tabs(["روزنامه رسمی", "تحلیل داده‌ها", "منابع دیگر (به زودی)"])

with tab1:
    # Main header with attractive styling
    st.markdown("""
    <div style="text-align: center; margin-bottom: 25px;">
        <h2 style="color: #333; font-size: 1.8rem;">📰 استخراج داده از روزنامه رسمی کشور</h2>
        <p style="color: #666; font-size: 1rem;">استخراج هوشمند اطلاعات شرکت‌ها و مدیران آن‌ها</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Clean organization of input parameters
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown('<h3 class="section-title">🔍 تنظیمات جستجو</h3>', unsafe_allow_html=True)
    
    # Single column layout for all search parameters
    st.markdown('<p class="param-title">عبارت کلیدی برای جستجو</p>', unsafe_allow_html=True)
    search_term = st.text_input("", value="نفت", help="مثال: نفت، پتروشیمی، فولاد و غیره", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<p class="param-title">فیلتر نتایج</p>', unsafe_allow_html=True)
    ceo_only = st.checkbox("👔 فقط مدیران عامل", value=False, help="در صورت انتخاب، فقط اطلاعات مدیران عامل استخراج می‌شود")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<p class="param-title">تنظیمات حجم داده</p>', unsafe_allow_html=True)
    max_samples = st.number_input("تعداد نمونه مورد نیاز", min_value=1, max_value=10000, value=100, help="حداکثر تعداد داده‌هایی که می‌خواهید استخراج کنید", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<p class="param-title">زمان انتظار (دقیقه)</p>', unsafe_allow_html=True)
    timeout_mins = st.number_input("timeout", min_value=1, max_value=60, value=30, help="حداکثر زمان انتظار برای بارگذاری صفحات (دقیقه)", label_visibility="collapsed", key="timeout_input")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<p class="param-title">نام فایل خروجی</p>', unsafe_allow_html=True)
    output_filename = st.text_input("filename", value="extracted_data.json", help="نام فایل برای ذخیره نتایج", label_visibility="collapsed", key="output_filename_input")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Improve button placement - make it inside the input section
    st.markdown('<div class="submit-btn">', unsafe_allow_html=True)
    start_btn = st.button("🚀 شروع استخراج داده‌ها", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close input-section
    
    # Data visualization and results section
    if "data" not in st.session_state:
        st.session_state.data = []
        st.session_state.crawling_complete = False
    
    # Start crawling when button is clicked
    if start_btn:
        st.session_state.data = []  # Reset data
        st.session_state.crawling_complete = False
        
        # Create progress indicators
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-title">⏳ وضعیت پیشرفت</h3>', unsafe_allow_html=True)
        progress_bar = st.progress(0)
        status_text = st.empty()
        result_count = st.empty()
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Session state for visualization
        if "viz_data" not in st.session_state:
            st.session_state.viz_data = {"positions": {}, "companies": []}
        
        # Load existing data
        filename = output_filename  # Use the user-defined filename
        existing_data = []
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                status_text.info(f"بارگیری {len(existing_data)} مورد از فایل {filename}")
            except Exception as e:
                st.error(f"خطا در بارگیری داده‌های موجود: {e}")
        
        # Create set for tracking duplicates
        seen_entries = {f"{entry.get('company_name', '')}-{entry.get('national_id', '')}-{entry.get('position', '')}" 
                       for entry in existing_data}
        
        # Setup position mapping
        position_map = {
            "رئیس هیئت مدیره": "chairman",
            "رئیس هیات مدیره": "chairman",
            "رئیس هیئت": "chairman",
            "نایب رئیس هیئت مدیره": "viceChairman",
            "نایب رئیس هیات مدیره": "viceChairman",
            "نایب رئیس": "viceChairman",
            "مدیر عامل": "ceo",
            "مدیرعامل": "ceo",
            "عضو هیئت مدیره": "boardmember",
            "عضو هیات مدیره": "boardmember",
            "عضو اصلی هیئت مدیره": "boardmember",
            "عضو علی البدل هیئت مدیره": "boardmember_alternate",
            "عضو هیئت": "boardmember",
            "عضو": "boardmember",
            "بازرس اصلی": "mainInspector",
            "بازرس علی البدل": "alternativeInspector",
            "بازرس علی": "alternativeInspector"
        }
        position_keywords = list(position_map.keys())
        
        status_text.info("در حال راه‌اندازی مرورگر...")
        
        try:
            # Install and setup webdriver
            geckodriver_autoinstaller.install()
            firefox_options = Options()
            firefox_options.add_argument("--headless")
            driver = webdriver.Firefox(options=firefox_options)
            
            # Set timeout (convert minutes to seconds)
            timeout_seconds = timeout_mins * 60
            wait = WebDriverWait(driver, timeout_seconds)
            general_wait = WebDriverWait(driver, timeout_seconds)
            initial_wait = WebDriverWait(driver, timeout_seconds)
            
            original_window = driver.current_window_handle
            extracted_data = []
            auto_increment_id = 1 if not existing_data else max(entry["id"] for entry in existing_data) + 1
            search_phrase = "به شماره ملی"
            filter_word = "سمت"
            start_words_list = ["آقای", "خانم"]
            current_page_number = 1
            sample_count = 0
            
            status_text.info(f"باز کردن وبسایت روزنامه رسمی و جستجوی '{search_term}'...")
            
            # Initial navigation
            target_url = "https://rrk.ir/ords/r/rrs/rrs-front/%D8%AF%D8%A7%D8%AF%D9%87-%D8%A8%D8%A7%D8%B2"
            driver.get(target_url)
            
            input_box = general_wait.until(EC.presence_of_element_located((By.ID, "P199_FOOTER")))
            input_box.send_keys(search_term)
            
            search_button = general_wait.until(EC.element_to_be_clickable((By.ID, "B912476867105247978")))
            search_button.click()
            time.sleep(1)
            
            initial_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tr a[href]")))
            
            # Pagination loop
            while sample_count < max_samples:
                status_text.info(f"در حال پردازش صفحه {current_page_number} (نمونه‌های یافت شده: {sample_count}/{max_samples})")
                
                try:
                    general_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tr a[href]")))
                    time.sleep(1)
                    result_trs = driver.find_elements(By.TAG_NAME, "tr")
                except TimeoutException:
                    status_text.warning(f"مهلت زمانی برای صفحه {current_page_number} به پایان رسید.")
                    break
                
                link_urls_to_process = []
                for index, tr in enumerate(result_trs):
                    try:
                        link_element = tr.find_element(By.TAG_NAME, "a")
                        link_url = link_element.get_attribute('href')
                        if link_url and link_url.startswith('http'):
                            link_urls_to_process.append((index, link_url))
                    except NoSuchElementException:
                        pass
                
                # Process links
                for link_index, link_url in link_urls_to_process:
                    if sample_count >= max_samples:
                        break
                    
                    status_text.info(f"بررسی لینک {link_index + 1} از {len(link_urls_to_process)}")
                    
                    company_name = None
                    reg_number = None
                    nat_id_display = None
                    
                    try:
                        driver.execute_script(f"window.open('{link_url}', '_blank');")
                        wait.until(EC.number_of_windows_to_be(len(driver.window_handles)))
                        all_windows = driver.window_handles
                        new_window = all_windows[-1]
                        driver.switch_to.window(new_window)
                        
                        body_locator = (By.TAG_NAME, "body")
                        general_wait.until(EC.presence_of_element_located(body_locator))
                        time.sleep(1)
                        
                        # Extract metadata
                        try:
                            company_input = driver.find_element(By.ID, "P28_COMPANYNAME")
                            company_name = company_input.get_attribute('value')
                        except NoSuchElementException: pass
                        
                        try:
                            reg_num_span = driver.find_element(By.ID, "P28_SABTNUMBER_DISPLAY")
                            reg_number = reg_num_span.text
                        except NoSuchElementException: pass
                        
                        try:
                            nat_id_display_element = driver.find_element(By.ID, "P28_SABTNATIONALID_DISPLAY")
                            nat_id_display = nat_id_display_element.text
                        except NoSuchElementException: pass
                        
                        # Get and clean HTML
                        body_element = driver.find_element(By.TAG_NAME, "body")
                        inner_html = body_element.get_attribute('innerHTML')
                        cleaned_text = remove_tags(inner_html)
                        
                        # Extract contexts
                        all_contexts = extract_all_phrase_contexts(cleaned_text, search_phrase, start_words=start_words_list, words_after=5)
                        
                        if all_contexts:
                            for context in all_contexts:
                                if sample_count >= max_samples:
                                    break
                                
                                if filter_word not in context:
                                    continue
                                
                                national_ids_found = re.findall(r'\b(\d{10})\b', context)
                                if len(national_ids_found) != 1:
                                    continue
                                
                                national_id = national_ids_found[0]
                                position = "unknown"
                                for keyword in position_keywords:
                                    if keyword in context:
                                        position = position_map[keyword]
                                        break
                                
                                # Skip if ceo_only and not CEO
                                if ceo_only and position != "ceo":
                                    continue
                                
                                # Check for duplicates
                                entry_key = f"{company_name}-{national_id}-{position}"
                                if entry_key in seen_entries:
                                    continue
                                
                                seen_entries.add(entry_key)
                                
                                # Add extracted data
                                new_entry = {
                                    "id": auto_increment_id,
                                    "company_name": company_name,
                                    "reg_number": reg_number,
                                    "nat_id_display": nat_id_display,
                                    "national_id": national_id,
                                    "position": position,
                                    "context": context,
                                    "extraction_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }
                                
                                extracted_data.append(new_entry)
                                st.session_state.data.append(new_entry)
                                
                                # Update position stats for visualization
                                position_display = {
                                    "chairman": "رئیس هیئت مدیره",
                                    "viceChairman": "نایب رئیس هیئت مدیره", 
                                    "ceo": "مدیرعامل",
                                    "boardmember": "عضو هیئت مدیره",
                                    "boardmember_alternate": "عضو علی البدل",
                                    "mainInspector": "بازرس اصلی",
                                    "alternativeInspector": "بازرس علی البدل",
                                    "unknown": "نامشخص"
                                }
                                
                                display_position = position_display.get(position, position)
                                if display_position in st.session_state.viz_data["positions"]:
                                    st.session_state.viz_data["positions"][display_position] += 1
                                else:
                                    st.session_state.viz_data["positions"][display_position] = 1
                                
                                # Add company if new
                                if company_name and company_name not in [c["name"] for c in st.session_state.viz_data["companies"]]:
                                    st.session_state.viz_data["companies"].append({
                                        "name": company_name,
                                        "count": 1
                                    })
                                elif company_name:
                                    for c in st.session_state.viz_data["companies"]:
                                        if c["name"] == company_name:
                                            c["count"] += 1
                                            break
                                
                                sample_count += 1
                                auto_increment_id += 1
                                
                                # Update progress
                                progress_bar.progress(min(1.0, sample_count / max_samples))
                                result_count.metric("تعداد نتایج", f"{sample_count} / {max_samples}")
                                
                                # Dynamically display latest data
                                if len(st.session_state.data) > 0:
                                    last_entry = st.session_state.data[-1]
                                    position_display_name = position_display.get(last_entry["position"], last_entry["position"])
                                    
                                    status_text.success(f"یافته شد: {last_entry['national_id']} - {position_display_name} در {last_entry['company_name'] or 'شرکت نامشخص'}")
                        
                    except Exception as e:
                        status_text.error(f"خطا در پردازش: {str(e)}")
                    finally:
                        if len(driver.window_handles) > 1:
                            driver.close()
                            driver.switch_to.window(original_window)
                
                # Save data periodically
                if extracted_data:
                    try:
                        if existing_data:
                            combined_data = existing_data + extracted_data
                            save_data_to_json(combined_data, filename)
                        else:
                            save_data_to_json(extracted_data, filename)
                        
                        # Reset for next batch
                        existing_data = existing_data + extracted_data
                        extracted_data = []
                    except Exception as e:
                        st.error(f"خطا در ذخیره داده: {str(e)}")
                
                if sample_count >= max_samples:
                    break
                
                # Try to navigate to next page
                next_page_number = current_page_number + 1
                status_text.info(f"تلاش برای رفتن به صفحه {next_page_number}...")
                
                found_next_page = False
                try:
                    # Find pagination buttons
                    page_buttons = driver.find_elements(By.CSS_SELECTOR, "button.a-GV-pageButton")
                    
                    # Try to click the button for the next page
                    for btn in page_buttons:
                        try:
                            btn_text = btn.text.strip()
                            if btn_text == str(next_page_number):
                                driver.execute_script("arguments[0].click();", btn)
                                time.sleep(3)
                                general_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tr a[href]")))
                                current_page_number = next_page_number
                                found_next_page = True
                                break
                        except Exception:
                            continue
                    
                    if not found_next_page:
                        status_text.warning(f"دکمه صفحه {next_page_number} پیدا نشد. پایان نتایج.")
                        break
                except Exception as page_nav_err:
                    status_text.error(f"خطا در تغییر صفحه: {str(page_nav_err)}")
                    break
            
            # End of loop
            st.session_state.crawling_complete = True
            progress_bar.progress(1.0)
            status_text.success(f"استخراج داده‌ها به پایان رسید. {sample_count} مورد ذخیره شد.")
            
        except Exception as e:
            st.error(f"خطای اصلی: {str(e)}")
        finally:
            try:
                driver.quit()
            except:
                pass
    
    # Display results if available
    if st.session_state.data or st.session_state.crawling_complete:
        colored_header(
            label="نتایج استخراج شده",
            description="داده های استخراج شده از روزنامه رسمی",
            color_name="red-70",
        )
        
        # Data stats and visualization
        if "viz_data" in st.session_state and st.session_state.viz_data["positions"]:
            col1, col2 = st.columns(2)
            
            with col1:
                # Position distribution chart
                st.markdown("<h3>توزیع سمت‌ها</h3>", unsafe_allow_html=True)
                position_data = pd.DataFrame({
                    'سمت': list(st.session_state.viz_data["positions"].keys()),
                    'تعداد': list(st.session_state.viz_data["positions"].values())
                })
                
                fig = px.pie(
                    position_data, 
                    values='تعداد', 
                    names='سمت',
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Bold
                )
                fig.update_layout(margin=dict(l=20, r=20, t=30, b=20))
                st.plotly_chart(fig, use_container_width=True, key="position_pie_chart_1")
            
            with col2:
                # Top companies
                st.markdown("<h3>شرکت‌های برتر</h3>", unsafe_allow_html=True)
                if st.session_state.viz_data["companies"]:
                    companies_sorted = sorted(st.session_state.viz_data["companies"], key=lambda x: x["count"], reverse=True)
                    top_companies = companies_sorted[:10]  # Top 10 companies
                    
                    company_data = pd.DataFrame({
                        'شرکت': [c["name"] or "نامشخص" for c in top_companies],
                        'تعداد': [c["count"] for c in top_companies]
                    })
                    
                    fig = px.bar(
                        company_data,
                        x='تعداد',
                        y='شرکت',
                        orientation='h',
                        color='تعداد',
                        color_continuous_scale='Reds'
                    )
                    fig.update_layout(margin=dict(l=20, r=20, t=30, b=20))
                    st.plotly_chart(fig, use_container_width=True, key="top_companies_bar_chart")
        
        # Data table
        if st.session_state.data:
            st.markdown("<h3>داده‌های استخراج شده</h3>", unsafe_allow_html=True)
            
            # Convert to DataFrame for display
            position_display = {
                "chairman": "رئیس هیئت مدیره",
                "viceChairman": "نایب رئیس هیئت مدیره", 
                "ceo": "مدیرعامل",
                "boardmember": "عضو هیئت مدیره",
                "boardmember_alternate": "عضو علی البدل",
                "mainInspector": "بازرس اصلی",
                "alternativeInspector": "بازرس علی البدل",
                "unknown": "نامشخص"
            }
            
            display_data = []
            for item in st.session_state.data:
                display_data.append({
                    "شناسه": item.get("id"),
                    "نام شرکت": item.get("company_name", "نامشخص"),
                    "شماره ثبت": item.get("reg_number", "نامشخص"),
                    "شناسه ملی": item.get("national_id", ""),
                    "سمت": position_display.get(item.get("position"), item.get("position", "نامشخص")),
                    "تاریخ استخراج": item.get("extraction_date", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                })
            
            df = pd.DataFrame(display_data)
            st.dataframe(df, use_container_width=True)
            
            # Export options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # CSV Download
                csv = df.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="extracted_data.csv" class="stButton"><button>دانلود CSV</button></a>'
                st.markdown(href, unsafe_allow_html=True)
            
            with col2:
                # Excel Download
                buffer = pd.ExcelWriter('extracted_data.xlsx', engine='xlsxwriter')
                df.to_excel(buffer, index=False, sheet_name='Sheet1')
                buffer.close()
                
                with open('extracted_data.xlsx', 'rb') as f:
                    excel_data = f.read()
                
                b64 = base64.b64encode(excel_data).decode()
                href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="extracted_data.xlsx" class="stButton"><button>دانلود Excel</button></a>'
                st.markdown(href, unsafe_allow_html=True)
            
            with col3:
                # JSON Download
                json_str = json.dumps(st.session_state.data, ensure_ascii=False, indent=4, cls=DateTimeEncoder)
                b64 = base64.b64encode(json_str.encode('utf-8')).decode()
                href = f'<a href="data:file/json;base64,{b64}" download="extracted_data.json" class="stButton"><button>دانلود JSON</button></a>'
                st.markdown(href, unsafe_allow_html=True)

with tab2:
    colored_header(
        label="تحلیل داده‌های استخراج شده",
        description="داشبورد هوشمند برای تحلیل داده‌های موجود",
        color_name="red-70",
    )
    
    # File selection for analysis
    analysis_filename = st.text_input("📂 انتخاب فایل برای تحلیل", value="extracted_data.json", help="نام فایل حاوی داده‌های استخراج شده")
    
    # Load existing data
    if os.path.exists(analysis_filename):
        with st.spinner("در حال بارگذاری داده‌ها..."):
            try:
                with open(analysis_filename, 'r', encoding='utf-8') as f:
                    analytics_data = json.load(f)
                
                # Convert to DataFrame
                df_analytics = pd.DataFrame(analytics_data)
                
                # Position translation mapping
                position_display = {
                    "chairman": "رئیس هیئت مدیره",
                    "viceChairman": "نایب رئیس هیئت مدیره", 
                    "ceo": "مدیرعامل",
                    "boardmember": "عضو هیئت مدیره",
                    "boardmember_alternate": "عضو علی البدل",
                    "mainInspector": "بازرس اصلی",
                    "alternativeInspector": "بازرس علی البدل",
                    "unknown": "نامشخص"
                }
                
                # Add Persian position display column
                df_analytics['position_display'] = df_analytics['position'].map(lambda x: position_display.get(x, x))
                
                # Add extraction date as datetime
                if 'extraction_date' in df_analytics.columns:
                    df_analytics['extraction_datetime'] = pd.to_datetime(df_analytics['extraction_date'])
                else:
                    # Use current date if no extraction date
                    df_analytics['extraction_datetime'] = datetime.now()
                
                # Display key metrics
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("<h3 class='section-title'>📊 آمارهای کلیدی</h3>", unsafe_allow_html=True)
                
                # Use CSS grid for better layout of metrics
                st.markdown("<div class='metrics-container'>", unsafe_allow_html=True)
                
                # Metrics without individual wrappers
                st.metric("تعداد کل افراد", f"{len(df_analytics)}")
                st.metric("تعداد شرکت‌ها", f"{df_analytics['company_name'].nunique()}")
                st.metric("تعداد مدیرعامل‌ها", f"{len(df_analytics[df_analytics['position'] == 'ceo'])}")
                st.metric("تعداد رؤسای هیئت مدیره", f"{len(df_analytics[df_analytics['position'] == 'chairman'])}")
                
                st.markdown("</div>", unsafe_allow_html=True) # Close metrics-container
                st.markdown("</div>", unsafe_allow_html=True) # Close card
                
                # Filter section
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("<h3>فیلترهای تحلیلی</h3>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Company filter
                    if len(df_analytics['company_name'].unique()) > 1:
                        company_filter = st.multiselect(
                            "انتخاب شرکت‌ها:",
                            options=sorted([c for c in df_analytics['company_name'].unique() if c]),
                            default=[]
                        )
                    else:
                        company_filter = []
                
                    # Position filter
                    position_options = df_analytics['position_display'].unique()
                    position_filter = st.multiselect(
                        "انتخاب سمت‌ها:",
                        options=sorted(position_options),
                        default=[]
                    )
                
                with col2:
                    # Date range filter if dates are available
                    if 'extraction_datetime' in df_analytics.columns:
                        min_date = df_analytics['extraction_datetime'].min().date()
                        max_date = df_analytics['extraction_datetime'].max().date()
                        
                        date_filter = st.date_input(
                            "محدوده تاریخی:",
                            value=(min_date, max_date),
                            min_value=min_date,
                            max_value=max_date
                        )
                
                # Apply filters
                filtered_df = df_analytics.copy()
                
                if company_filter:
                    filtered_df = filtered_df[filtered_df['company_name'].isin(company_filter)]
                
                if position_filter:
                    filtered_df = filtered_df[filtered_df['position_display'].isin(position_filter)]
                
                if 'extraction_datetime' in filtered_df.columns and len(date_filter) == 2:
                    start_date, end_date = date_filter
                    filtered_df = filtered_df[
                        (filtered_df['extraction_datetime'].dt.date >= start_date) & 
                        (filtered_df['extraction_datetime'].dt.date <= end_date)
                    ]
                
                # Show filter status
                if len(filtered_df) < len(df_analytics):
                    st.info(f"نمایش {len(filtered_df)} مورد از {len(df_analytics)} (فیلتر شده)")
                else:
                    st.success(f"نمایش همه {len(df_analytics)} مورد")
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Visualizations section
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.markdown("<h3>توزیع سمت‌ها</h3>", unsafe_allow_html=True)
                    
                    # Position distribution
                    position_counts = filtered_df['position_display'].value_counts().reset_index()
                    position_counts.columns = ['سمت', 'تعداد']
                    
                    fig = px.pie(
                        position_counts,
                        values='تعداد',
                        names='سمت',
                        hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Bold
                    )
                    fig.update_layout(margin=dict(l=20, r=20, t=30, b=20))
                    st.plotly_chart(fig, use_container_width=True, key="tab2_position_pie_chart")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.markdown("<h3>شرکت‌های دارای بیشترین افراد</h3>", unsafe_allow_html=True)
                    
                    # Top companies by number of individuals
                    company_counts = filtered_df['company_name'].value_counts().reset_index()
                    company_counts.columns = ['شرکت', 'تعداد']
                    
                    # Take top 10
                    top_companies = company_counts.head(10)
                    
                    fig = px.bar(
                        top_companies,
                        x='تعداد',
                        y='شرکت',
                        orientation='h',
                        color='تعداد',
                        color_continuous_scale='Reds',
                        text='تعداد'
                    )
                    fig.update_layout(margin=dict(l=20, r=20, t=30, b=20))
                    fig.update_traces(textposition='auto')
                    st.plotly_chart(fig, use_container_width=True, key="tab2_companies_bar_chart")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # Remove the word cloud section
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.markdown("<h3>توزیع سمت‌ها در شرکت‌های برتر</h3>", unsafe_allow_html=True)
                    
                    if not filtered_df.empty:
                        # Get top 5 companies
                        top_5_companies = company_counts.head(5)['شرکت'].tolist()
                        
                        if top_5_companies:
                            # Filter for those companies
                            top_companies_df = filtered_df[filtered_df['company_name'].isin(top_5_companies)]
                            
                            # Group by company and position
                            company_position_counts = top_companies_df.groupby(['company_name', 'position_display']).size().reset_index()
                            company_position_counts.columns = ['شرکت', 'سمت', 'تعداد']
                            
                            # Create stacked bar chart
                            fig = px.bar(
                                company_position_counts,
                                x='شرکت',
                                y='تعداد',
                                color='سمت',
                                color_discrete_sequence=px.colors.qualitative.Bold,
                                text='تعداد'
                            )
                            fig.update_layout(margin=dict(l=20, r=20, t=30, b=20))
                            fig.update_traces(textposition='auto')
                            st.plotly_chart(fig, use_container_width=True, key="position_by_company_chart")
                        else:
                            st.warning("داده‌ای برای نمایش نمودار یافت نشد.")
                    else:
                        st.warning("داده‌ای برای نمایش نمودار یافت نشد.")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # Network analysis section
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("<h3>تحلیل شبکه‌ای افراد مشترک در شرکت‌ها</h3>", unsafe_allow_html=True)
                
                st.markdown("<p>این نمودار ارتباط شرکت‌هایی را نشان می‌دهد که افراد مشترک در آنها حضور دارند.</p>", unsafe_allow_html=True)
                
                # Check if we have enough data for network analysis
                if not filtered_df.empty and len(filtered_df['company_name'].unique()) > 1:
                    # Create network graph
                    G = nx.Graph()
                    
                    # Find people who are in multiple companies
                    person_companies = filtered_df.groupby('national_id')['company_name'].apply(list).reset_index()
                    
                    # Only keep people in multiple companies
                    person_companies = person_companies[person_companies['company_name'].apply(lambda x: len(set(x)) > 1)]
                    
                    # Add edges between companies that share people
                    edges_added = set()
                    for _, row in person_companies.iterrows():
                        companies = list(set(row['company_name']))
                        for i in range(len(companies)):
                            for j in range(i+1, len(companies)):
                                if companies[i] and companies[j]:  # Ensure companies are not None/empty
                                    edge = tuple(sorted([companies[i], companies[j]]))
                                    if edge not in edges_added:
                                        G.add_edge(companies[i], companies[j], weight=1)
                                        edges_added.add(edge)
                                    else:
                                        G[edge[0]][edge[1]]['weight'] += 1
                    
                    if G.number_of_edges() > 0:
                        # Layout
                        pos = nx.spring_layout(G, k=0.5, iterations=50)
                        
                        # Create a plotly figure
                        edge_x = []
                        edge_y = []
                        edge_weights = []
                        
                        for edge in G.edges(data=True):
                            x0, y0 = pos[edge[0]]
                            x1, y1 = pos[edge[1]]
                            edge_x.extend([x0, x1, None])
                            edge_y.extend([y0, y1, None])
                            edge_weights.append(edge[2]['weight'])
                        
                        # Scale edge width by weight
                        max_weight = max(edge_weights) if edge_weights else 1
                        scaled_weights = [2 + 8 * (w / max_weight) for w in edge_weights]
                        
                        # Create traces for edges
                        edge_trace = go.Scatter(
                            x=edge_x, y=edge_y,
                            line=dict(width=1, color='#888'),
                            hoverinfo='none',
                            mode='lines')
                        
                        # Create traces for nodes
                        node_x = []
                        node_y = []
                        node_text = []
                        node_sizes = []
                        
                        for node in G.nodes():
                            x, y = pos[node]
                            node_x.append(x)
                            node_y.append(y)
                            # Text will be company name and degree
                            node_text.append(f"{node}: {G.degree(node)} ارتباط")
                            # Node size based on degree
                            node_sizes.append(10 + 5 * G.degree(node))
                        
                        node_trace = go.Scatter(
                            x=node_x, y=node_y,
                            mode='markers',
                            hoverinfo='text',
                            text=node_text,
                            marker=dict(
                                showscale=True,
                                colorscale='YlOrRd',
                                size=node_sizes,
                                color=[G.degree(node) for node in G.nodes()],
                                colorbar=dict(
                                    thickness=15,
                                    title='تعداد ارتباطات',
                                    xanchor='left',
                                    titleside='right'
                                ),
                                line_width=2))
                        
                        # Create figure
                        fig = go.Figure(data=[edge_trace, node_trace],
                                        layout=go.Layout(
                                            showlegend=False,
                                            hovermode='closest',
                                            margin=dict(b=20, l=5, r=5, t=40),
                                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                            height=600,
                                            title='شبکه ارتباطات شرکت‌ها از طریق افراد مشترک'
                                        ))
                        
                        st.plotly_chart(fig, use_container_width=True, key="network_graph")
                    else:
                        st.warning("داده‌های کافی برای ساخت نمودار شبکه‌ای یافت نشد. هیچ فردی در چند شرکت حضور ندارد.")
                else:
                    st.warning("داده‌های کافی برای ساخت نمودار شبکه‌ای یافت نشد.")
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Display simple data table
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("<h3>داده‌های استخراج شده</h3>", unsafe_allow_html=True)
                
                # Formatting for display
                display_df = filtered_df[['id', 'company_name', 'national_id', 'position_display', 'extraction_date']].copy() if not filtered_df.empty else pd.DataFrame()
                if not display_df.empty:
                    display_df.columns = ['شناسه', 'نام شرکت', 'کد ملی', 'سمت', 'تاریخ استخراج']
                    st.dataframe(display_df, use_container_width=True)
                else:
                    st.warning("هیچ داده‌ای یافت نشد.")
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Export options
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("<h3>دانلود داده‌های فیلتر شده</h3>", unsafe_allow_html=True)
                
                export_filename = st.text_input("📝 نام فایل خروجی برای دانلود", value="filtered_data", help="نام فایل بدون پسوند")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # CSV Download
                    csv = display_df.to_csv(index=False)
                    b64 = base64.b64encode(csv.encode()).decode()
                    href = f'<a href="data:file/csv;base64,{b64}" download="{export_filename}.csv" class="stButton"><button>دانلود CSV</button></a>'
                    st.markdown(href, unsafe_allow_html=True)
                
                with col2:
                    # Excel Download
                    buffer = pd.ExcelWriter(f'{export_filename}.xlsx', engine='xlsxwriter')
                    display_df.to_excel(buffer, index=False, sheet_name='Sheet1')
                    buffer.close()
                    
                    with open(f'{export_filename}.xlsx', 'rb') as f:
                        excel_data = f.read()
                    
                    b64 = base64.b64encode(excel_data).decode()
                    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{export_filename}.xlsx" class="stButton"><button>دانلود Excel</button></a>'
                    st.markdown(href, unsafe_allow_html=True)
                
                with col3:
                    # JSON Download
                    json_data = filtered_df.to_dict(orient='records')
                    try:
                        json_str = json.dumps(json_data, ensure_ascii=False, indent=4, cls=DateTimeEncoder)
                        b64 = base64.b64encode(json_str.encode('utf-8')).decode()
                        href = f'<a href="data:file/json;base64,{b64}" download="{export_filename}.json" class="stButton"><button>دانلود JSON</button></a>'
                        st.markdown(href, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"خطا در تبدیل داده به JSON: {str(e)}")
                
                st.markdown("</div>", unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"خطا در بارگذاری فایل {analysis_filename}: {str(e)}")
    else:
        st.warning(f"فایل داده ({analysis_filename}) یافت نشد. لطفاً ابتدا با استفاده از تب 'روزنامه رسمی' داده‌ها را استخراج کنید.")
        st.info("راهنما: به تب 'روزنامه رسمی' بروید، اطلاعات مورد نیاز را وارد کرده و دکمه 'شروع استخراج داده‌ها' را بزنید.")

with tab3:
    st.markdown("<div style='text-align: center; padding: 50px;'>", unsafe_allow_html=True)
    st.image("https://img.icons8.com/color/96/000000/coming-soon.png", width=150)
    st.markdown("<h2>به زودی...</h2>", unsafe_allow_html=True)
    st.markdown("<p>در حال توسعه منابع داده‌ای جدید هستیم. لطفاً دوباره بررسی کنید.</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center;'>© 2025 Persian Data Crawler | طراحی و توسعه با ❤️</p>", unsafe_allow_html=True) 