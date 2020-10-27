#!/usr/bin/python3
import argparse

import yaml

DAYS_PER_MONTH = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
DAYS_PER_YEAR = 365
MONTHS_PER_YEAR = 12
VISUAL_SCALE = 1_000_000


class Args:
    def __init__(self):
        cmd = argparse.ArgumentParser()
        cmd.add_argument('--config', default='config.yaml')
        self._args = cmd.parse_args()

    @property
    def config(self):
        return self._args.config


class Config:
    def __init__(self, args: Args):
        with open(args.config) as config_file:
            data = config_file.read()
            self._params = yaml.load(data, Loader=yaml.FullLoader)

    @property
    def initial_balance(self):
        return self._params['initial_balance']

    @property
    def interest_rate(self):
        return self._params['interest_rate']

    @property
    def month_savings(self):
        return self._params['month_savings']

    @property
    def months_to_move(self):
        # todo: use schema
        assert 1 <= self._params['months_to_move']
        return self._params['months_to_move']

    @property
    def mortgage_rate(self):
        return self._params['mortgage_rate']

    @property
    def property_price(self):
        return self._params['property_price']

    @property
    def property_price_ratio(self):
        # todo: use schema
        assert 0 <= self._params['property_price_ratio'] <= 1
        return self._params['property_price_ratio']

    @property
    def rent_price(self):
        return self._params['rent_price']

    @property
    def years(self):
        return self._params['years']


class Calculator:
    def __init__(self, config: Config):
        self._config = config
        self._balance = config.initial_balance
        self._savings = config.month_savings
        self._have_property = False

    def rent_and_save(self):
        self.print_header('Rent and save')
        for year in range(self._config.years):
            self.print_balance(year)
            for month in range(MONTHS_PER_YEAR):
                self.add_interest(self._config.interest_rate, month)
                self.add_savings()

        self.print_balance(self._config.years)

    def save_to_buy(self):
        self.print_header('Save to buy')
        months = 0
        for year in range(self._config.years):
            self.print_balance(year)
            for month in range(MONTHS_PER_YEAR):
                if self._have_property:
                    months += 1
                    if self._config.months_to_move == months:
                        self._savings += self._config.rent_price

                self.add_interest(self._config.interest_rate, month)
                self.add_savings()
                if self._have_property:
                    continue

                max_property_price = self._balance * self._config.property_price_ratio
                if self._config.property_price <= max_property_price:
                    self.buy_property()

        self.print_balance(self._config.years)

    def take_mortgage(self):
        self.print_header('Take a mortgage')
        self.buy_property()
        months = 0
        for year in range(self._config.years):
            self.print_balance(year)
            for month in range(MONTHS_PER_YEAR):
                months += 1
                if self._config.months_to_move == months:
                    self._savings += self._config.rent_price

                if self._balance < 0:
                    self.add_interest(self._config.mortgage_rate, month)
                elif 0 < self._balance:
                    self.add_interest(self._config.interest_rate, month)

                self.add_savings()

        self.print_balance(self._config.years)

    def add_interest(self, rate: float, month_idx: int):
        days = DAYS_PER_MONTH[month_idx]
        interest = self._balance * rate * days / DAYS_PER_YEAR
        self._balance += interest

    def add_savings(self):
        self._balance += self._savings

    def buy_property(self):
        print(f'Buying a property for {self._config.property_price:,}')
        self._balance -= self._config.property_price
        self._have_property = True

    @staticmethod
    def print_header(text: str):
        header = f' {text} '
        header = header.center(100, '*')
        print(header)

    def print_balance(self, year: int):
        print('$' * int(self._balance / VISUAL_SCALE),
              '{:,}'.format(int(self._balance)),
              f'after year {year}' if year else 'initially')


def main():
    args = Args()
    config = Config(args)
    Calculator(config).rent_and_save()
    Calculator(config).save_to_buy()
    Calculator(config).take_mortgage()


if __name__ == '__main__':
    main()
