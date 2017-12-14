#!/usr/bin/env python    
# coding:utf-8
"""
  ベアメタルのOSを再ロードしてします。 
  OSをリロードすることで、ディスクのデータが全て消去されますが、確認もプロンプトはありません。 

  再ロード時に、下記のOSの変更、ssh Key、Post-Install スクリプトの指定ができます。

   priceId = ベアメタル用 OSを含めたイメージの番号で、
             listBaremetalImageId.pyでリストできます。

   sshKey1 = ログインに利用するssh公開鍵のIDです。
             slcli sshkey list コマンドで取得できます。

   serverId = ベアメタル・サーバーのIDです。
             slcli server list コマンドで取得できます。

   pScriptUrl = OSをリロードした後に一回だけ実行されるスクリプトのURLです。
               GitHubを利用することもできます。以下はGitHubを指定するURLの例です。
    'https://raw.githubusercontent.com/takara9/ProvisioningScript/master/ubuntu_hack1'

 環境変数
   export SOFTLAYER_API_KEY=<API KEYをセット>
   export SOFTLAYER_USERNAME=<USER NAMEをセット>
   環境変数は、IBM Cloud Infrastructure （旧SoftLayer カスタマーポータル）
   のメニューバーから Accout -> Users -> API KEY で参照できます。

"""

import SoftLayer
from pprint import pprint as pp

class doReloadOS():

    def __init__(self):
        self.client = SoftLayer.Client()

    def main(self):
        """
        OSをリロードすることで、ディスクのデータが全て消去されます。
        """
        # 以下を変更してください
        priceId = 37622
        sshKey1 = 395475
        sshKey2 = 355919
        serverId = 866447
        pScriptUrl = 'https://raw.githubusercontent.com/takara9/ProvisioningScript/master/ubuntu_hack1'

        config = {
            'customProvisionScriptUri': pScriptUrl,
            'sshKeyIds': [sshKey1, sshKey2],
            'itemPrices': [{'id': priceId}]
        }

        output = self.client['Hardware_Server'].reloadOperatingSystem('FORCE', config, id=serverId)
        pp(config)
        print "RESULT =",output


if __name__ == "__main__":
    main = doReloadOS()
    main.doReloadOS()
