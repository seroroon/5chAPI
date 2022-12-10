# 暗号ハッシュ関数でメッセージ認証する標準ライブラリ
import hmac
# ハッシュ化する標準ライブラリ
import hashlib
# http通信ライブラリ
import httpx
# 文字化け対策ライブラリ
import cchardet

class authenticate_5chAPI:
    
    # 使うapiキーとHMkeyとuserAgentとX-2ch-UAはセット。
    # https://prokusi.wiki.fc2.com/wiki/%E8%AC%8E%E3%81%AE%E6%96%87%E5%AD%97%E5%88%97
    def __init__(    

        self,
        AppKey,
        HMKey,
        # この値は何でもいいらしいけど変更したいならインスタンス作成時に引数からどうぞ
        CT="1234567890",
        AppUrl = 'https://api.5ch.net/v1/auth/',
        # User-AgentとX-2ch-UAはAppKeyとHMKeyと対応するものを使用。変更したいならインスタンス作成時に引数からどうぞ
        headers = { 'User-Agent' : 'Monazilla/1.00 JaneStyle/4.23 Windows/10.0.22000', 'X-2ch-UA': 'JaneStyle/4.23'},
    
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
        values = {'ID' : '', 'PW' : '', 'KY' : self.AppKey, 'CT' : self.CT, 'HB' : HB }
            
        response = httpx.post(self.App_Url,data=values,headers=self.headers)

        #邪魔な文字列あるからsessionIDだけ上手い感じで抽出
        sid = response.text
        sid_split_num = len(sid.split(':')[0])+1
        sid = sid[sid_split_num:]
        sid = sid.split('\'')[0]
        
        return sid


class use_5chAPI(authenticate_5chAPI):

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





# ************処理テスト用(name == mainがあるのでモジュールとして読み込まれたときには実行されない)************* #



def main():

    instance = use_5chAPI(
    
    AppKey = 'a6kwZ1FHfwlxIKJWCq4XQQnUTqiA1P',
    HMKey = 'ZDzsNQ7PcOOGE2mXo145X6bt39WMz6',
    CT = '1234567890',
    AppUrl = 'https://api.5ch.net/v1/auth/',
    headers =  { 'User-Agent' : 'Monazilla/1.00 JaneStyle/4.23 Windows/10.0.22000', 'X-2ch-UA': 'JaneStyle/4.23'}
    
    )

    dat = instance.getDAT('mi', 'news4vip', '1670646031', sid=instance.sessionIdentifier_Create())
    print(dat)

if __name__ == '__main__':
    main()

