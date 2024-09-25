from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain.agents import initialize_agent
from .tools import LawTool, RedirectTool, FAQTool, UniAdvisorTool
from .decorators import calculate_cost
from .memory import create_memory
from .utils import get_urls_from_text, get_deed_and_article_pairs, get_majors
import pathlib
from django.conf import settings

PATH = pathlib.Path(__file__).parent.resolve()


class mAsystent:
    def __init__(self, memory):
        self.law_tool = LawTool()
        self.redirect_tool = RedirectTool()
        self.faq_tool = FAQTool()
        self.uni_advisor_tool = UniAdvisorTool()

        tools = [
            self.law_tool,
            self.redirect_tool,
            self.faq_tool,
            self.uni_advisor_tool,
        ]
        turbo_llm = ChatOpenAI(temperature=0, api_key=settings.OPENAI_API_KEY)

        self.agent = initialize_agent(
            agent="chat-conversational-react-description",
            tools=tools,
            llm=turbo_llm,
            verbose=True,
            max_iterations=5,
            early_stopping_method="generate",
            return_intermediate_steps=True,
            memory=memory,
        )

        self.agent.agent.llm_chain.prompt.messages[
            0
        ].prompt.template = """Asystent to duży model językowy szkolony przez OpenAI.

        Asystent działa w aplikacji, która ma wiele zakładek i chce pomóc jej użytkownikom.

        Asystent został zaprojektowany, aby móc pomagać w różnego rodzaju zadaniach, począwszy od odpowiadania na proste pytania, a skończywszy na dostarczaniu dogłębnych wyjaśnień i dyskusji na szeroki zakres tematów. Jako model językowy, Asystent jest zdolny do generowania tekstów zbliżonych do ludzkich na podstawie otrzymywanych informacji, co pozwala na prowadzenie rozmów brzmiących naturalnie i dostarczanie odpowiedzi spójnych i adekwatnych do tematu.

        Asystent nie zna zakładek w aplikacji i nie umie pokazywać ich. Użyj do tego odpowiedniego narzędzia.

        Asystent nie zna aktów prawnych. Użyj odpowiedniego narzędzia aby się o nich dowiedzieć i udzielić odpowiedzi użytkownikowi.

        Asystent nie zna aplikacji mObywatel. Użyj do tego odpowiedniego narzędzia aby odpowiedzieć na pytania użytkowników.
        
        Asystent nie zna kierunków studiów. Użyj do tego odpowiedniego narzędzia aby na podstawie zainteresowań użytkownika zaproponować odpowiednie kierunki studiów.

        Asystent stale się uczy i rozwija, a jego możliwości nieustannie się rozszerzają. Potrafi przetwarzać i rozumieć duże ilości tekstu, co pozwala mu dostarczać dokładne i informacyjne odpowiedzi na szeroki zakres pytań. Dodatkowo, Asystent jest w stanie generować własny tekst na podstawie otrzymywanych informacji, co pozwala mu na uczestniczenie w dyskusjach oraz dostarczanie wyjaśnień i opisów na różnorodne tematy.

        Ogólnie rzecz biorąc, Asystent to potężny system, który może pomóc w różnych zadaniach i dostarczać cenne wskazówki i informacje na szeroki wachlarz tematów. Niezależnie od tego, czy potrzebujesz pomocy przy konkretnym pytaniu, czy po prostu chcesz porozmawiać na określony temat, Asystent jest tutaj, aby pomóc.

        Asystent rozmawia w języku Polskim."""

    def _get_observation(self, response):
        return response["intermediate_steps"][0][-1].split("\nanswers:")[-1]

    @calculate_cost
    def __call__(self, input):
        response = self.agent({"input": input})
        data = {"output": response["output"]}
        for action, _ in response["intermediate_steps"]:
            data["tool"] = action.tool
            if action.tool == self.redirect_tool.name:
                data["page"] = action.tool_input
            elif action.tool == self.law_tool.name:
                observations = self._get_observation(response)
                pairs = get_deed_and_article_pairs(observations)
                data["resources"] = {}
                if pairs:
                    for pair in pairs:
                        if pair[0] not in data["resources"]:
                            data["resources"][pair[0]] = [pair[1]]
                        else:
                            data["resources"][pair[0]].append(pair[1])
            elif action.tool == self.faq_tool.name:
                observations = self._get_observation(response)
                data["urls"] = get_urls_from_text(observations)
            elif action.tool == self.uni_advisor_tool.name:
                observations = self._get_observation(response)
                data["majors"] = get_majors(observations)

        return data


if __name__ == "__main__":
    memory = create_memory()
    asistant = mAsystent(memory)
    resp = asistant(
        "Nie wiem jaki kierunek studiów wybrać. Lubie piłkę nozna oraz programowanie. W wolnym czasie ogladam filmy"
    )

    print(resp)
