## Intro:

A local server for mobile rhythm game `Pianista`, implemented using `starlette`.

~~This project is for game preservation purposes only. Therefore, it is the author `qwerfd2`'s policy to only release them after the game's official server has shut down and no adiquate offline support has been provided to the players.~~

~~For redundancy sake, various trusted members from the game community should be invited to test, or at least posess, the repository to eliminate single point of failure.~~

~~It is the `author`'s expectation that these members do not use this repo to harm the game developer or reap personal gains from this work.~~

I've decided to release it early for the following reasons.

1) The developer is dead. It no longer exists.

2) No support is available from them. Email goes unanswered, ios app delisted for months.

3) No one cares about this game - I do my research on the game community during and after development, and this game in particular is all but dead.

For these reasons, I deem the impact of releasing this early minimal.

## At the Start

First, you need to set up the server. Use the `Setup the Server First` section.

Next, there are 2 ways to set up the connection. Pick one.

1. Proxy. Requires more setup, but the install package can remain unmodified.

2. File modification. Easier setup, but file edit is necessary.

For method 1, use the `Instruction for Use (for official client)` section.

For method 2, use the `Instruction for Use (For modified client)` section.

## Setup the Server First

### PC/MAC (Easier)

Download the server, and extract everything to your folder of choice.

Install `python` and `pip` on your PC/MAC.

Note that MAC uses `python3`. Code examples in this document will use the default of Windows, which is `python`. After the installation, install dependencies using `pip install ...`.

Open command on Windows (MAC open terminal). Type `ipconfig` (MAC `ifconfig`), and obtain your IPV4 address. This assumes that you are connected to a WIFI, and it should start with 192 or 172.

Open the `config.py` of the private server, and change the `IP` accordingly.

Type `cmd` in the file directory on the top of the file explorer, and press enter. A command prompt will be opened for that directory.

Type `pip install -r requirements.txt` to install all the dependencies.

If any dependencies are missing you can install them using `pip install ....`

Type `python 11000.py` to start the server. If an error pops up, resolve it now – did you install all the dependencies? Is the IP correct?

### Android (Harder)

<details>
<summary>Details</summary>
<br>

Install [Termux](https://github.com/termux/termux-app/releases).

Type the following commands.

`termux-setup-storage`

`pkg install python`

Use

`pip install ...`

to install `rust`, `starlette`, `pycryptodome`, `requests`.

If ssl errors pop up, you might need to ``pkg up ssl -y``.

Copy the server to phone, or upzip the server files on the phone. (Skip the iOS files if not needed, it takes up a lot of space)

change `config.py`'s `IP` to `127.0.0.1` (this is `loopback`. Feel free to use your android device's `IPv4` via `ifconfig` if you are connected to a WIFI, to enable the server to the entire network).

`cd storage/shared/.... (server location on android file system)`

`python 11000.py` to start the server.

</details>

### iOS (Hard)

<details>
<summary>Details</summary>
<br>

I did some research on `Pythonista` and it seems possible, but you are on your own for this one.

</details>

## Instruction for Use (for official client) 

<details>
<summary>Details</summary>
<br>

### Android

For android 9+ devices, you need to bypass `https` in order to MITM the connection between game client and server. If you have root, you can install Certificate Authorities to system level, allowing the device to trust it. If you don't have root, I don't think it is possible and you might have to modify the client.

I will demonstrate the `VProxid` + `Charles` method.

Install `VProxid` on your `android` device.

Install `Charles` on your `Windows PC`. `Charles` has a free trial period, but there are ways to register it for free. Please do your own research on that subject.

Your server should already be running. 

Install `Charles Certificate Authority` on your `android` device by going to Charles UI `top bar`: `Help` – `SSL Proxying` – `Install Charles Root Certificate on a mobile device`. Follow its instructions. Install the downloaded certificate on the `android` device. Follow [this](https://gist.github.com/pwlin/8a0d01e6428b7a96e2eb) guide to move the user-level certificate to system level. Once done, go to the `android` device's `system setting` – `certificates`, and double check that `Charles` certificate appears at the bottom of the system certificates.

In `Charles`, open `top bar`: `Proxy` – `Proxy Settings`. Enable `SOCKS` proxy on port `8889`. Enable `http proxying over socks`, include default ports. 

![](https://studio.code.org/v3/assets/BDOGr35iuNT4hc06y6O_ES5P96xr3SMqhQ2tdwI1KOY/help1.JPG)

Then, in `top bar`: `Tools` – `Map Remote`, map a URL to your Server `IP address:port`, under `http`. The URL is: `https://pianista-cdn.pianista.io`. 

![](https://studio.code.org/v3/assets/BDOGr35iuNT4hc06y6O_ES5P96xr3SMqhQ2tdwI1KOY/help3.png)

![](https://studio.code.org/v3/assets/BDOGr35iuNT4hc06y6O_ES5P96xr3SMqhQ2tdwI1KOY/test2.JPG)

On your `android` device, open `VProxid`. Create a new profile, with the server being `your computer’s IP`, port `8889`, type `socks5`, and select `Pianista` using the app selector. Once created, click the play button on the profile to activate it.

![](https://studio.code.org/v3/assets/BDOGr35iuNT4hc06y6O_ES5P96xr3SMqhQ2tdwI1KOY/help3.jpg)

Make sure the private server is running on your PC. Make sure Charles acknowledges the connection from the device. Make sure VProxid is running. Make sure your phone and laptop are under the same network. Start the game, and ovserve the server.

### iOS

I did not test this method on iOS. If you know how to proxy stuff there, feel free read the Android guide and try the equivalent on iOS.

</details>

## Instruction for Use (For modified client) 

<details>
<summary>Details</summary>
<br>

### Android & iOS

Download the `apk` or `ipa` file from your site of choice.

Extract the packages, and locate the following file: `build` textAsset in `assets/bin/Data/570e46b0868640144a2e9beacd712c93` . Use Unity Asset Bundle Extractor or a similar unity extract tool (unitypy, etc.).

This file contains the server URL that the game uses.

The file looks like this. Simply edit the manifest URL to your server address.

`
{
  "buildNumber": 1,
  "versionBuiltIn": 220,
  "versionApi": 3,
  "manifestBaseUrl": "http://test.domain.com", // Modify this (ex. http://192.168.1.1:9060)
  "channel": 2,
  "channelString": "2"
}
`

Import the new textAsset and save. Replace the official asset with the new one. 

Sign the package if necessary. Install the package on your device.

Open the game and observe the server output.

</details>


## Features that are supported

Config files and CDN delivery

Collection game play

Tour game play

Leaderboards and rankings

Piano unlocks, upgrade, and equipment

Static Prestige membership, which allows for unlimited play and all song unlocks

Limited shop functionality (gem to coin)

Limited PostBox support (messages, attachment gems, coins, pianos, and items)

League reimplementation with bots, limited set of news feed, daily reward which rewards gems.

nickname change

Full unlock mode (all packs, patterns, and piano unlocked) and normal unlock mode.

Facebook OAuth (beta testing, not recommended for use, disabled in code now (guest account is migratable, server must have access to facebook, etc.))

Guest Account Migration via webpage /Migrate.

Admin database management page /Login. Create admin account in the `admins` table - generate your own `bcrypt` hash for password.

## Features that will not be supported

Music point related functions (consume, recovery, reward), since the currency has no use.

Some gem related functions (IAP, music point purchases), since the currency has no use when it comes to the above functions.

Prestige related function (IAP, time accumulation/decrement, item daily provision), since it is either unlocked by default on full unlock mode or off.

Certain PostBox rewards (debug, prestige time, music points), since they have no use.

Apple login, since there's no way to get the tokens.

League lobbies that contains more than 1 real player, since this is a server meant to run locally.

Various useless functionalities such as welcome music point reward

Security and efficiency (I mean it)

## Known issues

Tour easy/normal/technical stage will not be unlocked after previous stage pass until game restart. (database object is clearly correctly written, packet is the same format as well, so I don't really know why)

## Config file documentation

### composerdata

`c`: Composer ID

### composerstatdata

`c`: Composer ID

`e`: EXP required to level up

### itemdata

`c`: Item ID

`ct`: Item type

`o`: Entitlement list

## gameconfig

everything is commented

