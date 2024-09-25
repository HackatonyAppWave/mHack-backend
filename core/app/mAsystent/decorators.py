from langchain_community.callbacks.manager import get_openai_callback
from csv import writer


def calculate_cost(agent):
    def inner(*args, **kwargs):
        with get_openai_callback() as cb:
            response = agent(*args, **kwargs)
            with open("logs.csv", "a") as f_object:
                writer_object = writer(f_object)
                writer_object.writerow(
                    [
                        cb.prompt_tokens,
                        cb.completion_tokens,
                        cb.total_tokens,
                        cb.total_cost,
                    ]
                )
            return response

    return inner
