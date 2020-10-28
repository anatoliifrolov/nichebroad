import typing

COMMISSION_RATES = {
    0: 0.014,
    500_000: 0.009,
    3_000_000: 0.005
}
INTEREST_RATE = 0.035
MONTHLY_INVESTMENT = 100_000
MONTHS_IN_YEAR = 12

# "Облигации Плюс" from 2017-10-23 to 2020-10-23
BONDS_PRICE_HISTORY = (
    3741.74,
    3767.22,
    3787.6,
    3861.09,
    3931.06,
    3959.46,
    3921.55,
    3953.64,
    3949.79,
    3964.15,
    3863.9,
    3875.97,
    3907.98,
    3910.74,
    3925.15,
    4002.74,
    4025.65,
    4063.61,
    4093.82,
    4140.52,
    4209.36,
    4247.81,
    4285.52,
    4354.63,
    4420.06,
    4452.62,
    4488.55,
    4560.36,
    4604.7,
    4363,
    4562.63,
    4655.02,
    4695.89,
    4718.28,
    4711.1,
    4747.56,
    4774.88
)

# "Ликвидные акции" from 2017-10-23 to 2020-10-23
SHARES_PRICE_HISTORY = (
    3859.41,
    4064.93,
    3942.53,
    4374.1,
    4481.34,
    4412.38,
    4391.72,
    4547.28,
    4515.96,
    4648.97,
    4656.81,
    4964.05,
    4908.94,
    4886.37,
    4899.49,
    5196.63,
    5141.94,
    5131.54,
    5309.35,
    5343.91,
    5710.68,
    5748.18,
    5688.8,
    5841.26,
    5957.72,
    6205.33,
    6345.63,
    6578.52,
    6592.28,
    4851.45,
    5498.12,
    5615.63,
    5893.07,
    6149.01,
    6345.99,
    6186.85,
    6158.35
)


class Fund:
    def __init__(self, price_history: typing.Sequence):
        self.price_history = price_history
        self._assets = 0.0

    def invest_periodically(self, period_length: int):
        history_length = len(self.price_history)
        invest_months = set(range(period_length - 1,
                                  history_length,
                                  period_length)) | {history_length - 1}
        self._invest_or_save(invest_months)

    def invest_if_cheaper(self):
        history_length = len(self.price_history)
        invest_months = self.find_cheaper_months() | {0, history_length - 1}
        self._invest_or_save(invest_months)

    def find_cheaper_months(self) -> typing.Set:
        history_length = len(self.price_history)
        month_indexes = {
            i
            for i in range(1, history_length)
            if self.price_history[i] < self.price_history[i - 1]
        }
        return month_indexes

    def _invest_or_save(self, invest_months: typing.Set):
        history_length = len(self.price_history)
        investment = 0
        for i in range(history_length):
            investment += MONTHLY_INVESTMENT
            if i in invest_months:
                self.buy_assets(investment, i)
                investment = 0
            else:
                interest = investment * INTEREST_RATE / MONTHS_IN_YEAR
                investment += interest

        assert investment == 0

    def buy_assets(self, investment: float, month_idx: int):
        commission_threshold = max(
            ct for ct in COMMISSION_RATES if ct <= investment
        )
        commission_rate = COMMISSION_RATES[commission_threshold]
        commission = investment * commission_rate
        investment -= commission
        price = self.price_history[month_idx]
        assets = investment / price
        self._assets += assets

    def estimate(self) -> typing.Tuple[float, float]:
        last_price = self.price_history[-1]
        value = self._assets * last_price
        history_length = len(self.price_history)
        investments = MONTHLY_INVESTMENT * history_length
        profit = value - investments
        profit_rate = profit / investments
        return value, profit_rate

    def __str__(self) -> str:
        value, profit_rate = self.estimate()
        return f'{value:.2f} ({profit_rate:.2%})'


class Investor:
    def __init__(self, stable_fund: Fund, volatile_fund: Fund):
        self._stable_fund = stable_fund
        self._volatile_fund = volatile_fund

    def invest(self):
        history_length = len(self._stable_fund.price_history)
        cheaper_months = self._volatile_fund.find_cheaper_months()
        for i in range(history_length):
            fund = self._volatile_fund if i in cheaper_months \
                else self._stable_fund
            fund.buy_assets(MONTHLY_INVESTMENT, i)

    def estimate(self):
        estimates = [
            f.estimate()
            for f in (self._stable_fund, self._volatile_fund)
        ]
        value = sum(v for v, _ in estimates)
        history_length = len(self._stable_fund.price_history)
        investments = MONTHLY_INVESTMENT * history_length
        profit = value - investments
        profit_rate = profit / investments
        return value, profit_rate

    def __str__(self) -> str:
        value, profit_rate = self.estimate()
        return f'{value:.2f} ({profit_rate:.2%})'


def main():
    bonds_fund = Fund(BONDS_PRICE_HISTORY)
    shares_fund = Fund(SHARES_PRICE_HISTORY)
    investor = Investor(bonds_fund, shares_fund)
    investor.invest()
    print(f'multi-fund strategy: {investor}')
    for price_history in (BONDS_PRICE_HISTORY,
                          SHARES_PRICE_HISTORY):
        print('#' * 100)
        fund = Fund(price_history)
        fund.invest_if_cheaper()
        print(f'cheaper strategy: {fund}')
        for i in (1, 2, 3, 4, 5, 6):
            fund = Fund(price_history)
            fund.invest_periodically(i)
            print(f'{i}-months strategy: {fund}')


if __name__ == '__main__':
    main()
