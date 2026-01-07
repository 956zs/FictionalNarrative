################################################################################
## 初始化
################################################################################

init offset = -1

################################################################################
## 點擊繼續提示 (CTC - Click to Continue)
################################################################################

## CTC 閃爍動畫 - 更顯眼的上下浮動 + 透明度 + 縮放變化
transform ctc_appear:
    alpha 0.0 yoffset 8 zoom 0.8
    pause 0.15
    ease 0.25 alpha 1.0 yoffset 0 zoom 1.0

transform ctc_blink:
    alpha 1.0 yoffset 0 zoom 1.0
    block:
        ease 0.35 alpha 0.5 yoffset 6 zoom 0.9
        ease 0.35 alpha 1.0 yoffset 0 zoom 1.1
        ease 0.2 zoom 1.0
        repeat

## 組合動畫：先出現，再閃爍（更顯眼版本）
transform ctc_animation:
    alpha 0.0 yoffset 8 zoom 0.8
    pause 0.15
    ease 0.25 alpha 1.0 yoffset 0 zoom 1.0
    block:
        ease 0.35 alpha 0.5 yoffset 6 zoom 0.9
        ease 0.35 alpha 1.0 yoffset 0 zoom 1.1
        ease 0.2 zoom 1.0
        repeat

## CTC 圖示定義 - 使用 Python 初始化（更大更亮的樣式）
init python:
    # 向下箭頭 - 更大、更亮、更粗的描邊
    ctc_arrow_text = Text("▼", size=28, color="#ffdd44", outlines=[(2, "#000000", 0, 0), (4, "#ff8800", 0, 0)])
    # 三角形
    ctc_triangle_text = Text("▶", size=26, color="#ffdd44", outlines=[(2, "#000000", 0, 0), (4, "#ff8800", 0, 0)])
    # 方括號 - 更醒目
    ctc_bracket_text = Text("【CLICK】", size=18, color="#ffee00", outlines=[(2, "#000000", 0, 0)])
    # 簡約箭頭
    ctc_simple_text = Text("»", size=34, color="#ffdd44", outlines=[(2, "#333333", 0, 0)])
    # 三個點
    ctc_dots_text = Text("●●●", size=18, color="#ffdd44", outlines=[(2, "#000000", 0, 0)])

image ctc_arrow:
    ctc_arrow_text
    ctc_animation

image ctc_triangle:
    ctc_triangle_text
    ctc_animation

image ctc_bracket:
    ctc_bracket_text
    ctc_animation

image ctc_simple:
    ctc_simple_text
    ctc_animation

image ctc_dots:
    ctc_dots_text
    ctc_animation


################################################################################
## Loading 畫面 (等待 AI 回應時顯示)
################################################################################

## Loading 旋轉動畫
transform loading_rotate:
    anchor (0.5, 0.5)
    block:
        rotate 0
        linear 1.0 rotate 360
        repeat

## Loading 淡入淡出動畫
transform loading_pulse:
    alpha 0.6
    block:
        ease 0.8 alpha 1.0
        ease 0.8 alpha 0.6
        repeat

## Loading 畫面（帶自動完成檢查）
screen loading_screen():
    zorder 200
    modal True

    ## 半透明黑色背景
    add Solid("#000000aa")

    ## Loading 圖片容器
    vbox:
        xalign 0.5
        yalign 0.5
        spacing 20

        ## Loading 動畫圖片（使用當前劇本的 loading-thinking.webp）
        add store.LOADING_IMAGE:
            xalign 0.5
            zoom 0.6

        ## Loading 文字
        text "[HEROINE_NAME]正在思考中..." size 24 color "#ffffff" xalign 0.5 at loading_pulse

    ## 每 0.1 秒檢查一次 API 是否完成
    timer 0.1 repeat True action If(is_api_done(), Return())

## 備用：如果 loading.gif 不存在，使用純文字 loading
screen loading_screen_text():
    zorder 200
    modal True

    add Solid("#000000aa")

    vbox:
        xalign 0.5
        yalign 0.5
        spacing 15

        ## 旋轉的圓圈符號
        text "◐" size 48 color "#ffffff" xalign 0.5 at loading_rotate

        text "AI正在努力思考中..." size 22 color "#ffffff" xalign 0.5 at loading_pulse


################################################################################
## 劇本選擇畫面（Hover 顯示全螢幕角色立繪）
################################################################################

## 淡入動畫
transform scenario_preview_appear:
    alpha 0.0
    ease 0.3 alpha 1.0

## 劇本選擇畫面
screen scenario_select_screen():
    tag menu
    modal True
    
    ## 追蹤當前 hover 的劇本 ID（0 = 無）
    default hovered_scenario = 0
    
    ## 預覽立繪路徑對應
    $ preview_images = {
        1: "images/ui/story1.png",
        2: "images/ui/story2.png",
        3: "images/ui/story3.png"
    }
    
    ## 背景層 - 根據 hover 狀態顯示對應角色立繪
    if hovered_scenario > 0 and hovered_scenario in preview_images:
        add preview_images[hovered_scenario]:
            xalign 0.5
            yalign 0.5
            fit "contain"
            at scenario_preview_appear
    else:
        ## 預設背景（深色漸層）
        add Solid("#1a1a2e")
    
    ## 半透明遮罩讓按鈕更清楚
    add Solid("#00000066")
    
    ## 選項容器
    vbox:
        xalign 0.5
        yalign 0.5
        spacing 25
        
        ## 標題
        text "選擇你想體驗的劇本" size 36 color "#ffffff" xalign 0.5:
            outlines [(3, "#000000", 0, 0)]
        
        null height 30
        
        ## 劇本選項
        for i, scenario in enumerate(SCENARIOS):
            button:
                xsize 600
                padding (30, 20)
                background Frame("gui/button/choice_idle_background.png", 10, 10)
                hover_background Frame("gui/button/choice_hover_background.png", 10, 10)
                
                ## Hover 事件
                hovered SetScreenVariable("hovered_scenario", scenario["id"])
                unhovered SetScreenVariable("hovered_scenario", 0)
                
                ## 點選事件
                action Return(scenario["id"])
                
                vbox:
                    spacing 8
                    text scenario["name"] size 26 color "#ffffff" bold True xalign 0.5:
                        outlines [(2, "#000000", 0, 0)]
                    text scenario["heroine_name"] size 20 color "#cccccc" xalign 0.5:
                        outlines [(1, "#000000", 0, 0)]

################################################################################
## 樣式
################################################################################

style default:
    properties gui.text_properties()
    language gui.language

style input:
    properties gui.text_properties("input", accent=True)
    adjust_spacing False

style hyperlink_text:
    properties gui.text_properties("hyperlink", accent=True)
    hover_underline True

style gui_text:
    properties gui.text_properties("interface")


style button:
    properties gui.button_properties("button")

style button_text is gui_text:
    properties gui.text_properties("button")
    yalign 0.5


style label_text is gui_text:
    properties gui.text_properties("label", accent=True)

style prompt_text is gui_text:
    properties gui.text_properties("prompt")


style bar:
    ysize gui.bar_size
    left_bar Frame("gui/bar/left.png", gui.bar_borders, tile=gui.bar_tile)
    right_bar Frame("gui/bar/right.png", gui.bar_borders, tile=gui.bar_tile)

style vbar:
    xsize gui.bar_size
    top_bar Frame("gui/bar/top.png", gui.vbar_borders, tile=gui.bar_tile)
    bottom_bar Frame("gui/bar/bottom.png", gui.vbar_borders, tile=gui.bar_tile)

style scrollbar:
    ysize gui.scrollbar_size
    base_bar Frame("gui/scrollbar/horizontal_[prefix_]bar.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/scrollbar/horizontal_[prefix_]thumb.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)

style vscrollbar:
    xsize gui.scrollbar_size
    base_bar Frame("gui/scrollbar/vertical_[prefix_]bar.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/scrollbar/vertical_[prefix_]thumb.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)

style slider:
    ysize gui.slider_size
    base_bar Frame("gui/slider/horizontal_[prefix_]bar.png", gui.slider_borders, tile=gui.slider_tile)
    thumb "gui/slider/horizontal_[prefix_]thumb.png"

style vslider:
    xsize gui.slider_size
    base_bar Frame("gui/slider/vertical_[prefix_]bar.png", gui.vslider_borders, tile=gui.slider_tile)
    thumb "gui/slider/vertical_[prefix_]thumb.png"


style frame:
    padding gui.frame_borders.padding
    background Frame("gui/frame.png", gui.frame_borders, tile=gui.frame_tile)



################################################################################
## 遊戲內畫面
################################################################################


################################################################################
## 選項選擇畫面（支援 title + desc 格式）
################################################################################

screen option_select_screen(options):
    modal True
    zorder 100

    ## 半透明背景
    add Solid("#00000088")

    ## 選項容器
    vbox:
        xalign 0.5
        yalign 0.5
        spacing 15
        xsize 900

        ## 標題
        text "選擇你的行動" size 28 color "#ffffff" xalign 0.5

        null height 10

        ## 動態生成選項按鈕
        for i, opt in enumerate(options):
            button:
                xfill True
                padding (20, 15)
                background Frame("gui/button/choice_idle_background.png", 10, 10) 
                hover_background Frame("gui/button/choice_hover_background.png", 10, 10)
                action Return(opt.get("title", opt) if isinstance(opt, dict) else opt)

                vbox:
                    spacing 5
                    # 標題
                    if isinstance(opt, dict):
                        text opt.get("title", "選項") size 22 color "#ffffff" bold True
                        # 描述（如果有）
                        if opt.get("desc"):
                            text opt.get("desc", "") size 16 color "#cccccc"
                    else:
                        text str(opt) size 22 color "#ffffff"

        null height 10

        ## 額外選項
        hbox:
            xalign 0.5
            spacing 30

            textbutton "不做動作" action Return("skip"):
                text_size 18
                text_color "#888888"

            textbutton "結束遊戲" action Return("quit"):
                text_size 18
                text_color "#ff6666"


## Say 畫面 ######################################################################
##
## Say 畫面用於向玩家顯示對話。它有兩個參數 who 和 what，分別是說話角色的名字
## 和要顯示的文字。（who 參數可以為 None 如果沒有給出名字。）
##
## 此畫面必須建立 id 為 "what" 的可顯示文字，因為 Ren'Py 使用它來管理文字顯
## 示。它還可以建立 id "who" 和 id "window" 的可顯示文字應用程式樣式屬性。
##
## https://www.renpy.org/doc/html/screen_special.html#say

screen say(who, what):

    window:
        id "window"

        if who is not None:

            window:
                id "namebox"
                style "namebox"
                text who id "who"

        text what id "what"

    ## 如果有側面影像，請將其顯示在文字上方。不要顯示在手機版本上 - 沒有空間。
    if not renpy.variant("small"):
        add SideImage() xalign 0.0 yalign 1.0


## 點擊繼續提示畫面 (CTC Screen)
## 這個畫面會在對話文字顯示完畢後自動出現
screen ctc(arg=None):
    zorder 100

    ## 使用 ctc_arrow 作為預設，你可以改成其他樣式：
    ## ctc_arrow - 向下箭頭 ▼
    ## ctc_triangle - 三角形 ▶
    ## ctc_dots - 三個點 ●●●
    ## ctc_bracket - 方括號 【CLICK】
    ## ctc_simple - 簡約箭頭 »

    add "ctc_arrow":
        xalign 0.98
        yalign 0.98
        xoffset -30
        yoffset -20


## 使名稱框可用於透過角色物件進行樣式設定。
init python:
    config.character_id_prefixes.append('namebox')

style window is default
style say_label is default
style say_dialogue is default
style say_thought is say_dialogue

style namebox is default
style namebox_label is say_label


style window:
    xalign 0.5
    xfill True
    yalign gui.textbox_yalign
    ysize gui.textbox_height

    background Image("gui/textbox.png", xalign=0.5, yalign=1.0)

style namebox:
    xpos gui.name_xpos
    xanchor gui.name_xalign
    xsize gui.namebox_width
    ypos gui.name_ypos
    ysize gui.namebox_height

    background Frame("gui/namebox.png", gui.namebox_borders, tile=gui.namebox_tile, xalign=gui.name_xalign)
    padding gui.namebox_borders.padding

style say_label:
    properties gui.text_properties("name", accent=True)
    xalign gui.name_xalign
    yalign 0.5

style say_dialogue:
    properties gui.text_properties("dialogue")

    xpos gui.dialogue_xpos
    xsize gui.dialogue_width
    ypos gui.dialogue_ypos

    adjust_spacing False

## 輸入畫面 ########################################################################
##
## 此畫面用於顯示 renpy.input 。prompt 參數用於傳入文字提示。
##
## 此畫面必須建立一個可顯示的輸入，透過 id "input" 以接受各種輸入參數。
##
## https://www.renpy.org/doc/html/screen_special.html#input

screen input(prompt):
    style_prefix "input"

    window:

        vbox:
            xanchor gui.dialogue_text_xalign
            xpos gui.dialogue_xpos
            xsize gui.dialogue_width
            ypos gui.dialogue_ypos

            text prompt style "input_prompt"
            input id "input"

style input_prompt is default

style input_prompt:
    xalign gui.dialogue_text_xalign
    properties gui.text_properties("input_prompt")

style input:
    xalign gui.dialogue_text_xalign
    xmaximum gui.dialogue_width


## 選擇畫面 ########################################################################
##
## 此畫面用於顯示選單語句所呈現的遊戲內選項。第一個參數，項目，是一個物件列
## 表，每個物件都有標題和操作欄位。
##
## https://www.renpy.org/doc/html/screen_special.html#choice

screen choice(items):
    style_prefix "choice"

    vbox:
        for i in items:
            textbutton i.caption action i.action


style choice_vbox is vbox
style choice_button is button
style choice_button_text is button_text

style choice_vbox:
    xalign 0.5
    ypos 405
    yanchor 0.5

    spacing gui.choice_spacing

style choice_button is default:
    properties gui.button_properties("choice_button")

style choice_button_text is default:
    properties gui.text_properties("choice_button")


## 快捷選單畫面 ######################################################################
##
## 快捷選單顯示在遊戲中，以便輕鬆存取遊戲外選單。

screen quick_menu():

    ## 確保它出現在其他螢幕的頂端。
    zorder 100

    if quick_menu:

        hbox:
            style_prefix "quick"
            style "quick_menu"

            textbutton _("返回") action Rollback()
            textbutton _("歷史") action ShowMenu('history')
            textbutton _("略過") action Skip() alternate Skip(fast=True, confirm=True)
            textbutton _("自動") action Preference("auto-forward", "toggle")
            textbutton _("儲存") action ShowMenu('save')
            textbutton _("Q.儲存") action QuickSave()
            textbutton _("Q.讀取") action QuickLoad()
            textbutton _("設定") action ShowMenu('preferences')


## 此代碼確保只要玩家沒有明確隱藏介面， quick_menu 畫面就會在遊戲中顯示。
init python:
    config.overlay_screens.append("quick_menu")

default quick_menu = True

style quick_menu is hbox
style quick_button is default
style quick_button_text is button_text

style quick_menu:
    xalign 0.5
    yalign 1.0

style quick_button:
    properties gui.button_properties("quick_button")

style quick_button_text:
    properties gui.text_properties("quick_button")


################################################################################
## 主選單和遊戲選單畫面
################################################################################

## 導覽畫面 ########################################################################
##
## 此畫面包含在主選單和遊戲選單中，並提供其他選單的導覽以及開始遊戲的導覽。

screen navigation():

    vbox:
        style_prefix "navigation"

        xpos gui.navigation_xpos
        yalign 0.5

        spacing gui.navigation_spacing

        if main_menu:

            textbutton _("開始") action Start()

        else:

            textbutton _("歷史") action ShowMenu("history")

            textbutton _("儲存") action ShowMenu("save")

        textbutton _("載入") action ShowMenu("load")

        textbutton _("設定") action ShowMenu("preferences")

        if _in_replay:

            textbutton _("結束回想") action EndReplay(confirm=True)

        elif not main_menu:

            textbutton _("標題畫面") action MainMenu()

        textbutton _("關於") action ShowMenu("about")

        if renpy.variant("pc") or (renpy.variant("web") and not renpy.variant("mobile")):

            ## 幫助對於行動裝置來說是不必要或不相關的。
            textbutton _("説明") action ShowMenu("help")

        if renpy.variant("pc"):

            ## 結束按鈕在 iOS 上被禁止，在 Android 和 Web 上則不必要。
            textbutton _("離開") action Quit(confirm=not main_menu)


style navigation_button is gui_button
style navigation_button_text is gui_button_text

style navigation_button:
    size_group "navigation"
    properties gui.button_properties("navigation_button")

style navigation_button_text:
    properties gui.text_properties("navigation_button")


## 主選單畫面 #######################################################################
##
## 用於在 Ren'Py 啟動時顯示主選單。
##
## https://www.renpy.org/doc/html/screen_special.html#main-menu

screen main_menu():

    ## 這可確保替換任何其他選單畫面。
    tag menu

    ## 深色底色（整個畫面）
    add Solid("#1a1a2e")

    ## 背景圖片只顯示在右側（左邊 420px 留給 UI）
    add gui.main_menu_background:
        xpos 420
        yalign 0.5
        fit "contain"

    ## 這個空框使主選單變暗。
    frame:
        style "main_menu_frame"

    ## use 語句在該畫面中包含另一個畫面。主選單的實際內容在導覽畫面中。
    use navigation

    if gui.show_name:

        vbox:
            style "main_menu_vbox"

            text "[config.name!t]":
                style "main_menu_title"

            text "[config.version]":
                style "main_menu_version"


style main_menu_frame is empty
style main_menu_vbox is vbox
style main_menu_text is gui_text
style main_menu_title is main_menu_text
style main_menu_version is main_menu_text

style main_menu_frame:
    xsize 420
    yfill True

    background "gui/overlay/main_menu.png"

style main_menu_vbox:
    xalign 1.0
    xoffset -30
    xmaximum 1200
    yalign 1.0
    yoffset -30

style main_menu_text:
    properties gui.text_properties("main_menu", accent=True)

style main_menu_title:
    properties gui.text_properties("title")

style main_menu_version:
    properties gui.text_properties("version")


## 遊戲選單畫面 ######################################################################
##
## 這列出了遊戲選單畫面的基本公共結構。它透過畫面標題進行呼叫，並顯示背景、標
## 題和導覽。
##
## 滾動參數可以是 None，或者是 "viewport" 與 "vpgrid" 的其中之一。此畫面是要與
## 一個或多個子畫面一起使用，這些子畫面被嵌入（放置）在其中。

screen game_menu(title, scroll=None, yinitial=0.0, spacing=0):

    style_prefix "game_menu"

    if main_menu:
        add gui.main_menu_background
    else:
        add gui.game_menu_background

    frame:
        style "game_menu_outer_frame"

        hbox:

            ## 為導覽部分保留空間。
            frame:
                style "game_menu_navigation_frame"

            frame:
                style "game_menu_content_frame"

                if scroll == "viewport":

                    viewport:
                        yinitial yinitial
                        scrollbars "vertical"
                        mousewheel True
                        draggable True
                        pagekeys True

                        side_yfill True

                        vbox:
                            spacing spacing

                            transclude

                elif scroll == "vpgrid":

                    vpgrid:
                        cols 1
                        yinitial yinitial

                        scrollbars "vertical"
                        mousewheel True
                        draggable True
                        pagekeys True

                        side_yfill True

                        spacing spacing

                        transclude

                else:

                    transclude

    use navigation

    textbutton _("返回"):
        style "return_button"

        action Return()

    label title

    if main_menu:
        key "game_menu" action ShowMenu("main_menu")


style game_menu_outer_frame is empty
style game_menu_navigation_frame is empty
style game_menu_content_frame is empty
style game_menu_viewport is gui_viewport
style game_menu_side is gui_side
style game_menu_scrollbar is gui_vscrollbar

style game_menu_label is gui_label
style game_menu_label_text is gui_label_text

style return_button is navigation_button
style return_button_text is navigation_button_text

style game_menu_outer_frame:
    bottom_padding 45
    top_padding 180

    background "gui/overlay/game_menu.png"

style game_menu_navigation_frame:
    xsize 420
    yfill True

style game_menu_content_frame:
    left_margin 60
    right_margin 30
    top_margin 15

style game_menu_viewport:
    xsize 1380

style game_menu_vscrollbar:
    unscrollable gui.unscrollable

style game_menu_side:
    spacing 15

style game_menu_label:
    xpos 75
    ysize 180

style game_menu_label_text:
    size gui.title_text_size
    color gui.accent_color
    yalign 0.5

style return_button:
    xpos gui.navigation_xpos
    yalign 1.0
    yoffset -45


## 關於畫面 ########################################################################
##
## 此畫面提供有關遊戲和Ren'Py的製作人員名單和版權資訊。
##
## 這個畫面沒有什麼特別的，因此它也可以作為如何製作自訂螢幕的範例。

screen about():

    tag menu

    ## 此 use 語句包含此畫面中的 game_menu 畫面。然後，vbox 子項將包含在
    ## game_menu 畫面內的視口內
    use game_menu(_("關於"), scroll="viewport"):

        style_prefix "about"

        vbox:

            label "[config.name!t]"
            text _("版本 [config.version!t]\n")

            ## gui.about 通常在 options.rpy 中設定。
            if gui.about:
                text "[gui.about!t]\n"

            text _("使用 {a=https://www.renpy.org/}Ren'Py{/a} [renpy.version_only] 製作。 \n\n[renpy.license!t]")


style about_label is gui_label
style about_label_text is gui_label_text
style about_text is gui_text

style about_label_text:
    size gui.label_text_size


## 載入和儲存畫面 #####################################################################
##
## 這些畫面負責讓玩家儲存遊戲並再次載入。由於它們幾乎共享所有共同點，因此兩者
## 都是透過第三個畫面 file_slots 實現的。
##
## https://www.renpy.org/doc/html/screen_special.html#save https://
## www.renpy.org/doc/html/screen_special.html#load

screen save():

    tag menu

    use file_slots(_("儲存"))


screen load():

    tag menu

    use file_slots(_("載入"))


screen file_slots(title):

    default page_name_value = FilePageNameInputValue(pattern=_("頁面 {}"), auto=_("自動儲存"), quick=_("快速儲存"))

    use game_menu(title):

        fixed:

            ## 這確保輸入將在任何按鈕之前獲得輸入事件。
            order_reverse True

            ## 頁面名稱，可以透過點選按鈕進行編輯。
            button:
                style "page_label"

                key_events True
                xalign 0.5
                action page_name_value.Toggle()

                input:
                    style "page_label_text"
                    value page_name_value

            ## 存檔槽的網格。
            grid gui.file_slot_cols gui.file_slot_rows:
                style_prefix "slot"

                xalign 0.5
                yalign 0.5

                spacing gui.slot_spacing

                for i in range(gui.file_slot_cols * gui.file_slot_rows):

                    $ slot = i + 1

                    button:
                        action FileAction(slot)

                        has vbox

                        add FileScreenshot(slot) xalign 0.5

                        text FileTime(slot, format=_("{#file_time}%A, %B %d %Y, %H:%M"), empty=_("空槽")):
                            style "slot_time_text"

                        text FileSaveName(slot):
                            style "slot_name_text"

                        key "save_delete" action FileDelete(slot)

            ## 存取其他頁面的按鈕。
            vbox:
                style_prefix "page"

                xalign 0.5
                yalign 1.0

                hbox:
                    xalign 0.5

                    spacing gui.page_spacing

                    textbutton _("<") action FilePagePrevious()
                    key "save_page_prev" action FilePagePrevious()

                    if config.has_autosave:
                        textbutton _("{#auto_page}A") action FilePage("auto")

                    if config.has_quicksave:
                        textbutton _("{#quick_page}Q") action FilePage("quick")

                    ## range(1, 10) 給出從 1 到 9 的數字。
                    for page in range(1, 10):
                        textbutton "[page]" action FilePage(page)

                    textbutton _(">") action FilePageNext()
                    key "save_page_next" action FilePageNext()

                if config.has_sync:
                    if CurrentScreenName() == "save":
                        textbutton _("上傳同步"):
                            action UploadSync()
                            xalign 0.5
                    else:
                        textbutton _("下載同步"):
                            action DownloadSync()
                            xalign 0.5


style page_label is gui_label
style page_label_text is gui_label_text
style page_button is gui_button
style page_button_text is gui_button_text

style slot_button is gui_button
style slot_button_text is gui_button_text
style slot_time_text is slot_button_text
style slot_name_text is slot_button_text

style page_label:
    xpadding 75
    ypadding 5
    xalign 0.5

style page_label_text:
    textalign 0.5
    layout "subtitle"
    hover_color gui.hover_color

style page_button:
    properties gui.button_properties("page_button")

style page_button_text:
    properties gui.text_properties("page_button")

style slot_button:
    properties gui.button_properties("slot_button")

style slot_button_text:
    properties gui.text_properties("slot_button")


## 首選項畫面 #######################################################################
##
## 首選項畫面允許玩家設定遊戲以更好地適合自己。
##
## https://www.renpy.org/doc/html/screen_special.html#preferences

screen preferences():

    tag menu

    use game_menu(_("設定"), scroll="viewport"):

        vbox:

            hbox:
                box_wrap True

                if renpy.variant("pc") or renpy.variant("web"):

                    vbox:
                        style_prefix "radio"
                        label _("顯示")
                        textbutton _("視窗") action Preference("display", "window")
                        textbutton _("全螢幕") action Preference("display", "fullscreen")

                vbox:
                    style_prefix "check"
                    label _("略過")
                    textbutton _("未讀文字") action Preference("skip", "toggle")
                    textbutton _("選擇後") action Preference("after choices", "toggle")
                    textbutton _("過渡") action InvertSelected(Preference("transitions", "toggle"))

                ## 可以在此處新增 "radio_pref" 或 "check_pref" 類型的其他
                ## vbox，以新增其他建立者定義的首選項。

            null height (4 * gui.pref_spacing)

            hbox:
                style_prefix "slider"
                box_wrap True

                vbox:

                    label _("文字顯示速度")

                    bar value Preference("text speed")

                    label _("自動前進時間")

                    bar value Preference("auto-forward time")

                vbox:

                    if config.has_music:
                        label _("音樂音量")

                        hbox:
                            bar value Preference("music volume")

                    if config.has_sound:

                        label _("音效音量")

                        hbox:
                            bar value Preference("sound volume")

                            if config.sample_sound:
                                textbutton _("測試") action Play("sound", config.sample_sound)


                    if config.has_voice:
                        label _("語音音量")

                        hbox:
                            bar value Preference("voice volume")

                            if config.sample_voice:
                                textbutton _("測試") action Play("voice", config.sample_voice)

                    if config.has_music or config.has_sound or config.has_voice:
                        null height gui.pref_spacing

                        textbutton _("全部靜音"):
                            action Preference("all mute", "toggle")
                            style "mute_all_button"


style pref_label is gui_label
style pref_label_text is gui_label_text
style pref_vbox is vbox

style radio_label is pref_label
style radio_label_text is pref_label_text
style radio_button is gui_button
style radio_button_text is gui_button_text
style radio_vbox is pref_vbox

style check_label is pref_label
style check_label_text is pref_label_text
style check_button is gui_button
style check_button_text is gui_button_text
style check_vbox is pref_vbox

style slider_label is pref_label
style slider_label_text is pref_label_text
style slider_slider is gui_slider
style slider_button is gui_button
style slider_button_text is gui_button_text
style slider_pref_vbox is pref_vbox

style mute_all_button is check_button
style mute_all_button_text is check_button_text

style pref_label:
    top_margin gui.pref_spacing
    bottom_margin 3

style pref_label_text:
    yalign 1.0

style pref_vbox:
    xsize 338

style radio_vbox:
    spacing gui.pref_button_spacing

style radio_button:
    properties gui.button_properties("radio_button")
    foreground "gui/button/radio_[prefix_]foreground.png"

style radio_button_text:
    properties gui.text_properties("radio_button")

style check_vbox:
    spacing gui.pref_button_spacing

style check_button:
    properties gui.button_properties("check_button")
    foreground "gui/button/check_[prefix_]foreground.png"

style check_button_text:
    properties gui.text_properties("check_button")

style slider_slider:
    xsize 525

style slider_button:
    properties gui.button_properties("slider_button")
    yalign 0.5
    left_margin 15

style slider_button_text:
    properties gui.text_properties("slider_button")

style slider_vbox:
    xsize 675


## 歷史畫面 ########################################################################
##
## 這是向玩家顯示對話歷史記錄的畫面。 雖然這個畫面沒有什麼特別的，但它必須存取
## 儲存在 _history_list 中的對話歷史記錄。
##
## https://www.renpy.org/doc/html/history.html

screen history():

    tag menu

    ## 避免預測該螢幕，因為它可能非常大。
    predict False

    use game_menu(_("歷史"), scroll=("vpgrid" if gui.history_height else "viewport"), yinitial=1.0, spacing=gui.history_spacing):

        style_prefix "history"

        for h in _history_list:

            window:

                ## 如果 history_height 為None，這會正確排列事物。
                has fixed:
                    yfit True

                if h.who:

                    label h.who:
                        style "history_name"
                        substitute False

                        ## 從角色中取得 who 文字的顏色（如果已設定）。
                        if "color" in h.who_args:
                            text_color h.who_args["color"]

                $ what = renpy.filter_text_tags(h.what, allow=gui.history_allow_tags)
                text what:
                    substitute False

        if not _history_list:
            label _("對話歷史記錄為空。")


## 這決定了允許在歷史螢幕上顯示哪些標籤。

define gui.history_allow_tags = { "alt", "noalt", "rt", "rb", "art" }


style history_window is empty

style history_name is gui_label
style history_name_text is gui_label_text
style history_text is gui_text

style history_label is gui_label
style history_label_text is gui_label_text

style history_window:
    xfill True
    ysize gui.history_height

style history_name:
    xpos gui.history_name_xpos
    xanchor gui.history_name_xalign
    ypos gui.history_name_ypos
    xsize gui.history_name_width

style history_name_text:
    min_width gui.history_name_width
    textalign gui.history_name_xalign

style history_text:
    xpos gui.history_text_xpos
    ypos gui.history_text_ypos
    xanchor gui.history_text_xalign
    xsize gui.history_text_width
    min_width gui.history_text_width
    textalign gui.history_text_xalign
    layout ("subtitle" if gui.history_text_xalign else "tex")

style history_label:
    xfill True

style history_label_text:
    xalign 0.5


## 幫助畫面 ########################################################################
##
## 提供有關按鍵和滑鼠綁定資訊的畫面。 它使用其他畫面 (keyboard_help,
## mouse_help, and gamepad_help) 來顯示實際幫助。

screen help():

    tag menu

    default device = "keyboard"

    use game_menu(_("説明"), scroll="viewport"):

        style_prefix "help"

        vbox:
            spacing 23

            hbox:

                textbutton _("鍵盤") action SetScreenVariable("device", "keyboard")
                textbutton _("滑鼠") action SetScreenVariable("device", "mouse")

                if GamepadExists():
                    textbutton _("遊戲手柄") action SetScreenVariable("device", "gamepad")

            if device == "keyboard":
                use keyboard_help
            elif device == "mouse":
                use mouse_help
            elif device == "gamepad":
                use gamepad_help


screen keyboard_help():

    hbox:
        label _("回車")
        text _("推進對話並啟動介面。")

    hbox:
        label _("空格")
        text _("無需選擇即可推進對話。")

    hbox:
        label _("方向鍵")
        text _("導覽介面。")

    hbox:
        label _("結束鍵")
        text _("存取遊戲選單。")

    hbox:
        label _("控制鍵")
        text _("按住時跳過對話。")

    hbox:
        label _("製表鍵")
        text _("保持對話跳過。")

    hbox:
        label _("上翻頁鍵")
        text _("回滾到之前的對話。")

    hbox:
        label _("下翻頁鍵")
        text _("前進到稍後的對話。")

    hbox:
        label "H"
        text _("隱藏使用者介面。")

    hbox:
        label "S"
        text _("截取螢幕截圖。")

    hbox:
        label "V"
        text _("切換輔助 {a=https://www.renpy.org/l/voicing} Self-Vocing {/a}.")

    hbox:
        label "Shift+A"
        text _("打開輔助功能選單")


screen mouse_help():

    hbox:
        label _("左鍵")
        text _("推進對話並啟動介面。")

    hbox:
        label _("中鍵")
        text _("隱藏使用者介面。")

    hbox:
        label _("右鍵")
        text _("存取遊戲選單。")

    hbox:
        label _("滑鼠滾輪向上")
        text _("回滾到之前的對話。")

    hbox:
        label _("滑鼠滾輪向下")
        text _("前進到稍後的對話。")


screen gamepad_help():

    hbox:
        label _("右扳機鍵 \nA/ 底鍵")
        text _("推進對話並啟動介面。")

    hbox:
        label _("左扳機 \n 左肩鍵")
        text _("回滾到之前的對話。")

    hbox:
        label _("右肩鍵")
        text _("前進到稍後的對話。")

    hbox:
        label _("十字鍵，搖桿")
        text _("導覽介面。")

    hbox:
        label _("開始，指南，B/右鍵")
        text _("存取遊戲選單。")

    hbox:
        label _("Y/頂鍵")
        text _("隱藏使用者介面。")

    textbutton _("矯正") action GamepadCalibrate()


style help_button is gui_button
style help_button_text is gui_button_text
style help_label is gui_label
style help_label_text is gui_label_text
style help_text is gui_text

style help_button:
    properties gui.button_properties("help_button")
    xmargin 12

style help_button_text:
    properties gui.text_properties("help_button")

style help_label:
    xsize 375
    right_padding 30

style help_label_text:
    size gui.text_size
    xalign 1.0
    textalign 1.0



################################################################################
## 附加畫面
################################################################################


## 確認畫面 ########################################################################
##
## 當 Ren'Py 想問玩家是或否問題時，會呼叫確認畫面。
##
## https://www.renpy.org/doc/html/screen_special.html#confirm

screen confirm(message, yes_action, no_action):

    ## 確保顯示此畫面時其他畫面不會收到輸入。
    modal True

    zorder 200

    style_prefix "confirm"

    add "gui/overlay/confirm.png"

    frame:

        vbox:
            xalign .5
            yalign .5
            spacing 45

            label _(message):
                style "confirm_prompt"
                xalign 0.5

            hbox:
                xalign 0.5
                spacing 150

                textbutton _("是") action yes_action
                textbutton _("否") action no_action

    ## 右鍵點選並結束回答 "no".
    key "game_menu" action no_action


style confirm_frame is gui_frame
style confirm_prompt is gui_prompt
style confirm_prompt_text is gui_prompt_text
style confirm_button is gui_medium_button
style confirm_button_text is gui_medium_button_text

style confirm_frame:
    background Frame([ "gui/confirm_frame.png", "gui/frame.png"], gui.confirm_frame_borders, tile=gui.frame_tile)
    padding gui.confirm_frame_borders.padding
    xalign .5
    yalign .5

style confirm_prompt_text:
    textalign 0.5
    layout "subtitle"

style confirm_button:
    properties gui.button_properties("confirm_button")

style confirm_button_text:
    properties gui.text_properties("confirm_button")


## 快進提示畫面 ######################################################################
##
## 顯示 skip_indicator 畫面以指示快進正在進行中。
##
## https://www.renpy.org/doc/html/screen_special.html#skip-indicator

screen skip_indicator():

    zorder 100
    style_prefix "skip"

    frame:

        hbox:
            spacing 9

            text _("快進中")

            text "▸" at delayed_blink(0.0, 1.0) style "skip_triangle"
            text "▸" at delayed_blink(0.2, 1.0) style "skip_triangle"
            text "▸" at delayed_blink(0.4, 1.0) style "skip_triangle"


## 此變換用於使箭頭依序閃爍。
transform delayed_blink(delay, cycle):
    alpha .5

    pause delay

    block:
        linear .2 alpha 1.0
        pause .2
        linear .2 alpha 0.5
        pause (cycle - .4)
        repeat


style skip_frame is empty
style skip_text is gui_text
style skip_triangle is skip_text

style skip_frame:
    ypos gui.skip_ypos
    background Frame("gui/skip.png", gui.skip_frame_borders, tile=gui.frame_tile)
    padding gui.skip_frame_borders.padding

style skip_text:
    size gui.notify_text_size

style skip_triangle:
    ## 我們必須使用帶有黑色右指小三角形字形的字型。
    font "DejaVuSans.ttf"


## 提醒畫面 ########################################################################
##
## 通知畫面用於向玩家顯示訊息。 （例如，當遊戲快速儲存或截取螢幕截圖時。）
##
## https://www.renpy.org/doc/html/screen_special.html#notify-screen

screen notify(message):

    zorder 100
    style_prefix "notify"

    frame at notify_appear:
        text "[message!tq]"

    timer 3.25 action Hide('notify')


transform notify_appear:
    on show:
        alpha 0
        linear .25 alpha 1.0
    on hide:
        linear .5 alpha 0.0


style notify_frame is empty
style notify_text is gui_text

style notify_frame:
    ypos gui.notify_ypos

    background Frame("gui/notify.png", gui.notify_frame_borders, tile=gui.frame_tile)
    padding gui.notify_frame_borders.padding

style notify_text:
    properties gui.text_properties("notify")


## NVL 畫面 ######################################################################
##
## 此畫面用於 NVL 模式對話和選單。
##
## https://www.renpy.org/doc/html/screen_special.html#nvl


screen nvl(dialogue, items=None):

    window:
        style "nvl_window"

        has vbox:
            spacing gui.nvl_spacing

        ## 在 vpgrid 或 vbox 中顯示對話。
        if gui.nvl_height:

            vpgrid:
                cols 1
                yinitial 1.0

                use nvl_dialogue(dialogue)

        else:

            use nvl_dialogue(dialogue)

        ## 顯示選單（如果給定）。如果 config.narrator_menu 設定為 True，則選單
        ## 可能無法正確顯示。
        for i in items:

            textbutton i.caption:
                action i.action
                style "nvl_button"

    add SideImage() xalign 0.0 yalign 1.0


screen nvl_dialogue(dialogue):

    for d in dialogue:

        window:
            id d.window_id

            fixed:
                yfit gui.nvl_height is None

                if d.who is not None:

                    text d.who:
                        id d.who_id

                text d.what:
                    id d.what_id


## 這控制可以一次顯示的 NVL 模式條目的最大數量。
define config.nvl_list_length = gui.nvl_list_length

style nvl_window is default
style nvl_entry is default

style nvl_label is say_label
style nvl_dialogue is say_dialogue

style nvl_button is button
style nvl_button_text is button_text

style nvl_window:
    xfill True
    yfill True

    background "gui/nvl.png"
    padding gui.nvl_borders.padding

style nvl_entry:
    xfill True
    ysize gui.nvl_height

style nvl_label:
    xpos gui.nvl_name_xpos
    xanchor gui.nvl_name_xalign
    ypos gui.nvl_name_ypos
    yanchor 0.0
    xsize gui.nvl_name_width
    min_width gui.nvl_name_width
    textalign gui.nvl_name_xalign

style nvl_dialogue:
    xpos gui.nvl_text_xpos
    xanchor gui.nvl_text_xalign
    ypos gui.nvl_text_ypos
    xsize gui.nvl_text_width
    min_width gui.nvl_text_width
    textalign gui.nvl_text_xalign
    layout ("subtitle" if gui.nvl_text_xalign else "tex")

style nvl_thought:
    xpos gui.nvl_thought_xpos
    xanchor gui.nvl_thought_xalign
    ypos gui.nvl_thought_ypos
    xsize gui.nvl_thought_width
    min_width gui.nvl_thought_width
    textalign gui.nvl_thought_xalign
    layout ("subtitle" if gui.nvl_text_xalign else "tex")

style nvl_button:
    properties gui.button_properties("nvl_button")
    xpos gui.nvl_button_xpos
    xanchor gui.nvl_button_xalign

style nvl_button_text:
    properties gui.text_properties("nvl_button")


## 氣泡畫面 ########################################################################
##
## 氣泡螢幕用於在使用對話氣泡時向玩家顯示對話。氣泡螢幕採用與 say 螢幕相同
## 的參數，必須建立一個 id 為 "what" 的可顯示內容，並且可以建立可顯示內容帶有
## "namebox", "who", 和 "window" ID。
##
## https://www.renpy.org/doc/html/bubble.html#bubble-screen

screen bubble(who, what):
    style_prefix "bubble"

    window:
        id "window"

        if who is not None:

            window:
                id "namebox"
                style "bubble_namebox"

                text who:
                    id "who"

        text what:
            id "what"

        default ctc = None
        showif ctc:
            add ctc

style bubble_window is empty
style bubble_namebox is empty
style bubble_who is default
style bubble_what is default

style bubble_window:
    xpadding 30
    top_padding 5
    bottom_padding 5

style bubble_namebox:
    xalign 0.5

style bubble_who:
    xalign 0.5
    textalign 0.5
    color "#000"

style bubble_what:
    align (0.5, 0.5)
    text_align 0.5
    layout "subtitle"
    color "#000"

define bubble.frame = Frame("gui/bubble.png", 55, 55, 55, 95)
define bubble.thoughtframe = Frame("gui/thoughtbubble.png", 55, 55, 55, 55)

define bubble.properties = {
    "bottom_left" : {
        "window_background" : Transform(bubble.frame, xzoom=1, yzoom=1),
        "window_bottom_padding" : 27,
    },

    "bottom_right" : {
        "window_background" : Transform(bubble.frame, xzoom=-1, yzoom=1),
        "window_bottom_padding" : 27,
    },

    "top_left" : {
        "window_background" : Transform(bubble.frame, xzoom=1, yzoom=-1),
        "window_top_padding" : 27,
    },

    "top_right" : {
        "window_background" : Transform(bubble.frame, xzoom=-1, yzoom=-1),
        "window_top_padding" : 27,
    },

    "thought" : {
        "window_background" : bubble.thoughtframe,
    }
}

define bubble.expand_area = {
    "bottom_left" : (0, 0, 0, 22),
    "bottom_right" : (0, 0, 0, 22),
    "top_left" : (0, 22, 0, 0),
    "top_right" : (0, 22, 0, 0),
    "thought" : (0, 0, 0, 0),
}



################################################################################
## 行動裝置變體
################################################################################

style pref_vbox:
    variant "medium"
    xsize 675

## 由於可能不存在滑鼠，我們將快捷選單替換為使用更少、更大、更容易觸控的按鈕的
## 版本。
screen quick_menu():
    variant "touch"

    zorder 100

    if quick_menu:

        hbox:
            style "quick_menu"
            style_prefix "quick"

            textbutton _("返回") action Rollback()
            textbutton _("略過") action Skip() alternate Skip(fast=True, confirm=True)
            textbutton _("自動") action Preference("auto-forward", "toggle")
            textbutton _("選單") action ShowMenu()


style window:
    variant "small"
    background "gui/phone/textbox.png"

style radio_button:
    variant "small"
    foreground "gui/phone/button/radio_[prefix_]foreground.png"

style check_button:
    variant "small"
    foreground "gui/phone/button/check_[prefix_]foreground.png"

style nvl_window:
    variant "small"
    background "gui/phone/nvl.png"

style main_menu_frame:
    variant "small"
    background "gui/phone/overlay/main_menu.png"

style game_menu_outer_frame:
    variant "small"
    background "gui/phone/overlay/game_menu.png"

style game_menu_navigation_frame:
    variant "small"
    xsize 510

style game_menu_content_frame:
    variant "small"
    top_margin 0

style game_menu_viewport:
    variant "small"
    xsize 1305

style pref_vbox:
    variant "small"
    xsize 600

style bar:
    variant "small"
    ysize gui.bar_size
    left_bar Frame("gui/phone/bar/left.png", gui.bar_borders, tile=gui.bar_tile)
    right_bar Frame("gui/phone/bar/right.png", gui.bar_borders, tile=gui.bar_tile)

style vbar:
    variant "small"
    xsize gui.bar_size
    top_bar Frame("gui/phone/bar/top.png", gui.vbar_borders, tile=gui.bar_tile)
    bottom_bar Frame("gui/phone/bar/bottom.png", gui.vbar_borders, tile=gui.bar_tile)

style scrollbar:
    variant "small"
    ysize gui.scrollbar_size
    base_bar Frame("gui/phone/scrollbar/horizontal_[prefix_]bar.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/phone/scrollbar/horizontal_[prefix_]thumb.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)

style vscrollbar:
    variant "small"
    xsize gui.scrollbar_size
    base_bar Frame("gui/phone/scrollbar/vertical_[prefix_]bar.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/phone/scrollbar/vertical_[prefix_]thumb.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)

style slider:
    variant "small"
    ysize gui.slider_size
    base_bar Frame("gui/phone/slider/horizontal_[prefix_]bar.png", gui.slider_borders, tile=gui.slider_tile)
    thumb "gui/phone/slider/horizontal_[prefix_]thumb.png"

style vslider:
    variant "small"
    xsize gui.slider_size
    base_bar Frame("gui/phone/slider/vertical_[prefix_]bar.png", gui.vslider_borders, tile=gui.slider_tile)
    thumb "gui/phone/slider/vertical_[prefix_]thumb.png"

style slider_vbox:
    variant "small"
    xsize None

style slider_slider:
    variant "small"
    xsize 900
