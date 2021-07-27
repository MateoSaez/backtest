from data import Data
from backtest import Backtest
import justpy as jp
app = jp.app

def hello_world():
    wp = jp.WebPage()
    d = jp.Div(text='Hello world!')
    wp.add(d)
    return wp

jp.justpy(hello_world, start_server=False)