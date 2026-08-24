import httpx

async def get_current_price(coin:str) -> float:
    """Getting current price of coin using Binance API"""
    
    #Binance use symols like BTCUSDT, ETHUSDT
    symbol = f"{coin}USDT"

    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"

    '''I found that creating a user using a fuction is a bad idea, the app 
    will work faster in case if user is created in the start of server. This should be rewrite using lifespan'''
    async with httpx.AsyncClient() as client:
        response = await client.get(url)

        #If not found
        if response.status_code != 200:
            print(f"Error when receiving the price {coin}: {response.status_code}")
            return 0.0
        
        data = response.json()
        price = float(data["price"])
        return price