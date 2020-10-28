import typing

import config
import prices

MONTHS_IN_YEAR = 12


class Fund:
    def __init__(self, params: config.Params, price_history: typing.Sequence):
        self._params = params
        self.price_history = price_history
        self._assets = 0.0

    def invest_periodically(self, period_length: int) -> float:
        invest_months = set(range(period_length - 1,
                                  prices.HISTORY_LENGTH,
                                  period_length))
        invest_months |= {prices.HISTORY_LENGTH - 1}
        return self._invest_or_save(invest_months)

    def invest_if_cheaper(self) -> float:
        cheaper_months = self.find_cheaper_months()
        invest_months = cheaper_months | {0, prices.HISTORY_LENGTH - 1}
        return self._invest_or_save(invest_months)

    def find_cheaper_months(self) -> typing.Set:
        cheaper_months = {
            i
            for i in range(1, prices.HISTORY_LENGTH)
            if self.price_history[i] < self.price_history[i - 1]
        }
        return cheaper_months

    def _invest_or_save(self, invest_months: typing.Set) -> float:
        investment = 0
        for i in range(prices.HISTORY_LENGTH):
            investment += self._params.monthly_investment
            if i in invest_months:
                self.buy_assets(investment, i)
                investment = 0
            else:
                annual_interest = investment * self._params.interest_rate
                interest = annual_interest / MONTHS_IN_YEAR
                investment += interest

        assert investment == 0
        return self.estimate()

    def buy_assets(self, investment: float, month_idx: int):
        commission_threshold = max(
            ct for ct in self._params.commission_rates if ct <= investment
        )
        commission_rate = self._params.commission_rates[commission_threshold]
        commission = investment * commission_rate
        investment -= commission
        price = self.price_history[month_idx]
        assets = investment / price
        self._assets += assets

    def estimate(self) -> float:
        last_price = self.price_history[-1]
        value = self._assets * last_price
        return value


class Investor:
    def __init__(self,
                 params: config.Params,
                 stable_fund: Fund,
                 volatile_fund: Fund):
        self._params = params
        self._stable_fund = stable_fund
        self._volatile_fund = volatile_fund

    def invest(self) -> float:
        cheaper_months = self._volatile_fund.find_cheaper_months()
        for i in range(prices.HISTORY_LENGTH):
            fund = self._volatile_fund if i in cheaper_months \
                else self._stable_fund
            fund.buy_assets(self._params.monthly_investment, i)

        return self.estimate()

    def estimate(self) -> float:
        value = sum(
            f.estimate()
            for f in (self._stable_fund, self._volatile_fund)
        )
        return value


class Report:
    def __init__(self, params: config.Params):
        self._params = params
        self._values = {}

    def add(self, name: str, value: float):
        self._values[name] = value

    def print(self):
        investments = self._params.monthly_investment * prices.HISTORY_LENGTH
        values = [(v, k) for k, v in self._values.items()]
        values.sort(reverse=True)
        for value, name in values:
            profit = value - investments
            profit_rate = profit / investments
            print(f'{profit_rate:.2%}, "{name}" strategy')


def main():
    params = config.Params()
    report = Report(params)

    bonds_fund = Fund(params, prices.BONDS_HISTORY)
    shares_fund = Fund(params, prices.SHARES_HISTORY)
    value = Investor(params, bonds_fund, shares_fund).invest()
    report.add('multi-fund', value)

    price_histories = {'bonds': prices.BONDS_HISTORY,
                       'shares': prices.SHARES_HISTORY}
    for asset_type, price_history in price_histories.items():
        value = Fund(params, price_history).invest_if_cheaper()
        report.add(f'cheaper {asset_type}', value)
        for i in (1, 2, 3, 4, 5, 6):
            value = Fund(params, price_history).invest_periodically(i)
            report.add(f'{i}-months {asset_type}', value)

    report.print()


if __name__ == '__main__':
    main()
