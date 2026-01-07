## 此文件包含可以更改以自訂您的遊戲的選項。
##
## 以兩個'#' 標記開頭的行是註釋，您不應取消註釋它們。以單一'#' 標記開頭的行是
## 註解掉的程式碼，您可能需要在適當的時候取消註解它們。


## 基本 ##########################################################################

## 一個人類可讀的遊戲名稱。這用於設定預設視窗標題，並顯示在介面和錯誤報告中。
##
## 字串周圍的 _() 標記其為符合翻譯條件。

define config.name = _("虛構敘事")


## 決定上面給出的標題是否顯示在主選單畫面上。將其設為 False 以隱藏標題。

define gui.show_name = False


## 遊戲的版本

define config.version = "1.0"


## 放置在遊戲的關於螢幕上的文字。將文字放在三引號之間，並在段落之間留一個空行。

define gui.about = _p("""
""")


## 遊戲的短名稱，用於建立發行版中的可執行檔和目錄。它必須只是 ASCII，並且不能
## 包含空格、冒號或分號。

define build.name = "FictionalNarrative"


## 聲音和音樂 #######################################################################

## 這三個變數控制預設向播放器顯示哪些混音器。將其中之一設為 False 將隱藏相應的
## 混音器。

define config.has_sound = True
define config.has_music = True
define config.has_voice = True


## 要允許使用者在聲音或語音通道上播放測試聲音，請取消註釋下面的行並使用它來設
## 定要播放的範例聲音。

# define config.sample_sound = "sample-sound.ogg"
# define config.sample_voice = "sample-voice.ogg"


## 取消註解以下行以設定玩家在主選單時播放的音訊檔案。該檔案將繼續在遊戲中播
## 放，直到停止或播放另一個檔案。

# define config.main_menu_music = "main-menu-theme.ogg"


## 過渡 ##########################################################################
##
## 這些變數設定在發生某些事件時使用的過渡。每個變數都應設定為過渡，或 None 表
## 示不應使用任何過渡。

## 進入或退出遊戲選單。

define config.enter_transition = dissolve
define config.exit_transition = dissolve


## 在遊戲選單畫面之間。

define config.intra_transition = dissolve


## 遊戲載入後使用的過渡。

define config.after_load_transition = None


## 在遊戲結束後進入主選單時使用。

define config.end_game_transition = None


## 用於設定遊戲開始時使用的過渡的變數不存在。相反，需要在顯示初始場景後使用
## with 語句。


## 視窗管理 ########################################################################
##
## 這控制何時顯示對話視窗。如果 "show" ，則始終顯示。如果 "hide" ，則僅在存在
## 對話時顯示。如果 "auto" ，則視窗在場景陳述之前隱藏，並在顯示對話後再次顯示。
##
## 遊戲開始後，可以使用 "window show", "window hide", 和 "window auto" 語句更
## 改。

define config.window = "show"


## 用於顯示和隱藏對話視窗的轉換

define config.window_show_transition = Dissolve(.2)
define config.window_hide_transition = Dissolve(.2)


## 首選項預設值 ######################################################################

## 控制預設文字速度。預設值 0 是無限的，而任何其他數字是每秒鍵入的字元數。

default preferences.text_cps = 0


## 預設自動轉送延遲。數字越大，等待時間越長，有效範圍為 0 到 30。

default preferences.afm_time = 15


## 儲存檔目錄 #######################################################################
##
## 控制Ren'Py將放置該遊戲的儲存文件的平臺特定位置。儲存文件將放置在：
##
## Windows: %APPDATA\RenPy\<config.save_directory>
##
## Macintosh: $HOME/Library/RenPy/<config.save_directory>
##
## Linux: $HOME/.renpy/<config.save_directory>
##
## 通常不應更改，如果更改，則應始終是文字字串，而不是表達式。

define config.save_directory = "galgametest-1756819193"


## 圖示 ##########################################################################
##
## 顯示在工作列或擴充座上的圖示。

define config.window_icon = "gui/window_icon.png"


## 構置設定 ########################################################################
##
## 本節控制Ren'Py如何將您的專案轉換為發布版本。

init python:

    ## 以下函式採用檔案模式。 檔案模式不區分大小寫，並與相對於基底目錄的路徑進
    ## 行匹配，無論是否有前導 /。 如果多個模式匹配，則使用第一個模式。
    ##
    ## 在一個模式中：
    ##
    ## / 是目錄分隔符號。
    ##
    ## * 匹配目錄分隔符號之外的所有字元。
    ##
    ## ** 匹配所有字元，包括目錄分隔符。
    ##
    ## 就比如， "*.txt" 匹配 base 目錄中的txt文件， "game/**.ogg" 匹配遊戲目錄
    ## 或其任何子目錄中的 ogg 文件，和 "**.psd" 匹配專案中任意位置的 psd 檔案。

    ## 將檔案分類為 None 以將它們從建置的發布版本中排除。

    build.classify('**~', None)
    build.classify('**.bak', None)
    build.classify('**/.**', None)
    build.classify('**/#**', None)
    build.classify('**/thumbs.db', None)

    ## 要歸檔文件，請將其分類為 'archive' 。

    # build.classify('game/**.png', 'archive')
    # build.classify('game/**.jpg', 'archive')

    ## 與文件模式匹配的文件在 Mac 應用程式建置中會重複，因此它們會同時出現在應
    ## 用程式和 zip 檔案中。

    build.documentation('*.html')
    build.documentation('*.txt')


## 執行應用程式內購買需要 Google Play 授權金鑰。它可以在 Google Play 開發者控
## 制台的 "Monetize" > "Monetization Setup" > "Licensing" 下找到。

# define build.google_play_key = "..."


## 與 itch.io 專案關聯的使用者名稱和專案名稱，以斜線分隔。

# define build.itch_project = "renpytom/test-project"
