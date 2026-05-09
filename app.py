import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="True Real-time Translator", layout="wide")
st.title("⚡ True Real-time Translator")
st.markdown("ระบบแปลภาษาด่วนแบบ Real-time พัฒนาโดยใช้เทคโนโลยี Web Speech API และ JavaScript")

custom_html = """
<!DOCTYPE html>
<html>
<head>
<style>
  body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #fff; background-color: #0e1117; }
  .container { padding: 10px; }
  .controls-container { display: flex; gap: 20px; margin-bottom: 25px; }
  .control-box { flex: 1; background: #1e2127; padding: 15px 20px; border-radius: 8px; border: 1px solid #333; display: flex; flex-direction: column; align-items: center; justify-content: center; }
  .control-title { font-size: 14px; color: #a3a8b8; margin-bottom: 12px; font-weight: bold; }
  .lang-selector { display: flex; gap: 25px; }
  .lang-selector label { font-size: 16px; cursor: pointer; color: #e6eaf1; }
  .slider-container { display: flex; align-items: center; gap: 15px; width: 90%; }
  input[type=range] { flex: 1; accent-color: #ff4b4b; cursor: pointer; }
  .slider-val { font-size: 16px; color: #e6eaf1; min-width: 80px; }
  .btn-container { text-align: center; margin-bottom: 20px; }
  button { padding: 12px 24px; font-size: 16px; font-weight: bold; border: none; border-radius: 8px; cursor: pointer; transition: 0.2s; }
  #startBtn { background-color: #ff4b4b; color: white; margin-right: 10px; }
  #stopBtn { background-color: #444; color: white; }
  
  .output-container { display: flex; gap: 20px; }
  .box { flex: 1; padding: 20px; border-radius: 8px; background: #1e2127; border: 1px solid #333; display: flex; flex-direction: column; height: 350px; box-sizing: border-box; }
  
  /* --- จัดรูปแบบ Header ของกล่องใหม่ เพื่อใส่ปุ่ม Copy --- */
  .box-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #333; padding-bottom: 10px; margin-bottom: 15px; flex-shrink: 0; }
  .title { font-weight: bold; color: #a3a8b8; font-size: 16px; margin: 0; }
  
  /* สไตล์ปุ่ม Copy */
  .copy-btn { padding: 6px 12px; font-size: 13px; font-weight: normal; background-color: transparent; color: #a3a8b8; border: 1px solid #555; border-radius: 6px; cursor: pointer; transition: 0.2s; }
  .copy-btn:hover { background-color: #333; color: #fff; }

  .scroll-area { flex: 1; overflow-y: scroll; padding-right: 10px; }
  .scroll-area::-webkit-scrollbar { width: 8px; }
  .scroll-area::-webkit-scrollbar-track { background: #1e2127; border-radius: 8px; }
  .scroll-area::-webkit-scrollbar-thumb { background: #555; border-radius: 8px; }
  .scroll-area::-webkit-scrollbar-thumb:hover { background: #777; }
  .text { font-size: 22px; color: #e6eaf1; line-height: 1.6; }
  .interim { color: #ff4b4b; } 
  .placeholder { color: #555; font-size: 18px; font-style: italic; }
  hr.history-divider { border: 0; border-top: 1px dashed #444; margin: 15px 0; }
</style>
</head>
<body>

<div class="container">
  <div class="controls-container">
    <div class="control-box">
        <div class="control-title">🌍 ทิศทางการแปล</div>
        <div class="lang-selector">
            <label><input type="radio" name="langMode" value="th2en" checked onchange="changeLang()"> 🇹🇭 ไทย ➡️ 🇬🇧 อังกฤษ</label>
            <label><input type="radio" name="langMode" value="en2th" onchange="changeLang()"> 🇬🇧 อังกฤษ ➡️ 🇹🇭 ไทย</label>
        </div>
    </div>
    <div class="control-box">
        <div class="control-title">⏱️ ถ้าเงียบเกินกี่วินาที ถึงจะตัดขึ้นพารากราฟใหม่?</div>
        <div class="slider-container">
            <input type="range" id="delaySlider" min="3" max="30" value="10" oninput="updateDelay()">
            <div class="slider-val"><span id="delayValue">10</span> วินาที</div>
        </div>
    </div>
  </div>

  <div class="btn-container">
      <button id="startBtn" onclick="startDictation()">🎤 กดเพื่อพูด (Live)</button>
      <button id="stopBtn" onclick="stopDictation()">⏹️ หยุด</button>
      <button id="clearBtn" onclick="clearAllHistory()" style="background-color: #333; color: #aaa; margin-left: 10px;">🗑️ ล้างหน้าจอทั้งหมด</button>
  </div>

  <div class="output-container">
    <!-- กล่องต้นฉบับ -->
    <div class="box">
      <div class="box-header">
        <div id="origTitle" class="title">🇹🇭 ต้นฉบับ (กำลังพูด):</div>
        <button id="copyOrigBtn" class="copy-btn" onclick="copyText('scrollOrig', 'copyOrigBtn')">📋 Copy</button>
      </div>
      <div class="scroll-area" id="scrollOrig">
        <div id="original" class="text"><span class="placeholder">[รอรับเสียง...]</span></div>
      </div>
    </div>
    
    <!-- กล่องคำแปล -->
    <div class="box">
      <div class="box-header">
        <div id="transTitle" class="title">🇬🇧 คำแปล (Real-time):</div>
        <button id="copyTransBtn" class="copy-btn" onclick="copyText('scrollTrans', 'copyTransBtn')">📋 Copy</button>
      </div>
      <div class="scroll-area" id="scrollTrans">
        <div id="translated" class="text"><span class="placeholder">[รอการแปล...]</span></div>
      </div>
    </div>
  </div>
</div>

<script>
  let recognition;       
  let isRecognizing = false;
  let isManualStop = false; 
  let isAutoClearing = false; 
  
  let globalFinalTranscript = ''; 
  let currentTranslatedText = ''; 
  
  let historyOrig = '';
  let historyTrans = '';
  
  let clearDelayMs = 10000; 
  let clearTimer;           
  let inactivityTimer;      
  
  let translateTimeout;     
  const DEBOUNCE_MS = 600; 
  const MAX_CHARS = 1000;  
  
  const IDLE_TIMEOUT_MS = 5 * 60 * 1000; 
  let sttLang = "th-TH";    
  let srcLang = "th";       
  let destLang = "en";      

  // 🌟 [NEW] ฟังก์ชันสำหรับปุ่ม Copy
  function copyText(elementId, btnId) {
      // ดึงข้อความดิบทั้งหมดออกมาจากกล่อง (innerText จะเปลี่ยนพวก <div> เป็นบรรทัดใหม่ให้อัตโนมัติ)
      let textToCopy = document.getElementById(elementId).innerText;
      
      // ทำความสะอาด: ลบพวกข้อความ Placeholder ทิ้งไปก่อนก๊อปปี้
      textToCopy = textToCopy.replace(/\[รอรับเสียง.*\]/g, '')
                             .replace(/\[ขึ้นพารากราฟใหม่...\]/g, '')
                             .replace(/\[ล้างข้อมูลแล้ว รอรับเสียง...\]/g, '')
                             .replace(/\[รอการแปล...\]/g, '')
                             .replace(/\[...\]/g, '')
                             .replace(/ปิดไมค์อัตโนมัติ.*/g, '')
                             .trim();

      // ใช้คำสั่งคัดลอกลง Clipboard ของเบราว์เซอร์
      navigator.clipboard.writeText(textToCopy).then(() => {
          let btn = document.getElementById(btnId);
          let originalText = btn.innerText;
          // เปลี่ยนข้อความปุ่มเพื่อให้ผู้ใช้รู้ว่าก๊อปปี้สำเร็จแล้ว
          btn.innerText = '✅ Copied!';
          btn.style.color = '#00cc66';
          btn.style.borderColor = '#00cc66';
          
          // คืนค่าปุ่มกลับเป็นเหมือนเดิมหลังจาก 2 วินาที
          setTimeout(() => { 
              btn.innerText = '📋 Copy'; 
              btn.style.color = '#a3a8b8';
              btn.style.borderColor = '#555';
          }, 2000);
      }).catch(err => {
          console.error('Failed to copy text: ', err);
          alert("ไม่สามารถ Copy ได้ กรุณาลองใหม่อีกครั้ง");
      });
  }

  function scrollToBottom(elementId) {
      let scrollBox = document.getElementById(elementId);
      scrollBox.scrollTop = scrollBox.scrollHeight;
  }

  function updateDelay() {
      let val = document.getElementById('delaySlider').value;
      document.getElementById('delayValue').innerText = val;
      clearDelayMs = parseInt(val) * 1000;
  }

  function triggerArchive() {
      if (globalFinalTranscript.trim() !== "") {
          historyOrig += "<div>" + globalFinalTranscript + "</div><hr class='history-divider'>";
          historyTrans += "<div>" + currentTranslatedText + "</div><hr class='history-divider'>";
      }
      globalFinalTranscript = ''; 
      currentTranslatedText = '';
      document.getElementById('original').innerHTML = historyOrig + "<span class='placeholder'>[รอรับเสียงพารากราฟใหม่...]</span>";
      document.getElementById('translated').innerHTML = historyTrans + "<span class='placeholder'>[...]</span>";
      scrollToBottom('scrollOrig');
      scrollToBottom('scrollTrans');

      if (isRecognizing) {
          isAutoClearing = true;
          recognition.stop(); 
      }
  }

  function clearAllHistory() {
      historyOrig = '';
      historyTrans = '';
      globalFinalTranscript = '';
      currentTranslatedText = '';
      document.getElementById('original').innerHTML = "<span class='placeholder'>[ล้างข้อมูลแล้ว รอรับเสียง...]</span>";
      document.getElementById('translated').innerHTML = "<span class='placeholder'>[...]</span>";
  }

  function resetClearTimer() {
      clearTimeout(clearTimer);
      clearTimer = setTimeout(triggerArchive, clearDelayMs);
  }

  function resetInactivityTimer() {
    clearTimeout(inactivityTimer); 
    if (isRecognizing) {
      inactivityTimer = setTimeout(() => {
        isManualStop = true; 
        recognition.stop();
        document.getElementById('original').innerHTML = historyOrig + "<span style='font-size:16px; color:#ff4b4b;'><i>ปิดไมค์อัตโนมัติ (ลืมปิดเกิน 5 นาที)</i></span>";
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
      resetInactivityTimer(); 
    };

    recognition.onend = function() {
      isRecognizing = false;
      clearTimeout(inactivityTimer);
      clearTimeout(clearTimer);
      if (isAutoClearing) { isAutoClearing = false; try { recognition.start(); } catch(e){} return; }
      if (!isManualStop) { try { recognition.start(); return; } catch(e) {} }
      document.getElementById('startBtn').innerText = "🎤 กดเพื่อพูด (Live)";
      document.getElementById('startBtn').style.backgroundColor = "#ff4b4b";
    };

    recognition.onresult = function(event) {
      resetInactivityTimer(); 
      clearTimeout(clearTimer); 
      let interim_transcript = '';
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) { globalFinalTranscript += event.results[i][0].transcript + ' '; } 
        else { interim_transcript += event.results[i][0].transcript; }
      }

      let currentText = globalFinalTranscript + interim_transcript;
      if (currentText.length > MAX_CHARS) { triggerArchive(); return; }

      document.getElementById('original').innerHTML = historyOrig + globalFinalTranscript + '<span class="interim">' + interim_transcript + '</span>';
      scrollToBottom('scrollOrig');

      if (currentText.trim() !== "") {
        clearTimeout(translateTimeout);
        translateTimeout = setTimeout(() => { translateText(currentText, srcLang, destLang); }, DEBOUNCE_MS); 
        resetClearTimer(); 
      }
    };
  }

  function startDictation() {
    if (!isRecognizing) { isManualStop = false; isAutoClearing = false; recognition.lang = sttLang; recognition.start(); }
  }

  function stopDictation() {
    if (isRecognizing) { isManualStop = true; recognition.stop(); setTimeout(triggerArchive, 1000); }
  }
  
  function changeLang() {
    let mode = document.querySelector('input[name="langMode"]:checked').value;
    if (mode === "th2en") {
        sttLang = "th-TH"; srcLang = "th"; destLang = "en";
        document.getElementById('origTitle').innerText = "🇹🇭 ต้นฉบับ (กำลังพูด):";
        document.getElementById('transTitle').innerText = "🇬🇧 คำแปล (Real-time):";
    } else {
        sttLang = "en-US"; srcLang = "en"; destLang = "th";
        document.getElementById('origTitle').innerText = "🇬🇧 ต้นฉบับ (กำลังพูด):";
        document.getElementById('transTitle').innerText = "🇹🇭 คำแปล (Real-time):";
    }
    if(isRecognizing) { isManualStop = true; stopDictation(); }
  }

  function translateText(text, src, dest) {
    let url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=${src}&tl=${dest}&dt=t&q=${encodeURI(text)}`;
    fetch(url)
      .then(response => response.json())
      .then(data => {
        let translated_text = '';
        for (let i = 0; i < data[0].length; i++) { translated_text += data[0][i][0]; }
        currentTranslatedText = translated_text; 
        document.getElementById('translated').innerHTML = historyTrans + currentTranslatedText;
        scrollToBottom('scrollTrans');
      })
      .catch(err => console.error("Translate Error:", err)); 
  }
</script>
</body>
</html>
"""

components.html(custom_html, height=650)
st.markdown("---")
st.markdown("<p style='text-align: center; color: #a3a8b8; font-size: 14px;'>Developed by <b>Joopiest Udomsaph</b></p>", unsafe_allow_html=True)