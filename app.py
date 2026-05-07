import streamlit as st
import streamlit.components.v1 as components

# ปรับ layout เป็น "wide" เพื่อให้มีพื้นที่แนวนอนกว้างขึ้น
st.set_page_config(page_title="True Real-time Translator", layout="wide")
st.title("⚡ True Real-time Translator")
st.markdown("ระบบนี้จะประมวลผลบนเบราว์เซอร์ของคุณโดยตรง พิมพ์และแปลข้อความ **ทันทีที่คุณกำลังพูด**")

# ==========================================
# ฝังโค้ด HTML + JavaScript เข้าไปใน Streamlit
# ==========================================
custom_html = """
<!DOCTYPE html>
<html>
<head>
<style>
  body { 
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
    color: #fff; 
    background-color: #0e1117; 
  }
  .container { padding: 10px; }
  
  /* --------------------------------------------------- */
  /* สไตล์สำหรับกล่องควบคุม (จัดวางแบบ 2 คอลัมน์) */
  /* --------------------------------------------------- */
  .controls-container {
      display: flex;
      gap: 20px;
      margin-bottom: 25px;
  }
  .control-box {
      flex: 1;
      background: #1e2127;
      padding: 15px 20px;
      border-radius: 8px;
      border: 1px solid #333;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
  }
  .control-title {
      font-size: 14px;
      color: #a3a8b8;
      margin-bottom: 12px;
      font-weight: bold;
  }
  .lang-selector {
      display: flex;
      gap: 25px;
  }
  .lang-selector label {
      font-size: 16px;
      cursor: pointer;
      color: #e6eaf1;
  }
  
  /* สไตล์สำหรับ Slider เลื่อนเวลา */
  .slider-container {
      display: flex;
      align-items: center;
      gap: 15px;
      width: 90%;
  }
  input[type=range] {
      flex: 1;
      accent-color: #ff4b4b; /* ให้สีเข้ากับปุ่มไมค์ */
      cursor: pointer;
  }
  .slider-val {
      font-size: 16px;
      color: #e6eaf1;
      min-width: 65px;
  }

  .btn-container { text-align: center; margin-bottom: 20px; }
  button { 
    padding: 12px 24px; 
    font-size: 16px; 
    font-weight: bold;
    border: none; 
    border-radius: 8px; 
    cursor: pointer; 
    transition: 0.2s;
  }
  #startBtn { background-color: #ff4b4b; color: white; margin-right: 10px; }
  #startBtn:hover { background-color: #ff3333; }
  #stopBtn { background-color: #444; color: white; }
  #stopBtn:hover { background-color: #555; }

  .output-container {
    display: flex;
    gap: 20px; 
  }
  .box { 
    flex: 1; 
    padding: 20px; 
    border-radius: 8px; 
    background: #1e2127; 
    border: 1px solid #333;
    min-height: 250px; 
  }
  
  .title { font-weight: bold; color: #a3a8b8; margin-bottom: 15px; font-size: 16px; border-bottom: 1px solid #333; padding-bottom: 10px;}
  .text { font-size: 22px; color: #e6eaf1; line-height: 1.6; }
  .interim { color: #ff4b4b; }
  .placeholder { color: #555; font-size: 18px; font-style: italic; }
</style>
</head>
<body>

<div class="container">
  
  <!-- กล่องควบคุมด้านบน -->
  <div class="controls-container">
    <!-- 1. เลือกภาษา -->
    <div class="control-box">
        <div class="control-title">🌍 ทิศทางการแปล</div>
        <div class="lang-selector">
            <label><input type="radio" name="langMode" value="th2en" checked onchange="changeLang()"> 🇹🇭 ไทย ➡️ 🇬🇧 อังกฤษ</label>
            <label><input type="radio" name="langMode" value="en2th" onchange="changeLang()"> 🇬🇧 อังกฤษ ➡️ 🇹🇭 ไทย</label>
        </div>
    </div>
    
    <!-- 2. ปรับเวลาล้างหน้าจอ -->
    <div class="control-box">
        <div class="control-title">⏱️ เวลาหน่วงก่อนขึ้นประโยคใหม่ (เมื่อหยุดพูด)</div>
        <div class="slider-container">
            <input type="range" id="delaySlider" min="1" max="15" value="4" oninput="updateDelay()">
            <div class="slider-val"><span id="delayValue">4</span> วินาที</div>
        </div>
    </div>
  </div>

  <div class="btn-container">
      <button id="startBtn" onclick="startDictation()">🎤 กดเพื่อพูด (Live)</button>
      <button id="stopBtn" onclick="stopDictation()">⏹️ หยุด</button>
  </div>

  <!-- กล่องแสดงผล -->
  <div class="output-container">
    <div class="box">
      <div id="origTitle" class="title">🇹🇭 ต้นฉบับ (กำลังพูด):</div>
      <div id="original" class="text"><span class="placeholder">[รอรับเสียง...]</span></div>
    </div>
    <div class="box">
      <div id="transTitle" class="title">🇬🇧 คำแปล (Real-time):</div>
      <div id="translated" class="text"><span class="placeholder">[รอการแปล...]</span></div>
    </div>
  </div>
</div>

<script>
  let recognition;
  let isRecognizing = false;
  let isManualStop = false; 
  let isAutoClearing = false; // ตัวแปรบอกว่าระบบกำลังตัดจบประโยคเอง
  
  // เวลาหน่วงเคลียร์ข้อความ (ค่าเริ่มต้น 4 วินาที)
  let clearDelayMs = 4000; 
  let clearTimer;
  
  // เวลาตัดไมค์เมื่อลืมปิด (5 นาที)
  let inactivityTimer;
  const IDLE_TIMEOUT_MS = 5 * 60 * 1000; 
  
  let sttLang = "th-TH";
  let srcLang = "th";
  let destLang = "en";

  // ฟังก์ชันอัปเดตค่าเวลาจาก Slider ทันทีที่เลื่อน
  function updateDelay() {
      let val = document.getElementById('delaySlider').value;
      document.getElementById('delayValue').innerText = val;
      clearDelayMs = parseInt(val) * 1000;
  }

  // ระบบนับเวลาเพื่อ "ขึ้นประโยคใหม่"
  function resetClearTimer() {
      clearTimeout(clearTimer);
      clearTimer = setTimeout(() => {
          // เคลียร์หน้าจอ
          document.getElementById('original').innerHTML = "<span class='placeholder'>[เริ่มประโยคใหม่...]</span>";
          document.getElementById('translated').innerHTML = "<span class='placeholder'>[...]</span>";
          
          // บังคับรีสตาร์ทไมค์เพื่อล้างความจำ (Buffer) ของประโยคเก่าทิ้งทั้งหมด
          if (isRecognizing) {
              isAutoClearing = true;
              recognition.stop(); 
          }
      }, clearDelayMs);
  }

  function resetInactivityTimer() {
    clearTimeout(inactivityTimer); 
    if (isRecognizing) {
      inactivityTimer = setTimeout(() => {
        isManualStop = true; 
        recognition.stop();
        document.getElementById('original').innerHTML = "<span style='font-size:16px; color:#ff4b4b;'><i>ปิดไมค์อัตโนมัติ เนื่องจากไม่มีเสียงพูดนานเกินไป...</i></span>";
        document.getElementById('translated').innerHTML = "...";
      }, IDLE_TIMEOUT_MS);
    }
  }

  if (window.hasOwnProperty('webkitSpeechRecognition')) {
    recognition = new webkitSpeechRecognition();
    recognition.continuous = true;       
    recognition.interimResults = true;   
    recognition.lang = sttLang;          

    recognition.onstart = function() {
      isRecognizing = true;
      document.getElementById('startBtn').innerText = "🟢 กำลังฟัง (พูดได้เลย)...";
      document.getElementById('startBtn').style.backgroundColor = "#00cc66";
      document.getElementById('original').innerHTML = "";
      document.getElementById('translated').innerHTML = "";
      
      resetInactivityTimer(); 
    };

    recognition.onend = function() {
      isRecognizing = false;
      clearTimeout(inactivityTimer);
      clearTimeout(clearTimer);
      
      // 1. ถ้าเป็นการตัดจบประโยคอัตโนมัติ ให้รีสตาร์ทไมค์ทันที
      if (isAutoClearing) {
          isAutoClearing = false;
          try { recognition.start(); } catch(e){}
          return;
      }

      // 2. ถ้าเบราว์เซอร์ตัดไมค์เอง (กันมือถือดับ)
      if (!isManualStop) {
          try {
              recognition.start();
              return; 
          } catch(e) {}
      }

      // 3. ถ้าผู้ใช้กดปุ่มหยุดเอง
      document.getElementById('startBtn').innerText = "🎤 กดเพื่อพูด (Live)";
      document.getElementById('startBtn').style.backgroundColor = "#ff4b4b";
    };

    recognition.onresult = function(event) {
      resetInactivityTimer(); // รีเซ็ต 5 นาที
      resetClearTimer();      // รีเซ็ตตัวนับล้างหน้าจอ ทุกครั้งที่มีเสียงเข้า!
      
      let interim_transcript = '';
      let final_transcript = '';

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          final_transcript += event.results[i][0].transcript;
        } else {
          interim_transcript += event.results[i][0].transcript;
        }
      }

      let currentText = final_transcript + interim_transcript;
      document.getElementById('original').innerHTML = 
        final_transcript + '<span class="interim">' + interim_transcript + '</span>';

      if (currentText.trim() !== "") {
        translateText(currentText, srcLang, destLang);
      }
    };
  } else {
    document.getElementById('original').innerHTML = "เบราว์เซอร์ของคุณไม่รองรับ แนะนำให้ใช้ Google Chrome หรือ Edge ครับ";
  }

  function startDictation() {
    if (!isRecognizing) {
      isManualStop = false; 
      isAutoClearing = false;
      recognition.lang = sttLang;
      recognition.start();
    }
  }

  function stopDictation() {
    if (isRecognizing) {
      isManualStop = true; 
      recognition.stop();
    }
  }
  
  function changeLang() {
    let mode = document.querySelector('input[name="langMode"]:checked').value;
    
    if (mode === "th2en") {
        sttLang = "th-TH";
        srcLang = "th";
        destLang = "en";
        document.getElementById('origTitle').innerText = "🇹🇭 ต้นฉบับ (กำลังพูด):";
        document.getElementById('transTitle').innerText = "🇬🇧 คำแปล (Real-time):";
    } else {
        sttLang = "en-US";
        srcLang = "en";
        destLang = "th";
        document.getElementById('origTitle').innerText = "🇬🇧 ต้นฉบับ (กำลังพูด):";
        document.getElementById('transTitle').innerText = "🇹🇭 คำแปล (Real-time):";
    }
    
    if(isRecognizing) {
        isManualStop = true; 
        stopDictation();
        document.getElementById('original').innerHTML = "<span class='placeholder'>ระบบหยุดฟังเพื่อเปลี่ยนภาษา... กดปุ่มพูดใหม่อีกครั้งครับ</span>";
        document.getElementById('translated').innerHTML = "...";
    } else {
        document.getElementById('original').innerHTML = "<span class='placeholder'>[รอรับเสียง...]</span>";
        document.getElementById('translated').innerHTML = "<span class='placeholder'>[รอการแปล...]</span>";
    }
  }

  function translateText(text, src, dest) {
    let url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=${src}&tl=${dest}&dt=t&q=${encodeURI(text)}`;
    
    fetch(url)
      .then(response => response.json())
      .then(data => {
        let translated_text = '';
        for (let i = 0; i < data[0].length; i++) {
           translated_text += data[0][i][0];
        }
        document.getElementById('translated').innerHTML = translated_text;
      })
      .catch(error => console.error('Error:', error));
  }
</script>
</body>
</html>
"""

# เพิ่มความสูงขึ้นนิดหน่อยเพื่อให้พื้นที่กับเมนูควบคุมใหม่
components.html(custom_html, height=520)

# ==========================================
# Credit Footer
# ==========================================
st.markdown("---")
st.markdown("<p style='text-align: center; color: #a3a8b8; font-size: 14px;'>Developed by <b>Joopiest Udomsaph</b></p>", unsafe_allow_html=True)