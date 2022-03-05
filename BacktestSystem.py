import matplotlib.pyplot as plt
import numpy as np
import TestingSystem as ts
import pandas as pd
from scipy import stats, signal
import plotly.express as px
import plotly.graph_objects as go

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


    def kernelDensityEstimator(self, data):
        volume = data["vol"]
        close = data["close"]
        kde_factor = 0.05
        num_samples = 500
        kde = stats.gaussian_kde(close, weights= volume, bw_method= kde_factor)
        xr = np.linspace(close.min(),close.max(),num_samples)
        kdy = kde(xr)
        ticks_per_sample = (xr.max() - xr.min()) / num_samples

        # vol distribution
        fig = go.Figure()
        fig.add_trace(go.Histogram(name='Vol Profile', x=close, y=volume, nbinsx=400, histfunc='sum', histnorm='probability density', marker_color='#B0C4DE'))
        fig.add_trace(go.Scatter(name='KDE', x=xr, y=kdy, mode='lines', marker_color='#D2691E'))

        # find vol nodes and set prominence to filter out insignificant nodes
        pk_marker_args = dict(size= 10)
        min_prom = kdy.max() * 0.3
        width_range=1
        peaks, peak_props = signal.find_peaks(kdy, prominence=min_prom, width= width_range)
        pkx = xr[peaks]
        pky = kdy[peaks]

        left_base = peak_props['left_bases']
        right_base = peak_props['right_bases']
        line_x = pkx
        line_y0 = pky
        line_y1 = pky - peak_props['prominences']

        # peak width
        left_ips = peak_props['left_ips']
        right_ips = peak_props['right_ips']
        width_x0 = xr.min() + (left_ips * ticks_per_sample)
        width_x1 = xr.min() + (right_ips * ticks_per_sample)
        width_y = peak_props['width_heights']
        fig.add_trace(go.Scatter(name='Peaks', x=pkx, y=pky, mode='markers', marker=pk_marker_args))

        # Draw peak height
        for x, y0, y1 in zip(line_x, line_y0, line_y1):
            fig.add_shape(type='line', xref='x', yref='y', x0=x, y0=y0, x1=x, y1=y1, line=dict(color='red', width=2, ))

        # Draw peak width
        for x0, x1, y in zip(width_x0, width_x1, width_y):
            fig.add_shape(type='line', xref='x', yref='y', x0=x0, y0=y, x1=x1, y1=y, line=dict(color='red', width=2, ))
            print(f"({x0}, {x1})")

        fig.show()

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

    data = pd.read_csv("dataSample.txt", sep= ",", header= None)
    data.columns = ["time", "open", "high", "low", "close", "vol"]
    data["time"] = pd.to_datetime(data["time"])
    mask = data["time"].between("2021-08-02 04:00:00", "2021-08-05 19:59:00")
    sys.kernelDensityEstimator(data[mask])



if __name__ == "__main__":
    main()
