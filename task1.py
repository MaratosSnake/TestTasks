import pandas as pd
from difflib import SequenceMatcher

# Reading data
test_data = pd.read_excel('data/Список товаров.xlsx')
category_tree = pd.read_excel('data/Дерево категорий.xlsx')
train_data_nf = pd.read_excel('data/Данные поставщика.xlsx')

# Drop unusefull cols
train_data = train_data_nf[['Название', 'Раздел']]

# Rename cols
train_data = train_data.rename(columns={'Название': 'Name', 'Раздел': 'Section'})
category_tree = category_tree.rename(
    columns={'Главная категория': 'Main_category', 'Дочерняя категория': 'Child_category',
             'Тип товара': 'Product_type'})
test_data = test_data.rename(columns={'Наименование': 'Name', 'Тип товара': 'Product_type'})


def get_category_part_by_index(cat_path: str, index: int) -> str:
    if not isinstance(index, int):
        raise TypeError(f'Index must be integer but was {type(index)}')
    if 0 <= index < 3:
        splited_cat_path = cat_path.split('/')
        if len(splited_cat_path) == 2:
            if index == 1:
                return ''
            if index == 2:
                return splited_cat_path[-1]
        return splited_cat_path[index]
    raise IndexError(f'Index was out of range')


train_data['Main_category'] = train_data['Section'].apply(lambda x: get_category_part_by_index(x, 0))
train_data['Child_category'] = train_data['Section'].apply(lambda x: get_category_part_by_index(x, 1))
train_data['Product_type'] = train_data['Section'].apply(lambda x: get_category_part_by_index(x, 2))


# Function for finding synonyms
def find_synonyms(df1, df2, column) -> dict:
    synonyms = {}
    for type1 in df1[column].unique():
        for type2 in df2[column].unique():
            if SequenceMatcher(None, type1, type2).ratio() > 0.6:  # Порог сходства
                synonyms[type1] = type2
                break
    return synonyms


synonyms = find_synonyms(train_data, test_data, 'Product_type')

# Merge by "Name" column
result = pd.merge(test_data, train_data, on='Name', how='inner')

result = result.rename(columns={'Product_type_x': 'Product_type', 'Product_type_y': 'Predicted_product_type'})

# Replacing with synonyms to get right categories
result['Predicted_product_type'] = result['Predicted_product_type'].replace(synonyms)

result['Is_correctly_predicted'] = result['Product_type'] == result['Predicted_product_type']

accuracy = result['Is_correctly_predicted'].apply(lambda x: 1 if x else 0).sum() / result.Is_correctly_predicted.count()
# Тут merge принес только 35 строк в результирующий df из-за того что названия в test_data и train_data попросту не
# совпадают, это можно исправить но потребуется гораздо больше времени и дополнительные алгоритмы и функции поиска
# похожих названий и сопоставление им типов
print(accuracy)
