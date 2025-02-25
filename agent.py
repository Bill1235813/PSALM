import os

import backoff
import openai
import anthropic

###############################################################################
#
# The agent that leverages classical planner to help LLMs to plan
#
###############################################################################


class Agent:
    def __init__(self, temperature=0.5, lm_ic_prompt_name="rollout_template_ic_v3", model="gpt-4-turbo"):
        self.openai_api_keys = self.load_openai_keys()
        self.anthropic_api_keys = self.load_anthropic_keys()
        self.model = model
        self.temperature = temperature
        self.lm_ic_prompt = open(f"./prompts/{lm_ic_prompt_name}").read()
        self.infer_cnf_prompt = open(f"./prompts/infer_cnf_template_v2").read()
        self.action_desp_prompt = open(f"./prompts/action_desp_template").read()
        self.cand_traj_str_starter = open(f"./prompts/cand_traj_starter").read()
        self.failed_traj_str_starter = open(f"./prompts/failed_traj_starter").read()

    @staticmethod
    def load_anthropic_keys():
        anthropic_keys_file = os.path.join(os.getcwd(), "keys/anthropic_keys.txt")
        with open(anthropic_keys_file, "r") as f:
            context = f.read()
        context_lines = context.strip().split('\n')
        print(context_lines)
        return context_lines

    @staticmethod
    def load_openai_keys():
        openai_keys_file = os.path.join(os.getcwd(), "keys/openai_keys.txt")
        with open(openai_keys_file, "r") as f:
            context = f.read()
        context_lines = context.strip().split('\n')
        print(context_lines)
        return context_lines

    def query(self, prompt_text, temperature=0.5):
        server_cnt = 0
        result_text = ""
        while server_cnt < 10:
            try:
                if self.model in ["gpt-4-turbo", "o1-preview"]:  # currently, we will always use chatgpt
                    @backoff.on_exception(backoff.expo, openai.RateLimitError)
                    def completions_with_backoff(**kwargs):
                        return openai.chat.completions.create(**kwargs)

                    self.update_openai_key()
                    if self.model == "o1-preview":
                        response = completions_with_backoff(
                            model=self.model,
                            max_completion_tokens=4096,
                            messages=[{"role": "user", "content": prompt_text}],
                        )
                    else:
                        response = completions_with_backoff(
                            model=self.model,
                            temperature=temperature,
                            max_completion_tokens=4096,
                            top_p=0.0,
                            frequency_penalty=0,
                            presence_penalty=0,
                            messages=[
                                {"role": "system", "content": "You are a helpful PDDL assistant."},
                                {"role": "user", "content": prompt_text},
                            ],
                        )
                    result_text = response.choices[0].message.content
                elif self.model in ["claude-3-5-sonnet-20240620"]:
                    client = anthropic.Anthropic()
                    self.update_anthropic_key(client)
                    response = client.messages.create(
                        model=self.model,
                        temperature=temperature,
                        max_tokens=4096,
                        system="You are a helpful assistant.",
                        messages=[{"role": "user", "content": prompt_text}],
                    )
                    result_text = response.content[0].text
                else:
                    raise ValueError("Not available model!")
                server_flag = 1
                if server_flag:
                    break
            except Exception as e:
                server_cnt += 1
                print(e)
        return result_text

    def update_anthropic_key(self, client):
        curr_key = self.anthropic_api_keys[0]
        client.api_key = curr_key
        self.anthropic_api_keys.remove(curr_key)
        self.anthropic_api_keys.append(curr_key)

    def update_openai_key(self):
        curr_key = self.openai_api_keys[0]
        openai.api_key = curr_key
        self.openai_api_keys.remove(curr_key)
        self.openai_api_keys.append(curr_key)

