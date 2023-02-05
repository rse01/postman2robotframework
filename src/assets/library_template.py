import requests

if variables and len(variables) > 0:
    from string import Template

class {{ name }}:
    {% for item in items %}

    def {{ item.def_name }}(self{% for var in item.variables %}, {{ var }}{% endfor %}):
        """
        {{ item.documentation }}
        """
        url = (Template("{{ item.url }}").substitute({% for var in item.variables %}{{ var }}={{ var }}{{ "," if not loop.last }}{% endfor %})) if item.variables and len(item.variables) > 0 else "{{ item.url }}"
        method = "{{ item.method }}"
        headers = {{ item.header }}
        data = (Template("{{ item.body | replace('\n','\\n') | replace('\"','\\"') }}").substitute({% for var in item.variables %}{{ var }}={{ var }}{{ "," if not loop.last }}{% endfor %})) if item.body and item.variables and len(item.variables) > 0 else "{{ item.body | replace('\n','\\n') | replace('\"','\\"') }}" if item.body else None
        response = requests.request(method, url, headers=headers, data=data if data else None)
        return response.text
    {% endfor %}
