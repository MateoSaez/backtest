import numpy as np
from data import Data
from backtest import Backtest

print('BIENVENIDO AL BACKTEST')
assets = Data()
print(assets.assets_df)
#Bloque para definir los DATOS y darles forma
while True:
    print('\n')
    print('GEOGRAFíAS DISPONIBLES: ')
    for k, v in assets.geos.items():
        print(f'{k} - {v}')
    print('___________________')
    print('0 - Exit')
    geo_key = int(input('Seleccionar una opción: '))

    if geo_key  == 0:
        exit()

    print('\n')
    print('DIVISA: ')
    print('\n')
    print('1 - Divisa Local')
    print('2 - EUR')
    print('___________________')
    print('0 - Exit')
    ccy_key = int(input('Seleccionar una opción: '))
    print('\n')

    if ccy_key  == 0:
        exit()

    if geo_key in list(assets.geos.keys()) and ccy_key in [0, 1, 2]:
        geo_value = assets.geos[geo_key]
        if ccy_key == 1:
            ccy_value = 'EUR'
        if ccy_key == 2:
            ccy_value = assets.ccys[geo_value]

        filtered_assets = assets.filter(geo=geo_value, ccy=ccy_value)

        filt_assets_uniq = filtered_assets.TIPO.unique()

        # Comprueba si la lista de activos incluye al menos 1 de cada tipo
        check_type = any(np.isin(assets.types, filt_assets_uniq, invert=True))

        if check_type:
            missing_assets = assets.types[np.isin(assets.types, filt_assets_uniq, invert=True)]
            print('Hemos detectado que para completar el backtest faltan los siguientes activos en la base de datos:')
            for asset in missing_assets:
                print(asset)
            print(f'Actualizar la base de datos para realizar un backtest de {geo_value}')
        else:
        # Acepta el continuar con el proceso
            print(f'Vamos a calcular un backtest sobre: {geo_value}')
            print(f'Los activos para {geo_value} son los siguientes: ')
            print(filtered_assets)
        # Bloque para seleccionar un activo para cada tipo
            print('\n')
            print('Indicar qué activo utilizar para cada parte de la composición:')
            print('\n')
            selected_assets_dict = {'DATE': 'DATE'}
            for asset in assets.types:
                selected_assets_dict[asset] = assets.assign_assets(type=asset, geo=geo_value, ccy=ccy_value)
            print('Ha elegido los siguientes activos: ')
            print('\n')
            selected_assets_df = assets.filter(id=list(selected_assets_dict.values()))
            print(selected_assets_df)
            min_date, max_date = assets.dates_range(selected_assets_df)
            print('\n')
            print(f'El cálculo se realizará desde el {min_date.date()} hasta el {max_date.date()}')
            print('__________________________________________________________________')
            print('\n')
            assets_data = assets.get_data(list(selected_assets_df.index), min_date, max_date)
            backtest = Backtest(assets_data)
            agg_value, daily_value = backtest.calculate(0.15, 0.35)
            metrics = backtest.metrics(agg_value)
            for k, v in metrics.items():
                v = "{:.2%}".format(v)
                print(f'{k} : {v}')
            backtest.plot(agg_value)
            break
    else:
        print('El valor introducido no es válido')











