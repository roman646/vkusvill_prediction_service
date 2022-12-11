import statsmodels.api as sm
import pandas as pd
import logging
from multiprocessing import Process, Manager


class ProfitabilityModels:
    def __init__(self, sales_data):
        self.data = pd.read_excel(sales_data, engine='openpyxl')
        logging.info('Loading data for prediction')
        self.data['profitability'] = (self.data['sell_price'] * self.data['amount']).pct_change()
        self.STORE_IDS = ['CA_1', 'CA_2', 'CA_3', 'CA_4',
                          'TX_1', 'TX_2', 'TX_3', 'WI_1',
                          'WI_2', 'WI_3']

    def get_data_sample(self, store_id, sample_size=300):
        return self.data[self.data['store_id'] == store_id].reset_index()['profitability'][-sample_size:]

    @staticmethod
    def _make_single_prediction(data_sample, store_id, results, n_weeks2predict=10, model_order=(38, 0, 38)):
        try:
            model = sm.tsa.arima.ARIMA(data_sample, order=model_order).fit()
            forecast_values = model.forecast(n_weeks2predict).values
            result = pd.DataFrame()
            result['day'] = [i + 1 for i in range(n_weeks2predict)]
            result['profitability_prediction'] = forecast_values
            result['amount_prediction'] = data_sample.iloc[-1] + (forecast_values * data_sample.iloc[-1] / 100)
            result['store_id'] = store_id
            results[store_id] = result
            logging.info(f'successfully predicted for store_id = {store_id}')
        except Exception as e:
            logging.error(f'Some error with prediction for store_id = {store_id}')
            logging.error(str(e))

    def make_predictions(self):
        processors = []
        with Manager() as manager:
            results = manager.dict()

            for store_id in self.STORE_IDS:
                data_sample = self.get_data_sample(store_id)
                logging.info(f'Model for {store_id} is fitting..')
                p = Process(target=self._make_single_prediction, args=(data_sample, store_id, results))
                p.start()
                processors.append(p)

            for processor in processors:
                processor.join()

            logging.info('Results are ready!')
            return pd.concat(results.values())


def is_allowed_file(filename):
    return str(filename).split('.')[-1] in ('xlsx', 'xls')
