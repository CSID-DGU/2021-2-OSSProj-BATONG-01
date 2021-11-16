import os
import sqlite3


main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')


class CoinData(object):
    path = os.path.join(data_dir, 'coins.db')

    def setCoins(coin):
        conn = sqlite3.connect(CoinData.path)
        c = conn.cursor()
        c.execute("UPDATE safe SET balance = ? WHERE id = 1", (coin,))
        conn.commit()
        conn.close()

    def load():
        conn = sqlite3.connect(CoinData.path)
        c = conn.cursor()
        c.execute("CREATE TABLE if not exists safe (id integer, balance integer DEFAULT 0)")
        c.execute("SELECT COUNT(*) FROM safe")
        l = c.fetchall()
        if l[0][0] == 0 :
            c.execute("INSERT INTO safe VALUES (1, 0)")
        c.fetchall()
        c.execute("SELECT balance FROM safe WHERE id = 1")
        coins = c.fetchone()[0]
        conn.commit()
        conn.close()
        return coins
        
    def buy(price) :
        conn = sqlite3.connect(CoinData.path)
        c = conn.cursor()
        c.execute("SELECT balance FROM safe WHERE id = 1")
        balance = c.fetchone()[0]
        balance -= price
        CoinData.setCoins(balance)
        conn.close()
