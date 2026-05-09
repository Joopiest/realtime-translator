import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="True Real-time Translator", layout="wide")
st.title("⚡ True Real-time Translator (Pro Interpreter Edition)")
st.markdown("ระบบแปลภาษาแบบ Sentence-by-Sentence ลื่นไหล ไม่โดนบล็อก (รองรับ ไทย, อังกฤษ, เกาหลี)")

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
  
  .lang-dropdown-container { display: flex; align-items: center; gap: 15px; }
  select { padding: 8px 12px; border-radius: 6px; background-color: #2b2f36; color: #e6eaf1; border: 1px solid #555; font-size: 16px; cursor: pointer; outline: none; transition: 0.2s; }
  select:hover { border-color: #ff4b4b; }
  
  .slider-container { display: flex; align-items: center; gap: 15px; width: 90%; }
  input[type=range] { flex: 1; accent-color: #ff4b4b; cursor: pointer; }
  .slider-val { font-size: 16px; color: #e6eaf1; min-width: 80px; }
  .btn-container { text-align: center; margin-bottom: 20px; }
  button { padding: 12px 24px; font-size: 16px; font-weight: bold; border: none; border-radius: 8px; cursor: pointer; transition: 0.2s; }
  #startBtn { background-color: #ff4b4b; color: white; margin-right: 10px; }
  #stopBtn { background-color: #444; color: white; }
  
  .output-container { display: flex; gap: 20px; }
  .box { flex: 1; padding: 20px; border-radius: 8px; background: #1e2127; border: 1px solid #333; display: flex; flex-direction: column; height: 350px; box-sizing: border-box; }
  
  .box-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #333; padding-bottom: 10px; margin-bottom: 15px; flex-shrink: 0; }
  .title { font-weight: bold; color: #a3a8b8; font-size: 16px; margin: 0; }
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
        <div class="control-title">🌍 เลือกคู่ภาษา (Pair)</div>
        <div class="lang-dropdown-container">
            <select id="srcLangSelect" onchange="changeLang()">
                <option value="th" selected>🇹🇭 ไทย</option>
                <option value="en">🇬🇧 อังกฤษ</option>
                <option value="ko">🇰🇷 เกาหลี</option>
            </select>
            <span style="font-size: 20px;">➡️</span>
            <select id="destLangSelect" onchange="changeLang()">
                <option value="en" selected>🇬🇧 อังกฤษ</option>
                <option value="th">🇹🇭 ไทย</option>
                <option value="ko">🇰🇷 เกาหลี</option>
            </select>
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
    <div class="box">
      <div class="box-header">
        <div id="origTitle" class="title">🎙️ ต้นฉบับ (🇹🇭 ไทย):</div>
        <button id="copyOrigBtn" class="copy-btn" onclick="copyText('scrollOrig', 'copyOrigBtn')">📋 Copy</button>
      </div>
      <div class="scroll-area" id="scrollOrig">
        <div id="original" class="text"><span class="placeholder">[รอรับเสียง...]</span></div>
      </div>
    </div>
    
    <div class="box">
      <div class="box-header">
        <div id="transTitle" class="title">🌐 คำแปล (🇬🇧 อังกฤษ):</div>
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
  
  const MAX_CHARS = 1000;  
  const IDLE_TIMEOUT_MS = 5 * 60 * 1000; 
  
  let sttLang = "th-TH";    
  let srcLang = "th";       
  let destLang = "en";      

  function changeLang() {
      let src = document.getElementById('srcLangSelect').value;
      let dest = document.getElementById('destLangSelect').value;

      if (src === dest) {
          if (src === 'th') document.getElementById('destLangSelect').value = 'en';
          else if (src === 'en') document.getElementById('destLangSelect').value = 'th';
          else document.getElementById('destLangSelect').value = 'th';
          dest = document.getElementById('destLangSelect').value;
      }

      if (src === 'th') sttLang = "th-TH";
      else if (src === 'en') sttLang = "en-US";
      else if (src === 'ko') sttLang = "ko-KR";

      srcLang = src;
      destLang = dest;

      let titles = { 'th': '🇹🇭 ไทย', 'en': '🇬🇧 อังกฤษ', 'ko': '🇰🇷 เกาหลี' };
      document.getElementById('origTitle').innerText = `🎙️ ต้นฉบับ (${titles[src]}):`;
      document.getElementById('transTitle').innerText = `🌐 คำแปล (${titles[dest]}):`;

      if(isRecognizing) { isManualStop = true; stopDictation(); }
  }

  function copyText(elementId, btnId) {
      let textToCopy = document.getElementById(elementId).innerText;
      textToCopy = textToCopy.replace(/\[รอรับเสียง.*\]/g, '').replace(/\[ขึ้นพารากราฟใหม่...\]/g, '').replace(/\[ล้างข้อมูลแล้ว รอรับเสียง...\]/g, '').replace(/\[รอการแปล...\]/g, '').replace(/\[...\]/g, '').replace(/ปิดไมค์อัตโนมัติ.*/g, '').trim();

      navigator.clipboard.writeText(textToCopy).then(() => {
          let btn = document.getElementById(btnId);
          btn.innerText = '✅ Copied!'; btn.style.color = '#00cc66'; btn.style.borderColor = '#00cc66';
          setTimeout(() => { btn.innerText = '📋 Copy'; btn.style.color = '#a3a8b8'; btn.style.borderColor = '#555'; }, 2000);
      }).catch(err => { alert("ไม่สามารถ Copy ได้"); });
  }

  function scrollToBottom(elementId) {
      let scrollBox = document.getElementById(elementId);
      scrollBox.scrollTop = scrollBox.scrollHeight;
  }

  function updateDelay() {
      clearDelayMs = parseInt(document.getElementById('delaySlider').value) * 1000;
      document.getElementById('delayValue').innerText = document.getElementById('delaySlider').value;
  }

  function triggerArchive() {
      if (globalFinalTranscript.trim() !== "") {
          historyOrig += "<div>" + globalFinalTranscript + "</div><hr class='history-divider'>";
          historyTrans += "<div>" + currentTranslatedText + "</div><hr class='history-divider'>";
      }
      globalFinalTranscript = ''; currentTranslatedText = '';
      document.getElementById('original').innerHTML = historyOrig + "<span class='placeholder'>[รอรับเสียงพารากราฟใหม่...]</span>";
      document.getElementById('translated').innerHTML = historyTrans + "<span class='placeholder'>[...]</span>";
      scrollToBottom('scrollOrig'); scrollToBottom('scrollTrans');
      if (isRecognizing) { isAutoClearing = true; recognition.stop(); }
  }

  function clearAllHistory() {
      historyOrig = ''; historyTrans = ''; globalFinalTranscript = ''; currentTranslatedText = '';
      document.getElementById('original').innerHTML = "<span class='placeholder'>[ล้างข้อมูลแล้ว รอรับเสียง...]</span>";
      document.getElementById('translated').innerHTML = "<span class='placeholder'>[...]</span>";
  }

  function resetClearTimer() { clearTimeout(clearTimer); clearTimer = setTimeout(triggerArchive, clearDelayMs); }

  function resetInactivityTimer() {
    clearTimeout(inactivityTimer); 
    if (isRecognizing) {
      inactivityTimer = setTimeout(() => {
        isManualStop = true; recognition.stop();
        document.getElementById('original').innerHTML = historyOrig + "<span style='font-size:16px; color:#ff4b4b;'><i>ปิดไมค์อัตโนมัติ (ลืมปิดเกิน 5 นาที)</i></span>";
      }, IDLE_TIMEOUT_MS);
    }
  }

  if (window.hasOwnProperty('webkitSpeechRecognition')) {
    recognition = new webkitSpeechRecognition();
    recognition.continuous = true; recognition.interimResults = true; recognition.lang = sttLang;          

    recognition.onstart = function() {
      isRecognizing = true; document.getElementById('startBtn').innerText = "🟢 กำลังฟัง (พูดได้เลย)..."; document.getElementById('startBtn').style.backgroundColor = "#00cc66"; resetInactivityTimer(); 
    };

    recognition.onend = function() {
      isRecognizing = false; clearTimeout(inactivityTimer); clearTimeout(clearTimer);
      if (isAutoClearing) { isAutoClearing = false; try { recognition.start(); } catch(e){} return; }
      if (!isManualStop) { try { recognition.start(); return; } catch(e) {} }
      document.getElementById('startBtn').innerText = "🎤 กดเพื่อพูด (Live)"; document.getElementById('startBtn').style.backgroundColor = "#ff4b4b";
    };

    recognition.onresult = function(event) {
      resetInactivityTimer(); clearTimeout(clearTimer); 
      let interim_transcript = '';
      let is_new_final_added = false; // ตัวจับว่ามีประโยคใหม่ถูกยืนยันหรือยัง

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) { 
            globalFinalTranscript += event.results[i][0].transcript + ' '; 
            is_new_final_added = true; // ✔️ เจอคำที่ยืนยันแล้ว
        } 
        else { 
            interim_transcript += event.results[i][0].transcript; 
        }
      }

      if (globalFinalTranscript.length > MAX_CHARS) { triggerArchive(); return; }

      // อัปเดตกล่องซ้าย (ต้นฉบับโชว์สีแดงเหมือนเดิม)
      document.getElementById('original').innerHTML = historyOrig + globalFinalTranscript + '<span class="interim">' + interim_transcript + '</span>';
      scrollToBottom('scrollOrig');

      // 🌟 [NEW] แปลภาษาเฉพาะตอนที่ "จบประโยค" เท่านั้น! (ข้ามพวกตัวหนังสือสีแดงไปเลย)
      if (is_new_final_added && globalFinalTranscript.trim() !== "") {
          translateTextPOST(globalFinalTranscript, srcLang, destLang);
          resetClearTimer(); 
      }
    };
  }

  function startDictation() { if (!isRecognizing) { isManualStop = false; isAutoClearing = false; recognition.lang = sttLang; recognition.start(); } }
  function stopDictation() { if (isRecognizing) { isManualStop = true; recognition.stop(); setTimeout(triggerArchive, 1000); } }

  // 🌟 [NEW] ยิง API ด้วย POST Method และซ่อน Payload ไว้ใน Body (Google จับยากขึ้นมากๆ)
  function translateTextPOST(text, src, dest) {
    let url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=${src}&tl=${dest}&dt=t`;
    
    fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ q: text })
    })
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