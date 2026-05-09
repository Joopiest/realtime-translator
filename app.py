import streamlit as st
import streamlit.components.v1 as components

# ตั้งค่าหน้าจอ
st.set_page_config(page_title="Turbo Real-time Translator", layout="wide")
st.title("⚡ Turbo Real-time Translator (2026 Edition)")

# 🌟 Sidebar สำหรับตั้งค่า
with st.sidebar:
    st.header("⚙️ API Configuration")
    api_key = st.text_input("OpenRouter API Key", type="password")
    
    # รวมรายชื่อ Model ที่จู๊ปคอนเฟิร์มว่า Work และตัวที่แนะนำเพิ่ม
    model_choice = st.selectbox("Select Model", [
        "google/gemini-3.1-flash-lite-preview",
        "google/gemini-2.5-flash-lite", 
        "google/gemini-3.1-pro-preview",
        "qwen/qwen-3-8b-instruct" # เพิ่ม Qwen3-8B ตามที่คุยกันครับ
    ], index=0)
    
    st.info("💡 แนะนำ: Gemini 3.1 Flash Lite สำหรับความเร็วสูงสุด")

# 🛑 ดักจับ API Key (ไม้ตายแก้บั๊ก Streamlit)
if not api_key:
    st.warning("👈 กรุณาใส่ API Key ใน Sidebar แล้วกด Enter ก่อนครับ")
    st.stop()

st.success(f"✅ เชื่อมต่อ {model_choice} พร้อมแปลแบบ Turbo!")

# 🌟 HTML / CSS / JavaScript
html_template = """
<!DOCTYPE html>
<html>
<head>
<style>
  body { font-family: 'Segoe UI', Tahoma, sans-serif; color: #fff; background-color: #0e1117; margin: 0; }
  .container { padding: 15px; }
  .controls-container { display: flex; gap: 15px; margin-bottom: 20px; }
  .control-box { flex: 1; background: #1e2127; padding: 15px; border-radius: 10px; border: 1px solid #333; }
  .control-title { font-size: 13px; color: #a3a8b8; margin-bottom: 10px; font-weight: bold; text-align: center; }
  
  select { padding: 10px; border-radius: 8px; background-color: #2b2f36; color: #e6eaf1; border: 1px solid #555; font-size: 15px; width: 100%; cursor: pointer; }
  
  .btn-group { display: flex; justify-content: center; gap: 15px; margin-bottom: 25px; }
  button { padding: 12px 28px; font-size: 16px; font-weight: bold; border: none; border-radius: 8px; cursor: pointer; transition: 0.3s; }
  #startBtn { background-color: #ff4b4b; color: white; }
  #clearBtn { background-color: #444; color: #eee; border: 1px solid #666; }
  #clearBtn:hover { background-color: #555; }
  
  .output-container { display: flex; gap: 20px; }
  .box { flex: 1; padding: 20px; border-radius: 12px; background: #1e2127; border: 1px solid #333; height: 420px; display: flex; flex-direction: column; box-sizing: border-box; }
  .box-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #333; padding-bottom: 12px; margin-bottom: 15px; }
  .title { font-weight: bold; color: #a3a8b8; font-size: 16px; }
  
  .scroll-area { flex: 1; overflow-y: auto; padding-right: 10px; }
  .scroll-area::-webkit-scrollbar { width: 6px; }
  .scroll-area::-webkit-scrollbar-thumb { background: #444; border-radius: 10px; }
  
  .text { font-size: 24px; color: #e6eaf1; line-height: 1.5; }
  .interim { color: #ff4b4b; font-style: italic; } 
  hr { border: 0; border-top: 1px dashed #444; margin: 15px 0; }
  
  #sysStatus { font-size: 13px; color: #00ffcc; text-align: right; margin-top: 12px; font-family: monospace; }
  #langWarning { color: #ff4b4b; text-align: center; margin-bottom: 10px; font-weight: bold; display: none; }
</style>
</head>
<body>

<div class="container">
  <div class="controls-container">
    <div class="control-box">
        <div class="control-title">🎙️ ต้นทาง (From)</div>
        <select id="srcLang" onchange="updateConfig()">
            <option value="th-TH|Thai" selected>🇹🇭 ไทย</option>
            <option value="en-US|English">🇬🇧 อังกฤษ</option>
            <option value="ko-KR|Korean">🇰🇷 เกาหลี</option>
        </select>
    </div>
    <div class="control-box">
        <div class="control-title">🌐 ปลายทาง (To)</div>
        <select id="destLang" onchange="updateConfig()">
            <option value="English" selected>🇬🇧 อังกฤษ</option>
            <option value="Thai">🇹🇭 ไทย</option>
            <option value="Korean">🇰🇷 เกาหลี</option>
        </select>
    </div>
  </div>

  <div id="langWarning">⚠️ คู่ภาษาซ้ำกัน! กรุณาเลือกภาษาที่ต่างกันครับ</div>

  <div class="btn-group">
      <button id="startBtn" onclick="toggleMic()">🎤 เริ่มรับเสียง</button>
      <button id="clearBtn" onclick="clearAll()">🗑️ ล้างข้อความทั้งหมด</button>
  </div>

  <div class="output-container">
    <div class="box">
      <div class="box-header"><div id="headOrig" class="title">🎙️ Original:</div></div>
      <div class="scroll-area" id="scrollOrig"><div id="txtOrig" class="text"></div></div>
    </div>
    
    <div class="box">
      <div class="box-header"><div id="headTrans" class="title">🌐 Translation:</div></div>
      <div class="scroll-area" id="scrollTrans"><div id="txtTrans" class="text"></div></div>
      <div id="sysStatus">System Ready</div>
    </div>
  </div>
</div>

<script>
  const API_KEY = "VAR_API_KEY";
  const MODEL_NAME = "VAR_MODEL_NAME";
  
  let recognition;
  let isListening = false;
  let finalTxt = ''; 
  let historyO = ''; 
  let historyT = '';
  let transDebounce; // สำหรับหน่วงเวลาส่งแปล

  let curSttLang = "th-TH";
  let curSrcName = "Thai";
  let curDestName = "English";

  function updateConfig() {
      const src = document.getElementById('srcLang').value.split('|');
      curSttLang = src[0]; curSrcName = src[1];
      curDestName = document.getElementById('destLang').value;
      
      const isSame = curSrcName === curDestName;
      document.getElementById('langWarning').style.display = isSame ? "block" : "none";
      document.getElementById('startBtn').disabled = isSame;
      document.getElementById('startBtn').style.opacity = isSame ? "0.3" : "1";
      
      document.getElementById('headOrig').innerText = "🎙️ Original (" + curSrcName + "):";
      document.getElementById('headTrans').innerText = "🌐 Translation (" + curDestName + "):";
      
      if(isListening) toggleMic(); 
  }

  // ✨ ฟังก์ชัน Clear All ที่จู๊ปต้องการ
  function clearAll() {
      finalTxt = ''; historyO = ''; historyT = '';
      document.getElementById('txtOrig').innerHTML = '';
      document.getElementById('txtTrans').innerHTML = '';
      document.getElementById('sysStatus').innerText = "🗑️ ล้างข้อมูลเรียบร้อย";
  }

  function toggleMic() {
      if (isListening) {
          isListening = false; recognition.stop();
          document.getElementById('startBtn').innerText = "🎤 เริ่มรับเสียง";
          document.getElementById('startBtn').style.background = "#ff4b4b";
      } else {
          recognition = new webkitSpeechRecognition();
          recognition.continuous = true;
          recognition.interimResults = true;
          recognition.lang = curSttLang;

          recognition.onresult = (event) => {
              let interim = '';
              let hasNewFinal = false;
              for (let i = event.resultIndex; i < event.results.length; ++i) {
                  if (event.results[i].isFinal) {
                      finalTxt += event.results[i][0].transcript + ' ';
                      hasNewFinal = true;
                  } else {
                      interim += event.results[i][0].transcript;
                  }
              }

              document.getElementById('txtOrig').innerHTML = historyO + finalTxt + '<span class="interim">' + interim + '</span>';
              document.getElementById('scrollOrig').scrollTop = document.getElementById('scrollOrig').scrollHeight;

              // 🚀 ปรับ Debounce ให้ไวขึ้นเป็น 600ms เพื่อความ Turbo
              if (hasNewFinal) {
                  clearTimeout(transDebounce);
                  document.getElementById('sysStatus').innerText = "⏳ รอจังหวะนิ่ง...";
                  transDebounce = setTimeout(() => {
                      callTranslate(finalTxt);
                  }, 600); 
              }
          };

          recognition.onend = () => { if (isListening) recognition.start(); };
          recognition.start();
          isListening = true;
          document.getElementById('startBtn').innerText = "⏹️ หยุดรับเสียง";
          document.getElementById('startBtn').style.background = "#444";
      }
  }

  async function callTranslate(text) {
      if (!text.trim()) return;
      document.getElementById('sysStatus').innerText = "🔄 กำลังแปล...";
      
      try {
          const resp = await fetch("https://openrouter.ai/api/v1/chat/completions", {
              method: "POST",
              headers: { 
                  "Authorization": "Bearer " + API_KEY, 
                  "Content-Type": "application/json" 
              },
              body: JSON.stringify({
                  "model": MODEL_NAME,
                  "messages": [
                      // System Prompt แบบ Turbo
                      { "role": "system", "content": "Translate " + curSrcName + " to " + curDestName + ". Output only translated text." },
                      { "role": "user", "content": text }
                  ],
                  "temperature": 0, // ปรับเป็น 0 เพื่อความเร็วสูงสุด
                  "max_tokens": 150
              })
          });
          const data = await resp.json();
          if (data.choices) {
              const translated = data.choices[0].message.content.trim();
              document.getElementById('txtTrans').innerHTML = historyT + translated;
              document.getElementById('sysStatus').innerText = "✅ " + new Date().toLocaleTimeString();
              document.getElementById('scrollTrans').scrollTop = document.getElementById('scrollTrans').scrollHeight;
          }
      } catch (e) {
          document.getElementById('sysStatus').innerText = "❌ Error: " + e.message;
      }
  }
</script>
</body>
</html>
"""

# Inject ค่าและแสดงผล
final_html = html_template.replace("VAR_API_KEY", api_key).replace("VAR_MODEL_NAME", model_choice)
components.html(final_html, height=750)