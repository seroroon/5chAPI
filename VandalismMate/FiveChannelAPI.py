# 暗号ハッシュ関数でメッセージ認証する標準ライブラリ
import hmac
# ハッシュ化する標準ライブラリ
import hashlib
# http通信ライブラリ
import httpx
# 文字化け対策ライブラリ
import cchardet

import json

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
        headers = {""},
    
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


# *********************************ここから自作がメインの処理*************************************** #

# デザインパターンのstateとStorageが使えそうなら使ってもいいかも


class create_requestDate_5ch:

    def __init__(

        self,
        nameField = None, # いわゆるハンドルネーム
        mailField = None, # メール欄
        textField = None, # 書き込み本文
        forumName = None, # urlの板名のところ, 例 → liveanarchy,news4vip
        threadNumber = None, # urlの10桁くらいの数字のところ, 例 → 1723801759
        time = None, 
        submit = None,
        oekakiThread1 = None

    ):

        self.nameField = nameField
        self.mailField = mailField
        self.textField = textField
        self.forumName = forumName
        self.threadNumber = threadNumber
        self.time = time
        self.submit = submit
        self.oekakiThread1 = oekakiThread1
    

    def create_requestDate_get(self):
        
        body = {

        "FROM": self.nameField,
        "mail": self.mailField,
        "MESSAGE": self.textField,
        "bbs": self.forumName,
        "key": self.threadNumber,
        "time": self.time,
        "submit": self.submit,
        "oekaki_thread1": self.oekakiThread1,

        }

        return body



class create_header_5ch():

    def __init__(

        self,
        bodyParam : create_requestDate_5ch,
        #リクエストラインの記述いるかも
        accept = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        acceptEncoding = None,
        acceptLanguage = None, # Noneで良いと思うけどこれ設定したら規制回避しやすいとかあるなら設定したらいい
        browserForgery = None, # Noneなら汎用ブラウザのUAを使用
        connection = "keep-alive", # スレ立てとかするときにいるかも
        cacheControl = "max-age=0", # キャッシュの期限。max-age=0ならキャッシュが生成された瞬間に期限切れ
        contentType = None,
        host = None, # ここで指定したところにリクエストが送られる。http/2ではauthorityで代替する。ブラウザによって変わるのかは不明。自動取得するようにしておく
        origin = None, # フェッチの原点 
        referer = None, # 現在リクエストされているページへのリンク先を持った直前のアドレス
        secFetchDest =  "document", # リクエストの宛先を示します(audioとかimageとか)宛先はドキュメント (HTML または XML) であり、要求はユーザーが開始したトップレベル ナビゲーションの結果です (たとえば、ユーザーがリンクをクリックした結果)。
        secFetchMode = "navigate",  
        secFetchSite = "same-origin",
        secFetchUser = "?1", # SFD～SFUはユーザーが同じオリジンの別のページへのリンクをクリックした場合のリクエストのテンプレみたいなもん
        secChUa =  '" Not A;Brand";v="99", "Chromium";v="92"',  # User-Agent Client Hints (新方式UserAgent)
        secChUaMobile =  "?0",  # ?0ならデスクトップ ?1ならモバイル
        upgradeInsecureRequests = "1", # Client側がhttpコンテンツをhttpsコンテンツにリダイレクトするのに対応しているかどうかの指定
        userAgent = None, # デフォルトでは汎用ブラウザのUAにしようかな
        
    
        #HTTPリクエストメッセージボディの設定が可能かも

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
        self.secFetchDest = secFetchDest
        self.secFetchMode = secFetchMode 
        self.secFetchSite = secFetchSite
        self.secFetchUser = secFetchUser
        self.secChUa = secChUa
        self.secChUaMobile = secChUaMobile
        self.upgradeInsecureRequests = upgradeInsecureRequests
        self.userAgent = userAgent
        
        # ほぼほぼreferer作成用
        self.bodyParam = bodyParam

    def createHeader_complete(self):

        if (self.browserForgery == None):
            self.userAgent = self.userAgent
            self.acceptEncoding = "gzip, deflate, br"
            self.acceptLanguage = "ja,en-US;q=0.9,en;q=0.8"
            self.contentType = "application/x-www-form-urlencoded"
            self.host = self.host if ".5ch.net" in self.host else self.host+".5ch.net"
            self.origin = f"https://{self.host}"
            self.referer = f"https://{self.host}/{self.bodyParam.forumName}/{self.bodyParam.threadNumber}"
            self.userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"

        
        if (self.browserForgery == "mate"):
            self.userAgent = "mateのua"
            self.acceptEncoding = "mateのae"
            self.contentType = "mateのct"



    def createHeader_Get(self):

        create_header_5ch.createHeader_complete(self)

        headers = {

            "accept": self.accept,
            "accept-encoding": self.acceptEncoding,
            "accept-language": self.acceptLanguage,
            "connection": self.connection,
            "cache-control": self.cacheControl,
            "content-type": self.contentType,
            "host": self.host,
            "origin": self.origin,
            "referer": self.referer,
            "sec-fetch-dest": self.secFetchDest,
            "sec-fetch-mode": self.secFetchMode,
            "sec-fetch-site": self.secFetchSite,
            "sec-fetch-user": self.secFetchUser,
            "sec-ch-ua": self.secChUa,
            "sec-ch-ua-mobile": self.secChUaMobile, 
            "upgrade-insecure-requests": self.upgradeInsecureRequests,
            "user-agent": self.userAgent

        }

        return json.dumps(headers)
        


# ************処理テスト用(name == mainがあるのでモジュールとして読み込まれたときには実行されない)************* #



def main():

    instance = use_5chAPI(
    
        AppKey = '',
        HMKey = '',
        CT = '',
        AppUrl = '',
        headers =  { }
    
    )

    #instance.send_message('mi', 'news4vip', '1670714221', sid=instance.sessionIdentifier_Create())

    dat = instance.getDAT('mi', 'news4vip', '1671003743', sid=instance.sessionIdentifier_Create())
    print(dat)

# header作成のテスト
def main2():


    instance1 = create_requestDate_5ch(

        nameField ="",
        mailField = "",
        textField = "てすｔｔっとお",
        forumName = "news4vip",
        threadNumber = "1671613929",
        time = "",
        submit = "書き込み",
        oekakiThread1 = ""

    )

    requestDate = instance1.create_requestDate_get()
    print(requestDate)
    print(requestDate["bbs"])

    instance2 = create_header_5ch(

        instance1, # create_requestDate_5chのインスタンス
        host = "mi", # サーバー名だけでもいいし「サーバー名.5ch.net」まで入力してもいい。両方の結果が同じになるようにしてる
        browserForgery=None

    )

    header_5ch = instance2.createHeader_Get()
    print(header_5ch)
    print(type(header_5ch))
    print(instance2.origin+"/test/bbs.cgi")
    httpx.post("https://mi.5ch.net/test/bbs.cgi",data=requestDate.encode("sjis"),json=header_5ch)

if __name__ == '__main__':
    main2()

