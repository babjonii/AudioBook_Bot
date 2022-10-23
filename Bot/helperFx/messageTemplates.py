import emoji
from jinja2 import Template

audio_item = Template(
    """
{{number}}  <strong>Title:</strong> {{Title}}
    <strong>Author:</strong> {{Author}}

"""
)
download_template = Template(
    """
{% if state == True %}
<strong>Downloading  <code>{{name}}</code></strong>{{emoji}}
{% else %}
<strong>Download Complete  <code>{{name}}</code></strong>{{emoji}}
{% endif %}
"""
)
