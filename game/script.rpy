# 遊戲腳本位於此檔案。

# 宣告該遊戲使用的角色。 color 參數
# 為角色的名稱著色。

# 啟用 CTC (Click to Continue) 提示
# ctc="ctc_arrow" - 使用向下箭頭
# ctc_pause=None - 文字顯示完畢後立即顯示 CTC
# ctc_position="fixed" - CTC 位置固定（不跟隨文字）

define e = Character("艾琳", ctc="ctc_arrow", ctc_pause=None, ctc_position="fixed")
define player = Character("玩家", color="#c8ffc8")

# 旁白也可以有 CTC
define narrator = Character(None, ctc="ctc_arrow", ctc_pause=None, ctc_position="fixed")

# 動態女主角角色（會在 load_scenario 時更新名稱）
# 使用 DynamicCharacter 讓名稱可以動態變化
define heroine = Character("[HEROINE_NAME]", ctc="ctc_arrow", ctc_pause=None, ctc_position="fixed")

# 背景與立繪位置/縮放
transform bg_cover:
    size (config.screen_width, config.screen_height)

transform heroine_center_bottom:
    xalign 0.5
    yalign 0.6


# 遊戲從這裡開始。

init python:
    import requests
    import json
    import re
    import os

    # 載入配置
    config_path = os.path.join(config.gamedir, "config.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        game_config = json.load(f)
    
    API_KEY = game_config["api_key"]
    MODEL = game_config["model"]
    SCENARIOS = game_config.get("scenarios", [])
    
    # 這些變數會在選擇劇本後設定
    HEROINE_NAME = ""
    STORY_CONTEXT = ""
    SYSTEM_PROMPT = ""
    OPTIONS_PROMPT_TEMPLATE = ""
    IMAGE_CONFIG = {}
    CURRENT_EMOTION = "normal"
    CURRENT_BG = ""
    SELECTED_EMOTION_IMAGE = ""
    SELECTED_BG_IMAGE = ""
    LOADING_IMAGE = "gui/loading_anim.png"
    
    def load_scenario(scenario_id):
        """載入指定劇本"""
        global HEROINE_NAME, STORY_CONTEXT, SYSTEM_PROMPT, OPTIONS_PROMPT_TEMPLATE, IMAGE_CONFIG, SELECTED_EMOTION_IMAGE, SELECTED_BG_IMAGE, CURRENT_EMOTION, CURRENT_BG, LOADING_IMAGE
        
        # 找到對應劇本
        scenario = None
        for s in SCENARIOS:
            if s["id"] == scenario_id:
                scenario = s
                break
        
        if not scenario:
            renpy.notify("找不到劇本！")
            return False
        
        # 重置情緒與背景狀態（設置預設值）
        SELECTED_EMOTION_IMAGE = ""
        SELECTED_BG_IMAGE = ""
        CURRENT_EMOTION = "normal"
        CURRENT_BG = "classroom"

        # 設定女主角名稱
        HEROINE_NAME = scenario["heroine_name"]
        
        # 設定當前劇本的 loading 圖片（Ren'Py 需要使用正斜線）
        scenario_folder = os.path.dirname(scenario["image_config"])
        LOADING_IMAGE = os.path.join(scenario_folder, "loading-thinking.webp").replace('\\', '/')
        
        # 載入劇情文件
        story_path = os.path.join(config.gamedir, scenario["story_file"])
        try:
            with open(story_path, 'r', encoding='utf-8') as f:
                STORY_CONTEXT = f.read().strip()
        except:
            renpy.notify(f"無法載入 {scenario['story_file']}")
            return False
        
        # 載入圖片配置
        image_config_path = os.path.join(config.gamedir, scenario["image_config"])
        try:
            with open(image_config_path, 'r', encoding='utf-8') as f:
                IMAGE_CONFIG = json.load(f)
        except:
            renpy.notify(f"無法載入 {scenario['image_config']}")
            IMAGE_CONFIG = {"emotions": {}, "backgrounds": {}}
        
        # 載入共用背景配置
        bg_config_path = os.path.join(config.gamedir, "images/background/backgrounds.json")
        try:
            with open(bg_config_path, 'r', encoding='utf-8') as f:
                bg_config = json.load(f)
                IMAGE_CONFIG["backgrounds"] = bg_config.get("backgrounds", {})
        except:
            renpy.notify("無法載入共用背景配置")
            IMAGE_CONFIG["backgrounds"] = {}

        # 預設背景/立繪路徑（若可載入）
        if IMAGE_CONFIG.get("backgrounds"):
            default_bg = IMAGE_CONFIG["backgrounds"].get("classroom", "")
            SELECTED_BG_IMAGE = resolve_image(default_bg, IMAGE_CONFIG["backgrounds"], fallback_key=None, label="default_bg")
            if SELECTED_BG_IMAGE:
                CURRENT_BG = map_path_to_key(SELECTED_BG_IMAGE, IMAGE_CONFIG.get("backgrounds", {})) or "classroom"
        if IMAGE_CONFIG.get("emotions"):
            default_emotion = IMAGE_CONFIG["emotions"].get("normal", "")
            SELECTED_EMOTION_IMAGE = resolve_image(default_emotion, IMAGE_CONFIG["emotions"], fallback_key=None, label="default_emotion")
        
        # 載入 prompts
        prompts_path = os.path.join(config.gamedir, "prompts.txt")
        with open(prompts_path, 'r', encoding='utf-8') as f:
            prompts_content = f.read()
        
        # 預處理：移除/替換變數語法
        prompts_content = process_prompt_variables(prompts_content)
        
        # 整個 prompts.txt 作為 SYSTEM_PROMPT
        SYSTEM_PROMPT = prompts_content.strip()
        
        debug_log(f"[載入] SYSTEM_PROMPT 長度: {len(SYSTEM_PROMPT)} 字元")
        debug_log(f"[載入] STORY_CONTEXT 長度: {len(STORY_CONTEXT)} 字元")
        
        # 顯示完整的初始 prompt 內容
        debug_log("\n" + "="*80, "INIT")
        debug_log("[初始化] 完整 STORY_CONTEXT:", "INIT")
        debug_log("="*80, "INIT")
        debug_log(STORY_CONTEXT, "INIT")
        debug_log("\n" + "="*80, "INIT")
        debug_log("[初始化] 完整 SYSTEM_PROMPT:", "INIT")
        debug_log("="*80, "INIT")
        debug_log(SYSTEM_PROMPT, "INIT")
        debug_log("="*80 + "\n", "INIT")
        
        return True
    
    def process_prompt_variables(text):
        """處理 prompt 中的變數語法，避免洩漏給 AI"""
        # 儲存變數值
        variables = {}
        
        # 提取 {{setvar::name::value}} 並儲存
        def extract_setvar(match):
            name = match.group(1)
            value = match.group(2)
            variables[name] = value.strip()
            return ""  # 移除 setvar 定義
        
        text = re.sub(r'\{\{setvar::([^:]+)::([^}]*)\}\}', extract_setvar, text, flags=re.DOTALL)
        
        # 替換 {{getvar::name}} 為實際值
        def replace_getvar(match):
            name = match.group(1)
            return variables.get(name, "")
        
        text = re.sub(r'\{\{getvar::([^}]+)\}\}', replace_getvar, text)
        
        # 替換 {{user}} 為 "我"
        text = text.replace("{{user}}", "我")
        
        # 移除其他未處理的變數語法
        text = re.sub(r'\{\{[^}]+\}\}', '', text)
        
        return text
    
    def detect_emotion(text):
        """從文字中偵測情緒"""
        emotion_keywords = {
            "smile": ["微笑", "笑", "開心", "高興"],
            "blush": ["臉紅", "害羞", "不好意思"],
            "worry": ["擔心", "憂慮", "不安"],
            "surprised": ["驚訝", "意外", "嚇", "愣"],
            "sad": ["難過", "傷心", "失落", "沮喪"],
            "angry": ["生氣", "憤怒", "火大"],
            "shy": ["害羞", "羞澀", "扭捏"],
            "thinking": ["思考", "想", "猶豫"]
        }
        
        for emotion, keywords in emotion_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return emotion
        return "normal"

    def map_path_to_key(path, mapping):
        """將圖片路徑反查對應的 key（完全匹配）"""
        for k, v in mapping.items():
            if v == path:
                return k
        return None

    def resolve_image(path, mapping, fallback_key=None, label=""):
        """嘗試取得可載入的圖片路徑；若失敗則使用 key/fallback 對應的合法檔案"""
        try:
            if path and renpy.loadable(path):
                return path
        except:
            pass

        # 先嘗試用 key 反查
        if path:
            key_from_path = map_path_to_key(path, mapping)
            if key_from_path:
                candidate = mapping.get(key_from_path, "")
                try:
                    if candidate and renpy.loadable(candidate):
                        return candidate
                except:
                    pass

            base = os.path.basename(path)
            stem, _ = os.path.splitext(base)

            # 若檔名對應 mapping 的 key
            if stem in mapping:
                candidate = mapping.get(stem, "")
                try:
                    if candidate and renpy.loadable(candidate):
                        return candidate
                except:
                    pass

            # 若檔名出現在 value 中
            for v in mapping.values():
                try:
                    if base in v and renpy.loadable(v):
                        return v
                except:
                    pass

        # fallback key
        if fallback_key and fallback_key in mapping:
            candidate = mapping.get(fallback_key, "")
            try:
                if candidate and renpy.loadable(candidate):
                    return candidate
            except:
                pass

        # 最後使用第一個可載入的 value
        for v in mapping.values():
            try:
                if v and renpy.loadable(v):
                    return v
            except:
                pass

        return ""
    
    def get_heroine_image():
        """取得當前女主角的圖片路徑"""
        # 優先使用 AI 指定的立繪路徑
        if SELECTED_EMOTION_IMAGE:
            return SELECTED_EMOTION_IMAGE
        if IMAGE_CONFIG and "emotions" in IMAGE_CONFIG:
            return IMAGE_CONFIG["emotions"].get(CURRENT_EMOTION, IMAGE_CONFIG["emotions"].get("normal", ""))
        return ""

    def get_background_image():
        """取得當前背景圖片路徑"""
        if SELECTED_BG_IMAGE:
            return SELECTED_BG_IMAGE
        if IMAGE_CONFIG and "backgrounds" in IMAGE_CONFIG:
            return IMAGE_CONFIG["backgrounds"].get(CURRENT_BG, "")
        return ""

    # 儲存所有對話
    chat_history = []
    
    # 完整日誌函數
    def debug_log(message, log_type="INFO"):
        """將調試信息輸出到 console 和完整日誌文件"""
        print(message)
        log_path = os.path.join(config.gamedir, "game_debug.log")
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] [{log_type}] {message}\n")
        except:
            pass
    
    def log_api_request(prompt_text):
        """記錄完整的 API 請求"""
        log_path = os.path.join(config.gamedir, "game_debug.log")
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"\n{'='*80}\n")
                f.write(f"[{timestamp}] [API REQUEST]\n")
                f.write(f"{'='*80}\n")
                f.write(prompt_text)
                f.write(f"\n{'='*80}\n\n")
        except:
            pass
    
    def log_api_response(response_data):
        """記錄完整的 API 回應"""
        log_path = os.path.join(config.gamedir, "game_debug.log")
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"\n{'='*80}\n")
                f.write(f"[{timestamp}] [API RESPONSE]\n")
                f.write(f"{'='*80}\n")
                f.write(response_data)
                f.write(f"\n{'='*80}\n\n")
        except:
            pass
    
    # 儲存完整對話歷史到本地（包含玩家和女主角）
    def save_heroine_history():
        history_path = os.path.join(config.gamedir, "heroine_history.txt")
        try:
            with open(history_path, 'w', encoding='utf-8') as f:
                f.write("=== 對話歷史記錄 ===\n\n")
                for msg in chat_history:
                    f.write(msg + "\n")
        except Exception as ex:
            renpy.notify("保存歷史記錄失敗：" + str(ex))

    # 儲存最近一次的選項（供遊戲迴圈使用）
    last_options = ["繼續聊天...", "換個話題吧", "嗯嗯，我知道了"]
    
    def extract_tag_content(text, tag_name):
        """提取指定標籤的內容"""
        pattern = f'<{tag_name}>(.*?)</{tag_name}>'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None
    
    def extract_options_from_tags(text):
        """從 <options> 標籤中提取選項（支援 title + desc 格式）"""
        debug_log(f"[標籤解析] 開始解析選項")
        
        # 先找到 <options> 區塊
        options_block = extract_tag_content(text, 'options')
        if not options_block:
            debug_log("[標籤解析] 未找到 <options> 標籤")
            return None
        
        debug_log(f"[標籤解析] options 區塊: {options_block[:200]}...")
        
        # 提取所有 <opt> 標籤內容
        opt_pattern = r'<opt>(.*?)</opt>'
        opts = re.findall(opt_pattern, options_block, re.DOTALL)
        
        if opts:
            options = []
            for opt in opts[:4]:  # 最多取 4 個
                opt = opt.strip()
                # 嘗試提取 title 和 desc
                title_match = re.search(r'<title>(.*?)</title>', opt, re.DOTALL)
                desc_match = re.search(r'<desc>(.*?)</desc>', opt, re.DOTALL)
                
                if title_match and desc_match:
                    title = title_match.group(1).strip()
                    desc = desc_match.group(1).strip()
                    # 渲染人名顏色
                    title = render_name_color(title)
                    desc = render_name_color(desc)
                    options.append({"title": title, "desc": desc})
                else:
                    # 舊格式相容：純文字選項
                    opt_rendered = render_name_color(opt)
                    options.append({"title": opt_rendered, "desc": ""})
            
            debug_log(f"[標籤解析] 成功提取選項: {[o['title'] for o in options]}")
            if len(options) >= 3:
                return options
        
        debug_log("[標籤解析] 選項數量不足")
        return None
    
    def validate_ai_response(raw_reply):
        """驗證 AI 回應格式是否正確
        
        Returns:
            tuple: (is_valid, error_message)
        """
        errors = []
        
        # 檢查必要標籤是否存在
        required_tags = ['gametxt', 'options']
        for tag in required_tags:
            open_tag = f'<{tag}>'
            close_tag = f'</{tag}>'
            
            has_open = open_tag in raw_reply
            has_close = close_tag in raw_reply
            
            if not has_open and not has_close:
                errors.append(f"缺少 <{tag}> 標籤")
            elif has_open and not has_close:
                errors.append(f"<{tag}> 標籤未閉合")
            elif not has_open and has_close:
                errors.append(f"<{tag}> 缺少開始標籤")
        
        # 檢查 gametxt 內容是否有效
        if '<gametxt>' in raw_reply and '</gametxt>' in raw_reply:
            gametxt = extract_tag_content(raw_reply, 'gametxt')
            if not gametxt or len(gametxt.strip()) < 5:
                errors.append("gametxt 內容過短或為空")
        
        # 檢查 options 是否至少有 3 個選項
        if '<options>' in raw_reply and '</options>' in raw_reply:
            options_block = extract_tag_content(raw_reply, 'options')
            if options_block:
                opt_count = options_block.count('<opt>')
                if opt_count < 3:
                    errors.append(f"選項數量不足（只有 {opt_count} 個，需要至少 3 個）")
        
        if errors:
            return False, "; ".join(errors)
        return True, None
    
    def parse_ai_response(raw_reply):
        """解析 AI 回應，提取 gametxt 和 options"""
        debug_log(f"[解析] 開始處理回應，長度: {len(raw_reply)}")
        debug_log(f"[解析] 原始回應前500字: {raw_reply[:500]}")
        
        # 因為使用卡 CoT 技巧，AI 回應會從 thinking 內容開始
        # 需要補上開頭的 <thinking> 標籤（如果缺失）
        if not raw_reply.strip().startswith('<thinking>'):
            # 檢查是否有 </thinking>，如果有代表 AI 從中間開始輸出
            if '</thinking>' in raw_reply:
                raw_reply = '<thinking>\n' + raw_reply
                debug_log("[解析] 補上了開頭的 <thinking> 標籤")
        
        # 提取 <thinking> 內容（用於 debug）
        thinking = extract_tag_content(raw_reply, 'thinking')
        if thinking:
            debug_log(f"[解析] thinking 內容: {thinking[:100]}...")
        
        # 提取 <gametxt> 內容
        gametxt = extract_tag_content(raw_reply, 'gametxt')
        if gametxt:
            debug_log(f"[解析] 找到 gametxt: {gametxt[:50]}...")
        else:
            debug_log("[解析] ⚠️ 未找到 <gametxt> 標籤")
            # 備用：嘗試移除 thinking 和 options 後的內容作為對話
            fallback = raw_reply
            fallback = re.sub(r'<thinking>.*?</thinking>', '', fallback, flags=re.DOTALL)
            fallback = re.sub(r'<options>.*?</options>', '', fallback, flags=re.DOTALL)
            # 移除其他可能的標籤殘留
            fallback = re.sub(r'<[^>]+>', '', fallback)
            fallback = fallback.strip()
            if fallback and len(fallback) > 10:
                gametxt = fallback
                debug_log(f"[解析] 使用備用內容: {gametxt[:50]}...")
        
        # 提取選項
        options = extract_options_from_tags(raw_reply)
        
        if not gametxt:
            gametxt = "..."
        
        return gametxt, options

    def extract_visual_selection(raw_reply):
        """從 AI 回應提取 emotion_image 與 bg_image 路徑"""
        emotion_path = None
        bg_path = None

        # 搜尋標記行，允許前後空白
        emotion_match = re.search(r"emotion_image\s*:\s*([^\n\r<]+)", raw_reply)
        bg_match = re.search(r"bg_image\s*:\s*([^\n\r<]+)", raw_reply)

        if emotion_match:
            emotion_path = emotion_match.group(1).strip()
        if bg_match:
            bg_path = bg_match.group(1).strip()

        return emotion_path, bg_path

    def get_gemini_reply(user_input):
        """取得 AI 回應（對話 + 選項一次完成）"""
        global last_options, CURRENT_EMOTION, CURRENT_BG, SELECTED_EMOTION_IMAGE, SELECTED_BG_IMAGE
        
        MAX_RETRIES = 3  # 最大重試次數
        
        debug_log("\n=== [DEBUG] 開始處理 AI 回應 ===")
        debug_log(f"[DEBUG] 玩家輸入: {user_input}")
        
        # 官方 Gemini API 端點: https://generativelanguage.googleapis.com/v1beta/models/
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
        headers = {"Content-Type": "application/json"}
        
        # 組合對話歷史（用於 {history} 替換）
        history_text = ""
        for msg in chat_history:
            history_text += msg + "\n"
        history_text += "玩家：" + user_input
        
        # 把 SYSTEM_PROMPT 中的 {history} 替換成實際對話歷史
        full_prompt = STORY_CONTEXT + "\n\n" + SYSTEM_PROMPT.replace("{history}", history_text)
        
        debug_log(f"[DEBUG] Prompt 總長度: {len(full_prompt)} 字元")
        debug_log(f"[DEBUG] 對話歷史筆數: {len(chat_history)}")
        
        # 記錄完整的 API 請求內容
        log_api_request(full_prompt)
        
        # Gemini 2.5 Flash API 請求
        data = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": full_prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 1.0,
                "topP": 0.95,
                "topK": 40,
                "responseMimeType": "text/plain",
                # 關閉 thinking 模式，讓模型直接輸出
                "thinkingConfig": {
                    "thinkingBudget": 0
                }
            },
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ]
        }
        
        # 記錄完整的請求 JSON 格式
        debug_log(f"[API REQUEST JSON]\n{json.dumps(data, ensure_ascii=False, indent=2)[:20000]}...", "API")
        debug_log(f"[API] URL: {url.replace(API_KEY, 'API_KEY_HIDDEN')}", "API")
        debug_log(f"[API] Model: {MODEL}", "API")
        
        # 重試迴圈
        raw_reply = None
        last_error = None
        
        for attempt in range(MAX_RETRIES):
            if attempt > 0:
                debug_log(f"[RETRY] 第 {attempt + 1} 次重試...", "RETRY")
            
            # 計時開始
            import time
            start_time = time.time()
            
            try:
                response = requests.post(url, headers=headers, json=data)
            except Exception as req_err:
                debug_log(f"[ERROR] 請求失敗: {req_err}", "ERROR")
                last_error = f"請求失敗: {req_err}"
                continue
            
            # 計時結束
            elapsed_time = time.time() - start_time
            debug_log(f"API 狀態碼: {response.status_code} | 回應時間: {elapsed_time:.2f} 秒", "API")
            
            # 記錄完整的 API 回應
            log_api_response(response.text)
            
            if response.status_code != 200:
                debug_log(f"API 錯誤！狀態碼: {response.status_code}", "ERROR")
                debug_log(f"錯誤內容: {response.text[:200]}", "ERROR")
                last_error = f"API 錯誤 {response.status_code}"
                continue
            
            result = response.json()
            
            # 安全地解析回應
            try:
                candidates = result.get("candidates", [])
                if not candidates:
                    debug_log(f"[ERROR] API 回應沒有 candidates: {result}", "ERROR")
                    last_error = "AI 沒有回應"
                    continue
                
                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                
                if not parts:
                    # 檢查是否被安全過濾
                    finish_reason = candidates[0].get("finishReason", "")
                    safety_ratings = candidates[0].get("safetyRatings", [])
                    debug_log(f"[ERROR] 沒有 parts，finishReason: {finish_reason}", "ERROR")
                    debug_log(f"[ERROR] safetyRatings: {safety_ratings}", "ERROR")
                    last_error = "AI 回應被過濾或為空"
                    continue
                
                raw_reply = parts[0].get("text", "").strip()
            except Exception as parse_err:
                debug_log(f"[ERROR] 解析回應失敗: {parse_err}", "ERROR")
                debug_log(f"[ERROR] 原始回應: {response.text[:500]}", "ERROR")
                last_error = f"解析失敗: {parse_err}"
                continue
            
            debug_log(f"[DEBUG] AI 原始輸出: {raw_reply[:500]}...")
            
            # 驗證回應格式
            is_valid, validation_error = validate_ai_response(raw_reply)
            if not is_valid:
                debug_log(f"[VALIDATION] ⚠️ 回應格式無效: {validation_error}", "VALIDATION")
                debug_log(f"[VALIDATION] 將進行重試 ({attempt + 1}/{MAX_RETRIES})", "VALIDATION")
                last_error = validation_error
                raw_reply = None  # 重置，繼續重試
                continue
            
            # 驗證通過，跳出重試迴圈
            debug_log(f"[VALIDATION] ✓ 回應格式驗證通過", "VALIDATION")
            break
        
        # 檢查是否有有效回應
        if raw_reply is None:
            debug_log(f"[ERROR] 重試 {MAX_RETRIES} 次後仍然失敗: {last_error}", "ERROR")
            return f"（AI 回應異常，請重試：{last_error}）"
        
        debug_log(f"[DEBUG] AI 原始輸出完整: {raw_reply}")
        
        # 解析 AI 回應（使用 XML 標籤）
        # 提前解析視覺素材選擇
        selected_emotion_image, selected_bg_image = extract_visual_selection(raw_reply)

        def coerce_visual_path(raw_path, mapping, fallback_key, label):
            """Clamp AI 提供的路徑到已知列表，避免不存在檔案"""
            if not raw_path:
                return raw_path
            base = os.path.basename(raw_path)
            stem, _ = os.path.splitext(base)

            # 允許直接傳入完整 value
            if raw_path in mapping.values():
                return raw_path

            # 若傳 key 名，轉成對應 value
            if stem in mapping:
                coerced = mapping.get(stem, "")
                debug_log(f"[WARN] AI {label} 非列表檔名，改用: {coerced}")
                return coerced

            # 其他情況，退回 fallback key
            fallback = mapping.get(fallback_key, "") if fallback_key else ""
            debug_log(f"[WARN] AI {label} 不在列表，改用預設: {fallback}")
            return fallback

        # 先將 AI 回傳值限制在合法列表內，再嘗試載入
        selected_emotion_image = coerce_visual_path(
            selected_emotion_image,
            IMAGE_CONFIG.get("emotions", {}),
            CURRENT_EMOTION or "normal",
            "emotion"
        )
        selected_bg_image = coerce_visual_path(
            selected_bg_image,
            IMAGE_CONFIG.get("backgrounds", {}),
            CURRENT_BG or "classroom",
            "bg"
        )
        # 嘗試解析為合法可載入路徑，給定預設 fallback
        selected_emotion_image = resolve_image(
            selected_emotion_image,
            IMAGE_CONFIG.get("emotions", {}),
            fallback_key=CURRENT_EMOTION or "normal",
            label="emotion"
        )
        selected_bg_image = resolve_image(
            selected_bg_image,
            IMAGE_CONFIG.get("backgrounds", {}),
            fallback_key=CURRENT_BG or "classroom",
            label="bg"
        )

        dialogue, options = parse_ai_response(raw_reply)
        
        # 如果成功提取選項，更新 last_options
        if options:
            last_options = options
            debug_log(f"[DEBUG] 提取到選項: {options}")
        else:
            debug_log("[DEBUG] ⚠️ 未能提取選項，使用預設選項")
        
        # 清理對話內容
        reply = dialogue
        
        # 移除 prompt 變數語法洩漏（如 {{setvar::xxx::yyy}}）
        reply = re.sub(r'\{\{[^}]+\}\}', '', reply).strip()
        
        # 移除可能的名字開頭
        if reply.startswith(HEROINE_NAME + "：") or reply.startswith(HEROINE_NAME + ":"):
            reply = reply.split("：", 1)[-1].split(":", 1)[-1].strip()
            debug_log("移除了名字開頭", "PROCESS")
        
        # 移除可能的玩家對話
        if "玩家：" in reply or "玩家:" in reply:
            reply = reply.split("玩家：")[0].split("玩家:")[0].strip()
            debug_log("[DEBUG] ⚠️ 移除了多餘的玩家對話")
        
        # 套用 AI 指定的立繪/背景，如果有的話
        mapped_emotion = None
        if selected_emotion_image:
            SELECTED_EMOTION_IMAGE = selected_emotion_image
            mapped_emotion = map_path_to_key(SELECTED_EMOTION_IMAGE, IMAGE_CONFIG.get("emotions", {}))
            if mapped_emotion:
                CURRENT_EMOTION = mapped_emotion
        if selected_bg_image:
            SELECTED_BG_IMAGE = selected_bg_image
            mapped_bg = map_path_to_key(SELECTED_BG_IMAGE, IMAGE_CONFIG.get("backgrounds", {}))
            if mapped_bg:
                CURRENT_BG = mapped_bg

        # 若未取得 AI 指定情緒，或無法反查 key，回退文字偵測
        if (not selected_emotion_image) or (selected_emotion_image and not mapped_emotion):
            CURRENT_EMOTION = detect_emotion(reply)
        debug_log(f"[DEBUG] 偵測到情緒: {CURRENT_EMOTION}")
        if SELECTED_EMOTION_IMAGE:
            debug_log(f"[DEBUG] 使用 AI 指定立繪: {SELECTED_EMOTION_IMAGE}")
        if SELECTED_BG_IMAGE:
            debug_log(f"[DEBUG] 使用 AI 指定背景: {SELECTED_BG_IMAGE}")
        debug_log(f"[DEBUG] 最終對話: {reply}")
        debug_log("=== [DEBUG] 處理完成 ===\n")
        
        # 儲存對話歷史
        chat_history.append("玩家：" + user_input)
        chat_history.append(HEROINE_NAME + "：" + reply)
        save_heroine_history()
        
        return reply

    def get_ai_options(context):
        """取得最近一次的選項（不額外呼叫 API）"""
        global last_options
        debug_log(f"[OPTIONS] 返回已快取的選項: {last_options}", "OPTIONS")
        return last_options

    # 人名顏色配置
    NAME_COLORS = {
        "default": "#ffcc66",  # 預設金黃色
        # 可以為特定角色設定不同顏色
        # "小雪": "#ff99cc",
        # "明輝": "#66ccff",
    }
    
    def render_name_color(text):
        """將 @人名@ 標記轉換為 Ren'Py 顏色標籤"""
        def replace_name(match):
            name = match.group(1)
            color = NAME_COLORS.get(name, NAME_COLORS["default"])
            return "{color=" + color + "}" + name + "{/color}"
        
        # 匹配 @人名@ 格式
        return re.sub(r'@([^@]+)@', replace_name, text)
    
    def parse_gametxt_segments(gametxt):
        """解析 gametxt 中的旁白和對話段落"""
        segments = []
        
        # 分割文字，保留 "" 對話、*內心* 標記
        # 模式：找出 "對話"、*內心*、和其他文字
        # 使用英文雙引號 "" 來標記對話，避免和中文「」混淆
        pattern = r'("(?:[^"\\]|\\.)*"|\*[^*]+\*)'
        parts = re.split(pattern, gametxt)
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            if part.startswith('"') and part.endswith('"'):
                # 女主角對話（英文雙引號）
                dialogue = part[1:-1]  # 移除 ""
                # 對話中也可能有人名標記
                dialogue = render_name_color(dialogue)
                segments.append({"type": "dialogue", "content": dialogue})
            elif part.startswith('*') and part.endswith('*'):
                # 內心獨白
                thought = part[1:-1]  # 移除 *
                thought = render_name_color(thought)
                segments.append({"type": "thought", "content": thought})
            else:
                # 旁白描述 - 渲染人名顏色
                narration = render_name_color(part)
                segments.append({"type": "narration", "content": narration})
        
        debug_log(f"[解析] gametxt 分段: {len(segments)} 段")
        return segments

    # 用於非同步 API 呼叫的全域變數
    async_api_result = [None, None, False]  # [reply, error, is_done]
    
    def async_fetch_reply(user_input):
        """在背景執行緒中呼叫 API"""
        global async_api_result
        async_api_result = [None, None, False]
        try:
            result = get_gemini_reply(user_input)
            async_api_result[0] = result
        except Exception as e:
            async_api_result[1] = str(e)
        async_api_result[2] = True  # 標記完成
    
    def is_api_done():
        """檢查 API 是否完成"""
        return async_api_result[2]
    
    def get_api_result():
        """取得 API 結果"""
        return async_api_result[0], async_api_result[1]

label start:
    # 隱藏對話框，讓選擇畫面更清爽
    window hide
    
    # 劇本選擇（使用自訂畫面，支援 hover 預覽）
    call screen scenario_select_screen
    $ selected_scenario = _return
    
    # 開始遊戲後重新顯示對話框
    window show
    
    # 載入選擇的劇本
    show screen loading_screen
    $ load_scenario(selected_scenario)
    hide screen loading_screen
    $ debug_log("[GAME] 劇本載入完成，準備開始遊戲", "GAME")
    "開始 [HEROINE_NAME] 的故事..."
    
    $ player_input = "你好"
    $ first_turn = True
    $ debug_log("[GAME] 進入主迴圈", "GAME")
    while True:
        $ debug_log(f"[GAME] 迴圈開始，player_input: {player_input}", "GAME")
        
        # 先清空畫面，避免上一輪的背景/立繪殘留
        scene
        hide heroine

        # 顯示背景（若 AI 有指定）
        $ bg_img = get_background_image()
        $ debug_log(f"[GAME] bg_img: {bg_img}", "GAME")
        if bg_img and renpy.loadable(bg_img):
            scene expression bg_img at bg_cover onlayer master
        elif bg_img:
            $ debug_log(f"[GAME] 背景未找到或無法載入: {bg_img}", "ERROR")
        
        # 顯示女主角圖片（如果有）
        $ heroine_img = get_heroine_image()
        $ debug_log(f"[GAME] heroine_img: {heroine_img}", "GAME")
        if heroine_img and renpy.loadable(heroine_img):
            show expression heroine_img as heroine at heroine_center_bottom onlayer master
        elif heroine_img:
            # 嘗試使用預設 normal 立繪當作備援
            $ fallback_heroine = resolve_image("", IMAGE_CONFIG.get("emotions", {}), fallback_key="normal", label="fallback_heroine")
            if fallback_heroine:
                $ debug_log(f"[GAME] 立繪未找到，使用預設: {fallback_heroine}", "WARN")
                show expression fallback_heroine as heroine at heroine_center_bottom onlayer master
            else:
                $ debug_log(f"[GAME] 立繪未找到或無法載入: {heroine_img}", "ERROR")
        
        # 顯示玩家輸入（除了第一輪）
        if not first_turn:
            player "[player_input]"
        $ first_turn = False
        
        # 女主角回應
        $ debug_log("[GAME] 準備呼叫 get_gemini_reply", "GAME")
        
        # 在背景執行緒啟動 API 呼叫
        $ renpy.invoke_in_thread(async_fetch_reply, player_input)
        
        # 顯示 Loading 畫面（會自動在 API 完成時關閉）
        call screen loading_screen
        
        # 取得結果
        $ reply, api_error = get_api_result()
        
        if api_error:
            $ reply = "（API 發生錯誤）"
            $ debug_log(f"[GAME] API 錯誤: {api_error}", "ERROR")
        
        $ debug_log(f"[GAME] get_gemini_reply 返回: {reply[:50] if reply else 'None'}...", "GAME")

        # 先依最新狀態切換背景，讓畫面在對話前就更新
        $ bg_img = get_background_image()
        $ debug_log(f"[GAME] updated bg_img: {bg_img}", "GAME")
        if bg_img and renpy.loadable(bg_img):
            scene expression bg_img at bg_cover onlayer master
        elif bg_img:
            $ debug_log(f"[GAME] 背景未找到或無法載入: {bg_img}", "ERROR")
        
        # 更新圖片到最新情緒
        $ heroine_img = get_heroine_image()
        hide heroine
        if heroine_img and renpy.loadable(heroine_img):
            show expression heroine_img as heroine at heroine_center_bottom onlayer master with dissolve
        elif heroine_img:
            $ fallback_heroine = resolve_image("", IMAGE_CONFIG.get("emotions", {}), fallback_key="normal", label="fallback_heroine")
            if fallback_heroine:
                $ debug_log(f"[GAME] 立繪未找到，使用預設: {fallback_heroine}", "WARN")
                show expression fallback_heroine as heroine at heroine_center_bottom onlayer master with dissolve
            else:
                $ debug_log(f"[GAME] 立繪未找到或無法載入: {heroine_img}", "ERROR")
        
        # 解析 gametxt 中的旁白和對話段落
        $ segments = parse_gametxt_segments(reply) if reply else []
        
        # 依序顯示每個段落
        if segments:
            python:
                for seg in segments:
                    if seg["type"] == "narration":
                        # 旁白描述
                        renpy.say(None, seg["content"])
                    elif seg["type"] == "dialogue":
                        # 女主角對話
                        renpy.say(store.HEROINE_NAME, seg["content"])
                    elif seg["type"] == "thought":
                        # 內心獨白（用斜體或特殊樣式）
                        renpy.say(None, "{i}" + seg["content"] + "{/i}")
        else:
            # 備用：如果解析失敗，直接顯示全部內容
            heroine "[reply]"
        
        # 讓 AI 生成選項
        $ options = get_ai_options(reply)
        
        # 顯示選項選擇畫面
        call screen option_select_screen(options)
        $ selected_option = _return
        
        # 處理選擇結果
        if selected_option == "quit":
            "遊戲結束。"
            return
        elif selected_option == "skip":
            $ player_action = ""
        else:
            $ player_action = selected_option
        
        # 再輸入對話
        $ player_talk = renpy.input("你要說什麼？（可留空）")
        
        # 組合動作和對話（選項包含 title 和 desc）
        if player_action and player_talk:
            $ player_input = "[" + player_action + "] " + player_talk
        elif player_action:
            $ player_input = "[" + player_action + "]"
        elif player_talk:
            $ player_input = player_talk
        else:
            $ player_input = "..."
        
        # 如果選項有描述，附加到輸入中
        python:
            if selected_option and selected_option != "quit" and selected_option != "skip":
                for opt in last_options:
                    if isinstance(opt, dict) and opt.get("title") == selected_option and opt.get("desc"):
                        player_input = player_input + "（" + opt["desc"] + "）"
                        break

label action_or_talk:
    jump start
