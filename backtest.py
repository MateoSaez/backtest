import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


class Backtest:

    def __init__(self, data, peso_inicial=0.25, base=100):
        self.data = data.pct_change().dropna()
        self.peso_inicial = peso_inicial
        self.base = base


    def __setDataFrame__(self, axis):
        # Se encarga de preconfigurar los dataframes necesarios para el cálculo
        index = axis['index']
        columns = axis['columns']

        constructor_df = pd.DataFrame(index=index, columns=columns)

        weight_df = pd.DataFrame(index=index, columns=columns)
        weight_df.iloc[0] = self.peso_inicial

        value_df = pd.DataFrame(index=index, columns=columns)

        balance_df = pd.DataFrame(index=index, columns=['ActivoSobrepasa', 'Up_Down'])

        df = {'constructor': constructor_df, # FINAL DEL DÍA / 4 ACTIVOS
              'weights': weight_df, # PRINCIPIO DEL DÍA / 4 ACTIVOS
              'value': value_df, # FINAL DEL DÍA / 4 ACTIVOS
              'balance': balance_df}
        return df

    def __balanceDF__(self, balance, check, tols):
        #Recibe la matriz de sobrepaso de tolerancia y apunta esos excedentes en la matriz "balance"
        asset = check.any(axis=0).index[check.any(axis=0)][0]
        date= check.any(axis=1).index[check.any(axis=1)][0]
        weight = check.loc[date, asset]
        balance['ActivoSobrepasa'].loc[date] = asset
        if weight > tols['up']:
            balance['Up_Down'].loc[date] = 'Up'
        elif weight < tols['down']:
            balance['Up_Down'].loc[date] = 'Down'
        return balance, date

    def __checkBalance__(self, weights_df, tols):
        #Recibe la matriz de pesos para devolver la matriz donde se sobrepasan los límites de tolerancia
        check_df = weights_df[(weights_df > tols['up']) | (weights_df < tols['down'])].dropna(how='all')
        return check_df

    def __weightsRefactor__(self, constructor):
        #Recibe el constructor para recalcular los pesos de los activos en función de CADA rebalanceo
        shifted_constructor = constructor.shift(periods=1, fill_value=self.peso_inicial)
        sum_constructor = constructor.shift(periods=1, fill_value=self.peso_inicial).sum(axis=1)
        weights = shifted_constructor.div(sum_constructor, axis=0)
        return weights

    def __buildConstructor__(self, value, constructor, date_cross):
        #Recibe el constructor y recalcula sus valores a partir de la fecha de rebalanceo "date_cross"
        day = constructor.index.get_loc(date_cross)
        num_assets = value.columns.size
        constructor.iloc[day] = value.iloc[day] * constructor.iloc[day - 1].sum() / num_assets
        constructor.iloc[day + 1:] = value.iloc[day + 1:]
        constructor.iloc[day:] = np.cumprod(constructor.iloc[day:])
        return constructor, day

    def __calculateFinalDF__(self, base_df, rent_df, down_tol, up_tol):
        base_df['value'] = rent_df + 1
        base_df['constructor'] = np.cumprod(base_df['value'])
        base_df['weights'] = self.__weightsRefactor__(base_df['constructor'])
        day_iloc = -1
        while True:
            #COMPROBAMOS SI EXISTE ACTIVACIÓN DE REBALANCEO. POR ORDEN
            check_df = self.__checkBalance__(base_df['weights'].iloc[day_iloc + 1:], {'down': down_tol, 'up': up_tol})
            if not check_df.empty:
                #DEVUELVE EL DF QUE ACTIVA REBALANCEOS Y LA PRIMERA FECHA DE ACTUACIÓN
                base_df['balance'], date_cross = self.__balanceDF__(base_df['balance'], check_df, {'down': down_tol, 'up': up_tol})
                #RECALCULAR el CONSTRUCTOR
                base_df['constructor'], day_iloc = self.__buildConstructor__(base_df['value'], base_df['constructor'], date_cross)
                #RECALCULAR PESOS
                base_df['weights'] = self.__weightsRefactor__(base_df['constructor'])
            else:
                base_df['balance'] = base_df['balance'].dropna()
                return base_df['weights'], base_df['balance']

    def __calculateComposition__(self, weights_df, rent_df):
        # Calcula la serie de Rentabilidades y devuelve el Número Índice
        previous_day = rent_df.index[0]+pd.Timedelta(days=-1)
        final_datetimeindex = rent_df.index.union([previous_day])
        calc_composition = weights_df.mul(rent_df).sum(axis=1) + 1
        composition_rent_df = pd.DataFrame(calc_composition, index=final_datetimeindex, columns=['Composition'])
        composition_rent_df.loc[str(previous_day)] = 1
        composition_perf = np.cumprod(composition_rent_df) * self.base
        return composition_perf , composition_rent_df

    #CÁLCULOS PRINCIPALES
    def calculate(self, down_tol, up_tol):
        #Cálculo principal del backtest
        rent_df = self.data
        axis = {'index': rent_df.index, 'columns': rent_df.columns}
        base_df = self.__setDataFrame__(axis)
        weights_df, balance_df = self.__calculateFinalDF__(base_df, rent_df, down_tol, up_tol)
        composition_perf, daily_value = self.__calculateComposition__(weights_df, rent_df)

        return composition_perf, daily_value

    #CALCULO DE MÉTRICAS
    def retorno_anual(self, composition_perf):
        #Devuelve una Serie con el retorno acumulado en cada fecha
        fd_value, fd_date = (composition_perf.iloc[0, 0], composition_perf.iloc[0].name)
        ld_value, ld_date = (composition_perf.iloc[-1, 0], composition_perf.iloc[-1].name)
        period =(ld_date - fd_date).days
        annual_return = (ld_value / fd_value)**(365/period) - 1
        return annual_return

    def drawdown(self, composition_perf):
        #Devuelve el DrawDown de la composición
        drawdown = composition_perf.div(np.maximum.accumulate(composition_perf)) - 1
        max_DD = drawdown.min()[0]
        max_DD_date = drawdown[drawdown == max_DD].dropna().index
        # max_DD = {'Date': max_DD_date, 'Max_DD': max_DD}
        return drawdown, max_DD

    def plot(self, composition_perf):
        #Plotear resultados
        composition_perf.plot.line()
        self.drawdown(composition_perf)[0].plot.area()
        plt.show()

    def metrics(self, composition_perf):
        metrics = {
            'Retorno anual' : self.retorno_anual(composition_perf),
            'Máximo DD' : self.drawdown(composition_perf)[1]
        }
        return metrics


if __name__ == "main":

    data = pd.read_excel('Prueba.xlsx', usecols='C:G', nrows=10, sheet_name='Hoja1', index_col='Date')
    backtest = Backtest(data)

    agg_value, daily_value = backtest.calculate(0.15, 0.35)

    backtest.drawdown(agg_value)

