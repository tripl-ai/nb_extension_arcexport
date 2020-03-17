{"stages": [
{% for cell in nb.cells -%}
  {{ cell.source }}{{ "," if not loop.last }}
{% endfor %}]}