## Intro:

A local server for mobile rhythm game `Pianista`, implemented using `starlette`.

This project is for game preservation purposes only. Therefore, it is the author `qwerfd2`'s policy to only release them after the game's official server has shut down and no adiquate offline support has been provided to the players.

For redundancy sake, various trusted members from the game community should be invited to test, or at least posess, the repository to eliminate single point of failure.

It is the `author`'s expectation that these members do not use this repo to harm the game developer or reap personal gains from this work.

## Setup:

Sites to proxy: `https://pianista-cdn.pianista.io`

Simply install official `apk` and set up proxy.

Modify `config.env` to local IP:port.

Install all dependencies, run `python 11000.py`.

(client has `build` textAsset in `570e46b0868640144a2e9beacd712c93` but https is enforced)

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

## Features that will not be supported

Music point related functions (consume, recovery, reward), since the currency has no use.

Most gem related functions (IAP, music pack purchases, music point purchases), since the currency has no use when it comes to the above functions.

Prestige related function (IAP, time accumulation/decrement, item daily provision), since it is unlocked by default.

Certain PostBox rewards (patterns, debug, music points), since they are either have no use or is unlocked by default.

Apple and Facebook login methods, since there's no way to get the tokens.

League lobbies that contains more than 1 real player, since this is a server meant to run locally.

Various useless functionalities such as ToS agreement and welcome music point reward

Security and efficiency (I mean it)