import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="True Real-time Translator", layout="wide")
st.title("⚡ True Real-time Translator (3-Language Edition)")
st.markdown("ระบบแปลภาษาด่วนแบบ Real-time รองรับ ไทย, อังกฤษ, และเกาหลี")

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
  .lang-selector { display: flex; gap: 20px; }
  .lang-selector label { font-size: 16px; cursor: pointer; color: #e6eaf1; }
  .slider-container { display: flex; align-items: center; gap: 15px; width: 90%; }
  input[type=range] { flex: 1; accent-color: #ff4b4b; cursor: pointer; }
  .slider-val { font-size: 16px; color: #e6eaf1; min-width: 80px; }
  .btn-container { text-align: center; margin-bottom: 20px; }
  button { padding: 12px 24px; font-size: 16px; font-weight: bold; border: none; border-radius: 8px; cursor: pointer; transition: 0.2s; }
  #startBtn { background-color: #ff4b4b; color: white; margin-right: 10px; }
  #stopBtn { background-color: #444; color: white; }
  
  .output-container { display: flex; gap: 15px; }
  .box { flex: 1; padding: 15px; border-radius: 8px; background: #1e2127; border: 1px solid #333; display: flex; flex-direction: column; height: 350px; box-sizing: border-box; }
  
  .box-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #333; padding-bottom: 10px; margin-bottom: 15px; flex-shrink: 0; }
  .title { font-weight: bold; color: #a3a8b8; font-size: 15px; margin: 0; }
  .copy-btn { padding: 5px 10px; font-size: 12px; font-weight: normal; background-color: transparent; color: #a3a8b8; border: 1px solid #555; border-radius: 6px; cursor: pointer; transition: 0.2s; }
  .copy-btn:hover { background-color: #333; color: #fff; }

  .scroll-area { flex: 1; overflow-y: scroll; padding-right: 10px; }
  .scroll-area::-webkit-scrollbar { width: 8px; }
  .scroll-area::-webkit-scrollbar-track { background: #1e2127; border-radius: 8px; }
  .scroll-area::-webkit-scrollbar-thumb { background: #555; border-radius: 8px; }
  .scroll-area::-webkit-scrollbar-thumb:hover { background: #777; }
  
  .text { font-size: 20px; color: #e6eaf1; line-height: 1.6; }
  .interim { color: #ff4b4b; } 
  .placeholder { color: #555; font-size: 16px; font-style: italic; }
  hr.history-divider { border: 0; border-top: 1px dashed #444; margin: 15px 0; }
</style>
</head>
<body>

<div class="container">
  <div class="controls-container">
    <div class="control-box">
        <div class="control-title">🎙️ เลือกภาษาต้นฉบับ (คนพูด)</div>
        <div class="lang-selector">
            <label><input type="radio" name="langMode" value="th" checked onchange="changeLang()"> 🇹🇭 ไทย</label>
            <label><input type="radio" name="langMode" value="en" onchange="changeLang()"> 🇬🇧 อังกฤษ</label>
            <label><input type="radio" name="langMode" value="ko" onchange="changeLang()"> 🇰🇷 เกาหลี</label>
        </div>
    </div>
    <div class="control-box">
        <div class="control-title">⏱️ เวลาหน่วงตัดพารากราฟ (วินาที)</div>
        <div class="slider-container">
            <input type="range" id="delaySlider" min="3" max="30" value="10" oninput="updateDelay()">
            <div class="slider-val"><span id="delayValue">10</span> วิ</div>
        </div>
    </div>
  </div>

  <div class="btn-container">
      <button id="startBtn" onclick="startDictation()">🎤 กดเพื่อพูด (Live)</button>
      <button id="stopBtn" onclick="stopDictation()">⏹️ หยุด</button>
      <button id="clearBtn" onclick="clearAllHistory()" style="background-color: #333; color: #aaa; margin-left: 10px;">🗑️ ล้างทั้งหมด</button>
  </div>

  <div class="output-container">
    <div class="box">
      <div class="box-header">
        <div id="origTitle" class="title">🇹🇭 ต้นฉบับ (ไทย):</div>
        <button id="copyOrigBtn" class="copy-btn" onclick="copyText('scrollOrig', 'copyOrigBtn')">📋 Copy</button>
      </div>
      <div class="scroll-area" id="scrollOrig">
        <div id="original" class="text"><span class="placeholder">[รอรับเสียง...]</span></div>
      </div>
    </div>
    
    <div class="box">
      <div class="box-header">
        <div id="trans1Title" class="title">🇬🇧 แปลเป็น อังกฤษ:</div>
        <button id="copyTrans1Btn" class="copy-btn" onclick="copyText('scrollTrans1', 'copyTrans1Btn')">📋 Copy</button>
      </div>
      <div class="scroll-area" id="scrollTrans1">
        <div id="translated1" class="text"><span class="placeholder">[รอการแปล...]</span></div>
      </div>
    </div>

    <div class="box">
      <div class="box-header">
        <div id="trans2Title" class="title">🇰🇷 แปลเป็น เกาหลี:</div>
        <button id="copyTrans2Btn" class="copy-btn" onclick="copyText('scrollTrans2', 'copyTrans2Btn')">📋 Copy</button>
      </div>
      <div class="scroll-area" id="scrollTrans2">
        <div id="translated2" class="text"><span class="placeholder">[รอการแปล...]</span></div>
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
  let currentTranslatedText1 = ''; 
  let currentTranslatedText2 = ''; 
  
  let historyOrig = '';
  let historyTrans1 = '';
  let historyTrans2 = '';
  
  let clearDelayMs = 10000; 
  let clearTimer;           
  let inactivityTimer;      
  
  let translateTimeout;     
  // 🌟 [NEW] เพิ่มเวลาหน่วงก่อนเริ่มแปลเป็น 1 วินาที (ใจเย็นขึ้น)
  const DEBOUNCE_MS = 1000; 
  const MAX_CHARS = 1000;  
  
  const IDLE_TIMEOUT_MS = 5 * 60 * 1000; 
  
  let sttLang = "th-TH";    
  let srcLang = "th";       
  let destLang1 = "en";      
  let destLang2 = "ko";      

  function copyText(elementId, btnId) {
      let textToCopy = document.getElementById(elementId).innerText;
      textToCopy = textToCopy.replace(/\[รอรับเสียง.*\]/g, '')
                             .replace(/\[ขึ้นพารากราฟใหม่...\]/g, '')
                             .replace(/\[ล้างข้อมูลแล้ว รอรับเสียง...\]/g, '')
                             .replace(/\[รอการแปล...\]/g, '')
                             .replace(/\[...\]/g, '')
                             .replace(/ปิดไมค์อัตโนมัติ.*/g, '')
                             .trim();

      navigator.clipboard.writeText(textToCopy).then(() => {
          let btn = document.getElementById(btnId);
          btn.innerText = '✅ Copied!';
          btn.style.color = '#00cc66';
          btn.style.borderColor = '#00cc66';
          setTimeout(() => { 
              btn.innerText = '📋 Copy'; 
              btn.style.color = '#a3a8b8';
              btn.style.borderColor = '#555';
          }, 2000);
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
          historyTrans1 += "<div>" + currentTranslatedText1 + "</div><hr class='history-divider'>";
          historyTrans2 += "<div>" + currentTranslatedText2 + "</div><hr class='history-divider'>";
      }
      globalFinalTranscript = ''; 
      currentTranslatedText1 = '';
      currentTranslatedText2 = '';
      
      document.getElementById('original').innerHTML = historyOrig + "<span class='placeholder'>[รอรับเสียงพารากราฟใหม่...]</span>";
      document.getElementById('translated1').innerHTML = historyTrans1 + "<span class='placeholder'>[...]</span>";
      document.getElementById('translated2').innerHTML = historyTrans2 + "<span class='placeholder'>[...]</span>";
      
      scrollToBottom('scrollOrig'); scrollToBottom('scrollTrans1'); scrollToBottom('scrollTrans2');

      if (isRecognizing) {
          isAutoClearing = true;
          recognition.stop(); 
      }
  }

  function clearAllHistory() {
      historyOrig = ''; historyTrans1 = ''; historyTrans2 = '';
      globalFinalTranscript = ''; currentTranslatedText1 = ''; currentTranslatedText2 = '';
      document.getElementById('original').innerHTML = "<span class='placeholder'>[ล้างข้อมูลแล้ว รอรับเสียง...]</span>";
      document.getElementById('translated1').innerHTML = "<span class='placeholder'>[...]</span>";
      document.getElementById('translated2').innerHTML = "<span class='placeholder'>[...]</span>";
  }

  function resetClearTimer() {
      clearTimeout(clearTimer);
      clearTimer = setTimeout(triggerArchive, clearDelayMs);
  }

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
      clearTimeout(inactivityTimer); clearTimeout(clearTimer);
      if (isAutoClearing) { isAutoClearing = false; try { recognition.start(); } catch(e){} return; }
      if (!isManualStop) { try { recognition.start(); return; } catch(e) {} }
      document.getElementById('startBtn').innerText = "🎤 กดเพื่อพูด (Live)";
      document.getElementById('startBtn').style.backgroundColor = "#ff4b4b";
    };

    recognition.onresult = function(event) {
      resetInactivityTimer(); clearTimeout(clearTimer); 
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
        translateTimeout = setTimeout(() => { 
            translateText(currentText, srcLang, destLang1, destLang2); 
        }, DEBOUNCE_MS); 
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
    if (mode === "th") {
        sttLang = "th-TH"; srcLang = "th"; destLang1 = "en"; destLang2 = "ko";
        document.getElementById('origTitle').innerText = "🇹🇭 ต้นฉบับ (ไทย):";
        document.getElementById('trans1Title').innerText = "🇬🇧 แปลเป็น อังกฤษ:";
        document.getElementById('trans2Title').innerText = "🇰🇷 แปลเป็น เกาหลี:";
    } else if (mode === "en") {
        sttLang = "en-US"; srcLang = "en"; destLang1 = "th"; destLang2 = "ko";
        document.getElementById('origTitle').innerText = "🇬🇧 ต้นฉบับ (อังกฤษ):";
        document.getElementById('trans1Title').innerText = "🇹🇭 แปลเป็น ไทย:";
        document.getElementById('trans2Title').innerText = "🇰🇷 แปลเป็น เกาหลี:";
    } else if (mode === "ko") {
        sttLang = "ko-KR"; srcLang = "ko"; destLang1 = "th"; destLang2 = "en";
        document.getElementById('origTitle').innerText = "🇰🇷 ต้นฉบับ (เกาหลี):";
        document.getElementById('trans1Title').innerText = "🇹🇭 แปลเป็น ไทย:";
        document.getElementById('trans2Title').innerText = "🇬🇧 แปลเป็น อังกฤษ:";
    }
    if(isRecognizing) { isManualStop = true; stopDictation(); }
  }

  // 🌟 [NEW] ฟังก์ชันแปลภาษาแบบเข้าคิว (หลบ Google Rate Limit)
  function translateText(text, src, target1, target2) {
    let url1 = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=${src}&tl=${target1}&dt=t&q=${encodeURI(text)}`;
    let url2 = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=${src}&tl=${target2}&dt=t&q=${encodeURI(text)}`;
    
    // คิวที่ 1: ยิงภาษาแรกทันที
    fetch(url1).then(res => res.json()).then(data => {
        let translated_text = '';
        for (let i = 0; i < data[0].length; i++) translated_text += data[0][i][0];
        currentTranslatedText1 = translated_text; 
        document.getElementById('translated1').innerHTML = historyTrans1 + currentTranslatedText1;
        scrollToBottom('scrollTrans1');
    }).catch(err => console.error("Error 1:", err)); 

    // คิวที่ 2: หน่วงเวลา 300ms ค่อยยิงภาษาที่สองตามไป
    setTimeout(() => {
        fetch(url2).then(res => res.json()).then(data => {
            let translated_text = '';
            for (let i = 0; i < data[0].length; i++) translated_text += data[0][i][0];
            currentTranslatedText2 = translated_text; 
            document.getElementById('translated2').innerHTML = historyTrans2 + currentTranslatedText2;
            scrollToBottom('scrollTrans2');
        }).catch(err => console.error("Error 2:", err)); 
    }, 300);
  }
</script>
</body>
</html>
"""

components.html(custom_html, height=650)
st.markdown("---")
st.markdown("<p style='text-align: center; color: #a3a8b8; font-size: 14px;'>Developed by <b>Joopiest Udomsaph</b></p>", unsafe_allow_html=True)