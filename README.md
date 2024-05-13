# finance
Webpage built using Flask. CS50 Problem Set 9.

Implement a website via which users can “buy” and “sell” stocks, à la the below.

<img width="1357" alt="Screenshot 2024-03-22 at 14 54 02" src="![image](https://github.com/Stebin-17/C-50-Finance/assets/114398468/0296e5b2-0d87-45f8-9704-c07ebbd9414a)">


## Background

If you’re not quite sure what it means to buy and sell stocks (i.e., shares of a company), head [here](https://www.investopedia.com/articles/basics/06/invest1000.asp) for a tutorial.

You’re about to implement C$50 Finance, a web app via which you can manage portfolios of stocks. Not only will this tool allow you to check real stocks’ actual prices and portfolios’ values, it will also let you buy (okay, “buy”) and sell (okay, “sell”) stocks by querying for stocks’ prices.

Indeed, there are tools (one is known as IEX) that let you download stock quotes via their API (application programming interface) using URLs like `https://api.iex.cloud/v1/data/core/quote/nflx?token=API_KEY`. Notice how Netflix’s symbol (NFLX) is embedded in this URL; that’s how IEX knows whose data to return. That link won’t actually return any data because IEX requires you to use an API key, but if it did, you’d see a response in JSON (JavaScript Object Notation) format like this:

```json
{
  "avgTotalVolume":6787785,
  "calculationPrice":"tops",
  "change":1.46,
  "changePercent":0.00336,
  "close":null,
  "closeSource":"official",
  "closeTime":null,
  "companyName":"Netflix Inc.",
  "currency":"USD",
  "delayedPrice":null,
  "delayedPriceTime":null,
  "extendedChange":null,
  "extendedChangePercent":null,
  "extendedPrice":null,
  "extendedPriceTime":null,
  "high":null,
  "highSource":"IEX real time price",
  "highTime":1699626600947,
  "iexAskPrice":460.87,
  "iexAskSize":123,
  "iexBidPrice":435,
  "iexBidSize":100,
  "iexClose":436.61,
  "iexCloseTime":1699626704609,
  "iexLastUpdated":1699626704609,
  "iexMarketPercent":0.00864679844447232,
  "iexOpen":437.37,
  "iexOpenTime":1699626600859,
  "iexRealtimePrice":436.61,
  "iexRealtimeSize":5,
  "iexVolume":965,
  "lastTradeTime":1699626704609,
  "latestPrice":436.61,
  "latestSource":"IEX real time price",
  "latestTime":"9:31:44 AM",
  "latestUpdate":1699626704609,
  "latestVolume":null,
  "low":null,
  "lowSource":"IEX real time price",
  "lowTime":1699626634509,
  "marketCap":192892118443,
  "oddLotDelayedPrice":null,
  "oddLotDelayedPriceTime":null,
  "open":null,
  "openTime":null,
  "openSource":"official",
  "peRatio":43.57,
  "previousClose":435.15,
  "previousVolume":2735507,
  "primaryExchange":"NASDAQ",
  "symbol":"NFLX",
  "volume":null,
  "week52High":485,
  "week52Low":271.56,
  "ytdChange":0.4790450244167119,
  "isUSMarketOpen":true
}
```

Notice how, between the curly braces, there’s a comma-separated list of key-value pairs, with a colon separating each key from its value. We’re going to be doing something very similar, with Yahoo Finance.


## Running

Start Flask’s built-in web server (within `finance/`):

```sh
$ flask run
```

Visit the URL outputted by flask to see the distribution code in action. You won’t be able to log in or register, though, just yet!

Within `finance/`, run `sqlite3 finance.db` to open `finance.db` with `sqlite3`. If you run `.schema` in the SQLite prompt, notice how ``finance.db`` comes with a table called `users`. Take a look at its structure (i.e., schema). Notice how, by default, new users will receive $10,000 in cash. But if you run `SELECT * FROM users;`, there aren’t (yet!) any users (i.e., rows) therein to browse.
