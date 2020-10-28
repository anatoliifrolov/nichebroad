# todo: move to a YAML file
COMMISSION_RATES = {
    0: 0.014,
    500_000: 0.009,
    3_000_000: 0.005
}
INTEREST_RATE = 0.035
MONTHLY_INVESTMENT = 100_000


class Params:
    @property
    def commission_rates(self):
        return COMMISSION_RATES

    @property
    def interest_rate(self):
        return INTEREST_RATE

    @property
    def monthly_investment(self):
        return MONTHLY_INVESTMENT
