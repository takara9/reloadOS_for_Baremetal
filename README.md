# IBM Cloud Infrastructure ベアメタルサーバーの OSリロードツール

OS reload tool of Barematal server with sshkey, post-install script, change Operationg system


### 使用前の準備事項

 環境変数を事前にセットしてください。

   export SOFTLAYER_API_KEY=<API KEYをセット>
   export SOFTLAYER_USERNAME=<USER NAMEをセット>

   環境変数は、IBM Cloud Infrastructure （旧SoftLayer カスタマーポータル）
   のメニューバーから Accout -> Users -> API KEY で参照できます。


### doReloadOSforBaremetal.py

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


### getInstalledOS.py

 ベアメタルサーバーにインストールされたOSのスペックを表示します。

 serverId を自身のベアメタルのIDに置き換えて利用ください。
   slcli server list でIDを表示することができます。


## listBaremetalImageId.py

 ベアメタルにインストールできるOSイメージをリストします。

 location と pkgId を自身の環境に合わせて変更してください。

 location はデータセンターを表す記号です。 
   東京DC tok02

 pkgIdは、ベアメタルのパッケージの番号です。
   getBaremetalPkg.pyでリストできます。


## getBaremetalPkg.py

 ベアメタルのインストール・パッケージのリストを表示します。
 注意 
   内部的に利用されているBluemix PaaSのパッケージなど含めれますので、
   全てが利用できるわけではありません。
