import streamlit as st
import streamlit.components.v1 as components

# ปรับ layout เป็น "wide" เพื่อให้มีพื้นที่แนวนอนกว้างขึ้นสำหรับจัดซ้าย-ขวา
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
  
  /* สไตล์สำหรับส่วนเลือกภาษา */
  .lang-selector {
    background: #1e2127;
    padding: 15px;
    border-radius: 8px;
    border: 1px solid #333;
    margin-bottom: 20px;
    display: flex;
    justify-content: center;
    gap: 30px;
  }
  .lang-selector label {
    font-size: 16px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
    color: #e6eaf1;
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

  /* --------------------------------------------------- */
  /* สไตล์ใหม่สำหรับการจัดเลย์เอาต์แบบ ซ้าย-ขวา (Flexbox) */
  /* --------------------------------------------------- */
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
</style>
</head>
<body>

<div class="container">
  <!-- ส่วนเลือกทิศทางการแปล -->
  <div class="lang-selector">
    <label>
      <input type="radio" name="langMode" value="th2en" checked onchange="changeLang()"> 
      🇹🇭 ไทย ➡️ 🇬🇧 อังกฤษ
    </label>
    <label>
      <input type="radio" name="langMode" value="en2th" onchange="changeLang()"> 
      🇬🇧 อังกฤษ ➡️ 🇹🇭 ไทย
    </label>
  </div>

  <div class="btn-container">
      <button id="startBtn" onclick="startDictation()">🎤 กดเพื่อพูด (Live)</button>
      <button id="stopBtn" onclick="stopDictation()">⏹️ หยุด</button>
  </div>

  <!-- กล่องแสดงผลแบบซ้าย-ขวา -->
  <div class="output-container">
    <div class="box">
      <div id="origTitle" class="title">🇹🇭 ต้นฉบับ (กำลังพูด):</div>
      <div id="original" class="text">รอรับเสียง...</div>
    </div>
    <div class="box">
      <div id="transTitle" class="title">🇬🇧 คำแปล (Real-time):</div>
      <div id="translated" class="text">รอการแปล...</div>
    </div>
  </div>
</div>

<script>
  let recognition;
  let isRecognizing = false;
  let isManualStop = false; // ตัวแปรสำหรับเช็คว่าผู้ใช้กดหยุดเองหรือไม่
  
  let sttLang = "th-TH";
  let srcLang = "th";
  let destLang = "en";

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
    };

    recognition.onend = function() {
      isRecognizing = false;
      
      // ท่าไม้ตายป้องกันไมค์ดับ: ถ้าเบราว์เซอร์แอบตัดไปเอง ให้เปิดขึ้นมาใหม่ทันที!
      if (!isManualStop) {
          try {
              recognition.start();
              return; // ออกจากฟังก์ชันไปเลย
          } catch(e) {
              console.error("Auto-restart failed: ", e);
          }
      }

      // ถ้าผู้ใช้กดปุ่มหยุดเอง ค่อยเปลี่ยนปุ่มกลับเป็นสีแดง
      document.getElementById('startBtn').innerText = "🎤 กดเพื่อพูด (Live)";
      document.getElementById('startBtn').style.backgroundColor = "#ff4b4b";
    };

    recognition.onresult = function(event) {
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
      isManualStop = false; // รีเซ็ตค่าว่าไม่ได้กดหยุดเอง
      recognition.lang = sttLang;
      recognition.start();
    }
  }

  function stopDictation() {
    if (isRecognizing) {
      isManualStop = true; // บอกระบบว่าฉันตั้งใจกดหยุดเอง
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
        isManualStop = true; // บังคับหยุดก่อนเปลี่ยนภาษาเพื่อไม่ให้บั๊ก
        stopDictation();
        document.getElementById('original').innerHTML = "<span style='font-size:16px; color:#a3a8b8;'><i>ระบบหยุดฟังเพื่อเปลี่ยนภาษา... กดปุ่มพูดใหม่อีกครั้งครับ</i></span>";
        document.getElementById('translated').innerHTML = "...";
    } else {
        document.getElementById('original').innerHTML = "รอรับเสียง...";
        document.getElementById('translated').innerHTML = "รอการแปล...";
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

# เรนเดอร์ HTML ด้วยความสูง 450 เพื่อไม่ให้ทับ Credit ด้านล่าง
components.html(custom_html, height=450)

# ==========================================
# Credit Footer
# ==========================================
st.markdown("---")
st.markdown("<p style='text-align: center; color: #a3a8b8; font-size: 14px;'>Developed by <b>Joopiest Udomsaph</b></p>", unsafe_allow_html=True)