import FiveChannelAPI


def use5chApiTest():

    instance = FiveChannelAPI.use_5chAPI(
        
        AppKey = '',
        HMKey = '',
        CT = '',
        AppUrl = 'https://api.5ch.net/v1/auth/',
        headers =  { 'User-Agent' : 'Monazilla/1.00 JaneStyle/4.23 Windows/10.0.22000', 'X-2ch-UA': 'JaneStyle/4.23'}
        
        )

    dat = instance.getDAT('swallow', 'livejupiter', '1609426799', sid=instance.sessionIdentifier_Create())
    


use5chApiTest()