from main_app.models import Smartphone
from django import template

from main_app.models import Smartphone

register = template.Library()

TABLE_HEAD = '''
<table class="table">   
    <tbody>
'''

TABLE_TAIL = '''
  </tbody>
</table>
'''

TABLE_CONTENT = '''
    <tr>
      <td class='pt-3 pb-3'>{key}</td>
      <td>{value}</td>
    </tr>
'''


PRODUCT_SPEC = {
    'notebook': {
        'Диагональ':  'diagonal',
        'Тип дисплея': 'display_type',
        'Процессор': 'processor_freq',
        'Оперативная память': 'ram',
        'Видеокарта': 'video',
        'Аккумулятор': 'time_without_charge',
    },
    'smartphone': {
        'Диагональ':  'diagonal',
        'Тип дисплея': 'display_type',
        'Разрежение экрана': "resolution",
        'Оперативная память': 'ram',
        'Присутствие sd': 'sd',
        'Объем sd': 'sd_volume_max',
        'Основная камера': 'main_cam_mp',
        'Фронтальная камера': 'frontal_cam_mp',
        'Аккумулятор': 'accum_volume',
    }
}


def get_product_spec(product, model_name):
    table_content = ''
    for key, value in PRODUCT_SPEC[model_name].items():
        table_content += TABLE_CONTENT.format(key=key, value=getattr(product, value))
    return table_content   


@register.filter
def product_spec(product):
    model_name = product.__class__._meta.model_name
    if isinstance(product, Smartphone):
        if not product.sd:
            PRODUCT_SPEC['smartphone'].pop('Объем sd')
        else:
            PRODUCT_SPEC['smartphone']['Объем sd'] = 'sd_volume_max'
    return TABLE_HEAD + get_product_spec(product, model_name) + TABLE_TAIL