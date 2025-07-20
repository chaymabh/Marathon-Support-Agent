from termcolor import colored
from models.openai_models import get_open_ai, get_open_ai_json
from utils.helper_functions import get_current_utc_datetime, check_for_content
from states.state import AgentGraphState
from utils.logger import logger

class Agent:
    def __init__(self, state: AgentGraphState, model=None, server=None, temperature=0, model_endpoint=None, stop=None, guided_json=None):
        #logger.debug("Initializing Agent with parameters: model={}, server={}, temperature={}, model_endpoint={}, stop={}, guided_json={}".format(model, server, temperature, model_endpoint, stop, guided_json))
        self.state = state
        self.model = model
        self.server = server
        self.temperature = temperature
        self.model_endpoint = model_endpoint
        self.stop = stop
        self.guided_json = guided_json

    def get_llm(self, json_model=True):
        #logger.debug("Getting LLM model with json_model={}".format(json_model))
        if self.server == 'openai':
            llm = get_open_ai_json(model=self.model, temperature=self.temperature) if json_model else get_open_ai(model=self.model, temperature=self.temperature)
            #logger.debug("LLM model retrieved successfully.")
            return llm

    def update_state(self, key, value):
        #logger.debug("Updating state with key '{}' and value '{}'".format(key, value))
        self.state = {**self.state, key: value}

class PlannerAgent(Agent):
    def invoke(self, memory, question, prompt):
        #logger.debug("PlannerAgent invoked with question: '{}'".format(question))

        planner_prompt = prompt.format(
            datetime=get_current_utc_datetime()
        )
        #logger.debug("Planner prompt formatted successfully.")

        messages = [
            {"role": "system", "content": planner_prompt},
            {"role": "user", "content": f"question: {question}"}
        ]
        #logger.debug("Messages prepared for LLM invocation.")

        llm = self.get_llm()
        ai_msg = llm.invoke(messages)
        response = ai_msg.content
        #logger.debug("LLM response received: '{}'".format(response))

        self.update_state("planner_responce", response)
        print(colored(f"Planner: {response}", 'cyan'))
        #logger.debug("State updated with planner response.")
        return self.state

class SummerizationAgent(Agent):
    def invoke(self, memory, question, email, state, prompt, research=None):
        #logger.debug("SummerizationAgent invoked with question: '{}' and email: '{}'".format(question, email))

        summerization_agent_prompt = prompt.format(
            datetime=get_current_utc_datetime(),
            state=state,
            email=email,
        )
        #logger.debug("Summerization agent prompt formatted successfully.")

        messages = [
            {"role": "system", "content": summerization_agent_prompt},
            {"role": "user", "content": f"question: {question}"}
        ]
        #logger.debug("Messages prepared for LLM invocation.")

        llm = self.get_llm(json_model=False)
        ai_msg = llm.invoke(messages)
        response = ai_msg.content
        #logger.debug("LLM response received: '{}'".format(response))

        print(colored(f"Summerization agent: {response}", 'yellow'))
        self.update_state("summerization_agent_responce", response)
        #logger.debug("State updated with summerization agent response.")
        return self.state

class ReporterAgent(Agent):
    def invoke(self, memory, question, planner, knowledge_base,  prompt, research=None):
        #logger.debug("ReporterAgent invoked with data: '{}'".format(knowledge_base))
        reporter_prompt = prompt.format(
            datetime=get_current_utc_datetime(),
           # desk_tool=edesk_tool,
            knowledge_base=knowledge_base,
            planner=planner,
        )
        #logger.debug("Reporter prompt formatted successfully.")

        messages = [
            {"role": "system", "content": reporter_prompt},
            {"role": "user", "content": f"question: {question}"}
        ]
        #logger.debug("Messages prepared for LLM invocation.")

        llm = self.get_llm(json_model=False)
        ai_msg = llm.invoke(messages)
        response = ai_msg.content
        #logger.debug("LLM response received: '{}'".format(response))

        print(colored(f"Reporter: {response}", 'yellow'))
        self.update_state("reporter_responce", response)
        #logger.debug("State updated with reporter response.")
        return self.state

class EndNodeAgent(Agent):
    def invoke(self):
        #logger.debug("EndNodeAgent invoked.")
        self.update_state("end_chain", "end_chain")
        #logger.debug("State updated with end_chain.")
        return self.state
