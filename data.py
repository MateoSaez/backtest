import pandas as pd
import numpy as np

class Data:

    def __init__(self):
        self.assets_df = pd.read_csv('INDEX.csv', index_col='ID')
        self.data_df = pd.read_csv('DATA.csv', sep=';', index_col='DATE', parse_dates=True).dropna(how='all')
        self.types = self.assets_df.TIPO.unique()
        self.ccys = {
            'Europe': 'EUR',
            'Swiss': 'CHF',
            'UK': 'GBP',
            'Japan': 'sdfJPY',
            'Canada': 'CAD',
            'Pacific': 'AUD',
            'USA': 'USD'
        }
        self.geos = dict(enumerate(self.assets_df.GEO.unique().flatten(),1))
        self.geos[8] = 'Global'

    # Comprueba el rango de datos disponibles (FECHAS) en función de los datos base para mostrarlos
    def __getDatesRange__(self, assets_df, data_df):
        for asset in data_df:
            assets_df.loc[asset, 'MIN_DATE'] = data_df[asset].dropna().index.min()
            assets_df.loc[asset, 'MAX_DATE'] = data_df[asset].dropna().index.max()
        return assets_df

    def av_ccys(self, geo):
        av_ccys = self.assets_df[self.assets_df.CCY == self.ccys[geo]]

    # FILTRA los activos disponibles en base a una serie de condiciones
    def filter(self, type=None, ccy=None, geo=None, id=None):
        # Devuelve una lista con los activos filtrados
        filtered_df = self.__getDatesRange__(self.assets_df, self.data_df)
        if type:
            filtered_df = filtered_df[(filtered_df.TIPO == type)]
        if ccy:
            if geo == self.geos[8]:
                pass
            else:
                filtered_df = filtered_df[(filtered_df.CCY == ccy)]
        if geo:
            if geo == self.geos[8]:
                pass
            else:
                filtered_df = filtered_df[(filtered_df.GEO == geo)]
        if id:
            filtered_df = filtered_df[np.isin(filtered_df.index, id)]

        return filtered_df

    # Asignación de activos elegidos para almacenar en memoria
    def assign_assets(self, type=None, ccy=None, geo=None):
        assets_filtered_df = self.filter(type=type, ccy=ccy, geo=geo).reset_index()

        while True:
            print(assets_filtered_df)
            selected = int(input(f'{type}: '))
            print('\n')
            if selected in list(assets_filtered_df.index):
                return assets_filtered_df['ID'].loc[selected]
            print('No se encuentra el valor')

    # Comprueba las fechas disponibles en base a los activos elegidos
    def dates_range(self, selected_assets):
        min_date = selected_assets['MIN_DATE'].max() + pd.Timedelta(days=1)
        max_date = selected_assets['MAX_DATE'].min()
        return min_date, max_date

    # Depuración de los datos en base a los datos obtenidos previamente
    def get_data(self, selected_assets, min_date, max_date):
         return self.data_df.loc[min_date:max_date, selected_assets]




