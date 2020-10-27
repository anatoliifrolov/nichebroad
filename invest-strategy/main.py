COMMISSION_RATES = {
    0: 0.014,
    500_000: 0.009,
    3_000_000: 0.005
}
INTEREST_RATE = 0.04
MONTHLY_INVESTMENT = 100_000
MONTHS_PER_YEAR = 12
SHARE_PRICE_HISTORY_BONDS = (
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
SHARE_PRICE_HISTORY_SHARES = (
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


class Calculator:
    def __init__(self, share_price_history):
        self._share_price_history = share_price_history
        self._shares_amount = 0.0

    def invest_periodically(self, period_length: int):
        history_length = len(self._share_price_history)
        invest_months = set(range(period_length - 1,
                                  history_length,
                                  period_length)) | {history_length - 1}
        self._invest(invest_months)

    def invest_if_cheaper(self):
        history_length = len(self._share_price_history)
        invest_months = {
            i
            for i in range(1, history_length)
            if self._share_price_history[i] < self._share_price_history[i - 1]
        } | {0, history_length - 1}
        self._invest(invest_months)

    def _invest(self, invest_months):
        investment = 0
        for i, share_price in enumerate(self._share_price_history):
            investment += MONTHLY_INVESTMENT
            if i in invest_months:
                self._buy_shares(investment, share_price)
                investment = 0
            else:
                interest = investment * INTEREST_RATE / MONTHS_PER_YEAR
                investment += interest

        assert investment == 0

    def get_profit_rate(self):
        balance = self.get_balance()
        history_length = len(self._share_price_history)
        investments = MONTHLY_INVESTMENT * history_length
        profit = balance - investments
        profit_rate = profit / investments
        return profit_rate

    def get_balance(self):
        last_share_price = self._share_price_history[-1]
        balance = self._shares_amount * last_share_price
        return balance

    def _buy_shares(self, investment, share_price):
        commission_threshold = 0
        for amount in COMMISSION_RATES:
            if amount <= investment:
                commission_threshold = max(commission_threshold, amount)

        commission_rate = COMMISSION_RATES[commission_threshold]
        commission = investment * commission_rate
        investment -= commission
        new_shares = investment / share_price
        self._shares_amount += new_shares

    def __str__(self):
        balance = self.get_balance()
        profit_rate = self.get_profit_rate()
        return f'{balance:.2f} ({profit_rate:.2%})'


def main():
    for share_price_history in (SHARE_PRICE_HISTORY_BONDS,
                                SHARE_PRICE_HISTORY_SHARES):
        print('#' * 100)
        calculator = Calculator(share_price_history)
        calculator.invest_if_cheaper()
        print(f'cheaper strategy: {calculator}')
        for i in (1, 2, 3, 4, 5, 6):
            calculator = Calculator(share_price_history)
            calculator.invest_periodically(i)
            print(f'{i}-months strategy: {calculator}')


if __name__ == '__main__':
    main()
