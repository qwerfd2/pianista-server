## Setup:

Sites to proxy: `https://pianista-api.pianista.io`

Simply install official `apk` and set up proxy.

Modify `config.env` to local IP:port.

## Features that are supported

Collection game play

Tour game play

Leaderboards and rankings

Piano unlocks, upgrade, and equipment

Static Prestige membership, which allows for unlimited play and all song unlocks

Limited shop functionality (gem to coin)

Limited PostBox support (messages, attachment gems, coins, pianos, and items)

League reimplementation with bots, limited set of news feed

renaming (which is actually free)

## Features that will not be supported

Music point related functions (consume, recovery, reward), since the currency has no use.

Most gem related functions (IAP, music pack purchases, music point purchases), since the currency has no use when it comes to the above functions.

Prestige related function (IAP, time accumulation/decrement, item daily provision), since it is unlocked by default.

Certain PostBox rewards (patterns, debug, music points), since they are either have no use or is unlocked by default.

Apple and Facebook login methods, since there's no way to get the tokens.

League lobbies that contains more than 1 real player, since this is a server meant to run locally.

League daily rewards, since there is no way to change it to something other than music points, which is removed.