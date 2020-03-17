{"stages": [
{% for cell in nb.cells if cell.cell_type == "code" and cell.source.strip() and (not cell.source.lstrip().startswith( "%" ) or cell.source.lstrip().startswith( "%arc" )) -%}
  {% if not cell.source.lstrip().startswith( "%arc" ) %}{{ cell.source }}{{ "," if not loop.last }}{% endif %}{% if cell.source.lstrip().startswith( "%arc" ) %}{{ "\n".join(cell.source.split("\n")[1:]) }}{{ "," if not loop.last }}{% endif %}
{% endfor %}]}