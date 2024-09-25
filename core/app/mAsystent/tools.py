from langchain.tools import BaseTool
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from .UniAdvisor import UniAdvisor
import pathlib
import os

PATH = pathlib.Path(__file__).parent.resolve()


class RedirectTool(BaseTool):
    name: str = "Znajdź lub pokaż zakładkę"
    description: str = (
        "Użyteczna kiedy użytkownik chce otworzyć zakładkę w aplikacji. Możliwe zakładki jako input to: dowod_osobisty, punkty_karne. "
    )
    tabs: dict[str, str] = {
        "dowod_osobisty": 'Wejdź na stronę główną. Na samej górze pojawi się okno z napisem "Dowód osobisty". Kliknij w celu otworzenia mDowodu.',
        "punkty_karne": "Aby sprawdzić swoje punkty karne kliknij zakładkę punkty karne.",
    }

    def _run(self, input: str):
        return self.tabs[input]

    async def _arun(self, *args, **kwargs) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("RedirectTool does not support async")


class LawTool(BaseTool):
    name: str = "akty_prawne"
    description: str = (
        "Użyteczna kiedy użytkownik zadaje pytanie o akty prawne, i ogólnie pojęte prawo. Może zadać pytanie o konsekwencje złamania przepisów. input to pytanie użytkownika oraz informacje, które mogą być potrzebne w przeszukiwaniu bazy danych."
    )

    def _run(self, input: str):
        embeddings = OpenAIEmbeddings()
        faq_db = FAISS.load_local(
            os.path.join(PATH, "akty_prawne"),
            embeddings,
            allow_dangerous_deserialization=True,
        )
        docs = faq_db.similarity_search(input, k=5)
        data = "\n".join([doc.page_content for doc in docs])
        return data + "\n\nWskaż konkretne artykuły i akty prawne."

    async def _arun(self, *args, **kwargs) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("LawTool does not support async")


class FAQTool(BaseTool):
    name: str = "FAQ"
    description: str = (
        "Użyteczna kiedy użytkownik chce zapytać jak działa aplikacja, co można za pomocą niej zrobić. Odpowiada także na pytania związane z mDowodem"
    )

    def _run(self, input: str):
        embeddings = OpenAIEmbeddings()
        faq_db = FAISS.load_local(os.path.join(PATH, "faq"), embeddings)

        docs = faq_db.similarity_search(input, k=2)

        data = "\n".join([doc.page_content for doc in docs])

        return data

    async def _arun(self, *args, **kwargs) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("FAQTool does not support async")


class UniAdvisorTool(BaseTool):
    name: str = "zaproponuj kierunki studiów"
    description: str = (
        "Użyteczna kiedy użytkownik szuka odpowiedniego kierunku studiów dla siebie i opisuje swoje zainteresowania. Jako input podaj opis zainteresowań użytkownika. Nie podawaj linków w odpowiedzi."
    )

    def _run(self, input: str):
        uni_advisor = UniAdvisor()
        output, majors = uni_advisor(input)
        output_data = f"output: {output}\nmajors: {majors}"

        return output_data

    async def _arun(self, *args, **kwargs) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("UniAdvisorTool does not support async")
