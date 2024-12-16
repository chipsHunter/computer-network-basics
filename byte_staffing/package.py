import re


class PackageManager:
    """
        FEND (frame end) - symbol indicates frame starts
        FESC (frame escape) - symbol indicates something was replaced
        TFEND (transposed frame end) - symbol replaces real FEND
        TFESC (transposed frame escape) - symbol replaces real FESC
    """

    def __init__(self, n, data):
        self.__n = n

        self.__FEND = "@" + chr(ord('a') + (n - 1))
        self.__FESC = "$"
        self.__TFEND = "*"
        self.__TFESC = "%"
        self.__EOD = "\\n"
        self.__data = data

    def get_controlls(self):
        return {"end": self.__FESC + self.__TFEND,
                "esc": self.__FESC + self.__TFESC,
                "eod": self.__EOD}

    def transform_data_to_package(self):
        self.__data = re.sub(re.escape(self.__FESC), self.__FESC + self.__TFESC, self.__data)
        self.__data = re.sub(re.escape(self.__FEND), self.__FESC + self.__TFEND, self.__data)
        if len(self.__data) % self.__n != 0:
            self.__data += "\\n"
        while len(self.__data) % self.__n != 0:
            self.__data += "0"
        return self.__data

    def transform_package_data_to_real(self):
        # print(f"WAS {self.__data}")
        eol = self.__data.find("\\n")
        if eol != -1:
            self.__data = self.__data[0:eol]
        self.__data = re.sub(re.escape(self.__FESC) + re.escape(self.__TFEND), self.__FEND, self.__data)
        self.__data = re.sub(re.escape(self.__FESC) + re.escape(self.__TFESC), self.__FESC, self.__data)
        # print(f"NOW {self.__data}")

        return self.__data


def get_data_from_package(data):
    return data[4:-1]


class Package:

    def __init__(self, n, port, data):
        self.__n = n

        self.flag = "@"
        self.destination_address = "0"
        self.source_address = f"{port[-1]}"
        self.data = data
        self.fcs = "0"

        self.package = ""
        self.form_package()

    def form_package(self):
        task_num = self.__n - 1
        self.flag += chr(ord('a') + task_num)
        self.package += self.flag
        self.package += self.destination_address
        self.package += self.source_address
        self.package += self.data
        self.package += self.fcs