import pandas as pd
import plotly.graph_objects as go
import os

# Функция для чтения данных из файла CSV, если файл существует
def read_csv_file(file_name):
    if os.path.exists(file_name):
        return pd.read_csv(file_name)
    else:
        return None

# Чтение данных из файлов CSV
data = read_csv_file('ss_data_backup.csv')

if data is not None:
    # Фильтрация строк, где message_type не равен 'Comment'
    filtered_data = data[data['message_type'] != 'Comment'].copy()

    # Проверка типа данных столбца 'time_base' и преобразование в datetime, если необходимо
    if not pd.api.types.is_datetime64_any_dtype(filtered_data['time_base']):
        filtered_data['time_base'] = pd.to_datetime(filtered_data['time_base'])

    # Создание полного списка дат и часов
    date_range = pd.date_range(start=filtered_data['time_base'].min().floor('H'),
                               end=filtered_data['time_base'].max().ceil('H'), freq='H')
    hours_range = pd.DataFrame({'time_base': date_range})

    # Группировка данных по часам и подсчет публикаций
    publications_per_hour = filtered_data.groupby(filtered_data['time_base'].dt.floor('H')).size().reindex(date_range, fill_value=0).reset_index(name='Publications')

    # Запись данных в файл publications_per_hour_not_comments.csv
    csv_file_filtered_per_hour = 'publications_per_hour_not_comments.csv'
    publications_per_hour.to_csv(csv_file_filtered_per_hour, index=False)

    # Замена пустых значений в столбце 'blog' на значения из столбца 'author'
    filtered_data.loc[filtered_data['blog'].isnull(), 'blog'] = filtered_data['author']

    # Проверка типа данных столбца 'time_base' и преобразование в datetime, если необходимо
    if not pd.api.types.is_datetime64_any_dtype(filtered_data['time_base']):
        filtered_data['time_base'] = pd.to_datetime(filtered_data['time_base'])

    # Фильтрация данных по определенной части текста в столбце 'blog'
    sorted_data = filtered_data[filtered_data['blog'].str.contains('M125|М125', case=False, na=False)]

    # Создание полного списка дат и часов
    date_range = pd.date_range(start=sorted_data['time_base'].min().floor('D'),
                               end=sorted_data['time_base'].max().ceil('D'), freq='H')
    hours_range = pd.DataFrame({'time_base': date_range})

    # Группировка данных по часам и подсчет публикаций
    publications_per_hour = sorted_data.groupby(sorted_data['time_base'].dt.floor('H')).size().reindex(date_range, fill_value=0).reset_index(name='Publications')

    # Обновление данных в существующем CSV файле или создание нового
    csv_file = 'publications_per_hour_full.csv'
    try:
        existing_data = pd.read_csv(csv_file)
        existing_data['time_base'] = hours_range['time_base']
        existing_data['Publications'] = publications_per_hour['Publications']
    except FileNotFoundError:
        existing_data = pd.concat([hours_range, publications_per_hour['Publications']], axis=1)

    # Экспорт данных в CSV файл
    existing_data.to_csv(csv_file, index=False)

    # Создание списка периодов по 24 часа с шагом в 1 час
    periods = pd.date_range(start=filtered_data['time_base'].min().floor('H'),
                            end=filtered_data['time_base'].max().ceil('H'),
                            freq='1H').to_list()

    results = []

    for i in range(len(periods) - 24):  # Проходим по периодам с окном в 24 часа
        start_period = periods[i]
        end_period = periods[i + 24]

        # Фильтрация данных для текущего периода
        current_period_data = filtered_data[(filtered_data['time_base'] >= start_period) &
                                            (filtered_data['time_base'] < end_period)].copy()

        # Подсчет количества публикаций со значением '125'
        publications_125 = len(current_period_data[current_period_data['blog'].str.contains('M125|М125', case=False, na=False)])

        # Общее количество публикаций в текущем периоде
        total_publications = len(current_period_data)

        # Расчет процента
        if total_publications > 0:
            percent_125 = (publications_125 / total_publications) * 100
        else:
            percent_125 = 0

        # Добавление результатов в список
        results.append({
            'Start Period': start_period,
            'End Period': end_period,
            'Publications with 125': publications_125,
            'Total Publications': total_publications,
            'Percent 125': percent_125
        })

    # Создание DataFrame из результатов
    result_df = pd.DataFrame(results)

    # Экспорт данных в CSV файл
    csv_file = 'percentages_per_24_hour_periods.csv'
    result_df.to_csv(csv_file, index=False)

    # Построение интерактивного графика
    fig = go.Figure()

    # Добавление графика с процентами
    fig.add_trace(go.Scatter(x=result_df['Start Period'], y=result_df['Percent 125'], mode='lines+markers', name='Percent 125'))

    # Настройка макета графика
    fig.update_layout(
        title='Процент публикаций со значением "125"',
        xaxis_title='Начальная дата периода',
        yaxis_title='Процент 125',
        hovermode='x unified'
    )

    # Отображение графика
    fig.show()

else:
    print("Файл 'ss_data_backup.csv' не найден.")