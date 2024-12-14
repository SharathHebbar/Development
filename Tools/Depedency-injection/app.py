from fastapi import FastAPI, Depends
from typing import Annotated

app = FastAPI()

class Logger:
    def log(self, message: str):
        print(f"Logging Message: {message}")


def get_logger():
    return Logger()


logger_dependency = Annotated[Logger, Depends(get_logger)]


@app.get("/log/{message}")
def log_message(message: str, logger: logger_dependency):
    Logger.log(message)
    return message