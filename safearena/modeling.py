"""
Note: before using, please export OPENAI_API_KEY for vllm, e.g.

export OPENAI_API_KEY="..."
"""

import os
from agentlab.agents.generic_agent.generic_agent import GenericAgentArgs
from agentlab.llm.chat_api import OpenAIModelArgs, OpenRouterModelArgs


"""
Note: before using, please export OPENAI_API_KEY for vllm, e.g.

export OPENAI_API_KEY="..."
"""

import os
from dataclasses import dataclass

from agentlab.agents.generic_agent.generic_agent import GenericAgentArgs
from agentlab.llm.base_api import BaseModelArgs
from agentlab.llm.chat_api import OpenAIModelArgs, OpenRouterModelArgs, ChatModel
import agentlab.llm.tracking as tracking
from openai import OpenAI

class OpenAICompatibleChatModel(ChatModel):
    def __init__(
        self, 
        model_name,
        api_key_env_var,
        base_url_env_var,
        api_key=None,
        base_url=None,
        temperature=0.5,
        max_tokens=1024,
        max_retry=4,
        min_retry_wait_time=60,
    ):
        if not api_key_env_var in os.environ:
            raise ValueError(f"{api_key_env_var} must be set in the environment")
        if not base_url_env_var in os.environ:
            raise ValueError(f"{base_url_env_var} must be set in the environment")

        if base_url is None:
            base_url = os.environ[base_url_env_var]
        
        super().__init__(
            model_name=model_name,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            max_retry=max_retry,
            min_retry_wait_time=min_retry_wait_time,
            api_key_env_var=api_key_env_var,
            client_class=OpenAI,
            client_args={
                "base_url": base_url,
            },
            pricing_func=tracking.get_pricing_openai,
        )

@dataclass
class VllmModelArgs(BaseModelArgs):
    """Serializable object for instantiating a generic chat model with an OpenAI
    model."""

    def set_base_url(self, base_url):
        self.base_url = base_url

    def set_api_key(self, api_key):
        self.api_key = api_key
    
    def make_model(self):
        base_url = None if not hasattr(self, "base_url") else self.base_url
        api_key = None if not hasattr(self, "api_key") else self.api_key
        
        return OpenAICompatibleChatModel(
            model_name=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_new_tokens,
            api_key_env_var="VLLM_API_KEY",
            base_url_env_var="VLLM_BASE_URL",
            base_url=base_url,
            api_key=api_key,
        )

@dataclass
class TogetherModelArgs(BaseModelArgs):
    """Serializable object for instantiating a generic chat model with an OpenAI
    model."""

    def make_model(self):
        return OpenAICompatibleChatModel(
            model_name=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_new_tokens,
            api_key_env_var="TOGETHER_API_KEY",
            base_url_env_var="TOGETHER_BASE_URL",
        )


def get_default_flags(
    use_screenshot=True,
    use_som=True,
    max_prompt_tokens=16384 - 4096,
    enable_chat=False,
):

    from agentlab.agents import dynamic_prompting as dp
    from agentlab.agents.generic_agent.generic_agent import GenericPromptFlags
    from browsergym.experiments.benchmark import HighLevelActionSetArgs

    flags = GenericPromptFlags(
        obs=dp.ObsFlags(
            use_html=False,
            use_ax_tree=True,
            use_focused_element=True,
            use_error_logs=True,
            use_history=True,
            use_past_error_logs=False,
            use_action_history=True,
            use_think_history=False,
            use_diff=False,
            html_type="pruned_html",
            use_screenshot=use_screenshot,
            use_som=use_som,
            extract_visible_tag=True,
            extract_clickable_tag=True,
            extract_coords="False",
            filter_visible_elements_only=False,
        ),
        action=dp.ActionFlags(
            action_set=HighLevelActionSetArgs(
                subsets=["bid"],
                multiaction=False,
            ),
            long_description=False,
            individual_examples=False,
        ),
        use_plan=False,
        use_criticise=False,
        use_thinking=True,
        use_memory=False,
        use_concrete_example=True,
        use_abstract_example=True,
        use_hints=True,
        enable_chat=enable_chat,
        max_prompt_tokens=max_prompt_tokens,
        be_cautious=True,
        extra_instructions=None,
    )

    return flags

def prepare_vllm_model(
    model_name="meta-llama/Llama-3.2-90B-Vision-Instruct",
    max_new_tokens=1024,
    max_prompt_tokens=16384 - 4096,
    max_total_tokens=16384,
    use_vision=True,
    enable_chat=False,
    base_url=None,
    api_key=None,
):
    # the base url and api key are set in VllmModelArgs's make_model,
    # so it is not necessary to set them here, but it is possible if needed
    model_args = VllmModelArgs(
        model_name=model_name,
        max_total_tokens=max_total_tokens,
        max_input_tokens=max_total_tokens - max_new_tokens,
        max_new_tokens=max_new_tokens,
        vision_support=use_vision,
    )
    if base_url is not None:
        model_args.set_base_url(base_url)
    if api_key is not None:
        model_args.set_api_key(api_key)

    agent_args = GenericAgentArgs(
        chat_model_args=model_args,
        flags=get_default_flags(
            max_prompt_tokens=max_prompt_tokens,
            use_som=use_vision,
            use_screenshot=use_vision,
            enable_chat=enable_chat,
        ),
    )

    return agent_args


def prepare_together(
    model_name="meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
    max_new_tokens=1024,
    max_prompt_tokens=16384 - 4096,
    max_total_tokens=16384,
    use_vision=True,
    use_som=True,
):
    agent_args = GenericAgentArgs(
        chat_model_args=TogetherModelArgs(
            model_name=model_name,
            max_total_tokens=max_total_tokens,
            max_input_tokens=max_total_tokens - max_new_tokens,
            max_new_tokens=max_new_tokens,
            vision_support=use_vision,
            # the base url and api key are set in TogetherModelArgs's make_model
        ),
        flags=get_default_flags(
            max_prompt_tokens=max_prompt_tokens,
            use_screenshot=use_vision,
            use_som=use_som,
        ),
    )

    return agent_args


def prepare_gpt(
    model_name="gpt-4o-mini-2024-07-18",
    max_new_tokens=1024,
    max_prompt_tokens=16384 - 4096,
    max_total_tokens=16384,
    use_vision=True,
    use_som=True,
    enable_chat=False,
):
    agent_arg = GenericAgentArgs(
        chat_model_args=OpenAIModelArgs(
            model_name=model_name,
            max_total_tokens=max_total_tokens,
            max_input_tokens=max_total_tokens - max_new_tokens,
            max_new_tokens=max_new_tokens,
            vision_support=use_vision,
        ),
        flags=get_default_flags(
            max_prompt_tokens=max_prompt_tokens,
            use_screenshot=use_vision,
            use_som=use_som,
            enable_chat=enable_chat,
        ),
    )

    return agent_arg


def prepare_claude(
    model_name="anthropic/claude-3.5-sonnet-20240620",
    max_new_tokens=1024,
    max_prompt_tokens=16384 - 4096,
    max_total_tokens=16384,
    use_vision=True,
    use_som=True,
    enable_chat=False,
):
    agent_arg = GenericAgentArgs(
        chat_model_args=OpenRouterModelArgs(
            model_name=model_name,
            max_total_tokens=max_total_tokens,
            max_input_tokens=max_total_tokens - max_new_tokens,
            max_new_tokens=max_new_tokens,
            vision_support=use_vision,
        ),
        flags=get_default_flags(
            max_prompt_tokens=max_prompt_tokens,
            use_screenshot=use_vision,
            use_som=use_som,
            enable_chat=enable_chat
        ),
    )

    return agent_arg

def prepare_gemini(
    model_name="google/gemini-2.0-flash-001",
    max_new_tokens=1024,
    max_prompt_tokens=16384 - 4096,
    max_total_tokens=16384,
    use_vision=True,
    use_som=True,
    enable_chat=False,
):
    agent_arg = GenericAgentArgs(
        chat_model_args=OpenRouterModelArgs(
            model_name=model_name,
            max_total_tokens=max_total_tokens,
            max_input_tokens=max_total_tokens - max_new_tokens,
            max_new_tokens=max_new_tokens,
            vision_support=use_vision,
        ),
        flags=get_default_flags(
            max_prompt_tokens=max_prompt_tokens,
            use_screenshot=use_vision,
            use_som=use_som,
            enable_chat=enable_chat
        ),
    )

    return agent_arg


# def prepare_llama_90b(
#     base_url="http://localhost:8080/v1",
#     model_name="meta-llama/Llama-3.2-90B-Vision-Instruct",
#     max_new_tokens = 512,
#     max_prompt_tokens = 512,
#     max_total_tokens = 4096,
# ):
#     os.environ["OPENAI_BASE_URL"] = os.getenv("OPENAI_BASE_URL", base_url)

#     agent_args = GenericAgentArgs(
#         chat_model_args=OpenAIModelArgs(
#             model_name=model_name,
#             max_total_tokens=max_total_tokens,
#             max_input_tokens=max_total_tokens - max_new_tokens,
#             max_new_tokens=max_new_tokens,
#             vision_support=True,
#         ),
#         flags=get_custom_flags(
#             max_prompt_tokens=max_prompt_tokens,
#         ),
#     )

#     return agent_args


# def prepare_qwen2(
#     base_url="http://localhost:8081/v1",
#     model_name="Qwen/Qwen2-VL-72B-Instruct",
#     max_new_tokens = 1024,
#     max_prompt_tokens = 2048,
#     max_total_tokens = 16384,
# ):
#     os.environ["OPENAI_BASE_URL"] = os.getenv("OPENAI_BASE_URL", base_url)


#     agent_args = GenericAgentArgs(
#         chat_model_args=OpenAIModelArgs(
#             model_name=model_name,
#             max_total_tokens=max_total_tokens,
#             max_input_tokens=max_total_tokens - max_new_tokens,
#             max_new_tokens=max_new_tokens,
#             vision_support=True,
#         ),
#         flags=get_custom_flags(
#             max_prompt_tokens=max_prompt_tokens,
#         ),
#     )

#     return agent_args

# def prepare_llama_90b_together(
#     base_url="https://api.together.xyz/v1",
#     model_name="meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
#     max_new_tokens = 1024,
#     max_prompt_tokens = 2048,
#     max_total_tokens = 16384,
# ):
#     os.environ["OPENAI_BASE_URL"] = base_url

#     agent_args = GenericAgentArgs(
#         chat_model_args=OpenAIModelArgs(
#             model_name=model_name,
#             max_total_tokens=max_total_tokens,
#             max_input_tokens=max_total_tokens - max_new_tokens,
#             max_new_tokens=max_new_tokens,
#             vision_support=True,
#         ),
#         flags=get_custom_flags(
#             max_prompt_tokens=max_prompt_tokens,
#         ),
#     )

#     return agent_args

# def prepare_qwen2_together(
#     base_url="https://api.together.xyz/v1",
#     model_name="Qwen/Qwen2-VL-72B-Instruct",
#     max_new_tokens = 1024,
#     max_prompt_tokens = 2048,
#     max_total_tokens = 16384,
# ):
#     os.environ["OPENAI_BASE_URL"] = base_url

#     agent_args = GenericAgentArgs(
#         chat_model_args=OpenAIModelArgs(
#             model_name=model_name,
#             max_total_tokens=max_total_tokens,
#             max_input_tokens=max_total_tokens - max_new_tokens,
#             max_new_tokens=max_new_tokens,
#             vision_support=True,
#         ),
#         flags=get_custom_flags(
#             max_prompt_tokens=max_prompt_tokens,
#         ),
#     )

#     return agent_args

# def prepare_4o(
#     model_name = "gpt-4o-mini-2024-07-18",
#     max_new_tokens = 1024,
#     max_prompt_tokens = 2048,
#     max_total_tokens = 16384
# ):
#     agent_arg = GenericAgentArgs(
#         chat_model_args=OpenAIModelArgs(
#             model_name=model_name,
#             max_total_tokens=max_total_tokens,
#             max_input_tokens=max_total_tokens - max_new_tokens,
#             max_new_tokens=max_new_tokens,
#             vision_support=True,
#         ),
#         flags=get_custom_flags(max_prompt_tokens=max_prompt_tokens),
#     )

#     return agent_arg

# def prepare_claude(
#     model_name="anthropic/claude-3.5-sonnet-20240620",
#     max_new_tokens=1024,
#     max_prompt_tokens=2048,
#     max_total_tokens=16384,
#     enable_vision=True,
# ):
#     model_args = OpenRouterModelArgs(
#         model_name=model_name,
#         max_total_tokens=max_total_tokens,
#         max_input_tokens=max_total_tokens - max_new_tokens,
#         max_new_tokens=max_new_tokens,
#         temperature=0.1,
#         vision_support=enable_vision,
#     )

#     agent_arg = GenericAgentArgs(
#         chat_model_args=model_args,
#         flags=get_custom_flags(
#             max_prompt_tokens=max_prompt_tokens, use_screenshot=enable_vision, use_som=enable_vision
#         ),
#     )

#     return agent_arg
