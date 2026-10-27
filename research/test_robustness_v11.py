#!/usr/bin/env python3
import sys,unittest,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from methodological_robustness_v11 import percentile,median,forecast_analysis
import tempfile, csv
class TestRobustness(unittest.TestCase):
 def test_percentile_and_median(self):
  self.assertEqual(median([3,1,2,4]),2.5)
  self.assertEqual(percentile([1,2,3,4,5],0.9),5)
 def test_forecast_rows_recompute(self):
  with tempfile.TemporaryDirectory() as td:
   agg,u=forecast_analysis(Path(td),bootstrap=100)
   self.assertEqual(agg[0]['n'],992)
   self.assertEqual(u['cluster_count'],24)
   self.assertEqual(agg[0]['persistence_MAE'],45.088)
   self.assertEqual(agg[0]['climate_RF_MAE'],50.294)
if __name__=='__main__':unittest.main()
