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
  .title { font-weight: bold; color: #a3a8b8; margin-bottom: 15px; font-size: 16px; border-bottom: 1px solid #333; padding-bottom: 10px; flex-shrink: 0; }
  .scroll-area { flex: 1; overflow-y: scroll; padding-right: 10px; }
  .scroll-area::-webkit-scrollbar { width: 8px; }
  .scroll-area::-webkit-scrollbar-track { background: #1e2127; border-radius: 8px; }
  .scroll-area::-webkit-scrollbar-thumb { background: #555; border-radius: 8px; }
  .scroll-area::-webkit-scrollbar-thumb:hover { background: #777; }
  .text { font-size: 22px; color: #e6eaf1; line-height: 1.6; }
  .interim { color: #ff4b4b; } 
  .placeholder { color: #555; font-size: 18px; font-style: italic; }
  /* เส้นคั่นระหว่างพารากราฟประวัติ */
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
      <!-- เพิ่มปุ่มล้างหน้าจอแบบ Manual เผื่อจู๊ปอยากลบประวัติเอง -->
      <button id="clearBtn" onclick="clearAllHistory()" style="background-color: #333; color: #aaa; margin-left: 10px;">🗑️ ล้างหน้าจอทั้งหมด</button>
  </div>

  <div class="output-container">
    <div class="box">
      <div id="origTitle" class="title">🇹🇭 ต้นฉบับ (กำลังพูด):</div>
      <div class="scroll-area" id="scrollOrig">
        <div id="original" class="text"><span class="placeholder">[รอรับเสียง...]</span></div>
      </div>
    </div>
    <div class="box">
      <div id="transTitle" class="title">🇬🇧 คำแปล (Real-time):</div>
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
  let currentTranslatedText = ''; // เก็บคำแปลล่าสุดก่อนถูกตัดพารากราฟ
  
  // 🌟 [NEW] ตัวแปรคลังสมบัติ เก็บประวัติข้อความทั้งหมด
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

  function scrollToBottom(elementId) {
      let scrollBox = document.getElementById(elementId);
      scrollBox.scrollTop = scrollBox.scrollHeight;
  }

  function updateDelay() {
      let val = document.getElementById('delaySlider').value;
      document.getElementById('delayValue').innerText = val;
      clearDelayMs = parseInt(val) * 1000;
  }

  // 🌟 [NEW] ฟังก์ชันสำหรับเก็บข้อความเข้าคลังประวัติ แทนการลบทิ้ง
  function triggerArchive() {
      if (globalFinalTranscript.trim() !== "") {
          // ดันข้อความเก่าเข้าคลัง พร้อมขีดเส้นประคั่น
          historyOrig += "<div>" + globalFinalTranscript + "</div><hr class='history-divider'>";
          historyTrans += "<div>" + currentTranslatedText + "</div><hr class='history-divider'>";
      }

      // เคลียร์เฉพาะ "ความจำระยะสั้น" เพื่อกัน Google บล็อก
      globalFinalTranscript = ''; 
      currentTranslatedText = '';

      // อัปเดตหน้าจอ โดยเอาประวัติมารวมกับ Placeholder
      document.getElementById('original').innerHTML = historyOrig + "<span class='placeholder'>[รอรับเสียงพารากราฟใหม่...]</span>";
      document.getElementById('translated').innerHTML = historyTrans + "<span class='placeholder'>[...]</span>";
      
      scrollToBottom('scrollOrig');
      scrollToBottom('scrollTrans');

      if (isRecognizing) {
          isAutoClearing = true;
          recognition.stop(); // บังคับไมค์รีสตาร์ทเพื่อเคลียร์ Buffer
      }
  }

  // ปุ่มสำหรับล้างประวัติทั้งหมด (กรณีอยากเริ่มพูดเรื่องใหม่หมดเลย)
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
      
      if (isAutoClearing) { 
          isAutoClearing = false;
          try { recognition.start(); } catch(e){}
          return;
      }

      if (!isManualStop) { 
          try { recognition.start(); return; } catch(e) {}
      }

      document.getElementById('startBtn').innerText = "🎤 กดเพื่อพูด (Live)";
      document.getElementById('startBtn').style.backgroundColor = "#ff4b4b";
    };

    recognition.onresult = function(event) {
      resetInactivityTimer(); 
      clearTimeout(clearTimer); 
      
      let interim_transcript = '';
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          globalFinalTranscript += event.results[i][0].transcript + ' ';
        } else {
          interim_transcript += event.results[i][0].transcript;
        }
      }

      let currentText = globalFinalTranscript + interim_transcript;
      
      if (currentText.length > MAX_CHARS) {
          triggerArchive();
          return;
      }

      // แสดงผล = ประวัติเก่า + ข้อความที่เพิ่งพูดจบ + คำที่กำลังเดา
      document.getElementById('original').innerHTML = 
        historyOrig + globalFinalTranscript + '<span class="interim">' + interim_transcript + '</span>';
      scrollToBottom('scrollOrig');

      if (currentText.trim() !== "") {
        clearTimeout(translateTimeout);
        translateTimeout = setTimeout(() => {
            translateText(currentText, srcLang, destLang);
        }, DEBOUNCE_MS); 
        
        resetClearTimer(); 
      }
    };
  }

  function startDictation() {
    if (!isRecognizing) { isManualStop = false; isAutoClearing = false; recognition.lang = sttLang; recognition.start(); }
  }

  function stopDictation() {
    if (isRecognizing) { 
        isManualStop = true; 
        recognition.stop(); 
        // เมื่อกดหยุด ให้ดันข้อความสุดท้ายเข้าคลังประวัติทันที
        setTimeout(triggerArchive, 1000); 
    }
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
        
        // แสดงผล = ประวัติเก่า + คำแปลชุดปัจจุบัน
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