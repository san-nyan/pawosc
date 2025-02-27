# pawosc
this is a terrible awful app that takes your current spotify song and sends an OSC message to the vrchat chatbox with the contents

called pawosc cause im paw on vrchat

please dont complain to me if this breaks for you but 

if (for some ungodly reason) you want to run this on your own machine good luck with the source code but ive also made a build in the releases tab but you will have to get spotify client id and secret

go to [releases](https://github.com/san-nyan/pawosc/releases/tag/Alpha) and download the zip extract it to a folder
go to https://developer.spotify.com/dashboard and sign in
make an app call it whatever you want and add anything for the description
for "Redirect URIs" type http://127.0.0.1:8888/callback and click add
in the "Which apis do you plan to use" click Web Api

once you create the app hit the settings button and keep the tab open for now
go to the folder where you extracted the files
open up the app folder in there and open up "keys.json"
from there replace the your_spotipy_client_id and your_spotipy_client_secret with the keys you get on the settings page for your app
dont give anyone these keys they could abuse them

![image](https://github.com/user-attachments/assets/5925dd7f-cacd-47a1-85ea-bc77832daa72)


you should be good now to run the pawosc.exe it will open a console window that shows you everything its doing and to close the app just close the console window

![image](https://github.com/user-attachments/assets/1ba2f618-611c-4c2a-b92a-590aeac749c4)
