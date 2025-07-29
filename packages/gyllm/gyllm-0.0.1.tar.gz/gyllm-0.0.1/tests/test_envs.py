from transformers import AutoTokenizer
from gyllm.envs.simple.iterated_games import TftIpdEnv



def test_tft():
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-3B-Instruct")
    env = TftIpdEnv(tokenize=tokenizer.apply_chat_template, tokenize_kwargs={"add_generation_prompt": True})

    [request] = env.initialize()

    for t in range(5):
        [request] = env.act({"player": "<action>A</action>"})

    assert request["reward"] == 15