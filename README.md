## Prof-X: AI Assisted Multi-view Persona Scraper for Any Researchers in Google Scholar
> Still a WIP now, use at your own risk!

### Things you need
- An OpenAI API key
  - For AI assisted info gathering
  - Could be replaced by any local OpenAI-like API <WIP\>
  - But original OpenAI API is still recommended, as it could provide a far better result
- A Tencent Translate API Key
  - For translating article names into your language 
  - Chinese only currently :) Will add multilingual support after on


### Environment Preparation

First, install all the python requirements.
<pre><code>$ pip install -r requirements.txt
</code></pre>

Then, rename `config_example.py` to `config.py`, and fill in the config parameters.

<pre><code>LOCAL_API_BASE = "https://my.api.link/v1"
REMOTE_API_BASE = "https://api.openai.com/v1"

OPENAI_KEY = "sk-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
TX_SECRET_ID = "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"
TX_SECRET_KEY = "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC"
</code></pre>

### Running

<pre><code>$ python prof_persona.py
</code></pre>