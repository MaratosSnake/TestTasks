import requests
from tabulate import tabulate


class ClassesPrinting:
    """
    A Class defines universal common __str__ and __repr__ methods
    """
    def __str__(self):
        attributes = self.__dict__.items()
        table = tabulate(attributes, tablefmt="grid")
        return f"{type(self).__name__}:\n{table}"

    def __repr__(self):
        attributes = ', '.join(f"{key}={value}" for key, value in self.__dict__.items())
        return f"{type(self).__name__}({attributes})"


class Location(ClassesPrinting):
    def __init__(self, data: dict):
        for key, value in data.items():
            setattr(self, key, value)


class WeatherData(ClassesPrinting):
    def __init__(self, data):
        self._process_data(data)

    def _process_data(self, data, prefix=""):
        """
        Deflates all nested dicts in data param and sets attributes according hierarchy
        :param data:
        :param prefix:
        :return:
        """
        for key, value in data.items():
            if key == 'location':
                self.location = Location(value)
            else:
                full_key = f"{prefix}_{key}" if prefix else key
                if isinstance(value, dict):
                    self._process_data(value, full_key)
                else:
                    setattr(self, full_key, value)


def get_current_weather_by_auto_ip() -> dict:
    """
    Function get weather by ip in JSON format
    :return: weather in JSON
    """
    url = 'http://api.weatherapi.com/v1/current.json'
    params = {
        'key': '33976f7b2b664d9eaf3220449240312',
        'q': 'auto:ip',
        'days': 1
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f'response was bad with status code {response.status_code}')
    return response.json()


def main():
    weather = WeatherData(get_current_weather_by_auto_ip())
    print(weather)


if __name__ == '__main__':
    main()
