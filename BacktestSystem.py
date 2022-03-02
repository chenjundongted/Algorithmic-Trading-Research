import matplotlib.pyplot as plt
import numpy as np
import TestingSystem as ts

class BacktestSystem:

    # Constructor
    def __init__(self, oneMinData= None, threeMinData= None, fiveMinData= None, fifteenMinData= None, hourData= None):
        self.oneMinData = oneMinData
        self.fiveMinData = fiveMinData
        self.fifteenMinData = fifteenMinData
        self.hourData = hourData

    # User configuration
    initial_capital = capital = 10000 # initial capital for user
    max_active_position = 2 # maximum active position that allowed
    positionSizePct = 0.25 # position size for each position

    # class variables
    position = [] # active position [time, symbol, behavior, price, shares]
    positionLog = [] # closed position [time, symbol, behavior, price, shares, closedTime, closedPrice, PL, totalPL]

    def updatePosition(self, time, symbol, behavior, price):
        # time -> time to open the position
        # behavoir (char: "bto" or "stc" or “sto” or "btc")
        # price (double) -> price for the position
        if len(self.position) < self.max_active_position and behavior in ["bto", "sto"]:
            # Refusing opening double position if there is existing active position in the same symbol
            for trade in self.position:
                if trade[1] == symbol:
                    #print("Double position error!")
                    return
            shares = round(self.initial_capital * self.positionSizePct / price)
            positionInfo = [time, symbol, "long", price, shares] if behavior == "bto" else [time, symbol, "short", price, shares]
            self.position.append(positionInfo)
            #print(f"Successfully opening {positionInfo[2]} position!")
            return

        if len(self.position) > 0 and behavior in ["stc", "btc"]:
            for trade in self.position:
                if trade[1] == symbol and ((trade[2] == "long" and behavior == "stc") or (trade[2] == "short" and behavior == "btc")):
                    PL = round(trade[4] * (price-trade[3]) if behavior == "stc" else trade[4] * (trade[3]-price), 2)
                    self.capital = round(self.capital + PL, 2)
                    trade.extend([time, price, PL, self.capital])
                    self.positionLog.append(trade)
                    self.position.remove(trade)
                    #print(f"Successfully closing {trade[2]} position!")
                    return
        #print("Unknown error!")


    def visualizePL(self, benchmark):
        # visualize P&L percentage comparing to the standard benchmark of SPY500
        # benchmark -> benchmark data: [date, endingPrice]
        date = []; cumulativePL = []; benchmarkDate = []; benchmarkPL = []; completePL = [];
        for idx, trade in enumerate(self.positionLog):
            completePL.append(trade[7]) # Do not aggregate trade P&l of same date
            # Aggregate trade P&L of same date
            newDate = trade[5].partition(" ")[0]
            if idx == 0 or (idx != 0 and newDate != date[-1]):
                date.append(newDate)
                cumulativePL.append(trade[-1])
                continue
            cumulativePL[-1] = trade[-1]
        for day in benchmark:
            benchmarkDate.append(day[0])
            benchmarkPL.append(day[1])

        max_consecutive_losing_trade_num = max_consecutive_wining_trade_num = 0
        pct_pl_drawdown_losing_trade = pct_pl_gain_wining_trade = 0.0
        largest_pct_drawdown_single_losing_trade = largest_pct_gain_single_wining_trade = 0.0
        avg_pct_drawdown_losing_trade = avg_pct_gain_wining_trade = 0.0
        # Helper Variables
        winCount = loseCount = 0
        winPctSum = losePctSum = 0.0
        for pl in completePL:
            pl_pct = round(pl/self.initial_capital * 100, 2)
            if pl_pct > 0:
                winCount += 1
                winPctSum += pl_pct
                # Largest Single Win
                if pl_pct > largest_pct_gain_single_wining_trade:
                    largest_pct_gain_single_wining_trade = pl_pct
            if pl_pct < 0:
                loseCount += 1
                losePctSum += pl_pct
                # Largest Single Drawdown
                if pl_pct < largest_pct_drawdown_single_losing_trade:
                    largest_pct_drawdown_single_losing_trade = pl_pct
        # Average Gain in Wining Trades
        # Average Lost in Losing Trades
        avg_pct_gain_wining_trade = round(winPctSum / winCount, 2)
        avg_pct_drawdown_losing_trade = round(losePctSum / loseCount, 2)

        print(f"Wining Trades = {winCount} vs. Losing Trades = {loseCount}")
        print(f"{round(winCount / (winCount + loseCount) * 100, 2)}% win rate in {round(winPctSum + losePctSum, 2)}% net profit")
        print(f"Largest Single Win = {largest_pct_gain_single_wining_trade}%")
        print(f"Largest Single Drawdown = {largest_pct_drawdown_single_losing_trade}%")
        print(f"Average Gain in Wining Trades = {avg_pct_gain_wining_trade}%")
        print(f"Average Drawdown in Losing Trades = {avg_pct_drawdown_losing_trade}%")

        plt.plot(benchmarkDate, [x/benchmarkPL[0]-1 for x in benchmarkPL], label = "SP500")
        plt.plot(date, [x/self.initial_capital-1 for x in cumulativePL], label = "Cumulative P&L")
        plt.legend()
        plt.show()


def main():
    sys = BacktestSystem()

    # Testing updatePosition()

    """
    for trade in ts.updatePositionTestingData:
        sys.updatePosition(trade[0], trade[1], trade[2], trade[3])
    print(f"\nCurrent Active Position: {sys.position}")
    print(f"\nClosed Position:")
    for log in sys.positionLog:
        print(f"{log}")
    """

    # Testing visualizePL()
    """
    for trade in ts.visualizePLData:
        sys.updatePosition(trade[0], trade[1], trade[2], trade[3])
    sys.visualizePL(ts.visualizePLBenchMarkData)
    """



if __name__ == "__main__":
    main()
