class Config:
    def __init__(self):
        self.LLM_HOST = 'localhost'
        self.LLM_PORT = [port for port in range(8000, 8008)]

        self.LOG_FILE = '/path/to/logfile.log'

    def display(self):
        for attribute, value in self.__dict__.items():
            print(f"{attribute}: {value}")