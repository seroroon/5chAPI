# 暗号ハッシュ関数でメッセージ認証する標準ライブラリ
import hmac
# ハッシュ化する標準ライブラリ
import hashlib
# http通信ライブラリ
import httpx
# 文字化け対策ライブラリ
import cchardet


# *****************************某所にあるAPIを使った処理******************************** #

#こいつの役目はsidの生成だけかもわからん
class authenticate_5chAPI_sidCreate:
    

    def __init__(    

        self,
        AppKey,
        HMKey,
        # この値は何でもいいらしいけど変更したいならインスタンス作成時に引数からどうぞ
        CT="",
        AppUrl = '',
        # User-AgentとX-2ch-UAはAppKeyとHMKeyと対応するものを使用。変更したいならインスタンス作成時に引数からどうぞ
        # そうでもないかも。ここのheaderを専ブラと同じにすると専ブラのsid取得できるかも
        headers = { 'User-Agent' : '', 'X-2ch-UA': ''},
    
    ):
        
        # インスタンス変数(作成するインスタンス毎に変数の中身が変わる)
        self.AppKey = AppKey
        self.HMKey = HMKey
        self.CT = CT
        self.App_Url = AppUrl
        self.headers = headers

    # セッションIDを作ってreturn
    def sessionIdentifier_Create(self):
        
        message = self.AppKey + self.CT
        # python3系統ではhmac.newの引数はbytearrayで変換すること
        HB = hmac.new(bytearray(self.HMKey,"ASCII"), bytearray(message,"ASCII"), hashlib.sha256).hexdigest()
        # 浪人にログインするならIDとPW入力
        values = {'ID' : '', 'PW' : '', 'KY' : self.AppKey, 'CT' : self.CT, 'HB' : HB }
            
        response = httpx.post(self.App_Url,data=values,headers=self.headers,timeout=None)

        #邪魔な文字列あるからsessionIDだけ上手い感じで抽出
        sid = response.text
        sid_split_num = len(sid.split(':')[0])+1
        sid = sid[sid_split_num:]
        sid = sid.split('\'')[0]
        
        return sid



class use_5chAPI(authenticate_5chAPI_sidCreate):

    def getDAT(
        
        self,
        serverName, 
        boardName, 
        threadId, 
        sid
    
        ):
    
        message = "/v1/" + serverName + "/" + boardName + "/" + threadId + sid + self.AppKey
        hobo = hmac.new(bytearray(self.HMKey,"ASCII"), bytearray(message,"ASCII"), hashlib.sha256).hexdigest()
        url = self.App_Url[:-5] + serverName + "/" + boardName + "/" + threadId
        values = { 'sid' : sid, 'hobo' : hobo, 'appkey': self.AppKey }
        response = httpx.post(url,data=values,headers=self.headers,timeout=None)
        # 文字コードにISO-8859-1が使われていて文字化けする場合は以下の1行を入れる
        response.encoding = cchardet.detect(response.content)["encoding"]
        return response.text
    
    def send_message(

        self,
        serverName, 
        boardName, 
        threadId, 
        sid

    ):

        message = "/v1/" + serverName + "/" + boardName + "/" + threadId + sid + self.AppKey
        hobo = hmac.new(bytearray(self.HMKey,"ASCII"), bytearray(message,"ASCII"), hashlib.sha256).hexdigest()
        url = self.App_Url[:-5] + serverName + "/" + boardName + "/" + threadId
        values = { 'sid' : sid, 'hobo' : hobo, 'appkey': self.AppKey }
        response = httpx.post(url,data=values,headers=self.headers,timeout=None)
        # 文字コードにISO-8859-1が使われていて文字化けする場合は以下の1行を入れる
        response.encoding = cchardet.detect(response.content)["encoding"]


# *********************************ここから自作処理*************************************** #

class create_header_5ch:

    def __init__(

        self,
        accept = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        acceptEncoding = None,
        acceptLanguage = None, # Noneで良いと思うけどこれ設定したら規制回避しやすいとかあるなら設定したらいい
        browserForgery = None, # Noneなら汎用ブラウザのUAを使用
        connection = "keep-alive", # スレ立てとかするときにいるかも
        cacheControl = "max-age=0", # キャッシュの期限。max-age=0ならキャッシュが生成された瞬間に期限切れ
        contentType = None,
        host = None, # http/2ではauthorityで代替する。ブラウザによって変わるのかは不明。自動取得するようにしておく
        origin = None, # フェッチの原点 
        referer = None, # 現在リクエストされているページへのリンク先を持った直前のアドレス
        userAgent = None, # デフォルトでは汎用ブラウザのUAにしようかな
        
        # UA_RandamSelect = 乱数  // 有効そうなUAを自動取得してきてその数のlen分の乱数を生成してそれによって使うUAを自動指定とか良さそう


    ):

        self.accept = accept
        self.acceptEncoding = acceptEncoding
        self.acceptLanguage = acceptLanguage
        self.browserForgery = browserForgery
        self.connection = connection
        self.cacheControl = cacheControl
        self.contentType = contentType
        self.host = host
        self.origin = origin
        self.referer = referer

        self.userAgent = userAgent
    
    def createHeader_complete(self):

        if (self.browserForgery == None):
            self.userAgent = self.userAgent
            self.acceptEncoding = "gzip, deflate, br"
            self.contentType = "application/x-www-form-urlencoded"
            self.host = "自動取得処理"
            self.origin = f"https://{self.host}"
            self.referer = f"https://{self.host}/自動取得/" # or そもそも完全に事前のurlを送れるような処理にするか

        
        if (self.browserForgery == "mate"):
            self.userAgent = "mateのua"
            self.acceptEncoding = "mateのae"
            self.contentType = "mateのct"


    def createHeader_Get(self,headerComplete=None):

        if (headerComplete == None) or (self.acceptEncoding == None):
            return print("createHeader_completeを引数に渡してください")
        

        


# ************処理テスト用(name == mainがあるのでモジュールとして読み込まれたときには実行されない)************* #



def main():

    instance = use_5chAPI(
    
        AppKey = '',
        HMKey = '',
        CT = '',
        AppUrl = '',
        headers =  { 'User-Agent' : '', ''}
    
    )

    #instance.send_message('mi', 'news4vip', '1670714221', sid=instance.sessionIdentifier_Create())

    dat = instance.getDAT('mi', 'news4vip', '1671003743', sid=instance.sessionIdentifier_Create())
    print(dat)

if __name__ == '__main__':
    main()

